import argparse
from robotremoteserver import RobotRemoteServer
from .iperf3 import Iperf3


if __name__ == '__main__':

    # create commandline parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.prog = 'python3 -m robotframework-iperf3'

    # add parser options
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        help="server listen address",
        default='0.0.0.0')

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="server listen port",
        default=8270)

    args = parser.parse_args()

    server = RobotRemoteServer(
        Iperf3(),
        host=args.address,
        port=args.port
    )

    server.serve()
