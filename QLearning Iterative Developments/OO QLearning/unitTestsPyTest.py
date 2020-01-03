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

class TestClass:
    agent = QLearnDistOrthogonal()

    def test_robot(self,robot:cozmo.robot.Robot):
        self.agent.robotMovement(2,"happy",2,robot)
        dist = self.agent.searchForFace(robot)
        assert dist < distance_mm(150)


