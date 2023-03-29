"""
Function referenced when: Pulse waveform nears the top of the screen
Description: Continue to zoom out vertically until the pulse waveform fits comfortably in the screen.
"""

from Oscilloscope_Scaling import incrOscVertScale
from Update_Trigger import updateTriggerCursor
from time import sleep

def adjustVerticalScale(self, measChannel, triggerChannel, pulseAmplitude, availableDisplay, verticalScale):
    while (pulseAmplitude > 0.9*availableDisplay):
        # Increment scale
        verticalScale = incrOscVertScale(verticalScale)
        # Update available display space
        availableDisplay = 6*verticalScale
        # Apply new scale
        self.scope.write(":CHANNEL%d:SCALe %.3f" % (measChannel, float(verticalScale)))
        # Obtain new measurement for pulse amplitude
        pulseAmplitude = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % measChannel)[0]
        if (measChannel == triggerChannel):
            updateTriggerCursor(pulseAmplitude, self.scope, availableDisplay)
        else:
            sleep(0.1) # If triggering occurs, this sleep gets included when the function is called.
    return verticalScale
