"""
Function referenced when: A measurement is made using the oscilloscope and current/voltage pulser.
Description: Updates the oscilloscope trigger level to between 25% and 90% of the total oscilloscope display.
"""

from time import sleep

def updateTriggerCursor(pulseAmplitude, scope, totalDisplay):
    new_trigger = 3*pulseAmplitude/4
    if (new_trigger < 0.1*totalDisplay):
        new_trigger = 0.1*totalDisplay
    elif (new_trigger > 0.9*totalDisplay):
        new_trigger = 0.5*totalDisplay
    scope.write(":TRIGger:GLITch:LEVel %.6f" % (new_trigger))
    sleep(0.1)

    return new_trigger
