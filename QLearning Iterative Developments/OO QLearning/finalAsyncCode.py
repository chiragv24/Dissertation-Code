import cozmo
import asyncio
from cozmo.util import distance_mm, speed_mmps
from random import randint
import numpy as np
import time
import abc
from threading import Thread
from microIntegration import voiceIntegration

class QLearnSuperClass(abc.ABC):

    def __init__(self):
        self.initState = 0
        self.gamma = 0.8
        self.nextActIndex = 0
        self.Q = []
        self.states = []
        self.actions = []
        self.rewards = []
        self.voice = voiceIntegration()
        self.loop = asyncio.get_event_loop()

    @abc.abstractmethod
    def robotMovement(self,*args,**kwargs):
        pass

    @abc.abstractmethod
    def nextAction(self,*args,**kwargs):
        pass

    @abc.abstractmethod
    def update(self,currentState,action,gamma):
        pass

    @abc.abstractmethod
    def findCurrentState(self):
        pass

    @abc.abstractmethod
    def trainCozmo(self,robot:cozmo.robot.Robot):
        pass

    @abc.abstractmethod
    def startLoop(self,loop):
        pass

    @abc.abstractmethod
    def makeThread(self):
        pass

##############FIRST ORTHOGONAL ######################################################3

class QLearnDistOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnDistOrthogonal, self).__init__()
        self.actions = [0,1,2,3]
        self.rewards = [[-1.1,-2.1,-1.5,-2],[-0.1,-0.1,1.5,0], [-2.1,-0.1,0.5,0]]
        self.Q = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.states = [0,1,2]
        self.gamma = 0.8
        self.initState = 0
        self.nextActIndex = 0
        self.currentState = 0
        self.facialExpression = ""
        self.robotHeadPosition = 0
        self.robotLiftPosition = 0
        self.robotHeadPositionBef = 0
        self.robotLiftPositionBef = 0
        self.distanceFromFace = 0
        self.voice = voiceIntegration()

    async def robotSayTextIdle(self, robot: cozmo.robot.Robot):
        await robot.say_text("I'm happy to stay here until you tell me to move").wait_for_completed()

    async def robotMoveBack(self, robot: cozmo.robot.Robot):
        await robot.drive_straight(distance_mm(-100), speed_mmps(50)).wait_for_completed()

    async def robotMoveFront(self, robot: cozmo.robot.Robot):
        await robot.drive_straight(distance_mm(100), speed_mmps(50)).wait_for_completed()

    async def robotGreet(self, robot: cozmo.robot.Robot):
        await robot.say_text("Hello how are you doing today?").wait_for_completed()

    async def robotMovement(self, actionNum, facialExp, currentState):
        assert 0 <= actionNum <= 3
        assert currentState == 0 or currentState == 1
        allExps = ["Unknown","Happy","Sad","Neutral","Surprised","Angry"]
        facial = False

        for i in range(allExps.__len__()):
            if facialExp.lower() == allExps[i].lower():
                facial = True
        assert facial == True

        if (currentState == 0 and facialExp == "happy"):
            print("staying far")
            await cozmo.run_program(self.robotSayTextIdle)
            return "staying far"

        elif (currentState == 2 and facialExp == "happy"):
            print("staying close")
            await cozmo.run_program(self.robotSayTextIdle)
            return "staying close"

        elif (actionNum == 0):
            print("Moving backwards")
            await cozmo.run_program(self.robotMoveBack)
            return "moving backwards"

        elif (actionNum == 1):
             print("Moved forward")
             await cozmo.run_program(self.robotMoveBack)
             return "moving forwards"

        elif (actionNum == 2):
            print("Greeted")
            await cozmo.run_program(self.robotGreet)
            return "greeting"

        else:
            print("idle")
            return "idle"

    def nextAction(self):
        nextActRand = randint(0,3)
        global nextActionIndex
        nextActionIndex = nextActRand
        return nextActionIndex

    async def robotHeadMoveHW(self,robot:cozmo.robot.Robot):
        self.robotHeadPositionBef = robot.head_angle
        self.robotLiftPositionBef = robot.lift_position.height.distance_mm

        if robot.lift_position != cozmo.robot.MIN_LIFT_HEIGHT:
            self.robotLiftPosition = cozmo.robot.MIN_LIFT_HEIGHT.distance_mm
            await robot.move_lift(-3)
        if robot.head_angle!=cozmo.robot.MAX_HEAD_ANGLE:
            self.robotHeadPosition = cozmo.robot.MAX_HEAD_ANGLE
            await robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

    def robotHeadMoveHelper(self):
        cozmo.run_program(self.robotHeadMoveHW)

    async def findCurrentStateHW(self,robot:cozmo.robot.Robot):
        face = None
        while True:
            if face and face.is_visible:
                for face in robot.world.visible_faces:
                    print()
                    print("Is this always the same face instance " + str(face))
                    print("THIS IS THE DISTANCE " + str(face.pose.position.x))
                    robot.pose.define_pose_relative_this(face.pose)
                    self.distanceFromFace = face.pose.position.x

                    if face.pose.position.x < float(350) and face.pose.position.x > float(150):
                        await robot.say_text("I'm currently in the optimal state").wait_for_completed()
                        self.currentState = 1
                    elif face.pose.position.x > float(350):
                        await robot.say_text("I´m currently in the far state").wait_for_completed()
                        self.currentState = 0
                    else:
                        await robot.say_text("I'm currently in the close state").wait_for_completed()
                        self.currentState = 2
                    return self.currentState
            else:
                try:
                    await robot.say_text("Sorry, I couldn´t find your face, 10 seconds to do it").wait_for_completed()
                    #This one might fail
                    face = await robot.world.wait_for_observed_face(timeout=10)
                except asyncio.TimeoutError:
                    await robot.say_text("Sorry, it will have to be next time").wait_for_completed()
                    print("Face not found")
                    return

    def findCurrentState(self):
        cozmo.run_program(self.findCurrentStateHW)

    async def facialExpEstimateHW(self, robot: cozmo.robot.Robot):
        face = None
        while True:
            if face and face.is_visible:
                robot.enable_facial_expression_estimation(True)
                self.facialExpression = face.expression
                return face.expression
            else:
                try:
                    face = await robot.world.wait_for_observed_face(timeout=10)
                except asyncio.TimeoutError:
                    await robot.say_text("Sorry it will have to be next time").wait_for_completed()
                    print("Didn't find a face.")
                    return

    def facialExpressionEstimate(self):
        cozmo.run_program(self.facialExpEstimateHW)

    def update(self,currentState,action,gamma):
        assert 0 <= currentState <= 2
        assert 0 <= action <= 3
        assert 0 <= gamma <= 1
        self.Q[currentState][action] = self.Q[currentState][action] + round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

    def startLoop(self,loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)

    async def voiceMove(self,robot:cozmo.robot.Robot,action):
            if action == 0:
                await robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
            elif action == 2:
                await robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
            elif action == 1:
                await robot.say_text("I'm in the best state though").wait_for_completed()

    async def trainCozmo(self,robot:cozmo.robot.Robot):
        self.makeThread()
        for i in range (5):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                print("This is the voice speech " + self.voice.speech)
                if "Move".lower() in self.voice.speech.lower():
                    dist = await self.findCurrentStateHW(robot)
                    randomAction = randint(0,3)
                    await self.voiceMove(robot,randomAction)
                    self.voice.QMove[dist,randomAction] =  self.Q[dist][randomAction] + round(self.rewards[dist][randomAction] + self.gamma * np.max(self.rewards[dist][:]), 2)
                elif "Stop".lower() in self.voice.speech.lower():
                    randomAction = randint(0,1)
                    if randomAction == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    self.voice.QStop[randomAction] = self.Q[randomAction] + round(self.rewards[randomAction] + self.gamma * np.max(self.rewards[:]), 2)
                    break
        await self.findCurrentState()
        act = self.nextAction()
        await self.facialExpressionEstimate()
        await self.robotMovement(act, self.facialExpression, self.currentState)
        self.update(self.currentState, nextActionIndex, self.gamma)

###########################SECOND ORTHOGONAL#############################################33

class QLearnGreetOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnGreetOrthogonal,self).__init__()
        #0 = Idle , 1 = Greet
        self.actions = [0, 1]
        self.rewards = [[-0.5, 1.5], [-1.5, 1]]
        self.Q = [[0, 0, 0, 0], [0, 0, 0, 0]]
        #Where 0 is not greeted and 1 is greeted
        self.states = [0, 1]
        self.gamma = 0
        self.initState = 0
        self.nextActIndex = 0
        ##Where 0 = false and 1 = true
        self.greeted = 0
        self.lastAction = ""
        self.dist = QLearnDistOrthogonal()
        self.voice = voiceIntegration()

    def findCurrentState(self):
        randomAction = randint(0,1)
        if randomAction == 0:
            self.greeted = 0
        else:
            self.greeted = 1
        return randomAction

    async def robotMovementHW(self, actionNum, robot: cozmo.robot.Robot):
        assert actionNum == 0 or actionNum == 1
        if (actionNum == 1):
            print("THIS IS THE GREET ORTHOGONAL")
            await robot.say_text("Hello how are you doing today?, I´m Cozmo").wait_for_completed()
            self.greeted = True
            self.lastAction = "Greeted"
            return actionNum
        else:
            print("THIS IS THE GREET AROUND ORTHOGONAL")
            await robot.say_text("I'm sad")
            self.lastAction = "Not Greeted"
            return actionNum

    def robotMovement(self):
        cozmo.run_program(self.robotMovementHW)

    def nextAction(self):
        nextActRand = randint(0, 1)
        global nextActionIndex
        nextActionIndex = nextActRand

    def update(self, currentState, action, gamma):
        assert currentState == 0 or currentState == 1
        assert action == 0 or action == 1
        assert 0 < gamma <= 1
        self.Q[currentState][action] = round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)

    async def trainCozmo(self, robot: cozmo.robot.Robot):
        self.makeThread()
        for i in range(5):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                if "Move".lower() in self.voice.speech.lower():
                    randomAction = randint(0,3)
                    dist = await self.dist.findCurrentStateHW(robot)
                    await self.dist.voiceMove(robot,randomAction)
                    self.voice.QMove[dist, randomAction] = self.Q[dist][randomAction] + round(self.rewards[dist][randomAction] + self.gamma * np.max(self.rewards[dist][:]), 2)
                elif "Stop".lower() in self.voice.speech.lower():
                    randomAction = randint(0,1)
                    if randomAction == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    self.voice.QStop[randomAction] = self.Q[randomAction] + round(self.rewards[randomAction] + self.gamma * np.max(self.rewards[:]), 2)
                break
            await self.findCurrentState()
            self.nextAction()
            await self.robotMovement()
            self.update(self.greeted, nextActionIndex, self.gamma)
            print(self.Q)
            time.sleep(5)

#########################THIRD ORTHOGONAL############################################33

class QLearnTurnOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnTurnOrthogonal, self).__init__()
        self.actions = [0, 1]
        self.rewards = [[-0.5, 1.5], [-1.5, 1]]
        self.Q = [[0, 0, 0, 0], [0, 0, 0, 0]]
        self.states = [0, 1]
        self.gamma = 0
        self.initState = 0
        self.nextActIndex = 0
        self.currentState = 0
        self.lastState = None
        self.dist = QLearnDistOrthogonal()
        self.voice = voiceIntegration()

    def nextAction(self):
        nextActRand = randint(0,1)
        global nextActionIndex
        nextActionIndex = nextActRand

    def findCurrentStateHW(self,robot:cozmo.robot.Robot):
        robot.enable_all_reaction_triggers(True)
        angle = str(robot.pose_pitch.degrees)
        if 90 < float(angle) < 180:
            self.currentState = 1
        else:
            self.currentState = 0
        return self.currentState

    def findCurrentState(self):
        cozmo.run_program(self.findCurrentStateHW)

    async def robotMovementHW(self,actionNum,robot:cozmo.robot.Robot):
        if(actionNum==1):
            print("THIS IS THE TURNED AROUND ORTHOGONAL")
            await robot.play_anim("anim_reacttocliff_faceplantroll_02").wait_for_completed()
            time.sleep(5)
        else:
            print("THIS IS THE TURNED AROUND ORTHOGONAL")
            await robot.say_text("I don´t like to be flipped, please rotate me around again").wait_for_completed()

    def robotMovement(self):
        cozmo.run_program(self.robotMovementHW)

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)

    def update(self,currentState,action,gamma):
        assert currentState == 0 or currentState == 1
        assert action == 0 or action == 1
        assert 0 < gamma <=1
        self.Q[currentState][action] = self.Q[currentState][action] +  round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

    async def trainCozmo(self, robot: cozmo.robot.Robot):
        self.makeThread()
        for i in range(15):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                if "Move".lower() in self.voice.speech.lower():
                    randomAction = randint(0,1)
                    dist = await self.dist.findCurrentStateHW(robot)
                    await self.dist.voiceMove(robot,randomAction)
                    self.voice.QMove[dist, randomAction] = self.Q[dist][randomAction] + round(
                        self.rewards[dist][randomAction] + self.gamma * np.max(self.rewards[dist][:]), 2)
                elif "Stop".lower() in self.voice.speech.lower():
                    randomAction = randint(0, 1)
                    if randomAction == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    self.voice.QStop[randomAction] = self.Q[randomAction] + round(
                        self.rewards[randomAction] + self.gamma * np.max(self.rewards[:]), 2)
                break
            else:
                await self.findCurrentState()
                self.nextAction()
                await self.robotMovement()
                self.update(self.currentState, nextActionIndex, self.gamma)
                print(self.Q)
                time.sleep(5)

###########################FOURTH ORTHOGONAL #################################################3

class QLearnLiftOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnLiftOrthogonal, self).__init__()
        self.actions = [0, 1, 2, 3]
        self.rewards = [[-0.5, 1.5], [-1.5, 1]]
        self.Q = [[0, 0, 0, 0], [0, 0, 0, 0]]
        self.states = [0, 1]
        self.gamma = 0.8
        self.initState = 0
        self.nextActIndex = 0
        self.currentState = None
        self.lastState = None
        self.dist = QLearnDistOrthogonal()
        self.voice = voiceIntegration()

    def findCurrentStateHW(self, robot: cozmo.robot.Robot):
        assert self.currentState == 0 or self.currentState == 1
        if robot.is_picked_up:
            self.currentState = 1
        else:
            self.currentState = 0
        return self.currentState

    def findCurrentState(self):
        cozmo.run_program(self.findCurrentStateHW)

    async def robotMovementHW(self, actionNum, robot: cozmo.robot.Robot):
        assert actionNum == 0 or actionNum == 1
        if actionNum == 0:
            self.lastState = "Picked Up"
            await robot.play_anim("anim_reacttocliff_pickup_01").wait_for_completed()
            print("THIS IS THE PICKED UP ORTHOG")
        elif actionNum == 1:
            print("THIS IS THE PICKED UP ORTHOG")
            self.lastState = "Not Picked Up"
            await robot.say_text("I like to be on the table, please don´t pick me up").wait_for_completed()
        return actionNum

    def robotMovement(self):
        cozmo.run_program(self.robotMovementHW)

    def nextAction(self):
        nextActRand = randint(0,1)
        global nextActionIndex
        nextActionIndex = nextActRand

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)

    async def trainCozmo(self, robot: cozmo.robot.Robot):
        self.makeThread()
        for i in range (15):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                if "Move".lower() in self.voice.speech.lower():
                    randomAction = randint(0, 3)
                    dist = await self.dist.findCurrentStateHW(robot)
                    await self.dist.voiceMove(robot,randomAction)
                    self.voice.QMove[dist, randomAction] = self.Q[dist][randomAction] + round(self.rewards[dist][randomAction] + self.gamma * np.max(self.rewards[dist][:]), 2)
                elif "Stop".lower() in self.voice.speech.lower():
                    randomAction = randint(0,1)
                    if randomAction == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    self.voice.QStop[randomAction] = self.Q[randomAction] + round(self.rewards[randomAction] + self.gamma * np.max(self.rewards[:]), 2)
                break
            else:
                await self.findCurrentState()
                self.nextAction()
                await self.robotMovement()
                self.update(self.currentState, nextActionIndex, self.gamma)
                print(self.Q)
                time.sleep(5)

    def update(self,currentState,action,gamma):
        assert currentState == 0 or currentState == 1
        assert action == 0 or action == 1
        assert 0 < gamma <=1
        self.Q[currentState][action] = self.Q[currentState][action] + round(self.rewards[currentState][action] + gamma
