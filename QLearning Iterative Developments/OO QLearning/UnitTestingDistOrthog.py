import unittest
import cozmo
import sys
from cozmo.util import distance_mm
#from QLearnSuperClass import QLearnDistOrthogonal
import numpy as np
from SuperClassParamTesting import QLearnDistOrthogonal

class robotMovementTesting(unittest.TestCase):

    def setUp(self):
        self.robot = cozmo.robot.Robot
        self.agent = QLearnDistOrthogonal()

    def test_closeButHappy(self):
        """Test robot close but human wants it there"""
        rob = self.agent.robotMovement(2,"happy",0)
        self.assertEqual(rob,"staying far")

    def test_farButHappy(self):
        rob = self.agent.robotMovement(2,"happy",0)
        self.assertEqual(rob,"staying close")

    def test_moveBack(self):
        rob = self.agent.robotMovement(0, "happy", 1)
        self.assertEqual(rob, "moving backwards")

    def test_moveFront(self):
        rob = self.agent.robotMovement(1,"neutral", 0)
        self.assertEqual(rob, "moving forwards")

    def test_moveGreet(self):
        rob = self.agent.robotMovement(2, "sad", 1)
        self.assertEqual(rob,"greeting")

    def test_idle(self):
        rob = self.agent.robotMovement(3,"sad",0)
        self.assertEqual(rob,"idle")

    def test_integer(self):
        with self.assertRaises(AssertionError):
            self.agent.robotMovement(2,2,4)

    def test_string(self):
        with self.assertRaises(TypeError):
            self.agent.robotMovement("hello","angry",1)

    def test_stringState(self):
        with self.assertRaises(AssertionError):
            self.agent.robotMovement(1,"angry","0")

    def test_notValidState(self):
        with self.assertRaises(AssertionError):
            self.agent.robotMovement(1,"happy",4)

    def test_notValidAction(self):
        with self.assertRaises(AssertionError):
            self.agent.robotMovement(4, "happy", 1)

    def test_notValidFace(self):
        with self.assertRaises(AssertionError):
            self.agent.robotMovement(0, "Joyful", 1)

class testNextAction(unittest.TestCase):

    def setUp(self):
        self.agent = QLearnDistOrthogonal()

    def test_nextActionLessFour(self):
        rob = self.agent.nextAction()
        self.assertLess(rob,4)

    def test_nextAction(self):
        rob = self.agent.nextAction()
        self.assertGreater(rob,0)

class testMoveRobotHead(unittest.TestCase):

    def setUp(self):
        self.agent = QLearnDistOrthogonal()

    def test_minLiftPosition(self):
        self.agent.moveRobotHead()
        difference = self.agent.robotLiftPositionBef - self.agent.robotLiftPosition
        if self.agent.robotLiftPositionBef!=cozmo.robot.MIN_LIFT_HEIGHT:
            self.assertGreaterEqual(difference,0.0)
        else:
            self.assertEqual(difference, 0.0)

    def test_notMinLiftPosition(self):
        self.agent.moveRobotHead()
        self.assertEqual(self.agent.robotLiftPosition,cozmo.robot.MIN_LIFT_HEIGHT.distance_mm)

    def test_maxHeadPosition(self):
        self.agent.moveRobotHead()
        self.assertEqual(self.agent.robotHeadPosition,cozmo.robot.MAX_HEAD_ANGLE)

    def test_alreadyAtHeadPosition(self):
        self.agent.moveRobotHead()
        difference = self.agent.robotHeadPositionBef.degrees - self.agent.robotHeadPosition.degrees
        if self.agent.robotHeadPositionBef != cozmo.robot.MAX_HEAD_ANGLE:
            self.assertGreaterEqual(difference, 0.0)
        else:
            self.assertEqual(difference,0.0)

class testFacialExpression(unittest.TestCase):

    def setUp(self):
        self.agent = QLearnDistOrthogonal()

    ###TEST THIS PROPERLY##################
    def test_face(self):
        self.agent.facialExpressionEstimate()
        if self.agent.facialExpression == "Happy":
            self.assertEqual(self.agent,"Happy")

    def test_noFace(self):
        with self.assertRaises(AssertionError):
            self.agent.facialExpressionEstimate()

class searchForFace(unittest.TestCase):

    def setup(self):
        self.agent = QLearnDistOrthogonal()

    def testFaceSearch(self):
        self.agent.searchForFace()
        if self.agent.distanceFromFace < float(150):
            self.assertEqual(self.agent.currentState,2)
        elif self.agent.distanceFromFace > float(350):
            self.assertEqual(self.agent.currentState,0)
        elif float(150) < self.agent.distanceFromFace < float(350):
            self.assertEqual(self.agent.currentState,1)

    def testNoFaceSearch(self):
        with self.assertRaises(AssertionError):
            self.agent.searchForFace()

class testUpdate(unittest.TestCase):

    def setUp(self):
        self.agent = QLearnDistOrthogonal()

    def test_qMatrixUpdate(self):
        currentState = 1
        action = 2
        gamma = 0.8
        valBefore = self.agent.Q[currentState][action]
        self.agent.update(currentState,action,0.8)
        valAfter = valBefore + self.agent.rewards[currentState][action] + gamma * np.max(self.agent.rewards[currentState][:])
        self.assertEqual(valAfter,self.agent.Q[currentState][action])

    def test_negativeState(self):
        with self.assertRaises(AssertionError):
            self.agent.update(-5,1,0.5)

    def test_decimalState(self):
        with self.assertRaises(TypeError):
            self.agent.update(0.5,1,0.5)

    def test_stringState(self):
        with self.assertRaises(TypeError):
            self.agent.update("Hello",2,0.5)

    def test_largeStateValue(self):
        with self.assertRaises(AssertionError):
            self.agent.update(15,1,0.5)

    def test_negativeAction(self):
        with self.assertRaises(AssertionError):
            self.agent.update(1,-2,0.5)

    def test_decimalAction(self):
        with self.assertRaises(TypeError):
            self.agent.update(2,0.5,0.5)

    def test_stringAction(self):
        with self.assertRaises(TypeError):
            self.agent.update(0,"2",0.5)

    def test_largeActionValue(self):
        with self.assertRaises(AssertionError):
            self.agent.update(1,17,0.5)

    def test_largeGamma(self):
        with self.assertRaises(AssertionError):
            self.agent.update(0,0,4)

    def test_stringGamma(self):
        with self.assertRaises(TypeError):
            self.agent.update(1,1,"0.3")

if __name__ == '__main__':
    unittest.main()
