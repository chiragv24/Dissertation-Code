import pytest
import cozmo
from cozmo.util import distance_mm
from QLearnSuperClass import QLearnDistOrthogonal
from cozmo.util import distance_mm, speed_mmps


# def func(x):
#     return x + 1
#
# def test_answer():
#     assert func(3) == 4


def test_robotMovement(robot:cozmo.robot.Robot):
    agent = QLearnDistOrthogonal()
    agent.robotMovement(2, "happy", 2, robot)
    dist = agent.searchForFace(robot)
    assert dist < distance_mm(150)

def pytest_generate_tests(metafunc):
    if "robot:cozmo.robot.Robot" in metafunc.fixturenames:
        metafunc.parametrize("robot:cozmo.robot.Robot",metafunc.config.getoption("robot:cozmo.robot.Robot"))



#
# class TestClass:
#
#     def test_robot(self,robot:cozmo.robot.Robot):
#         agent = QLearnDistOrthogonal()
#         agent.robotMovement(2,"happy",2,robot)
#         dist = agent.searchForFace(robot)
#         assert dist < distance_mm(150)


