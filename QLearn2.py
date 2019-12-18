import numpy as np
from random import seed
from random import randint
#
#Where 1 = far dist, 2 = close dist
states = [0,1]
#Where 1 = forward, 2 = backward, 3 = greet, 4 = idle
actions = [0,1,2,3]
#states = [(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3)]
rewards = [[-1.1,-2.1,-1.5,-2],[-2.1,-0.1,0.5,0]]
gamma = 0.8
exploreVExploit = 0.2
reward = 0.1
#Q = np.matrix(np.zeros([2,4]))
Q = [[0,0,0,0],[0,0,0,0]]
initState = 0

def availActions(state):
    currentStateRow = rewards[state][:]
    print(currentStateRow)
    return currentStateRow

allActs = availActions(initState)
#
def nextAction(allActs):
    nextActRand = randint(0,3)
    nextAct = allActs[nextActRand]
    return allActs.index(nextAct)
#
nextAct = nextAction(allActs)
#
#ATM ACTION AND CURRENTSTATE ARE CHANGED ROUND, THIS HAS TO BE FIXED
def update(currentState,action,gamma):
    print("currentstate in the method update")
    print(currentState)
    print(np.max(rewards[currentState][:]))
    Q[currentState][action] = rewards[currentState][action] + (exploreVExploit  * (reward + gamma * (np.max(rewards[currentState][:])))) - rewards[currentState][action]
    return currentState

val = update(initState,nextAct,gamma)

#NOW TRAIN THE MODEL SO IT ACTUALLY COMES OUT WITH SOMETHING USEFUL
for i in range (1000):
    #currentStateRand = randint(0,1)
    # #currentState = Q[currentStateRand]
    # #actions = availActions(currentState)
    # bestAction = nextAction(actions)
    # print("CURRENTINTHELOOP")
    # print(currentStateRand)
    # print("BESTINTHELOOP")
    # print(bestAction)
    # eval = update(currentStateRand,bestAction,gamma)

    currentStateRand = randint(0,1)
    action = nextAction(actions)
    eval = update(currentStateRand, action, gamma)
    print(Q)

print("THIS IS THE FINAL RESULT")
print(Q)
































# def update(state,action):
#     print("Before")
#     print(rewards)
#     print(rewards[state][action])
#     rewards[state][action] = rewards[state][action] + exploreVExploit * (reward + gamma * np.max(rewards[state][:])) - rewards[state][action]
#     print("After")
#     print(rewards)




#exploration v exploitation
# gamma = 0.5
# learnR = 0.5
# epochs = 5


