import unittest
import numpy as np
from random import randint
import cozmo
import asyncio
import aiounittest
#from SuperClassParamTesting
from asyncioTesting import QLearnGreetOrthogonal
from generalTesting import generalTestingMethods


class currentStateTesting(generalTestingMethods):

    def setUp(self):
        self.agent = QLearnGreetOrthogonal()
        self.robot = cozmo.robot.Robot

    async def test_NoGreet(self):
        self.agent.findCurrentState(self.robot)

    def test_currentStates(self):
        super().tCurrentStates(self.robot)

class robotMovementTesting(generalTestingMethods):

    def setUp(self):
        self.robot = cozmo.robot.Robot
        self.agent = QLearnGreetOrthogonal()
        self.greeted = False
        self.lastAction = ""

    async def test_RobotMovement1(self):
        #await cozmo.run_program(self.agent.robotMovement(1,self.robot))
        loop =  asyncio.get_event_loop()
        await loop.run_until_complete(cozmo.run_program(self.agent.robotMovement))
        #y = await self.agent.robotMovement(1,self.robot)
        self.assertEquals(self.agent.lastAction,"Greeted")




        # robot = cozmo.robot.Robot
        # randomAction = randint(0,1)
        # loop  = asyncio.get_event_loop()
        # await loop.run_until_complete(self.robotMovement(randomAction,robot))
        #act = await self.robotMovement(randomAction,robot)

        # robot = cozmo.robot.Robot
        # randomAction = randint(0,1)
        # action = await self.agent.robotMovement(randomAction,robot)
        # if action == 1:
        #     self.assertEqual(self.agent.lastAction,"Greeted")
        # elif action == 0:
        #     self.assertEqual(self.agent.lastAction,"Not Greeted")
        # else:
        #     with self.assertRaises(AssertionError):
        #         await self.agent.robotMovement(randomAction,robot)

class testUpdate(generalTestingMethods):

    def setUp(self):
        self.agent = QLearnGreetOrthogonal()

    def test_qMatrixUpdate(self):
        print(self.agent.Q)
        currentState = 1
        action = 0
        maxValue = np.max(self.agent.Q[currentState][:])
        valBefore = self.agent.Q[currentState][action]
        print(self.agent.Q)
        valAfter = (1 - self.agent.rate) * self.agent.Q[currentState][action] + (self.agent.rate * round(self.agent.rewards[currentState][action] + self.agent.gamma * maxValue, 2))
        self.agent.update(currentState, action, self.agent.gamma)
        self.assertEqual(valAfter+valBefore, self.agent.Q[currentState][action])

    def test_negativeState(self):
        super().tnegativeAction()

    def test_decimalState(self):
        super().tdecimalState()

    def test_stringState(self):
        super().tstringState()

    def test_largeStateValue(self):
        super().tlargeStateValue()

    def test_negativeAction(self):
        super().tnegativeAction()

    def test_decimalAction(self):
        super().tdecimalAction()

    def test_stringAction(self):
        super().tstringAction()

    def test_largeActionValue(self):
        super().tlargeActionValue()

    def test_largeGamma(self):
        super().tlargeGamma()

    def test_stringGamma(self):
        super().tstringGamma()

class testNextMax(generalTestingMethods):

    def setUp(self):
        self.robot = cozmo.robot.Robot
        self.agent = QLearnGreetOrthogonal()

    async def test_negativeMaxState(self):
        await super().tstringStateMax(self.robot)

    async def test_decimalMaxState(self):
        await super().tnegStateMax(self.robot)

    async def test_stringStateMax(self):
        await super().tdecStateMax(self.robot)

    async def test_testNextMax(self):
        await super().tTestNextMax(self.robot)