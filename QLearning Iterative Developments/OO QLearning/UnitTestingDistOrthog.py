import unittest
import cozmo
from cozmo.util import distance_mm
from QLearnSuperClass import QLearnDistOrthogonal

class availableActions(unittest.TestCase):

    agent = QLearnDistOrthogonal()

    def test_allActionsTestFar(self):
        """Tests the result of the far state"""
        result = self.agent.allActions(0)
        self.assertEqual(result,[-1.1,-2.1,-1.5,-2])

    def test_allActionsTestOpt(self):
        """Tests the result of the optimal state"""
        result = self.agent.allActions(1)
        self.assertEqual(result,[-0.1,-0.1,1.5,0])

    def test_allActionsTestClose(self):
        "Test the result of the close state"
        result = self.agent.allActions(2)
        self.assertEqual(result,[-2.1,-0.1,0.5,0])

    def test_allActionsTestNeg(self):
        "Test negative parameter value"
        with self.assertRaises(AssertionError):
            self.agent.allActions(-1)

    def test_allActionsTestString(self):
        "Test with a string"
        with self.assertRaises(TypeError):
            self.agent.allActions("Hello")

class robotMovementTesting(unittest.TestCase):

    agent = QLearnDistOrthogonal()
    robot = cozmo.robot.Robot

    def test_closeButHappy(self,robot):
        robot = self.robot
        """Test robot close but human wants it there"""
        self.agent.robotMovement(2,"happy",2,robot)
        #cozmo.run_program(self.agent.robotMovement)
        #self.agent.robotMovement(2,"happy",2,robot)
        dist = self.agent.searchForFace(robot)
        self.assertLessEqual(dist,distance_mm(150))

    # def test_farButHappy(self,robot):
    #     self.robot = cozmo.robot.Robot
    #     "Test robot far but human wants it there"
    #     self.agent.robotMovement(0,"happy",0,robot)
    #     dist = self.agent.searchForFace(robot)
    #     self.assertGreater(dist,distance_mm(350))
    #
    # #THIS IS WHERE THE PROGRAM IS FAILING ATM
    # def test_action_back(self,robot):
    #     self.robot = cozmo.robot.Robot
    #     distBefore = self.agent.searchForFace(self.robot)
    #     self.agent.robotMovement(0, "happy", 0, self.robot)
    #     distAfter = self.agent.searchForFace(self.robot)
    #     self.assertAlmostEqual(distBefore-10,distAfter)

if __name__ == '__main__':
    unittest.main()
