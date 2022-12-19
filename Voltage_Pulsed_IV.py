import pyvisa
from time import sleep, strftime
import numpy as np
from numpy import size
import os
import shutil
import matplotlib.pyplot as plt
import tkFileDialog as FileDialog
from Tkinter import Label, Entry, Button, LabelFrame, OptionMenu, StringVar, IntVar, END

rm = pyvisa.ResourceManager()

class VPulse_IV():

    def start_iv_pulse(self):
        # Range of values for vertical scale on oscilloscope
        scales = [0.001, 0.002, 0.005, 0.01, 0.02,
                  0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]

        # Connect to oscilloscope
        self.scope = rm.open_resource(self.scope_address.get())

        # Initialize oscilloscope
        self.scope.write("*RST")
        self.scope.write("*CLS")
        self.scope.write(":CHANnel%d:IMPedance FIFTy" %self.current_channel.get())
        self.scope.write(":CHANnel%d:IMPedance FIFTy" %self.voltage_channel.get())

        pulseWidth = float(self.pulse_width_entry.get())

        # Mulitplication by 10 is due to a peculiarty of this oscilloscope
        self.scope.write(":TIMebase:RANGe %.6fus" %(0.5*pulseWidth*10))

        self.scope.write(":TRIGger:MODE GLITch")
        self.scope.write(":TRIGger:GLITch:SOURce CHANnel%d" %self.current_channel.get())
        self.scope.write(":TRIGger:GLITch:QUALifier RANGe")

        # Define glitch trigger range as: [50% of PW, 150% of PW]
        glitchTriggerLower = pulseWidth*0.5
        glitchTriggerUpper = pulseWidth*1.5

        self.scope.write(":TRIGger:GLITch:RANGe %.6fus,%.6fus" %(glitchTriggerLower,glitchTriggerUpper))

        # Set initial trigger point to 1 mV
        self.scope.write("TRIGger:GLITch:LEVel 1E-3")

        # Channel scales - set each channel to 1mV/div to start
        vertScaleCurrent = 0.001
        vertScaleVoltage = 0.001

        # Initial scale for current channel
        self.scope.write(":CHANNEL%d:SCALe %.3f" %(self.current_channel.get(), vertScaleCurrent))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.current_channel.get())
        # Initial scale for voltage channel
        self.scope.write(":CHANNEL%d:SCALe %.3f" %(self.voltage_channel.get(), vertScaleVoltage))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.voltage_channel.get())

        # Move each signal down two divisions for a better view on the screen
        self.scope.write(":CHANnel%d:OFFset %.3fV" %(self.current_channel.get(), 2*vertScaleCurrent))
        self.scope.write(":CHANnel%d:OFFset %.3fV" %(self.voltage_channel.get(), 2*vertScaleVoltage))

        # Total mV based on 6 divisions to top of display
        totalDisplayCurrent = 6*vertScaleCurrent
        totalDisplayVoltage = 6*vertScaleVoltage

        # Connect to AVTECH Voltage Pulser
        self.pulser = rm.open_resource(self.pulse_address.get())

        # Initialize pulser
        self.pulser.write("*RST")
        self.pulser.write("*CLS")
        self.pulser.write("OUTPut:IMPedance 50")
        self.pulser.write("SOURce INTernal")
        self.pulser.write("PULSe:WIDTh "+ self.pulse_width_entry.get() + "us")
        self.pulser.write("FREQuency " + self.frequency_entry.get() + "kHz")
        self.pulser.write("OUTPut ON")

        # Calculate number of points based on step size
        voltageRangeStart = float(self.start_voltage_entry.get())
        voltageRangeStop = float(self.stop_voltage_entry.get()) + float(self.step_size_entry.get())/1000
        voltageRangeStep = float(self.step_size_entry.get())/1000

        voltageSourceValues = np.arange(voltageRangeStart, voltageRangeStop, voltageRangeStep)

        # Lists for data values
        currentData = list()  # To be plotted on y-axis
        voltageData = list()  # To be plotted on x-axis

        i = 1

        voltageData.append(0)
        currentData.append(0)

        # Handling glitch points
        prevPulserVoltage = 0
        V_glitch_1 = 7.13

        for V_s in voltageSourceValues:

            # Handle glitch issues
            #if (V_s > 7 and V_s < 7.5) or (V_s > 21.3 and V_s < 21.9) or (V_s > 68 and V_s < 68.5):
            #    self.pulser.write("OUTPut OFF")
            #    self.pulser.write("VOLT %.3f" % V_s)
            #    sleep(1)
            if (prevPulserVoltage < V_glitch_1 <= V_s):
                self.pulser.write("output off")
                self.pulser.write("volt %.3f" %V_s)
                sleep(3)
            else:
                self.pulser.write("VOLT %.3f" % (V_s))
                self.pulser.write("OUTPut ON")
                sleep(0.1)
                # Read current amplitude from oscilloscope; multiply by 2 to use 50-ohms channel
                current_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]

                # Read photodetector output
                voltage_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]

                # Update trigger cursor to three quarters of the measured current amplitude
                totalDisplayCurrent = 6*vertScaleCurrent
                old_trigger = 1e-3
                old_trigger = self.updateTriggerCursor(
                    current_ampl_osc, self.scope, vertScaleCurrent, old_trigger, totalDisplayCurrent)
                
                # Adjust vertical scales if measured amplitude reaches top of screen (99% of display)
                while (current_ampl_osc > 0.99*totalDisplayCurrent):
                    vertScaleCurrent = self.incrOscVertScale(vertScaleCurrent)
                    totalDisplayCurrent = 6*vertScaleCurrent
                    self.scope.write(":CHANNEL%d:SCALe %.3f" % (self.current_channel.get(), float(vertScaleCurrent)))
                    current_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                    voltage_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
                    old_trigger = self.updateTriggerCursor(current_ampl_osc, self.scope, totalDisplayCurrent)
                    sleep(0.75)
                while (voltage_ampl_osc > 0.99*totalDisplayVoltage):
                    vertScaleVoltage = self.incrOscVertScale(vertScaleVoltage)
                    totalDisplayVoltage = 6*vertScaleVoltage
                    self.scope.write(":CHANNEL%d:SCALe %.3f" % (self.voltage_channel.get(), float(vertScaleVoltage)))
                    current_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                    voltage_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
                    old_trigger = self.updateTriggerCursor(current_ampl_osc, self.scope, totalDisplayCurrent)
                    sleep(0.75)

                R_S = 50.0  # AVTECH pulser source resistance
                current_ampl_device = 2*current_ampl_osc
                voltage_ampl_device = voltage_ampl_osc

                voltageData.append(voltage_ampl_device)
                currentData.append(current_ampl_device)

                # Handling glitch points
                prevPulserVoltage = V_s

                i = i + 1
        # Convert current and voltage readings to mA and mV values
        currentData[:] = [x*1000 for x in currentData]
        voltageData[:] = [x*1000 for x in voltageData]

        # Turn off the pulser, and clear event registers
        self.pulser.write("OUTPut OFF")
        self.pulser.write("*CLS")
        # Stop acquisition on oscilloscope
        self.scope.write(":STOP")

        try:
            if not os.path.exists(self.txt_dir_entry.get()):
                os.makedirs(self.txt_dir_entry.get())
        except:
            print('Error: Creating directory: '+self.txt_dir_entry.get())

        filename = strftime("%Y%m%d_%HH%MM") + '.txt'
        filesave1 = os.path.join(self.txt_dir_entry.get(), filename)
        filesave2 = os.path.join(self.txt_dir_entry.get(
        ), 'no' + self.file_name_entry.get()+'.txt')
        i = 1

        while(os.path.exists(filesave2)):
            filesave2 = os.path.join(self.txt_dir_entry.get(
            ), 'no' + self.file_name_entry.get()+str(i)+'.txt')
            i = i+1

        f = open(filesave2, 'w+')
        f.writelines('\n')
        f.writelines('Current (mA), Voltage (mV)\n')
        for i in range(0, len(currentData)):
            f.writelines(str(currentData[i]))
            f.writelines(' ')
            f.writelines(str(voltageData[i]))
            f.writelines('\r\n')
        f.close()
        print(filesave2)
        print(filesave1)
        shutil.copy(filesave2, filesave1)

        # ------------------ Plot measured characteristic ----------------------------------

        fig, ax1 = plt.subplots()
        ax1.set_xlabel('Measured device current (mA)')
        ax1.set_ylabel('Measured device voltage (mV)')
        ax1.plot(currentData, voltageData, color='blue',
                 label='I-V Characteristic')
        ax1.legend(loc='upper left')

        plt.show()

        try:
            if not os.path.exists(self.plot_dir_entry.get()):
                os.makedirs(self.plot_dir_entry.get())
        except:
            print('Error: Creating directory: ' + self.plot_dir_entry.get())

    """
    Function referenced when: 
    Description: 
    """

    def updateTriggerCursor(self, pulseAmplitude, scope, totalDisplay):
        new_trigger = 3*pulseAmplitude/4.0
        if (new_trigger < 0.25*totalDisplay):
            new_trigger = 0.25*totalDisplay
        elif (new_trigger > 0.9*totalDisplay):
            new_trigger = 0.5*totalDisplay
        scope.write(":TRIGger:GLITch:LEVel %.6f" % (new_trigger))
        return new_trigger

    """
    Function referenced when: 
    Description: 
    """

    def incrOscVertScale(self, currentScale):
        # Range of values for vertical scale on oscilloscope
        scaleValues = [0.001, 0.002, 0.005, 0.01,
                       0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]
        scaleIndex = scaleValues.index(currentScale)
        scaleIndex = scaleIndex + 1
        newScale = scaleValues[scaleIndex]
        return newScale

    """
    Function referenced when: Creating "Browse" button in the init function for the plot file entry
    Description: Configure the button as a File Dialog asking for a directory,
    store that directory string in the entry box
    """

    def browse_txt_file(self):
        # Retrieve directory for text file
        self.txt_dir = FileDialog.askdirectory()
        # Update entry box to display the directory
        self.txt_dir_entry.delete(0, END)
        self.txt_dir_entry.insert(0, self.txt_dir)

    """
    Function referenced when: Creating "Browse" button in the init function for the plot file entry
    Description: Configure the button as a File Dialog asking for a directory,
    store that directory string in the entry box
    """

    def browse_plot_file(self):
        # Retrieve directory for plot file
        self.plot_dir = FileDialog.askdirectory()
        # Update entry box to display the directory
        self.plot_dir_entry.delete(0, END)
        self.plot_dir_entry.insert(0, self.plot_dir)

    """
    Function referenced when: Initializing the application window
    Description: Creates the base geometry and all top-level widgets of the application window.
    """

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('Voltage Pulse Measurement: I-V')

        # Pulse settings frame
        self.pulseFrame = LabelFrame(self.master, text='Pulse Settings')
        # Display pulse settings frame
        self.pulseFrame.grid(column=0, row=0, rowspan=2, sticky='N', padx=(10, 5), pady=(0,10))

        # Create plot directory label, button, and entry box
        # Plot File Label
        self.plot_dir_label = Label(
            self.pulseFrame, text='Plot file directory:')
        self.plot_dir_label.grid(column=1, row=0, sticky='W', columnspan=2)
        # Plot directory Entry Box
        self.plot_dir_entry = Entry(self.pulseFrame, width=30)
        self.plot_dir_entry.grid(column=1, row=1, padx=(3, 0), columnspan=2)
        # Browse button
        self.plot_dir_file = Button(
            self.pulseFrame, text='Browse', command=self.browse_plot_file)
        self.plot_dir_file.grid(column=3, row=1, ipadx=5)

        # Create text directory label, button, and entry box
        # Text file label
        self.txt_dir_label = Label(
            self.pulseFrame, text='Text file directory:')
        self.txt_dir_label.grid(column=1, row=2, sticky='W', columnspan=2)
        # Text directory entry box
        self.txt_dir_entry = Entry(self.pulseFrame, width=30)
        self.txt_dir_entry.grid(column=1, row=3, padx=(3, 0), columnspan=2)
        # Browse button
        self.txt_dir_file = Button(
            self.pulseFrame, text='Browse', command=self.browse_txt_file)
        self.txt_dir_file.grid(column=3, row=3, ipadx=5)

        # Create label for file name entry box
        self.file_name_label = Label(self.pulseFrame, text='File name:')
        self.file_name_label.grid(column=1, row=4, sticky='W', columnspan=2)
        # File name entry box
        self.file_name_entry = Entry(self.pulseFrame, width=30)
        self.file_name_entry.grid(
            column=1, row=5, sticky='W', padx=(3, 0), columnspan=3)

        # Step size label
        self.step_size_label = Label(self.pulseFrame, text='Step size (mV)')
        self.step_size_label.grid(column=1, row=6)
        # Step size entry box
        self.step_size_entry = Entry(self.pulseFrame, width=5)
        self.step_size_entry.grid(column=1, row=7)

        # Delay label
        self.delay_label = Label(self.pulseFrame, text='Delay (ms)')
        self.delay_label.grid(column=2, row=6)
        # Delay entry box
        self.delay_entry = Entry(self.pulseFrame, width=5)
        self.delay_entry.grid(column=2, row=7)

        # Pulse width label
        self.pulse_width_label = Label(self.pulseFrame, text='Pulse Width (' + u'\u03BC' + 's)')
        self.pulse_width_label.grid(column=3, row=6)
        # Pulse width entry box
        self.pulse_width_entry = Entry(self.pulseFrame, width=5)
        self.pulse_width_entry.grid(column=3, row=7)

        # Start voltage label
        self.start_voltage_label = Label(self.pulseFrame, text='Start (V)')
        self.start_voltage_label.grid(column=1, row=8)
        # Start voltage entry box
        self.start_voltage_entry = Entry(self.pulseFrame, width=5)
        self.start_voltage_entry.grid(column=1, row=9, pady=(0,10))

        # Stop voltage label
        self.stop_voltage_label = Label(self.pulseFrame, text='Stop (V)')
        self.stop_voltage_label.grid(column=2, row=8)
        # Stop voltage entry box
        self.stop_voltage_entry = Entry(self.pulseFrame, width=5)
        self.stop_voltage_entry.grid(column=2, row=9, pady=(0,10))

        # Frequency label
        self.frequency_label = Label(self.pulseFrame, text='Frequency (kHz)')
        self.frequency_label.grid(column=3, row=8)
        # Frequency entry box
        self.frequency_entry = Entry(self.pulseFrame, width=5)
        self.frequency_entry.grid(column=3, row=9, pady=(0,10))

        # Start Button
        self.start_button = Button(
            self.master, text='Start', command=self.start_iv_pulse)
        self.start_button.grid(column=1, row=1, ipadx=10, pady=5)
        # # Stop Button
        # self.stop_button = Button(
        #     self.setFrame, text='Stop', state=DISABLED, command=self.stop_pressed)
        # self.stop_button.grid(column=3, row=11, ipadx=10, pady=5)

        # Device settings frame
        self.devFrame = LabelFrame(self.master, text='Device Settings')
        # Display device settings frame
        self.devFrame.grid(column=1, row=0, sticky='N', padx=(10, 5))

        # Device addresses
        connected_addresses = list(rm.list_resources())
        # Pulser and scope variables
        self.pulse_address = StringVar()
        self.scope_address = StringVar()

        # If no devices detected
        if size(connected_addresses) is 0:
            connected_addresses = ['No devices detected.']

        # Set the pulser and scope variables to default values
        self.pulse_address.set('Choose pulser address.')
        self.scope_address.set('Choose oscilloscope address.')

        # Pulser address label
        self.pulse_label = Label(self.devFrame, text='Pulser Address')
        self.pulse_label.grid(column=0, row=0, sticky='W')
        # Pulser address dropdown
        self.pulse_addr = OptionMenu(
            self.devFrame, self.pulse_address, *connected_addresses)
        self.pulse_addr.grid(column=0, columnspan=2, row=1,
                             padx=5, pady=5, sticky='W')

        # Oscilloscope address label
        self.scope_label = Label(self.devFrame, text='Oscilloscope Address')
        self.scope_label.grid(column=0, row=2, sticky='W')
        # Oscilloscope address dropdown
        self.scope_addr = OptionMenu(
            self.devFrame, self.scope_address, *connected_addresses)
        self.scope_addr.grid(column=0, columnspan=2, row=3,
                             padx=5, pady=5, sticky='W')

        # Oscilloscope channel options
        channels = [1, 2, 3, 4]
        self.current_channel = IntVar()
        self.voltage_channel = IntVar()

        # Set current channel to 1
        self.current_channel.set(1)
        # Set voltage channel to 2
        self.voltage_channel.set(2)

        # Current measurement channel label
        self.curr_channel_label = Label(self.devFrame, text='Current Channel')
        self.curr_channel_label.grid(column=0, row=4)
        # Current measurement channel dropdown
        self.curr_channel_dropdown = OptionMenu(
            self.devFrame, self.current_channel, *channels)
        self.curr_channel_dropdown.grid(column=0, row=5)

        # Voltage measurement channel label
        self.voltage_channel_label = Label(self.devFrame, text='Voltage Channel')
        self.voltage_channel_label.grid(column=1, row=4)
        # Voltage measurement channel dropdown
        self.voltage_channel_dropdown = OptionMenu(
            self.devFrame, self.voltage_channel, *channels)
        self.voltage_channel_dropdown.grid(column=1, row=5)