import unittest

rewards = [[-1.1,-2.1,-1.5,-2],[-0.1,-0.1,1.5,0], [-2.1,-0.1,0.5,0]]

def availActions(state):
    assert state >= 0 and state < len(rewards),"Sorry the state is not valid"
    currentStateRow = rewards[state][:]
    return currentStateRow

# class availableActions(unittest.TestCase):
#
#     def setUp(self):
#         pass
#
#     def test_availActionsTestFar(self):
#         """Tests the result of the far state"""
#         result = availActions(0)
#         self.assertEqual(result,[-1.1,-2.1,-1.5,-2])
#
#     def test_availActionsTestOpt(self):
#         """Tests the result of the optimal state"""
#         result = availActions(1)
#         self.assertEqual(result,[-0.1,-0.1,1.5,0])
#
#     def test_availActionsTestClose(self):
#         result = availActions(2)
#         self.assertEqual(result,[-2.1,-0.1,0.5,0])
#
#
# if __name__ == '__main__':
#     unittest.main()