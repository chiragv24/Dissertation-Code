import unittest
import numpy as np
from SuperClassParamTesting import QLearnTurnOrthogonal
from generalTesting import generalTestingMethods

class currentStateTesting(generalTestingMethods):

    def setUp(self):
        self.agent = QLearnTurnOrthogonal()

    def testCurrentStates(self):
        super().tCurrentStates()

class robotMovementTesting(generalTestingMethods):

    def setUp(self):
        self.agent = QLearnTurnOrthogonal()

    def testRobotMovement(self):
        ###FINISH OFF THIS TEST#####

class updateTesting(generalTestingMethods):

    def setUp(self):
        self.agent = QLearnTurnOrthogonal()

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