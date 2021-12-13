from .iperf3 import Iperf3

# define functions/keywords at module-level so that we can use just
# "Library robotframework-iperf3" instead of "Library robotframework-iperf3.Iperf3"
_inst = Iperf3()
__doc__ = _inst.__doc__
start_server = _inst.start_server
stop_server = _inst.stop_server
run_client = _inst.run_client
