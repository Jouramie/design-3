import cv2
import numpy as np

from src.domain.environment.robot import Robot
from src.vision.coordinateConverter import CoordinateConverter
from src.vision.cameraParameters import CameraParameters
from src.domain.environment.environment import *


class FrameDrawer:
    def __init__(self, cam_param: CameraParameters, coordinate_converter: CoordinateConverter):
        self.camParam = cam_param
        self.coordinateConverter = coordinate_converter

    def drawRobot(self, frame, robot: Robot):
        robot_corners = robot.get_corners()

        robot_projected_points = self.__projectPoints(robot_corners)

        cv2.line(frame, tuple(robot_projected_points[0][0]), tuple(robot_projected_points[1][0]), (204, 0, 204), 3)
        cv2.line(frame, tuple(robot_projected_points[1][0]), tuple(robot_projected_points[2][0]), (204, 0, 204), 3)
        cv2.line(frame, tuple(robot_projected_points[2][0]), tuple(robot_projected_points[3][0]), (204, 0, 204), 3)
        cv2.line(frame, tuple(robot_projected_points[3][0]), tuple(robot_projected_points[0][0]), (204, 0, 204), 3)

    def __projectPoints(self, points):
        camera_to_world_parameters = self.coordinateConverter.get_camera_to_world().to_parameters()
        camera_to_world_tvec = np.array([camera_to_world_parameters[0], camera_to_world_parameters[1], camera_to_world_parameters[2]])
        camera_to_world_rvec = np.array([camera_to_world_parameters[3], camera_to_world_parameters[4], camera_to_world_parameters[5]])
        projected_points, jac = cv2.projectPoints(points, camera_to_world_rvec, camera_to_world_tvec, self.camParam.CameraMatrix, self.camParam.Distorsion)

        return projected_points

    def draw_real_path(self, frame, points):
        i = 0
        if len(points) != 0:
            world_points = self.__projectPoints(points)
            number_of_points = (len(world_points) - 1)
            while i < number_of_points:
                cv2.line(frame, tuple(world_points[i][0]), tuple(world_points[i + 1][0]), (255, 0, 0), 3)
                i = i + 1

    def draw_projected_path(self, frame, points):
        i = 0
        number_of_points = (len(points) - 1)
        while i < number_of_points:
            cv2.line(frame, points[i], points[i + 1], (0, 255, 0), 3)
            i = i + 1

    def draw_cube(self, frame, cube: Cube):
        cv2.rectangle(frame, cube.get_corner(0), cube.get_corner(1), cube.color.bgr, thickness=3)

    def draw_target_zone(self, frame, target_zone: TargetZone):
        cv2.rectangle(frame, target_zone.corners[0], target_zone.corners[1], Color.SKY_BLUE.bgr, thickness=3)

    def draw_obstacle(self, frame, obstacle: Obstacle):
        cv2.circle(frame, obstacle.center, obstacle.radius, Color.PINK.bgr, thickness=3, lineType=cv2.LINE_AA)
