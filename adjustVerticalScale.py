"""
Function referenced when:
Description:
"""

from Oscilloscope_Scaling import incrOscVertScale
from Update_Trigger import updateTriggerCursor

def adjustVerticalScale(self, measChannel, triggerChannel, pulseAmplitude, availableDisplay, verticalScale):
    while (pulseAmplitude > 0.9*availableDisplay):
        verticalScale = self.incrOscVertScale(verticalScale)
        availableDisplay = 6*verticalScale
        self.scope.write(":CHANNEL%d:SCALe %.3f" % (self.channel, float(verticalScale)))
        pulseAmplitude = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.channel.get())[0]
        if (measChannel == triggerChannel):
            self.updateTriggerCursor(pulseAmplitude, self.scope, availableDisplay)