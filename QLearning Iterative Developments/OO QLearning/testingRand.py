from random import randint
actions = [0,1,2,3]
rewards = [[-1.1,-2.1,-1.5,-2],[-0.1,-0.1,1.5,0], [-2.1,-0.1,0.5,0]]

def nextAction():
    # nextActRand = randint(0, 3)
    # nextAct = actions[nextActRand]

    # allActs = availActions(currentState)
    nextActRand = randint(0,3)
    nextAct = allActs[nextActRand]
    indexOfNextAct = allActs.index(nextAct)
    return indexOfNextAct

def availActions(state):
    assert state >= 0 and state < len(rewards),"Sorry the state is not valid"
    currentStateRow = rewards[state][:]
    return currentStateRow

allActs = availActions(0)
nextAction()
