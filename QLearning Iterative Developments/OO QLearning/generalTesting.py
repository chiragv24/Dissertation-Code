import unittest
import cozmo
import sys
from cozmo.util import distance_mm
#from QLearnSuperClass import QLearnDistOrthogonal
import numpy as np
import abc
from SuperClassParamTesting import QLearnTurnOrthogonal
from SuperClassParamTesting import QLearnGreetOrthogonal
from SuperClassParamTesting import QLearnLiftOrthogonal
from SuperClassParamTesting import QLearnSuperClass

class generalTestingMethods(unittest.TestCase):

    def setUp(self):
        self.type = ""
        if self.type.lower() == "turn":
            self.agent = QLearnTurnOrthogonal()
        elif self.type.lower() == "lift":
            self.agent = QLearnLiftOrthogonal()
        elif self.type.lower() == "greet":
            self.agent = QLearnGreetOrthogonal()

    def tCurrentStates(self):
        state = self.agent.findCurrentState()
        if self.agent.lastAction == 0:
            self.assertEqual(state, 0)
        elif self.agent.lastAction == 1:
            self.assertEqual(state, 1)
        else:
            with self.assertRaises(AssertionError):
                self.agent.findCurrentState()

    def tQMatrixUpdate(self):
        currentState = 1
        action = 0
        gamma = 0.8
        valBefore = self.agent.Q[currentState][action]
        self.agent.update(currentState,action,0.8)
        valAfter = valBefore + self.agent.rewards[currentState][action] + gamma * np.max(self.agent.rewards[currentState][:])
        self.assertEqual(valAfter,self.agent.Q[currentState][action])

    def tnegativeState(self):
        with self.assertRaises(AssertionError):
            self.agent.update(-5,1,0.5)

    def tdecimalState(self):
        with self.assertRaises(AssertionError):
            self.agent.update(0.5,1,0.5)

    def tstringState(self):
        with self.assertRaises(AssertionError):
            self.agent.update("Hello",2,0.5)

    def tlargeStateValue(self):
        with self.assertRaises(AssertionError):
            self.agent.update(15,1,0.5)

    def tnegativeAction(self):
        with self.assertRaises(AssertionError):
            self.agent.update(1,-2,0.5)

    def tdecimalAction(self):
        with self.assertRaises(AssertionError):
            self.agent.update(1,0.5,0.5)

    def tstringAction(self):
        with self.assertRaises(AssertionError):
            self.agent.update(0,"2",0.5)

    def tlargeActionValue(self):
        with self.assertRaises(AssertionError):
            self.agent.update(1,17,0.5)

    def tlargeGamma(self):
        with self.assertRaises(AssertionError):
            self.agent.update(0,0,4)

    def tstringGamma(self):
        with self.assertRaises(TypeError):
            self.agent.update(1,1,"0.3")