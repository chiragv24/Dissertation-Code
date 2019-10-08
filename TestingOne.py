#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Wait for Cozmo to see a face, and then turn on his backpack light.

This is a script to show off faces, and how they are easy to use.
It waits for a face, and then will light up his backpack when that face is visible.
'''

import asyncio
import time

import collections
import cozmo
import cozmoclad
from cozmoclad.clad.externalInterface import messageEngineToGame as messageEngineToGame
from cozmoclad.clad.externalInterface import messageEngineToGame as messageGameToEngine

# import cozmo.faces
# from cozmo import event
# from cozmo.faces import EvtFaceObserved


__all__ = ['FACE_VISIBILITY_TIMEOUT',
           'FACIAL_EXPRESSION_UNKNOWN', 'FACIAL_EXPRESSION_NEUTRAL', 'FACIAL_EXPRESSION_HAPPY',
           'FACIAL_EXPRESSION_SURPRISED', 'FACIAL_EXPRESSION_ANGRY', 'FACIAL_EXPRESSION_SAD',
           'EvtErasedEnrolledFace', 'EvtFaceAppeared', 'EvtFaceDisappeared',
           'EvtFaceIdChanged', 'EvtFaceObserved', 'EvtFaceRenamed',
           'erase_all_enrolled_faces', 'erase_enrolled_face_by_id',
           'update_enrolled_face_by_id']

_clad_to_engine_anki = messageGameToEngine.Anki
_clad_to_engine_cozmo = messageGameToEngine.Anki.Cozmo
_clad_to_engine_iface = messageGameToEngine.Anki.Cozmo.ExternalInterface
_clad_to_game_anki = messageEngineToGame.Anki
_clad_to_game_cozmo = messageEngineToGame.Anki.Cozmo
_clad_to_game_iface = messageEngineToGame.Anki.Cozmo.ExternalInterface
_clad_enum = _clad_to_engine_cozmo.ExecutableBehaviorType


def greet(robot: cozmo.robot.Robot):
# Move lift down and tilt the head up
#     robot.move_lift(-3)
#     robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

    print("Press CTRL-C to quit")
    face = None
    while True:
        if not robot.head_angle == cozmo.robot.MAX_HEAD_ANGLE:
            robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
        if face and face.is_visible:
            robot.say_text("Hello, how are you?").wait_for_completed()
            robot.enable_facial_expression_estimation(True)
            if not _clad_to_game_anki.Vision.FacialExpression == _clad_to_game_anki.Vision.FacialExpression.Happiness:
                robot.say_text("Please cheer up, it would make me so happy, please play with me").wait_for_completed()
                #robot.start_behavior(robot,cozmo.behavior.BehaviorTypes.PounceOnMotion)
                robot.play_anim_trigger(cozmo.anim.Triggers.MajorWin).wait_for_completed()
            else:
                robot.say_text("Good to see that you are happy today").wait_for_completed()
        else:
            robot.say_text("Sorry, no face found").wait_for_completed()
            try:
                face = robot.world.wait_for_observed_face(timeout=30)
            except asyncio.TimeoutError:
                print("Didn't find a face.")
                return

        time.sleep(.1)


cozmo.run_program(greet, use_viewer=True, force_viewer_on_top=True)