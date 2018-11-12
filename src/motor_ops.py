#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import time
import atexit
import threading
import random


class MotorOps(Adafruit_MotorHAT):

    """
    Summary: Inherits Motor specific functionality and acts as the brains while
    instructing motors based on message received from alexa skill.

    Params: message DICT - message containing action and curtain it pertains to

    """
    def __init__(self, message):
        self.message = message
        # Create a default object, no changes to I2C address or frequency
        Adafruit_MotorHAT.__init__(self)
        # TODO: Ensure that this works like a teardown of the class
        atexit.register(self.turnOffMotors)
        # 200 steps/rev, motor port #1
        self.leftStepper = super().getStepper(steps=200, num=1)
        # 200 steps/rev, motor port #2
        self.rightStepper = super().getStepper(steps=200, num=2)
        self.leftStepper.setSpeed(rpm=60) # 60 rpm
        self.rightStepper.setSpeed(rpm=60) # 60 rpm

    def interpret_message(self):
        """
        Summary: Interprets the meaning of the message. Whether to power
        both motors, one motor, and the specific action on the curtain
        """
        pass

    def turnOffMotors(self):
        """
        Summary: auto disables motors upon shutdown
        """
        #TODO: try with get stepper instead. Remove get motor if it works
        super().getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        super().getMotor(2).run(Adafruit_MotorHAT.RELEASE)

# create empty threads (these will hold the stepper 1 and 2 threads)
st1 = threading.Thread()
st2 = threading.Thread()

stepstyles = [Adafruit_MotorHAT.SINGLE, Adafruit_MotorHAT.DOUBLE, Adafruit_MotorHAT.INTERLEAVE, Adafruit_MotorHAT.MICROSTEP]

def stepper_worker(stepper, numsteps, direction, style):
    stepper.step(numsteps, direction, style)

while (True):
    if not st1.isAlive():
        randomdir = random.randint(0, 1)
        print("Stepper 1"),
        if (randomdir == 0):
            dir = Adafruit_MotorHAT.FORWARD
            print("forward"),
        else:
            dir = Adafruit_MotorHAT.BACKWARD
            print("backward"),
        randomsteps = random.randint(10,50)
        print("%d steps" % randomsteps)
        st1 = threading.Thread(target=stepper_worker, args=(myStepper1, randomsteps, dir, stepstyles[random.randint(0,3)],))
        st1.start()

    if not st2.isAlive():
        print("Stepper 2"),
        randomdir = random.randint(0, 1)
        if (randomdir == 0):
            dir = Adafruit_MotorHAT.FORWARD
            print("forward"),
        else:
            dir = Adafruit_MotorHAT.BACKWARD
            print("backward"),

        randomsteps = random.randint(10,50)
        print("%d steps" % randomsteps)

        st2 = threading.Thread(target=stepper_worker, args=(myStepper2, randomsteps, dir, stepstyles[random.randint(0,3)],))
        st2.start()
    
    time.sleep(0.1)  # Small delay to stop from constantly polling threads (see: https://forums.adafruit.com/viewtopic.php?f=50&t=104354&p=562733#p562733)
