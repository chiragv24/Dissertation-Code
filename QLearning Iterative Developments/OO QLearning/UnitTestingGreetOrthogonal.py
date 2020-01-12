import unittest
import numpy as np
from SuperClassParamTesting import QLearnGreetOrthogonal
import generalTestingMethods

class currentStateTesting(generalTestingMethods):

    def setUp(self):
        self.agent = QLearnGreetOrthogonal()

    def test_currentStates(self):
        super().tCurrentStates()

class robotMovementTesting(generalTestingMethods):
    def setUp(self):
        self.agent = QLearnGreetOrthogonal()

    def test_values(self):
        action = self.agent.robotMovement()
        if action == 1:
            self.assertEqual(self.agent.lastAction,"Greeted")
        elif action == 0:
            self.assertEqual(self.agent.lastAction,"Not Greeted")
        else:
            with self.assertRaises(AssertionError):
                self.agent.robotMovement()

class testUpdate(generalTestingMethods):

    def setUp(self):
        self.agent = QLearnGreetOrthogonal()

    def test_qMatrixUpdate(self):
        super().tQMatrixUpdate()

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