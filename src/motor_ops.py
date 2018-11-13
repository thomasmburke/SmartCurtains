#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import atexit
import threading


class MotorOps(Adafruit_MotorHAT):

    """
    Summary: Inherits Motor specific functionality and acts as the brains while
    instructing motors based on message received from alexa skill.

    Params: message DICT - message containing action and curtain it pertains to

    """
    MAX_STEPS = 200

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
        # If neither cutain is specified then operate on both
        if not self.message['direction'] or self.message['direction'] == 'both':
            # TODO: see if we can use super() below
            leftStepperThread = threading.Thread(target=self.stepper_worker, args=(self.leftStepper, self.MAX_STEPS, self.FORWARD, Adafruit_MotorHAT.SINGLE))
            rightStepperThread = threading.Thread(target=self.stepper_worker, args=(self.rightStepper, self.MAX_STEPS, super().FORWARD, Adafruit_MotorHAT.SINGLE))
            leftStepperThread.start()
            rightStepperThread.start()

    def turnOffMotors(self):
        """
        Summary: auto disables motors upon shutdown
        """
        #TODO: try with get stepper instead. Remove get motor if it works
        super().getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        super().getMotor(2).run(Adafruit_MotorHAT.RELEASE)

    def stepper_worker(self, stepper, numsteps, direction, style):
        stepper.step(numsteps, direction, style)
