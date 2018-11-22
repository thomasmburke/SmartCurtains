#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_StepperMotor
import atexit
import threading
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class MotorOps(Adafruit_MotorHAT):

    """
    Summary: Inherits Motor specific functionality and acts as the brains while
    instructing motors based on message received from alexa skill.

    Params: message DICT - message containing action and curtain it pertains to

    """
    MAX_STEPS = 2000000

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
        self.leftStepper.setSpeed(rpm=6000) # rpm
        self.rightStepper.setSpeed(rpm=6000) # rpm

    def interpret_message(self):
        """
        Summary: Interprets the meaning of the message. Whether to power
        both motors, one motor, and the specific action on the curtain along
        with the percentage of the action
        """
        if 'left' in self.message:
            numSteps = int(self.MAX_STEPS * float(self.message['left']['percentage']))
            direction = self.FORWARD if self.message['left']['action'] == 'open' else self.BACKWARD
            logger.info('Left Motor - numSteps={0}, direction={1}'.format(numSteps,direction))
            leftStepperThread = threading.Thread(target=self.stepper_worker, args=(self.leftStepper, numSteps, direction, self.SINGLE))
            leftStepperThread.start()
        if 'right' in self.message:
            numSteps = int(self.MAX_STEPS * float(self.message['right']['percentage']))
            direction = self.FORWARD if self.message['right']['action'] == 'open' else self.BACKWARD
            logger.info('Right Motor - numSteps={0}, direction={1}'.format(numSteps,direction))
            rightStepperThread = threading.Thread(target=self.stepper_worker, args=(self.rightStepper, numSteps, direction, self.SINGLE))
            rightStepperThread.start()

    def turnOffMotors(self):
        """
        Summary: auto disables motors upon shutdown
        """
        super().getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        super().getMotor(2).run(Adafruit_MotorHAT.RELEASE)

    def stepper_worker(self, stepper, numsteps, direction, style):
        stepper.step(numsteps, direction, style)

if __name__=='__main__':
    MotorOps(message={'left': {'percentage':0.5, 'action': 'open'}, 'right': {'percentage':0.5, 'action': 'close'}}).interpret_message()
