import unittest
import cozmo
import sys
from cozmo.util import distance_mm
#from QLearnSuperClass import QLearnDistOrthogonal
import numpy as np
from SuperClassParamTesting import QLearnTurnOrthogonal
from SuperClassParamTesting import QLearnLiftOrthogonal
from generalTesting import generalTestingMethods

class currentStateTesting(generalTestingMethods):

    def setUp(self):
        self.agent = QLearnLiftOrthogonal()

    def testCurrentStates(self):
        super().tCurrentStates(self)

class robotMovementTesting(generalTestingMethods):

    def setUp(self):
        generalTestingMethods.agent = QLearnLiftOrthogonal()

    def test_values(self):
        action = self.agent.robotMovement()
        if action == 1:
            self.assertEqual(self.agent.lastAction,"Picked Up")
        elif action == 0:
            self.assertEqual(self.agent.lastAction,"Not Picked Up")
        else:
            with self.assertRaises(AssertionError):
                self.agent.robotMovement()

class testUpdate(generalTestingMethods):

    def setUp(self):
        self.agent = QLearnLiftOrthogonal()

    def test_qMatrixUpdate(self):
        super().tQMatrixUpdate(self)

    def test_negativeState(self):
        super().tnegativeState(self)

    def test_decimalState(self):
        super().tdecimalState(self)

    def test_stringState(self):
        super().tstringState(self)

    def test_largeStateValue(self):
        super().tlargeStateValue(self)

    def test_negativeAction(self):
        super().tnegativeAction(self)

    def test_decimalAction(self):
        super().tdecimalAction(self)

    def test_stringAction(self):
        super().tstringAction(self)

    def test_largeActionValue(self):
        super().tlargeActionValue(self)

    def test_largeGamma(self):
        super().tlargeGamma(self)

    def test_stringGamma(self):
        super().tstringGamma(self)


