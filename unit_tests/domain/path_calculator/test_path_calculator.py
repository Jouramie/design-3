from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import Mock

from src.domain.environments.navigation_environment import NavigationEnvironment
from src.domain.objects.obstacle import Obstacle
from src.domain.path_calculator.grid import Grid
from src.domain.path_calculator.path_calculator import PathCalculator

SPECIFIC_OBSTACLE_1_VALUE = (104, 0)
SPECIFIC_OBSTACLE_2_VALUE = (42, 54)
SPECIFIC_STARTING_POINT = (50, 15)
SPECIFIC_ENDING_POINT = (102, 33)

SOME_VALUE_0 = 0
SOME_VALUE_1 = 1
SOME_VALUE_2 = 2
SOME_OBSTACLE_LOCATION = 50
END_POINT_VALUE = 0
UNASSIGNED_VALUE = -1


class TestPathCalculator(TestCase):
    def test_when_calculate_path_then_validate_path_exist(self):
        starting_point = (SOME_VALUE_2, SOME_VALUE_1)
        starting_vertex = MagicMock()
        ending_point = (SOME_VALUE_2, SOME_VALUE_1)
        grid = Mock()
        path_calculator = PathCalculator(MagicMock())
        grid.attach_mock(Mock(return_value=starting_vertex), 'get_vertex')

        path_calculator.calculate_path(starting_point, ending_point, grid)

        self.assertEquals(2, starting_vertex.get_step_value.call_count)

    def test_when_calculate_path_then_set_ending_point_step_value(self):
        environment = NavigationEnvironment(MagicMock())
        environment.create_grid()
        starting_point = (SOME_VALUE_0, SOME_VALUE_0)
        ending_point = (SOME_VALUE_1, SOME_VALUE_0)
        path_calculator = PathCalculator(MagicMock())

        path_calculator.calculate_path(starting_point, ending_point, environment.get_grid())
        expected = environment.get_grid().get_vertex(ending_point).get_step_value() + 1

        self.assertEqual(expected, environment.get_grid().get_vertex(starting_point).get_step_value())

    def test_when_calculate_path_then_increment_neighbor_step_value(self):
        environment = NavigationEnvironment(MagicMock())
        environment.create_grid()
        starting_point = (SOME_VALUE_0, SOME_VALUE_0)
        ending_point = (SOME_VALUE_1, SOME_VALUE_0)
        path_calculator = PathCalculator(MagicMock())

        path_calculator.calculate_path(starting_point, ending_point, environment.get_grid())
        expected = END_POINT_VALUE

        self.assertEqual(expected, environment.get_grid().get_vertex(ending_point).get_step_value())

    def test_when_calculate_path_then_calculate_path(self):
        environment = NavigationEnvironment(MagicMock())
        environment.create_grid()
        starting_point = (SOME_VALUE_1, SOME_VALUE_0)
        ending_point = (SOME_VALUE_0, SOME_VALUE_0)
        path_calculator = PathCalculator(MagicMock())

        path_calculator.calculate_path(starting_point, ending_point, environment.get_grid())
        expected = [starting_point, ending_point]

        self.assertEqual(expected, path_calculator.get_calculated_path())

    def test_when_calculating_then_recommend_forward(self):
        environment = NavigationEnvironment(MagicMock())
        environment.create_grid()
        environment.add_obstacles([Obstacle(SPECIFIC_OBSTACLE_1_VALUE, NavigationEnvironment.OBSTACLE_RADIUS),
                                   Obstacle(SPECIFIC_OBSTACLE_2_VALUE, NavigationEnvironment.OBSTACLE_RADIUS)])

        starting_point = SPECIFIC_STARTING_POINT
        ending_point = SPECIFIC_ENDING_POINT

        path_calculator = PathCalculator(MagicMock())

        path_calculator.calculate_path(starting_point, ending_point, environment.get_grid())

        expected_square = [(50, 15), (50, 16), (50, 17), (50, 18), (50, 19), (50, 20), (50, 21), (50, 22), (50, 23),
                           (50, 24), (50, 25), (50, 26), (50, 27), (50, 28), (50, 29), (50, 30), (50, 31), (51, 31),
                           (52, 31), (53, 31), (54, 31), (55, 31), (56, 31), (57, 31), (58, 31), (59, 31), (60, 31),
                           (61, 31), (62, 31), (63, 31), (64, 31), (65, 31), (66, 31), (67, 31), (68, 31), (69, 31),
                           (70, 31), (71, 31), (72, 31), (73, 31), (74, 31), (75, 31), (76, 31), (77, 31), (78, 31),
                           (79, 31), (80, 31), (81, 31), (82, 31), (83, 31), (84, 31), (85, 31), (86, 31), (87, 31),
                           (88, 31), (89, 31), (90, 31), (91, 31), (92, 31), (93, 31), (94, 31), (95, 31), (96, 31),
                           (97, 31), (98, 31), (99, 31), (100, 31), (101, 31), (102, 31), (102, 32), (102, 33)]

        self.assertEqual(expected_square, path_calculator.get_calculated_path())

    def test_when_straight_line_then_does_not_zigzag(self):
        environment = NavigationEnvironment(MagicMock())
        environment.create_grid()
        starting_point = (0, 0)
        ending_point = (10, 0)
        path_calculator = PathCalculator(MagicMock())

        path_calculator.calculate_path(starting_point, ending_point, environment.get_grid())
        expected = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0)]

        self.assertEqual(expected, path_calculator.get_calculated_path())

    def test_when_diagonal_line_then_does_a_triangle(self):
        environment = NavigationEnvironment(MagicMock())
        environment.create_grid()
        starting_point = (0, 0)
        ending_point = (10, 10)
        path_calculator = PathCalculator(MagicMock())

        path_calculator.calculate_path(starting_point, ending_point, environment.get_grid())
        expected = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (1, 10),
                    (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10)]

        self.assertEqual(expected, path_calculator.get_calculated_path())

    def test_when_obstacle_then_goes_around_it(self):
        environment = NavigationEnvironment(MagicMock())
        environment.create_grid()
        environment.add_obstacles([Obstacle((SOME_OBSTACLE_LOCATION, SOME_OBSTACLE_LOCATION),
                                            NavigationEnvironment.OBSTACLE_RADIUS)])

        starting_point_next_to_obstacle = (SOME_OBSTACLE_LOCATION + Grid.DEFAULT_OFFSET -
                                           NavigationEnvironment.OBSTACLE_RADIUS - 1, SOME_OBSTACLE_LOCATION + 1)
        ending_point_next_to_obstacle = (SOME_OBSTACLE_LOCATION - Grid.DEFAULT_OFFSET +
                                         NavigationEnvironment.OBSTACLE_RADIUS, SOME_OBSTACLE_LOCATION)
        path_calculator = PathCalculator(MagicMock())

        path_calculator.calculate_path(starting_point_next_to_obstacle, ending_point_next_to_obstacle,
                                       environment.get_grid())

        for position in path_calculator.get_calculated_path():
            self.assertFalse(environment.get_grid().is_obstacle(position))

