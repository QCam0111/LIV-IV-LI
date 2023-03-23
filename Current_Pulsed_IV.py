import pyvisa
from time import sleep, strftime
import numpy as np
from numpy import size
import os
import shutil
import matplotlib.pyplot as plt
from Tkinter import Label, Entry, Button, LabelFrame, OptionMenu, StringVar, IntVar

# Import Browse button functions
from Browse_buttons import browse_plot_file, browse_txt_file


rm = pyvisa.ResourceManager()

class IPulse_IV():

    # Import Oscilloscope scaling
    from Oscilloscope_Scaling import incrOscVertScale
    # Import trigger updating
    from Update_Trigger import updateTriggerCursor

    def start_iv_pulse(self):
        # Range of values for vertical scale on oscilloscope
        scales = [0.001, 0.002, 0.005, 0.01, 0.02,
                  0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]

        # Connect to oscilloscope
        self.scope = rm.open_resource(self.scope_address.get())

        # Initialize oscilloscope
        self.scope.write("*RST")
        self.scope.write("*CLS")
        self.scope.write(":CHANnel%d:IMPedance FIFTy" %
                         self.current_channel.get())
        self.scope.write(":CHANnel%d:IMPedance FIFTy" %
                         self.voltage_channel.get())

         pulseWidth = float(self.pulse_width_entry.get())

        # Mulitplication by 10 is due to a peculiarty of this oscilloscope
        self.scope.write(":TIMebase:RANGe %.6fus" %(0.5*pulseWidth*10))

        self.scope.write(":TRIGger:MODE GLITch")
        self.scope.write(":TRIGger:GLITch:SOURce CHANnel%d" %
                         self.trigger_channel.get())
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

        self.scope.write(":CHANNEL%d:SCALe %.3f" %(self.current_channel.get(), vertScaleCurrent))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.current_channel.get())
        self.scope.write(":CHANNEL%d:SCALe %.3f" %(self.voltage_channel.get(), vertScaleVoltage))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.voltage_channel.get())

        # Move each signal down two divisions for a better view on the screen
        self.scope.write(":CHANnel%d:OFFset %.3fV" %(self.current_channel.get(), 2*vertScaleCurrent))
        self.scope.write(":CHANnel%d:OFFset %.3fV" %(self.voltage_channel.get(), 2*vertScaleVoltage))

        # Total mV based on 6 divisions to top of display
        totalDisplayCurrent = 6*vertScaleCurrent
        totalDisplayVoltage = 6*vertScaleVoltage

        # Connect to Current Pulser
        self.pulser = rm.open_resource(self.pulse_address.get())

        # Initialize pulser
        self.pulser.write("*RST")
        self.pulser.write("*CLS")
        self.pulser.write(":PW " + self.pulse_width_entry.get())
        self.pulser.write(":DIS:LDI")
        self.pulser.write("LIMit:I " + self.current_limit_entry.get())
        self.pulser.write("OUTPut OFF")

        # Calculate number of points based on step size
        currentRangeStart = float(self.start_current_entry.get())
        currentRangeStop = float(
            self.stop_current_entry.get()) + float(self.step_size_entry.get())/1000
        currentRangeStep = float(self.step_size_entry.get())/1000

        currentSourceValues = np.arange(
            currentRangeStart, currentRangeStop, currentRangeStep)

        # Lists for data values
        currentData = list()  # To be plotted on y-axis
        voltageData = list()  # To be plotted on x-axis

        voltageData.append(0)
        currentData.append(0)

        for I_s in currentSourceValues:

            self.pulser.write(":LDI %.3f" % (I_s))
            self.pulser.write("OUTPut ON")
            sleep(0.1)
            # Read current amplitude from oscilloscope; multiply by 2 to use 50-ohms channel
            current_ampl_osc = self.scope.query_ascii_values(
                "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                            # Update trigger cursor if it being applied to the current waveform
            if (self.trigger_channel.get() == self.current_channel.get()):
                    self.updateTriggerCursor(current_ampl_osc, self.scope, totalDisplayCurrent)

            # Read photodetector output
            voltage_ampl_osc = self.scope.query_ascii_values(
                "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
            # Update trigger cursor if it being applied to the current waveform
                if (self.trigger_channel.get() == self.voltage_channel.get()):
                    self.updateTriggerCursor(voltage_ampl_osc, self.scope, totalDisplayVoltage)

            # Adjust vertical scales if measured amplitude reaches top of screen (90% of display)
            vertScaleCurrent = self.adjustVerticalScale(self.current_channel.get(), self.trigger_channel.get(),\
                current_ampl_osc, totalDisplayCurrent, vertScaleCurrent)                
            vertScaleVoltage = self.adjustVerticalScale(self.voltage_channel.get(), self.trigger_channel.get(),\
                voltage_ampl_osc, totalDisplayVoltage, vertScaleVoltage)

            # Get updated readings
            current_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
            voltage_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
                
            # Update available display
            totalDisplayCurrent = 6*vertScaleCurrent
            totalDisplayVoltage = 6*vertScaleVoltage

            R_S = 50.0  # AVTECH pulser source resistance

            current_ampl_device = 2*current_ampl_osc
            voltage_ampl_device = voltage_ampl_osc - seriesResistance*current_ampl_device

            voltageData.append(voltage_ampl_device)
            currentData.append(current_ampl_device)
            
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
                 label='Current Pulsed V-I Characteristic')
        ax1.legend(loc='upper left')

        plt.show()

        try:
            if not os.path.exists(self.plot_dir_entry.get()):
                os.makedirs(self.plot_dir_entry.get())
        except:
            print('Error: Creating directory: ' + self.plot_dir_entry.get())

    """
    Function referenced when: Initializing the application window
    Description: Creates the base geometry and all top-level widgets of the application window.
    """

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('Current Pulsed Measurement: i-v')

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
            self.pulseFrame, text='Browse', command=lambda:browse_plot_file(self))
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
            self.pulseFrame, text='Browse', command=lambda:browse_txt_file(self))
        self.txt_dir_file.grid(column=3, row=3, ipadx=5)

        # Create label for file name entry box
        self.file_name_label = Label(self.pulseFrame, text='File name:')
        self.file_name_label.grid(column=1, row=4, sticky='W', columnspan=2)
        # File name entry box
        self.file_name_entry = Entry(self.pulseFrame, width=30)
        self.file_name_entry.grid(
            column=1, row=5, sticky='W', padx=(3, 0), columnspan=3)

        # Step size label
        self.step_size_label = Label(self.pulseFrame, text='Step size (mA)')
        self.step_size_label.grid(column=1, row=6)
        # Step size entry box
        self.step_size_entry = Entry(self.pulseFrame, width=5)
        self.step_size_entry.grid(column=1, row=7)

        # Current limit label
        self.current_limit_label = Label(self.pulseFrame, text='Current Limit (mA)')
        self.current_limit_label.grid(column=2, row=6)
        # Current limit entry box
        self.current_limit_entry = Entry(self.pulseFrame, width=5)
        self.current_limit_entry.grid(column=2, row=7)

        # Pulse width label
        self.pulse_width_label = Label(
            self.pulseFrame, text='Pulse Width (' + u'\u03BC' + 's)')
        self.pulse_width_label.grid(column=3, row=6)
        # Pulse width entry box
        self.pulse_width_entry = Entry(self.pulseFrame, width=5)
        self.pulse_width_entry.grid(column=3, row=7)

        # Start current label
        self.start_current_label = Label(self.pulseFrame, text='Start (mA)')
        self.start_current_label.grid(column=1, row=8)
        # Start current entry box
        self.start_current_entry = Entry(self.pulseFrame, width=5)
        self.start_current_entry.grid(column=1, row=9, pady=(0,10))

        # Stop current label
        self.stop_current_label = Label(self.pulseFrame, text='Stop (mA)')
        self.stop_current_label.grid(column=2, row=8)
        # Stop current entry box
        self.stop_current_entry = Entry(self.pulseFrame, width=5)
        self.stop_current_entry.grid(column=2, row=9, pady=(0,10))

        # Frequency label
        self.frequency_label = Label(self.pulseFrame, text='Frequency (kHz)')
        self.frequency_label.grid(column=3, row=8)
        # Frequency entry box
        self.frequency_entry = Entry(self.pulseFrame, width=5)
        self.frequency_entry.grid(column=3, row=9, pady=(0,10))

        # Series resistance label
        self.series_resistance_label = Label(self.pulseFrame, text='Series resistance (ohms)')
        self.series_resistance_label.grid(column=1, row=10)
        # Series resistance entry box
        self.series_resistance_entry = Entry(self.pulseFrame, width=5)
        self.series_resistance_entry.grid(column=1, row=11, pady=(0,10))

        # Start Button
        self.start_button = Button(
            self.master, text='Start', command=self.start_iv_pulse)
        self.start_button.grid(column=1, row=1, ipadx=10, pady=5)
        # # Stop Button
        # self.stop_button = Button(
        #     self.setFrame, text='Stop', state=DISABLED, command=self.stop_pressed)
        # self.stop_button.grid(column=3, row=11, ipadx=10, pady=5)

        # Device settings frame
        self.devFrame = LabelFrame(self.master, text='Equipment Settings')
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
        self.pulse_label = Label(self.devFrame, text='Current Pulser Address')
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
        self.trigger_channel = IntVar()

        # Set current channel to 1
        self.current_channel.set(1)
        # Set voltage channel to 2
        self.voltage_channel.set(2)
        # Set trigger channel to 2
        self.trigger_channel.set(2)

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

        # Trigger channel label
        self.trigger_channel_label = Label(self.devFrame, text='Trigger channel')
        self.trigger_channel_label.grid(column=2, row=4)
        # Trigger channel dropdown
        self.trigger_channel_dropdown = OptionMenu(
            self.devFrame, self.trigger_channel, *channels)
        self.trigger_channel_dropdown.grid(column=2, row=5)