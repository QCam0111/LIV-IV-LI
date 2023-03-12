"""
Function referenced when: A measurement is made using the oscilloscope and current/voltage pulser.
Description: Updates the oscilloscope trigger level to between 25% and 90% of the total oscilloscope display.
"""

from time import sleep

def updateTriggerCursor(self, pulseAmplitude, scope, totalDisplay):
    new_trigger = 3*pulseAmplitude/4.0
    if (new_trigger < 0.25*totalDisplay):
        new_trigger = 0.25*totalDisplay
    elif (new_trigger > 0.75*totalDisplay):
        new_trigger = 0.5*totalDisplay
    scope.write(":TRIGger:GLITch:LEVel %.6f" % (new_trigger))
    sleep(0.5)

    return new_trigger
