import unittest
import asyncio
import cozmo
import sys
from cozmo.util import distance_mm
#from QLearnSuperClass import QLearnDistOrthogonal
import numpy as np
import abc
import aiounittest
from asyncioTesting import QLearnTurnOrthogonal
from asyncioTesting import QLearnGreetOrthogonal
from asyncioTesting import QLearnLiftOrthogonal
from asyncioTesting import QLearnSuperClass

class generalTestingMethods(aiounittest.AsyncTestCase):

    def setUp(self):
        self.type = ""
        if self.type.lower() == "turn":
            self.agent = QLearnTurnOrthogonal()
        elif self.type.lower() == "lift":
            self.agent = QLearnLiftOrthogonal()
        elif self.type.lower() == "greet":
            self.agent = QLearnGreetOrthogonal()

    def tCurrentStates(self,robot:cozmo.robot.Robot):
        state = self.agent.findCurrentState(robot)
        if self.agent.greeted == 0:
            self.assertEqual(state, 0)
        elif self.agent.greeted == 1:
            self.assertEqual(state, 1)
        else:
            with self.assertRaises(AssertionError):
                self.agent.findCurrentState(robot)

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

    async def tstringStateMax(self,robot:cozmo.robot.Robot):
        with self.assertRaises(AssertionError):
            await self.agent.nextActionMax("Hello",robot)

    async def tnegStateMax(self,robot:cozmo.robot.Robot):
        with self.assertRaises(AssertionError):
            await self.agent.nextActionMax(-1,robot)

    async def tdecStateMax(self,robot:cozmo.robot.Robot):
        with self.assertRaises(AssertionError):
            await self.agent.nextActionMax(0.5,robot)

    async def tTestNextMax(self,robot:cozmo.robot.Robot):
        self.agent.Q = [[0,1],[1,2]]
        maxValue = 2
        await self.agent.nextActionMax(1,robot)
        self.assertEqual(maxValue,self.agent.maxAction)

