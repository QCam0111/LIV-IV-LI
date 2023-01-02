"""
Function referenced when: A measurement is made using the oscilloscope and current/voltage pulser.
Description: Updates the oscilloscope trigger level to between 25% and 90% of the total oscilloscope display.
"""

def updateTriggerCursor(self, scope):
    if (trigger_channel == current_channel)
        trigger_prev = self.adjustTriggerCursor(current_ampl_osc, self.scope, totalDisplayCurrent)
    elif(trigger_channel == voltage_channel)
        trigger_prev = self.adjustTriggerCursor(voltage_ampl_osc, self.scope, totalDisplayVoltage)

def adjustTriggerCursor(self, pulseAmplitude, scope, totalDisplay):
    new_trigger = 3*pulseAmplitude/4.0
    if (new_trigger < 0.25*totalDisplay):
        new_trigger = 0.25*totalDisplay
    elif (new_trigger > 0.9*totalDisplay):
        new_trigger = 0.5*totalDisplay
    scope.write(":TRIGger:GLITch:LEVel %.6f" % (new_trigger))
    sleep(0.1)
    return new_trigger