from logging import Logger
from socket import socket, AF_INET, SOCK_STREAM

from ..domain.path_calculator.movement import Movement, Rotate
from .command import Command
from .encoder import Encoder
from .network_controller import NetworkController
from .network_exception import NetworkException, WrongCommand


class ServerNetworkController(NetworkController):

    def __init__(self, logger: Logger, port: int, encoder: Encoder):
        super().__init__(logger, port, encoder)

    def host_network(self) -> None:
        raise NotImplementedError("This is an interface...")

    def send_start_command(self) -> None:
        raise NotImplementedError("This is an interface...")

    def send_reset_command(self) -> None:
        raise NotImplementedError("This is an interface...")

    def ask_infrared_signal(self) -> None:
        raise NotImplementedError("This is an interface...")

    def check_infrared_signal(self) -> int:
        raise NotImplementedError("This is an interface...")

    def send_end_of_task_signal(self) -> int:
        raise NotImplementedError("This is an interface...")

    def send_ask_if_can_grab_cube_command(self) -> None:
        raise NotImplementedError("This is an interface...")

    def send_grab_cube_command(self) -> None:
        raise NotImplementedError("This is an interface...")

    def send_drop_cube_command(self) -> None:
        raise NotImplementedError("This is an interface...")

    def send_move_forward_command(self, movement: Movement):
        raise NotImplementedError("This is an interface...")

    def send_move_backward_command(self, movement: Movement):
        raise NotImplementedError("This is an interface...")

    def send_rotate_command(self, movement: Movement):
        raise NotImplementedError("This is an interface...")


class SocketServerNetworkController(ServerNetworkController):

    def __init__(self, logger: Logger, port: int, encoder: Encoder):
        super().__init__(logger, port, encoder)
        self._server = socket(AF_INET, SOCK_STREAM)

    def host_network(self) -> None:
        self._logger.info("Creating server on port " + str(self._port))
        self._server.bind(('', self._port))

        while self._socket is None:
            self._server.listen(5)
            self._socket, address = self._server.accept()
            self._socket.settimeout(2)
            self._logger.info("{} connected".format(address))

            self._send_command(Command.HELLO, {'msg': 'ThAnKs YoU fOr CoNnEcTiNg !!!!!'})

            try:
                msg = self._receive_message()
            except socket.timeout:
                self._socket.close()
                raise NetworkException('No answer from client.')

            if msg['command'] != Command.HELLO:
                self._socket.close()
                raise WrongCommand(Command.HELLO, msg['command'])

            self._logger.info(msg)
        self._socket.setblocking(0)

    def send_start_command(self) -> None:
        self._send_command(Command.START)

        self._logger.info("Start command sent!")

    def send_reset_command(self) -> None:
        self._send_command(Command.RESET)

        self._logger.info("Reset command sent!")

    def ask_infrared_signal(self) -> None:
        self._send_command(Command.INFRARED_SIGNAL)

        self._logger.info("Infrared signal asked!")

    def check_infrared_signal(self) -> int:
        msg = self._receive_message()

        country_code = msg['country_code']
        self._logger.info("Infrared signal received! {code}".format(code=country_code))
        return country_code

    def send_end_of_task_signal(self) -> None:
        self._send_command(Command.END_SIGNAL)

        self._logger.info("End of task signal sent, the led should go on!")

    def send_ask_if_can_grab_cube_command(self) -> None:
        self._send_command(Command.CAN_I_GRAB)

        self._logger.info("Can i grab a cube command sent!")

    def send_grab_cube_command(self) -> None:
        self._send_command(Command.GRAB)

        self._logger.info("Grab command sent!")

    def send_drop_cube_command(self) -> None:
        self._send_command(Command.DROP)

        self._logger.info("Drop cube command sent!")

    def send_move_forward_command(self, movement: Movement) -> None:
        self._send_command(Command.MOVE_FORWARD, {'amplitude' : movement.amplitude})

        self._logger.info("Commmand {} : sent!".format(movement))

    def send_move_backward_command(self, movement: Movement):
        self._send_command(Command.MOVE_BACKWARD, {'amplitude': movement.amplitude})

        self._logger.info("Commmand {} : sent!".format(movement))

    def send_rotate_command(self, movement: Movement):
        self._send_command(Command.MOVE_ROTATE, {'amplitude': movement.amplitude})

        self._logger.info("Commmand {} : sent!".format(movement))


class MockedServerNetworkController(ServerNetworkController):
    def __init__(self, logger: Logger, port: int = 0, encoder: Encoder = None):
        super().__init__(logger, port, encoder)
        self.COUNTRY_CODE = 31
<<<<<<< HEAD
        self.MOVEMENT = Rotate(30)
=======
        self.COMMAND = bytearray(b'\x21\x00\x5a')
>>>>>>> ddb9ad1f026e63de04809fb7d1a75e0eaccac681

    def host_network(self) -> None:
        self._logger.info("Creating server on port " + str(self._port))
        self._logger.info("{} connected".format('fake network'))
        pass

    def send_start_command(self) -> None:
        self._logger.info("Start command sent!")

    def send_reset_command(self) -> None:
        self._logger.info("Reset command sent!")

    def ask_infrared_signal(self) -> None:
        self._logger.info("Infrared signal asked!")

    def check_infrared_signal(self) -> int:
        self._logger.info("Infrared signal received! {code}".format(code=self.COUNTRY_CODE))
        return self.COUNTRY_CODE

    def send_end_of_task_signal(self) -> None:
        self._logger.info("End of task signal sent, the led should go on!")

    def send_grab_cube(self) -> None:
        self._logger.info("Grab command sent!")

    def send_ask_if_can_grab_cube(self) -> None:
        self._logger.info("Can i grab a cube command sent!")

    def send_drop_cube(self) -> None:
        self._logger.info("Drop cube command sent!")

<<<<<<< HEAD
    def send_move_forward_command(self, movement: Movement) -> None:
        self._logger.info("Commmand {} : sent!".format(self.MOVEMENT))
=======
    def send_move_command(self, command: bytearray) -> None:
        self._logger.info("Commmand {} : sent!".format(self.COMMAND.decode()))
>>>>>>> ddb9ad1f026e63de04809fb7d1a75e0eaccac681

    def send_move_backward_command(self, movement: Movement):
        self._logger.info("Commmand {} : sent!".format(movement))

    def send_rotate_command(self, movement: Movement):
        self._logger.info("Commmand {} : sent!".format(movement))
