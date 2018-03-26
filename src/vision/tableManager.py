import cv2.aruco
import numpy as np

from src.vision.transform import Transform
from src.vision.table import Table


class TableManager:
    def __init__(self):
        self.cam_path = ["",
                         "",
                         "",
                         "../../calibration/table4_2018-03-01.yml",
                         "",
                         ""]
        self.world_calibration_path = ["",
                                       "",
                                       "",
                                       "../../calibration/world_calibration_4.npy",
                                       "",
                                       ""]

    def create_table(self, id):
        if 1 <= id <= 6:
            cam_param = cv2.aruco.CameraParameters()
            cam_param.readFromXMLFile(self.cam_path[id-1])
            world_to_camera = Transform.from_matrix(np.load(self.world_calibration_path[id-1]))

            return Table(id, cam_param, world_to_camera)
        else:
            raise ValueError("Invalid table number.")



