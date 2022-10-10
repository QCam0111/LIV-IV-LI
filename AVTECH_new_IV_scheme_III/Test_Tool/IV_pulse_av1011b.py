from core import *
from numpy import *
from core import *
from numpy import *
import sys
import LDP3840B 
import InfiniiumScope
import base
import matplotlib.pyplot as plt
import time
from time import strftime
import ipywidgets
import os
import pyvisa
import pylab
import shutil

# This is a program to measure a device's pulsed L-I-V characteristic
# The program drives the AVTECH 1011B voltage pulser and an oscilloscope.

#------------------ 1 Set up and initialize boxes for input parameters --------------

AV1011B_dd = ipywidgets.Dropdown(description='AV1011B :', options=res_list, value=res_list[0])
InfiniiumScope_dd = ipywidgets.Dropdown(description='Infiniium_scope:', options=res_list, value=res_list[0])

channel_current = ipywidgets.Dropdown(description='Current measurement channel', options=[1,2,3,4], value=1)
channel_voltage = ipywidgets.Dropdown(description='Voltage measurement channel', options=[1,2,3,4], value=3)

# Initial parameter values
ini_poi_del = 10
ch_scale_init = 0.005
V_i = 0
V_f = 10
voltageStep = 100
fn = 'outputFolder'
PW = 0.5
freq = 10 # kHz
Inc_t = 1
R_ser = 0

# Set up boxes for inputting parameter values
fn_t = ipywidgets.Text(description='Filename:',value = fn)
ttl_trash_sample = ipywidgets.IntText(description='ini_point_del (ini):', value = ini_poi_del)
current_ch_scale_t = ipywidgets.FloatText(description='Current channel vertical scale (initial):', value = ch_scale_init)
voltage_ch_scale_t = ipywidgets.FloatText(description='Voltage channel vertical scale (initial):', value = ch_scale_init)
V_start_t = ipywidgets.FloatText(description='Start voltage (V):',value = V_i)
V_stop_t = ipywidgets.FloatText(description='End voltage (V):',value = V_f)
voltageStep_t = ipywidgets.FloatText(description = 'Voltage step (mV)', value = voltageStep)
delay_t = ipywidgets.FloatText(description='Delay (ms):', value = 0)
PW_t = ipywidgets.FloatText(description='Pulse width (us):', value = PW)
freq_kHz_t = ipywidgets.FloatText(description='Frequency (kHz):', value = freq)
R_ser_t = ipywidgets.FloatText(description='Series resistance (ohms):', value = R_ser)

# Sample number
device_no = 10
trial = 1
device_no_t = ipywidgets.IntText(description='device_no:',value=device_no)
trial_t = ipywidgets.IntText(description='trial:',value=trial)

# A function to adjust an oscilloscope's waveform's vertical scale
def incrOscVertScale(currentScale):
    scaleValues = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10] # Range of values for vertical scale on oscilloscope
    scaleIndex = scaleValues.index(currentScale)
    scaleIndex = scaleIndex + 1
    newScale = scaleValues[scaleIndex]
    return newScale

# A function to read pulse amplitude measured on oscilloscope
# def readPulseAmplitude(oscChannel, maxValue):
#     amplitudeReading = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d;'%oscChannel.value)[0]
#     if amplitudeReading > maxValue:
#         vertScale = scope.query_ascii_values(r'SINGLE;*OPC;:CHANNEL%d:SCALe ' %(oscChannel))
#         vertScale = incrOscVertScale(vertScale)
#     return amplitudeReading

def makeArray(interval, start, stop):
    interval = round(interval, 3)
    start = interval*round(start/interval)
    stop = interval*round(stop/interval)
    nrPts = int((stop - start)/interval + 1)
    values = [round(start + i*interval,3) for i in range(nrPts)]
    return values

def updateTriggerCursor(pulseAmplitude, scope):
    new_trigger = pulseAmplitude/2.0
    scope.write(":TRIGger:LEVel %.6f"%(new_trigger))

#------------------ 2 Set oscilloscope and turn on pulser output --------------------

# This is the main function, which is executed when the start button is clicked
@btn_dec
def Start(btn):
    
    # Obtain inputted parameter values
    fn = fn_t.value
    voltageStep = voltageStep_t.value/1000    # Divide by 1000 to convert from mV to V
    V_i = V_start_t.value
    V_f = V_stop_t.value
    current_ch_scale = current_ch_scale_t.value
    voltage_ch_scale = voltage_ch_scale_t.value
    pw = PW_t.value
    freq = 1000*freq_kHz_t.value
    R_ser = R_ser_t.value

    scale = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10] # Range of values for vertical scale on oscilloscope
    rm = visa.ResourceManager() # PyVisa

    # Oscilloscope settings
    scope = rm.open_resource(host+InfiniiumScope_dd.value)
    scope.write("*RST")
    scope.write("*CLS")
    scope.write(":AUToscale")
    # scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.3f' %(channel_current.value, float(current_ch_scale)))
    scope.write(":CHANnel%d:DISPlay ON" %channel_current.value)
    # scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.3f' %(channel_voltage.value, float(voltage_ch_scale)))
    scope.write(":CHANnel%d:DISPlay ON" %channel_voltage.value)
    
    # Scale indices
    vertScaleCurrent = 0.001
    print("Vertical scale for current channel:"+ ''+ str(current_ch_scale))
    vertScaleVoltage = 0.001

    # Pulser voltage
    V_s = 0.5
    # Pulser settings
    AVTECH = rm.open_resource(host+AV1011B_dd.value)
    AVTECH.write("*rst")
    AVTECH.write("output:impedance 50")
    AVTECH.write("source internal")
    AVTECH.write("pulse:width %.2f us" %pw)
    AVTECH.write("frequency %d" %freq)
    AVTECH.write("output on ")

    #------------------ 3 Set up sweep variables ----------------------------------------

    maxValue = 100; # For adjusting vertical scale
    
    # Construct list of voltage values to be inputted to pulser
    #voltageSourceValues = [V_i + (0 if not i else ((V_f-V_i) / (points - 1) * i)) for i in range(int(points))]
    # Calculate number of points based on step size
    voltageSourceValues = makeArray(voltageStep, V_i, V_f)
    
    # Lists for data values
    currentData = list() # To be plotted on y-axis
    voltageData = list() # To be plotted on x-axis
    
    i = 1

    #------------------ 4 Specify directories for output files --------------------------

    datafolder = 'data_text'+'/'+fn_t.value+'/'+'no'+str(device_no_t.value) # Folder that stores data in text file
    pltfolder = 'plots'+'/'+ fn_t.value +'/'+'no'+str(device_no_t.value)

    #------------------ 5 Measure desired device characteristic -------------------------

    voltageData.append(0)
    currentData.append(0)

    for V_s in voltageSourceValues: # This Python line specifies for V_s to be iterated over the range of values in voltageSourceValues
        #AVTECH.write(r'volt %.3f'%(V_s))
       
       # Handle glitch issue
        if (V_s> 21.3 and V_s<21.9) or (V_s>7 and V_s < 7.5):
            AVTECH.write("output off ")
            AVTECH.write(r'volt %.3f'%(V_s))
            time.sleep(1)
        else:
#             if (AVTECH.query_ascii_values(r'output?') == '0'):
#                 AVTECH.write("output on ")
#                 AVTECH.write(r'volt %.3f'%(V_s))
#                 time.sleep(2)
#                 print('output switched on\n')
#             else:
#                 AVTECH.write("output on ")
#                 time.sleep(0.1)
#                 AVTECH.write(r'volt %.3f'%(V_s))
            AVTECH.write(r'volt %.3f'%(V_s))
            AVTECH.write("output on ")
            time.sleep(0.1)

            # Read current amplitude from oscilloscope; multiply by 2 to use 50-ohms channel
            current_ampl_osc = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d;'%channel_current.value)[0]
            # Read photodetector output
            voltage_ampl_osc = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d;'%channel_voltage.value)[0]
            
            # Adjust vertical scales if necessary
            # while (current_ampl_osc > maxValue):
            #     vertScaleCurrent = incrOscVertScale(vertScaleCurrent)
            #     scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.3f'%(channel_current.value,float(vertScaleCurrent)))
            #     current_ampl_osc = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d;'%channel_current.value)[0]
            #     voltage_ampl_osc = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d;'%channel_voltage.value)[0]
            #     time.sleep(0.75)
            # while (voltage_ampl_osc > maxValue):
            #     vertScaleVoltage = incrOscVertScale(vertScaleVoltage)
            #     scope.write(r'SINGLE;*OPC;:CHANNEL%d:SCALe %.3f'%(channel_voltage.value,float(vertScaleVoltage)))
            #     current_ampl_osc = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d;'%channel_current.value)[0]
            #     voltage_ampl_osc = scope.query_ascii_values(r'SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d;'%channel_voltage.value)[0]
            #     time.sleep(0.75)
                
            # Update trigger cursor to half of measured current amplitude
            updateTriggerCursor(current_ampl_osc, scope)
            
            R_S = 50.0; # AVTECH pulser source resistance
            current_ampl_device = 2*current_ampl_osc
            voltage_ampl_device = voltage_ampl_osc - R_ser*current_ampl_device

            voltageData.append(voltage_ampl_device)
            currentData.append(current_ampl_device)
            
            i = i + 1
        
    # Convert current and voltage readings to mA and mV values
    currentData[:] = [x*1000 for x in currentData]
    voltageData[:] = [x*1000 for x in voltageData]
                
    #------------------ 6 Terminate pulser operation ------------------------------------
    AVTECH.write("output off")
    AVTECH.write('*CLS;:STOP')
    scope.write(':STOP;*OPC?')
    
    #------------------ 7 Save output files ---------------------------------------------
    try:
        if not os.path.exists('./'+datafolder):
            os.makedirs('./'+datafolder)
    except:
        print('Error: Creating directory.'+datafolder)
        
    filename = strftime("%Y%m%d_%HH%MM") + '.txt'
    filesave1 = os.path.join(datafolder,filename)
    filesave2 = os.path.join(datafolder,'no'+ str(trial_t.value)+'.txt')
    i = 1

    while(os.path.exists(filesave2)):
        filesave2 = os.path.join(datafolder,'no'+ str(trial_t.value+i)+'.txt')
        i = i+1
     
    f = open(filesave2,'w+')
    f.writelines('\n')
    f.writelines('Current (mA), Voltage (mV)\n')
    for i in range(0,len(currentData)):
        f.writelines(str(currentData[i]))
        f.writelines(' ')
        f.writelines(str(voltageData[i]))
        f.writelines('\r\n')
    f.close()
    print(filesave2)
    print(filesave1)
    shutil.copy(filesave2,filesave1)

    #------------------ 8 Plot measured characteristic ----------------------------------
    #fig = plt.figure()
    #ax1 = plt.axes()
    #ax1.plot(currentData, voltageData, 'b-') # Plot data
    #ax1.set_xlabel('Device current (mA)')
    #ax1.set_ylabel('Device voltage (V)')
    #plt.show(block=False)
    
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Measured device voltage (mV)')
    ax1.set_ylabel('Measured device current (mA)')
    ax1.plot(voltageData, currentData, color='blue', label='I-V characteristic')
    ax1.legend(loc='upper left')
    
    plt.show()
    
    try: 
        if not os.path.exists('./'+pltfolder):
            os.makedirs('./'+pltfolder)
    except:
        print('Error: Creating directory./'+pltfolder)
        
    #fig.savefig(os.path.join(pltfolder,strftime('no'+ str(trial_t.value)+'-'+ "%Y%m%d_%HH%MM") + '.png'))

start_btn = ipywidgets.Button(description='Start')
start_btn.on_click(Start)

Pages.append(ipywidgets.Box(children=[AV1011B_dd, InfiniiumScope_dd, channel_current, channel_voltage, ttl_trash_sample, \
    current_ch_scale_t, voltage_ch_scale_t, V_start_t, V_stop_t, voltageStep_t, delay_t, fn_t, PW_t, freq_kHz_t, R_ser_t, \
    device_no_t, trial_t, start_btn],layout=ipywidgets.Layout(
    #display='flex',
    flex_flow='column',
    align_items='stretch',
    width='50%'
)))
Names.append("Pulsed I-V measurement")
