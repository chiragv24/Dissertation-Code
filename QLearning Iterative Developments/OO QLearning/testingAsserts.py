def robotMovement(actionNum, facialExp, currentState):
    allExps = ["Unknown", "Happy", "Sad", "Neutral", "Surprised", "Angry"]
    assert 0 <= actionNum <= 2
    assert currentState == 0 or currentState == 1
    facial = False
    for i in range(allExps.__len__()):
        if facialExp.lower() == allExps[i].lower():
            facial = True
    assert facial == True
    print(actionNum)
    print(facialExp)
    print(currentState)

robotMovement(1,"Happy",1)

