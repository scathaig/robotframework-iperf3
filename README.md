# robotframework-iperf3
This Robot Framework library uses iPerf3 to measure the bandwidth between two peers.

The library assumes that iPerf3 is installed and that the executable can be found within the PATH variable.

The library can also be run as a remote library so that the PC running iPerf3 and connected to the DUT does not have
to be the same one as the PC running the test. The remote library can be started with:

    usage: python3 -m robotframework-iperf3 [-h] [-a ADDRESS] [-p PORT]
    
    optional arguments:
      -h, --help            show this help message and exit
      -a ADDRESS, --address ADDRESS
                            server listen address (default: 0.0.0.0)
      -p PORT, --port PORT  server listen port (default: 8270)

[iperf3-python](https://pypi.org/project/iperf3/) which uses iPerf3's library directly caused errors which made it
unreliable to use, so I decided to just use the binary. Bonus: now it works on Windows, too.

For remote access the library uses [PythonRemoteServer](https://github.com/robotframework/PythonRemoteServer) which uses
XML-RPC to communicate with Robot's [Remote interface](https://github.com/robotframework/RemoteInterface). XML-RPC is
limited to 2^32 integers. Because of that all values larger than that are converted to float - so don't be surprised to
see for example 4294967297.0 transmitted bytes :)

If an argument expects a bool value it may be given as bool or a string that looks like a bool: ${TRUE}, ${FALSE},
true, True, false, False are fine.
