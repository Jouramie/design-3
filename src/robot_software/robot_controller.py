from logging import Logger
from src.d3_network.ip_provider import IpProvider
from src.d3_network.client_network_controller import ClientNetworkController


class RobotController:

    def __init__(self, logger: Logger, ip_provider: IpProvider, network: ClientNetworkController):
        self._logger = logger
        self._network_scanner = ip_provider
        self._network = network

    def start(self) -> None:
        host_ip = self._network_scanner.get_host_ip()
        self._network.pair_with_host(host_ip)

        self._network.wait_start_command(self.on_receive_start_command)

    def on_receive_start_command(self) -> None:
        self._logger.info("Start command received... LEEETTTS GOOOOOO!! ")
        self._main_loop()

    def _main_loop(self):
        pass


