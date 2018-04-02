import cv2
import numpy as np

from src.domain.vision_environment.robot import Robot
from src.vision.coordinate_converter import CoordinateConverter
from src.vision.camera_parameters import CameraParameters


class FrameDrawer:
    def __init__(self, cam_param: CameraParameters, coordinate_converter: CoordinateConverter):
        self.cam_param = cam_param
        self.coordinate_converter = coordinate_converter

    def draw_robot(self, frame, robot: Robot):
        robot_corners = robot.get_corners()

        robot_projected_points = self.__projectPoints(robot_corners)

        cv2.line(frame, tuple(robot_projected_points[0][0]), tuple(robot_projected_points[1][0]), (204, 0, 204), 3)
        cv2.line(frame, tuple(robot_projected_points[1][0]), tuple(robot_projected_points[2][0]), (204, 0, 204), 3)
        cv2.line(frame, tuple(robot_projected_points[2][0]), tuple(robot_projected_points[3][0]), (204, 0, 204), 3)
        cv2.line(frame, tuple(robot_projected_points[3][0]), tuple(robot_projected_points[0][0]), (204, 0, 204), 3)

    def __projectPoints(self, points):
        camera_to_world_parameters = self.coordinate_converter.get_camera_to_world().to_parameters()
        camera_to_world_tvec = np.array([camera_to_world_parameters[0], camera_to_world_parameters[1], camera_to_world_parameters[2]])
        camera_to_world_rvec = np.array([camera_to_world_parameters[3], camera_to_world_parameters[4], camera_to_world_parameters[5]])
        projected_points, jac = cv2.projectPoints(points, camera_to_world_rvec, camera_to_world_tvec, self.cam_param.camera_matrix, self.cam_param.distortion)

        return projected_points

    def draw_real_path(self, frame, points):
        i = 0
        world_points = self.__projectPoints(points)
        number_of_points = (len(world_points) - 1)
        while i < number_of_points:
            cv2.line(frame, tuple(world_points[i][0]), tuple(world_points[i + 1][0]), (255, 0, 0), 3)
            i = i + 1

    def draw_planned_path(self, frame, points):
        i = 0
        number_of_points = (len(points) - 1)
        while i < number_of_points:
            cv2.line(frame, points[i], points[i + 1], (0, 255, 0), 3)
            i = i + 1
