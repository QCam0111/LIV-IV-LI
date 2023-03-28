"""
Function referenced when: The measured oscilloscope signal exceeds 99% of total oscilloscope display.
Description: Increases the vertical range of the oscilloscope display, measured in mV/division.
"""

def incrOscVertScale(currentScale):
    # Range of values for vertical scale on oscilloscope
    scaleValues = [0.001, 0.002, 0.005, 0.01,
                    0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]
    scaleIndex = scaleValues.index(currentScale)
    scaleIndex = scaleIndex + 1
    newScale = scaleValues[scaleIndex]
    return newScale