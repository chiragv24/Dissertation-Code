import unittest
from QLearn3States import availActions


#Unit test class

class availableActions(unittest.TestCase):
    def test_availActionsTestFar(self):
        """Tests the result of the far state"""
        result = availActions(0)
        self.assertEqual(result,[-1.1,-2.1,-1.5,-2])

    def test_availActionsTestOpt(self):
        """Tests the result of the optimal state"""
        result = availActions(1)
        self.assertEqual(result,[-0.1,-0.1,1.5,0])

    def test_availActionsTestClose(self):
        result = availActions(2)
        self.assertEqual(result,[-2.1,-0.1,0.5,0])

    def test_availActionsTestNeg(self):
        #result = availActions(-1)
        with self.assertRaises(AssertionError):
            availActions(-1)

    def test_availActionsTestString(self):
        #result = availActions(-1)
        with self.assertRaises(TypeError):
            availActions("Hello")

if __name__ == '__main__':
    unittest.main()