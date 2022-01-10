import re
import json
import shlex
import subprocess


class Iperf3(object):
    """
    This library uses iPerf3 to measure the bandwidth between two peers.

    The library assumes that iPerf3 is installed and that the executable can be found within the PATH variable.

    The library can also be run as a remote library so that the PC running iPerf3 and connected to the DUT does not have
    to be the same one as the PC running the test. The remote library can be started with:
    | python3 -m robotframework_iperf3 [-a <address>] [-p <port>]

    If an argument expects a bool value it may be given as bool or a string that looks like a bool: ${TRUE}, ${FALSE},
    true, True, false, False are fine.
    """

    def __init__(self):
        self.server = None

    def __del__(self):
        self.stop_server()

    @staticmethod
    def _to_bool(val):
        """
        helper function so that the user can use ${True}, "True" or "true" as bool value. makes life easier in robot.
        """
        val = str(val).lower()

        # check if value is like "true" or "false", else every string NOT "true" will be handled as false.
        if val not in ['true', 'false']:
            raise ValueError("value not bool-like")

        return val == 'true'

    def _int_to_float(self, o):
        """
        converts all integers within an object to float if these integers are not in range of signed int32
        solves <class 'OverflowError'>:int exceeds XML-RPC limits
        """

        if isinstance(o, dict):

            for key, value in o.items():

                if isinstance(value, dict):
                    o[key] = self._int_to_float(value)

                elif isinstance(value, list):
                    for l_index, l_value in enumerate(value):
                        o[key][l_index] = self._int_to_float(l_value)

                else:
                    if isinstance(value, int):
                        if not -(2 ** 31) < value < 2 ** 31:
                            o[key] = float(value)

        elif isinstance(o, list):
            for l_index, l_value in enumerate(o):
                o[l_index] = self._int_to_float(l_value)

        else:
            if isinstance(o, int):
                if not -(2 ** 31) < o < 2 ** 31:
                    o = float(o)

        return o

    def start_server(self, server_port=None, bind_address=None):
        """
        Starts the iPerf3 server which listens on an option port and can be bound to a given address. If a there is
        already a running server the keyword will not start another one.

        Arguments:
            - server_port: (int), port to listen on, default: None (use default iPerf3 port)
            - bind_address: (str), IPv4 or IPv6 address to bind to, default: None (listen on all interfaces)

        Example:
        | Start Server |  |  |
        | Start Server | 11211 |  |
        | Start Server | 11211 | 192.168.1.1 |
        """

        command = f'iperf3 -s -J'

        if server_port:
            command += f' -p {server_port}'

        if bind_address:
            command += f' -B {bind_address}'

        self.server = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        # by design, we do not check if the server start was successful. if run as robotremoteserver, users tend to
        # not stop the server before the test stops or the test ends because of errors and there is no teardown.
        # in that case there is still an iperf3 server instance running which is fine for us in the next run.
        # if the initial server start fails the user will get an error by the iperf3 client anyway.

    def stop_server(self):
        """
        Stops a running iPerf3 server which was started by this library instance. Returns a list of dictionaries with
        statistics for each connected client. See _Run Client_ for an example for such dictionary.
        """
        stats = []

        try:
            self.server.kill()
            stdout, stderr = self.server.communicate()
            stats = [json.loads(js) for js in re.split(r'(?<=})\n(?={)', stdout.decode())]
        except AttributeError:
            pass
        except Exception as e:
            print("*ERROR* error getting statistics: %s" % e)
        finally:
            self.server = None

        return stats

    def run_client(
        self,
        server_address,
        server_port=None,
        bind_address=None,
        protocol='tcp',
        duration=10,
        num_streams=None,
        reverse=False,
        bitrate=None,
        num_bytes=None,
        bidir=False,
        tos=None,
        dscp=None
    ):
        """
        Runs the iPerf3 client. The client connect to the peer given by _server_address_ (and optionally _server_port_).
        The client may bind itself to an interface identified by its _bind_address_.

        Returns a dictionary, see example below

        Arguments:
            - server_address: (str), IPv4 or IPv6 address to connect to
            - server_port: (int), port to connect to, default: None (use default iPerf3 port)
            - bind_address: (str), IPv4 or IPv6 address to bind to, default: None
            - protocol: (str), "tcp" or "udp"
            - duration: (int), time in seconds to transmit for, default: 10
            - num_streams: (int), number of parallel client streams to run, default: None (no parallel streams)
            - reverse: (bool), reverse the direction of a test, so that the server sends data to the client, default:\
             False
            - bitrate: (str), n[KM], set the bitrate to n [K,M]bits/s. Use "0" to disable bitrate limits, default:\
             None (1 Mbit/sec for UDP, unlimited for TCP)
            - num_bytes: (str), n[KM], number of bytes to transmit (instead of duration)
            - bidir: (bool), run in bidirectional mode
            - tos: (int), set the IP type of service. The usual prefixes for octal and hex can be used, i.e. 52, 064\
             and 0x34 all specify the same value
            - dscp: (int), set the IP DSCP bits.  Both numeric and symbolic values are accepted. Numeric values can be\
             specified in decimal, octal and hex

        Example:
        | Run Client | 192.168.1.1 |       |              |            |                 |
        | Run Client | 192.168.1.1 | 11211 |              |            |                 |
        | Run Client | 192.168.1.1 | 11211 | protocol=tcp | duration=5 | bidir=True      |
        | Run Client | 192.168.1.1 | 11211 | protocol=udp | bitrate=5M | reverse=${TRUE} |

        Example for returned dictionary:
            - Note: due to limitations within the XML-RPC protocol int values > 2^32 have to be converted to float when\
             using the Remote library.
        | {
        |   "start": {
        |     "connected": [
        |       {
        |         "socket": 5,
        |         "local_host": "127.0.0.1",
        |         "local_port": 39762,
        |         "remote_host": "127.0.0.1",
        |         "remote_port": 11211
        |       }
        |     ],
        |     "version": "iperf 3.7",
        |     "system_info": "Linux ryzen 5.13.0-22-generic #22~20.04.1-Ubuntu SMP Tue Nov 9 15:07:24 UTC 2021 x86_64",
        |     "timestamp": {
        |       "time": "Mon, 13 Dec 2021 09:06:27 GMT",
        |       "timesecs": 1639386387
        |     },
        |     "connecting_to": {
        |       "host": "127.0.0.1",
        |       "port": 11211
        |     },
        |     "cookie": "stk3tj6ajh4ezai5uzkdixxujsif77wxz7um",
        |     "tcp_mss_default": 32768,
        |     "sock_bufsize": 0,
        |     "sndbuf_actual": 16384,
        |     "rcvbuf_actual": 131072,
        |     "test_start": {
        |       "protocol": "TCP",
        |       "num_streams": 1,
        |       "blksize": 131072,
        |       "omit": 0,
        |       "duration": 1,
        |       "bytes": 0,
        |       "blocks": 0,
        |       "reverse": 0,
        |       "tos": 0
        |     }
        |   },
        |   "intervals": [
        |     {
        |       "streams": [
        |         {
        |           "socket": 5,
        |           "start": 0,
        |           "end": 1.000084,
        |           "seconds": 1.0000840425491333,
        |           "bytes": 11527782400,
        |           "bits_per_second": 92214509257.57492,
        |           "retransmits": 0,
        |           "snd_cwnd": 1047728,
        |           "rtt": 10,
        |           "rttvar": 2,
        |           "pmtu": 65535,
        |           "omitted": False,
        |           "sender": True
        |         }
        |       ],
        |       "sum": {
        |         "start": 0,
        |         "end": 1.000084,
        |         "seconds": 1.0000840425491333,
        |         "bytes": 11527782400,
        |         "bits_per_second": 92214509257.57492,
        |         "retransmits": 0,
        |         "omitted": False,
        |         "sender": True
        |       }
        |     }
        |   ],
        |   "end": {
        |     "streams": [
        |       {
        |         "sender": {
        |           "socket": 5,
        |           "start": 0,
        |           "end": 1.000084,
        |           "seconds": 1.000084,
        |           "bytes": 11527782400,
        |           "bits_per_second": 92214513180.8928,
        |           "retransmits": 0,
        |           "max_snd_cwnd": 1047728,
        |           "max_rtt": 10,
        |           "min_rtt": 10,
        |           "mean_rtt": 10,
        |           "sender": True
        |         },
        |         "receiver": {
        |           "socket": 5,
        |           "start": 0,
        |           "end": 1.00009,
        |           "seconds": 1.000084,
        |           "bytes": 11527782400,
        |           "bits_per_second": 92213959943.60509,
        |           "sender": True
        |         }
        |       }
        |     ],
        |     "sum_sent": {
        |       "start": 0,
        |       "end": 1.000084,
        |       "seconds": 1.000084,
        |       "bytes": 11527782400,
        |       "bits_per_second": 92214513180.8928,
        |       "retransmits": 0,
        |       "sender": True
        |     },
        |     "sum_received": {
        |       "start": 0,
        |       "end": 1.00009,
        |       "seconds": 1.00009,
        |       "bytes": 11527782400,
        |       "bits_per_second": 92213959943.60509,
        |       "sender": True
        |     },
        |     "cpu_utilization_percent": {
        |       "host_total": 99.72215450647207,
        |       "host_user": 1.1345607423599982,
        |       "host_system": 98.58749385562825,
        |       "remote_total": 4.859361246926124,
        |       "remote_user": 0.1985516757285985,
        |       "remote_system": 4.6608157780710044
        |     },
        |     "sender_tcp_congestion": "cubic",
        |     "receiver_tcp_congestion": "cubic"
        |   }
        | }
        """
        command = f'iperf3 -J -c {server_address}'

        if server_port:
            command += f' -p {server_port}'

        if bind_address:
            command += f' -B {bind_address}'

        if protocol not in ['tcp', 'udp']:
            raise ValueError(f'unsupported protocol: {protocol}')
        else:
            if protocol == 'udp':
                command += f' -u'

        if duration is not None:
            command += f' --time {duration}'

        if num_streams is not None:
            command += f' --parallel {num_streams}'

        if self._to_bool(reverse):
            command += f' --reverse'

        if bitrate is not None:
            command += f' -b {bitrate}'

        if num_bytes is not None:
            command += f' --bytes {num_bytes}'

        if self._to_bool(bidir):
            command += f' --bidir'

        if tos is not None:
            command += f' --tos {tos}'

        if dscp is not None:
            command += f' --dscp {dscp}'

        p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        if p.returncode:
            reason = stderr.decode()

            try:
                reason = json.loads(stdout)["error"]
            finally:
                raise Exception(reason)

        return self._int_to_float(json.loads(stdout))
