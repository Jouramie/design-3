import subprocess
import time
from logging import Logger

import numpy as np

from src.d3_network.network_exception import MessageNotReceivedYet
from src.d3_network.server_network_controller import ServerNetworkController
from src.domain.country_loader import CountryLoader
from src.domain.environments.navigation_environment import NavigationEnvironment
from src.domain.environments.real_world_environment_factory import RealWorldEnvironmentFactory
from src.domain.objects.color import Color
from src.domain.path_calculator.direction import Direction
from src.domain.path_calculator.grid import Grid
from src.domain.path_calculator.movement import Forward, Backward, Rotate, Right, Left
from src.domain.path_calculator.path_calculator import PathCalculator
from src.domain.path_calculator.path_converter import PathConverter
from src.vision.camera import Camera
from src.vision.robot_detector import RobotDetector
from src.vision.world_vision import WorldVision
from .station_model import StationModel


class StationController(object):
    DISTANCE_FROM_CUBE = NavigationEnvironment.BIGGEST_ROBOT_RADIUS + 5

    def __init__(self, model: StationModel, network: ServerNetworkController, camera: Camera,
                 real_world_environment_factory: RealWorldEnvironmentFactory, robot_detector: RobotDetector,
                 logger: Logger, config: dict):
        self.model = model
        self.logger = logger
        self.config = config
        self.network = network

        self.camera = camera

        self.country_loader = CountryLoader(config)
        self.world_vision = WorldVision(logger, config)
        self.path_calculator = PathCalculator(logger)
        self.path_converter = PathConverter(logger.getChild("PathConverter"))
        self.navigation_environment = NavigationEnvironment(logger.getChild("NavigationEnvironment"))
        self.navigation_environment.create_grid()

        self.real_world_environment_factory = real_world_environment_factory
        self.robot_detector = robot_detector

        self.obstacle_pos = []

        self.model.world_camera_is_on = True

    def start_robot(self):
        self.model.robot_is_started = True
        self.model.start_time = time.time()

        if self.config['robot']['update_robot']:
            subprocess.call("./src/scripts/boot_robot.bash", shell=True)

        self.logger.info("Waiting for robot to connect.")
        self.network.host_network()
        self.network.send_start_command()
        self.interactive_testing()

    def interactive_testing(self):
        while True:
            command = input('enter something:ir, grab, drop, light, forward, backward, rotate')
            command = command.split(" ")
            self.logger.info('You entered : {}'.format(command[0]))

            if command[0] == 'ir':
                self.network.ask_infrared_signal()
                self.__check_infrared_signal()
            elif command[0] == 'grab':
                self.network.send_grab_cube_command()
            elif command[0] == 'drop':
                self.network.send_drop_cube_command()
            elif command[0] == 'led':
                self.network.send_end_of_task_signal()
            elif command[0] == 'f':
                self.network.send_move_command(Forward(float(command[1])))
            elif command[0] == 'r':
                self.network.send_move_command(Right(float(command[1])))
            elif command[0] == 'l':
                self.network.send_move_command(Left(float(command[1])))
            elif command[0] == 'b':
                self.network.send_move_command(Backward(float(command[1])))
            elif command[0] == 'r':
                self.network.send_move_command(Rotate(float(command[1])))


    def __check_infrared_signal(self) -> int:
        try:
            return self.network.check_infrared_signal()
        except MessageNotReceivedYet:
            return None

    def __find_country(self):
        self.model.country = self.country_loader.get_country(self.model.country_code)
        self.logger.info(
            "Found " + str(self.model.country) + " flag: " + str(self.model.country.stylized_flag.flag_cubes))

    def __select_next_cube_color(self):
        cube_index = self.model.current_cube_index
        while cube_index < 9:
            flag_cube = self.model.country.stylized_flag.flag_cubes[cube_index]
            if flag_cube.color is not Color.TRANSPARENT:
                self.model.current_cube_index = cube_index + 1
                self.model.next_cube = flag_cube
                self.logger.info("New cube color {}".format(self.model.next_cube.color.name))
                break
            else:
                cube_index = cube_index + 1
        if cube_index >= 9:
            self.model.flag_is_finish = True

    def update(self):
        self.model.frame = self.camera.get_frame()
        self.model.robot = self.robot_detector.detect(self.model.frame)

        if self.model.robot is not None:
            robot_center_3d = self.model.robot.get_center_3d()
            self.model.real_path.append(np.float32(robot_center_3d))

        if not self.model.robot_is_started:
            return

        self.model.passed_time = time.time() - self.model.start_time

        if self.model.real_world_environment is None:
            self.__generate_environments()

        if not self.model.infrared_signal_asked:
            self.logger.info("Entering new step, asking country-code.")

            if self.model.robot is None:
                self.logger.warning("Robot position is undefined. Waiting to know robot position to find path.")
                return
            self.logger.info("Robot: {}".format(self.model.robot))

            target_position = (6, 36)
            is_possible = self.path_calculator.calculate_path(self.model.robot.center, target_position,
                                                              self.navigation_environment.get_grid())

            if not is_possible:
                self.logger.warning("Path to infra-red reception is not possible.\n Target: {}".format(target_position))
                return

            movements, self.model.planned_path = self.path_converter.convert_path(
                self.path_calculator.get_calculated_path(), self.model.robot, Direction.SOUTH)
            self.logger.info("Path planned: {}".format(" ".join(str(mouv) for mouv in movements)))

            for movement in movements:
                self.network.send_move_command(movement)

            self.network.ask_infrared_signal()
            self.model.robot_is_moving = True
            self.model.infrared_signal_asked = True
            if self.config['robot']['use_mocked_robot_detector']:
                self.robot_detector.robot_position = target_position
                self.robot_detector.robot_direction = Direction.SOUTH.angle
            return

        if self.model.robot_is_moving:
            self.model.robot_is_moving = False
            self.model.real_world_environment = None
            # TODO Envoyer update de position ou envoyer la prochaine commande de déplacement/grab/drop
            return

        if self.model.country_code is None:
            country_received = self.__check_infrared_signal()

            if country_received is not None:
                self.model.country_code = country_received
                self.__find_country()
                self.__select_next_cube_color()
            else:
                return

        if not self.model.flag_is_finish:
            if self.model.robot_is_holding_cube:
                self.logger.info("Entering new step, moving to target_zone to place cube.")

                if self.model.robot is None:
                    self.logger.warning("Robot position is undefined. Waiting to know robot position to find path.")
                    return
                self.logger.info("Robot: {}".format(self.model.robot))

                cube_destination = self.model.country.stylized_flag.flag_cubes[self.model.current_cube_index - 1].center
                target_position = (cube_destination[0] + self.config['distance_between_robot_center_and_cube_center'],
                                   cube_destination[1])
                self.logger.info("Target position: {}".format(str(target_position)))
                is_possible = self.path_calculator.calculate_path(self.model.robot.center, target_position,
                                                                  self.navigation_environment.get_grid())

                if not is_possible:
                    self.logger.warning(
                        "Path to target_zone is not possible.\n Target: {}".format(target_position))
                    return

                movements, self.model.planned_path = self.path_converter.convert_path(
                    self.path_calculator.get_calculated_path(), self.model.robot, Direction.WEST)
                self.logger.info("Path planned: {}".format(" ".join(str(mouv) for mouv in movements)))

                for movement in movements:
                    self.network.send_move_command(movement)
                self.network.send_drop_cube_command()
                distance_backward = self.DISTANCE_FROM_CUBE - self.config[
                    'distance_between_robot_center_and_cube_center']
                self.network.send_move_command(Backward(distance_backward))

                self.logger.info("Dropping cube.")

                self.model.country.stylized_flag.flag_cubes[self.model.current_cube_index - 1].place_cube()
                self.__select_next_cube_color()

                self.model.robot_is_moving = True
                self.model.robot_is_holding_cube = False
                if self.config['robot']['use_mocked_robot_detector']:
                    self.robot_detector.robot_position = (target_position[0] + distance_backward, target_position[1])
                    self.robot_detector.robot_direction = Direction.WEST.angle

            else:
                if self.model.robot_is_grabbing_cube:
                    self.logger.info("Entering new step, moving to grab the cube.")

                    self.network.send_move_command(Forward(self.DISTANCE_FROM_CUBE))
                    self.network.send_grab_cube_command()
                    self.network.send_move_command(Backward(self.DISTANCE_FROM_CUBE + 1))

                    self.model.robot_is_moving = True
                    self.model.robot_is_grabbing_cube = False
                    self.model.robot_is_holding_cube = True

                else:
                    self.logger.info("Entering new step, travel to the cube.")
                    target_cube = self.model.real_world_environment.find_cube(self.model.next_cube.color)
                    if target_cube is None:
                        self.logger.warning("The target cube is None. Cannot continue, exiting.")
                        return

                    if self.model.robot is None:
                        self.logger.warning("Robot position is undefined. Waiting to know robot position to find path.")
                        return
                    self.logger.info("Robot: {}".format(self.model.robot))

                    if target_cube.center[1] < Grid.DEFAULT_OFFSET + 5:
                        self.logger.info("Le cube {} est en bas.".format(str(target_cube)))
                        target_position = (int(target_cube.center[0]),
                                           int(target_cube.center[1] + self.DISTANCE_FROM_CUBE))
                        desired_direction = Direction.SOUTH
                        pass
                    elif target_cube.center[1] > NavigationEnvironment.DEFAULT_WIDTH + Grid.DEFAULT_OFFSET - 10:
                        self.logger.info("Le cube {} est en haut.".format(str(target_cube)))
                        target_position = (int(target_cube.center[0]),
                                           int(target_cube.center[1] - self.DISTANCE_FROM_CUBE))
                        desired_direction = Direction.NORTH
                        pass
                    elif target_cube.center[0] > NavigationEnvironment.DEFAULT_HEIGHT + Grid.DEFAULT_OFFSET - 5:
                        self.logger.info("Le cube {} est au fond.".format(str(target_cube)))
                        target_position = (int(target_cube.center[0] - self.DISTANCE_FROM_CUBE),
                                           int(target_cube.center[1]))
                        desired_direction = Direction.EAST
                        pass
                    else:
                        self.logger.warning("Le cube {} n'est pas à la bonne place.".format(str(target_cube)))
                        return

                    is_possible = self.path_calculator.calculate_path(self.model.robot.center, target_position,
                                                                      self.navigation_environment.get_grid())

                    if not is_possible:
                        self.logger.warning("Path to the cube is not possible.\n Target: {}".format(target_position))
                        return

                    movements, self.model.planned_path = self.path_converter.convert_path(
                        self.path_calculator.get_calculated_path(), self.model.robot, desired_direction)
                    self.logger.info("Path planned: {}".format(" ".join(str(mouv) for mouv in movements)))

                    for movement in movements:
                        self.network.send_move_command(movement)

                    self.model.robot_is_moving = True
                    self.model.robot_is_grabbing_cube = True
                    if self.config['robot']['use_mocked_robot_detector']:
                        self.robot_detector.robot_position = target_position
                        self.robot_detector.robot_direction = desired_direction.angle
        else:
            if self.model.light_is_lit:
                self.logger.info("Entering new step, resetting for next flag.")
                pass
            else:
                self.logger.info("Entering new step, exiting zone to light led.")

                # TODO Calculer le path vers l'exterieur de la zone
                # TODO Envoyer la commande de déplacement + led

                self.network.send_end_of_task_signal()

                self.model.robot_is_moving = True
                self.model.light_is_lit = True

    def __generate_environments(self):
        # self.camera.take_picture()
        self.model.vision_environment = self.world_vision.create_environment(self.model.frame,
                                                                             self.config['table_number'])
        self.logger.info("Vision Environment:\n{}".format(str(self.model.vision_environment)))
        self.model.real_world_environment = self.real_world_environment_factory.create_real_world_environment(
            self.model.vision_environment)
        if self.model.country is not None:
            for cube in self.model.country.stylized_flag.flag_cubes:
                if cube.is_placed:
                    self.model.real_world_environment.cubes.append(cube)

        self.logger.info("Real Environment:\n{}".format(str(self.model.real_world_environment)))
        # self.navigation_environment.create_grid()
        self.navigation_environment.add_real_world_environment(self.model.real_world_environment)
