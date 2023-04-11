import pyvisa
from time import sleep
import numpy as np
from numpy import append, zeros, arange, logspace, log10, size
import os
import shutil
from time import sleep, strftime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Tkinter import Label, Entry, Button, LabelFrame, OptionMenu, Radiobutton, StringVar, IntVar, DISABLED, NORMAL

# Import Browse button functions
from Browse_buttons import browse_plot_file, browse_txt_file
# Import Oscilloscope scaling
from Oscilloscope_Scaling import incrOscVertScale, channelImpedance
# Import trigger updating
from Update_Trigger import updateTriggerCursor

rm = pyvisa.ResourceManager()

class VPulse_LIV():

    # Import vertical scaling
    from adjustVerticalScale import adjustVerticalScale

    def start_liv_pulse(self):

        # Connect to oscilloscope
        self.scope = rm.open_resource(self.scope_address.get())

        # Initialize oscilloscope
        self.scope.write("*RST")
        self.scope.write("*CLS")

        # Set channel impedance to 50 ohms
        self.scope.write(":CHANnel%d:IMPedance %s" %(self.light_channel.get(), channelImpedance(self.light_channel_impedance.get())))
        self.scope.write(":CHANnel%d:IMPedance %s" %(self.current_channel.get(), channelImpedance(self.curr_channel_impedance.get())))
        self.scope.write(":CHANnel%d:IMPedance %s" %(self.voltage_channel.get(), channelImpedance(self.volt_channel_impedance.get())))

        pulseWidth = float(self.pulse_width_entry.get())

        # Mulitplication by 10 is due to a peculiarty of this oscilloscope
        self.scope.write(":TIMebase:RANGe %.6fus" %(0.5*pulseWidth*10))

        self.scope.write(":TRIGger:MODE GLITch")
        self.scope.write(":TRIGger:GLITch:SOURce CHANnel%d" %self.trigger_channel.get())
        self.scope.write(":TRIGger:GLITch:QUALifier RANGe")

        # Define glitch trigger range as: [50% of PW, 150% of PW]
        glitchTriggerLower = pulseWidth*0.5
        glitchTriggerUpper = pulseWidth*1.5
        self.scope.write(":TRIGger:GLITch:RANGe %.6fus,%.6fus" %(glitchTriggerLower,glitchTriggerUpper))

        # Set initial trigger point to 1 mV
        self.scope.write("TRIGger:GLITch:LEVel 1E-3")
        # Note previous trigger level before updating the trigger cursor
        trigger_prev = 1e-3

        # Channel scales - set each channel to 1mV/div to start
        vertScaleLight = 0.001
        vertScaleCurrent = 0.001
        vertScaleVoltage = 0.001

        # Initial scale for light channel
        self.scope.write(":CHANNEL%d:SCALe %.3f" %(self.light_channel.get(), vertScaleLight))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.light_channel.get())
        # Initial scale for current channel
        self.scope.write(":CHANNEL%d:SCALe %.3f" %(self.current_channel.get(), vertScaleCurrent))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.current_channel.get())
        # Initial scale for voltage channel
        self.scope.write(":CHANNEL%d:SCALe %.3f" %(self.voltage_channel.get(), vertScaleVoltage))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.voltage_channel.get())

        # Move each signal down two divisions for a better view on the screen
        self.scope.write(":CHANnel%d:OFFset %.3fV" %(self.light_channel.get(), 2*vertScaleLight))
        self.scope.write(":CHANnel%d:OFFset %.3fV" %(self.current_channel.get(), 2*vertScaleCurrent))
        self.scope.write(":CHANnel%d:OFFset %.3fV" %(self.voltage_channel.get(), 2*vertScaleVoltage))

        # Total mV based on 6 divisions to top of display
        totalDisplayLight = 6*vertScaleLight
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

        # Obtain series resistance value from entry box
        seriesResistance = float(self.series_resistance_entry.get())

        voltageSourceValues = np.arange(voltageRangeStart, voltageRangeStop, voltageRangeStep)

        # Lists for data values
        lightData = list() 
        currentData = list()  # To be plotted on y-axis
        voltageData = list()  # To be plotted on x-axis

        lightData.append(0)
        voltageData.append(0)
        currentData.append(0)

        # Handling glitch points
        prevPulserVoltage = 0
        V_glitch_1 = 7.12
        V_glitch_2 = 21.6
        V_glitch_3 = 68

        for V_s in voltageSourceValues:
            if ((prevPulserVoltage <= V_glitch_1 < V_s) or (prevPulserVoltage <= V_glitch_2 < V_s) or (prevPulserVoltage <= V_glitch_3 < V_s)):
                self.pulser.write("output off")
                self.pulser.write("volt %.3f" %V_s)
                prevPulserVoltage = V_s
                sleep(4)
            else:
                self.pulser.write("VOLT %.3f" % (V_s))
                self.pulser.write("OUTPut ON")

                # Read light amplitude from oscilloscope
                light_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.light_channel.get())[0]
                # Update trigger cursor if it being applied to the current waveform
                if (self.trigger_channel.get() == self.light_channel.get()):
                    updateTriggerCursor(light_ampl_osc, self.scope, totalDisplayLight)

                # Read current amplitude from oscilloscope; multiply by 2 to use 50-ohms channel
                current_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                # Update trigger cursor if it being applied to the current waveform
                if (self.trigger_channel.get() == self.current_channel.get()):
                    updateTriggerCursor(current_ampl_osc, self.scope, totalDisplayCurrent)

                # Read voltage amplitude
                voltage_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
                # Update trigger cursor if it being applied to the current waveform
                if (self.trigger_channel.get() == self.voltage_channel.get()):
                    updateTriggerCursor(voltage_ampl_osc, self.scope, totalDisplayVoltage)
                    
                # Adjust vertical scales if measured amplitude reaches top of screen (90% of display)
                vertScaleLight = self.adjustVerticalScale(self.light_channel.get(), self.trigger_channel.get(),\
                    light_ampl_osc, totalDisplayLight, vertScaleLight)      
                vertScaleCurrent = self.adjustVerticalScale(self.current_channel.get(), self.trigger_channel.get(),\
                    current_ampl_osc, totalDisplayCurrent, vertScaleCurrent)                
                vertScaleVoltage = self.adjustVerticalScale(self.voltage_channel.get(), self.trigger_channel.get(),\
                    voltage_ampl_osc, totalDisplayVoltage, vertScaleVoltage)

                # Get updated readings
                light_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.light_channel.get())[0]
                current_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                voltage_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
                
                # Update available display
                totalDisplayLight = 6*vertScaleLight
                totalDisplayCurrent = 6*vertScaleCurrent
                totalDisplayVoltage = 6*vertScaleVoltage

                current_ampl_device = 2*current_ampl_osc
                voltage_ampl_device = voltage_ampl_osc - seriesResistance*current_ampl_device

                lightData.append(light_ampl_osc)
                voltageData.append(voltage_ampl_device)
                currentData.append(current_ampl_device)

                # Handling glitch points
                prevPulserVoltage = V_s

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

        # open file and write in data
        txtDir = self.txt_dir_entry.get()
        filename = self.device_name_entry.get() + '_VP-LIV_' + self.device_temp_entry.get() + \
            'C_' + self.device_dim_entry.get() + '_' + self.test_laser_button_var.get()
        filepath = os.path.join(txtDir + '/' + filename + '.txt')
        fd = open(filepath, 'w+')
        i = 1

        fd.writelines('Device light output (W)\tCurrent (mA)\tVoltage (mV)\n')
        for i in range(0, len(currentData)):
            fd.writelines(str(lightData[i]))
            fd.writelines('\t')
            fd.writelines(str(currentData[i]))
            fd.writelines('\t')
            fd.writelines(str(voltageData[i]))
            fd.writelines('\n')
        fd.close()


        # ------------------ Plot measured characteristic ----------------------------------

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax2.set_ylabel('Measured device light output (W)', color='red')
        ax1.set_xlabel('Measured device current (mA)')
        ax1.set_ylabel('Measured device voltage (mV)', color='blue')
        ax1.plot(currentData, voltageData, color='blue', label='I-V Characteristic')
        ax2.plot(currentData, lightData, color='red', label='L-I Characteristic')
        ax1.legend(loc='upper left')

        plotString = 'Device Name: ' + self.device_name_entry.get() + '\n' 'Test Type: VP-LIV\n' + 'Temperature (' + u'\u00B0' + 'C): ' + self.device_temp_entry.get() + \
            '\n' + 'Device Dimensions: ' + self.device_dim_entry.get() + '\n' + \
            'Test Structure or Laser: ' + self.test_laser_button_var.get()

        plt.figtext(0.02, 0.02, plotString, fontsize=12)

        plt.subplots_adjust(bottom=0.3)

        plt.savefig(self.plot_dir_entry.get() + '/' + filename + ".png")
        plt.show()

        try:
            if not os.path.exists(self.plot_dir_entry.get()):
                os.makedirs(self.plot_dir_entry.get())
        except:
            print('Error: Creating directory: ' + self.plot_dir_entry.get())

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('Voltage Pulse Measurement: I-V')

        """ Pulse settings frame """
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

        # Step size label
        self.step_size_label = Label(self.pulseFrame, text='Step size (mV)')
        self.step_size_label.grid(column=1, row=4)
        # Step size entry box
        self.step_size_entry = Entry(self.pulseFrame, width=5)
        self.step_size_entry.grid(column=1, row=5)

        # Delay label
        self.delay_label = Label(self.pulseFrame, text='Delay (ms)')
        self.delay_label.grid(column=2, row=4)
        # Delay entry box
        self.delay_entry = Entry(self.pulseFrame, width=5)
        self.delay_entry.grid(column=2, row=5)

        # Pulse width label
        self.pulse_width_label = Label(self.pulseFrame, text='Pulse Width (' + u'\u03BC' + 's)')
        self.pulse_width_label.grid(column=3, row=4)
        # Pulse width entry box
        self.pulse_width_entry = Entry(self.pulseFrame, width=5)
        self.pulse_width_entry.grid(column=3, row=5)

        # Start voltage label
        self.start_voltage_label = Label(self.pulseFrame, text='Start (V)')
        self.start_voltage_label.grid(column=1, row=6)
        # Start voltage entry box
        self.start_voltage_entry = Entry(self.pulseFrame, width=5)
        self.start_voltage_entry.grid(column=1, row=7)

        # Stop voltage label
        self.stop_voltage_label = Label(self.pulseFrame, text='Stop (V)')
        self.stop_voltage_label.grid(column=2, row=6)
        # Stop voltage entry box
        self.stop_voltage_entry = Entry(self.pulseFrame, width=5)
        self.stop_voltage_entry.grid(column=2, row=7)

        # Frequency label
        self.frequency_label = Label(self.pulseFrame, text='Frequency (kHz)')
        self.frequency_label.grid(column=3, row=6)
        # Frequency entry box
        self.frequency_entry = Entry(self.pulseFrame, width=5)
        self.frequency_entry.grid(column=3, row=7)

        # Series resistance label
        self.series_resistance_label = Label(self.pulseFrame, text='Series resistance (' + u'\u03A9' + ')')
        self.series_resistance_label.grid(column=1, row=8)
        # Series resistance entry box
        self.series_resistance_entry = Entry(self.pulseFrame, width=5)
        self.series_resistance_entry.grid(column=1, row=9, pady=(0,10))

        # Start Button
        self.start_button = Button(self.pulseFrame, text='Start', command=self.start_liv_pulse)
        self.start_button.grid(column=3, row=8, rowspan=2, ipadx=10, pady=5)

        """ Device settings frame """
        self.devFrame = LabelFrame(self.master, text='Device Settings')
        # Display device settings frame
        self.devFrame.grid(column=1, row=0, sticky='W', padx=(10, 5), pady=(5,0))
        
        # Create label for device name entry box
        self.device_name_label = Label(self.devFrame, text='Device name:')
        self.device_name_label.grid(column=0, row=0, sticky='W')
        # Device name entry box
        self.device_name_entry = Entry(self.devFrame, width=15)
        self.device_name_entry.grid(column=0, row=1, sticky='W', padx=(3, 0))

        # Create label for device dimensions entry box
        self.device_dim_label = Label(self.devFrame, text='Device dimensions:')
        self.device_dim_label.grid(column=0, row=2, sticky='W')
        # Device dimensions entry box
        self.device_dim_entry = Entry(self.devFrame, width=15)
        self.device_dim_entry.grid(column=0, row=3, sticky='W', padx=(3, 0))

        self.test_laser_button_var = StringVar()

        self.laser_radiobuttom = Radiobutton(self.devFrame, text='Laser', variable=self.test_laser_button_var, value='Laser')
        self.laser_radiobuttom.grid(column=0, row=4, padx=(10, 0), sticky='W')
        self.test_radiobuttom = Radiobutton(self.devFrame, text='Test', variable=self.test_laser_button_var, value='Test')
        self.test_radiobuttom.grid(column=1, row=4, padx=(10, 0), sticky='W')

        self.test_laser_button_var.set('Laser')


        # Create label for device temperature entry box
        self.device_temp_label = Label(self.devFrame, text='Temperature (' + u'\u00B0' +'C):')
        self.device_temp_label.grid(column=1, row=0, sticky='W')
        # Device name entry box
        self.device_temp_entry = Entry(self.devFrame, width=5)
        self.device_temp_entry.grid(column=1, row=1, sticky='W', padx=(3, 0))

        """ Device settings frame """
        self.devFrame = LabelFrame(self.master, text='Device Settings')
        # Display device settings frame
        self.devFrame.grid(column=1, row=0, sticky='W', padx=(10, 5), pady=(5,0))
        
        # Create label for device name entry box
        self.device_name_label = Label(self.devFrame, text='Device name:')
        self.device_name_label.grid(column=0, row=0, sticky='W')
        # Device name entry box
        self.device_name_entry = Entry(self.devFrame, width=15)
        self.device_name_entry.grid(column=0, row=1, sticky='W', padx=(3, 0))

        # Create label for device dimensions entry box
        self.device_dim_label = Label(self.devFrame, text='Device dimensions:')
        self.device_dim_label.grid(column=0, row=2, sticky='W')
        # Device dimensions entry box
        self.device_dim_entry = Entry(self.devFrame, width=15)
        self.device_dim_entry.grid(column=0, row=3, sticky='W', padx=(3, 0))

        self.test_laser_button_var = StringVar()

        self.laser_radiobuttom = Radiobutton(self.devFrame, text='Laser', variable=self.test_laser_button_var, value='Laser')
        self.laser_radiobuttom.grid(column=0, row=4, padx=(10, 0), sticky='W')
        self.test_radiobuttom = Radiobutton(self.devFrame, text='Test Structure', variable=self.test_laser_button_var, value='TestStructure')
        self.test_radiobuttom.grid(column=1, row=4, padx=(10, 0), sticky='W')

        self.test_laser_button_var.set('Laser')


        # Create label for device temperature entry box
        self.device_temp_label = Label(self.devFrame, text='Temperature (' + u'\u00B0' +'C):')
        self.device_temp_label.grid(column=1, row=0, sticky='W')
        # Device name entry box
        self.device_temp_entry = Entry(self.devFrame, width=5)
        self.device_temp_entry.grid(column=1, row=1, sticky='W', padx=(3, 0))

        """ Instrument settings frame """
        self.instrFrame = LabelFrame(self.master, text='Instrument Settings')
        # Display device settings frame
        self.instrFrame.grid(column=1, row=1, sticky='N', padx=(10, 5))

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
        self.pulse_label = Label(self.instrFrame, text='Pulser address')
        self.pulse_label.grid(column=0, row=0, sticky='W')
        # Pulser address dropdown
        self.pulse_addr = OptionMenu(
            self.instrFrame, self.pulse_address, *connected_addresses)
        self.pulse_addr.grid(column=0, columnspan=2, row=1,
                             padx=5, pady=5, sticky='W')

        # Oscilloscope address label
        self.scope_label = Label(self.instrFrame, text='Oscilloscope address')
        self.scope_label.grid(column=0, row=2, sticky='W')
        # Oscilloscope address dropdown
        self.scope_addr = OptionMenu(
            self.instrFrame, self.scope_address, *connected_addresses)
        self.scope_addr.grid(column=0, columnspan=2, row=3,
                             padx=5, pady=5, sticky='W')

        # Oscilloscope channel options
        channels = [1, 2, 3, 4]
        self.light_channel = IntVar()
        self.current_channel = IntVar()
        self.voltage_channel = IntVar()
        self.trigger_channel = IntVar()

        # Set light channel to 1
        self.light_channel.set(1)
        # Set current channel to 2
        self.current_channel.set(2)
        # Set voltage channel to 3
        self.voltage_channel.set(3)
        # Set trigger channel to 3
        self.trigger_channel.set(3)

        # Light measurement channel label
        self.light_channel_label = Label(self.instrFrame, text='Light channel')
        self.light_channel_label.grid(column=0, row=4)
        # Light measurement channel dropdown
        self.light_channel_dropdown = OptionMenu(self.instrFrame, self.light_channel, *channels)
        self.light_channel_dropdown.grid(column=0, row=5, pady=(0,10))

        self.light_imp_label = Label(self.instrFrame, text='Impedance')
        self.light_imp_label.grid(column=0, row=6, sticky='W')

        light_impedance = ['50' + u'\u03A9', '1M' + u'\u03A9']

        self.light_channel_impedance = StringVar()
        self.light_channel_impedance.set('50' + u'\u03A9')

        self.light_impedance_dropdown = OptionMenu(self.instrFrame, self.light_channel_impedance, *light_impedance)
        self.light_impedance_dropdown.grid(column=0, row=7, padx=5,pady=(0,5), sticky='W')

        # Current measurement channel label
        self.curr_channel_label = Label(self.instrFrame, text='Current channel')
        self.curr_channel_label.grid(column=1, row=4)
        # Current measurement channel dropdown
        self.curr_channel_dropdown = OptionMenu(
            self.instrFrame, self.current_channel, *channels)
        self.curr_channel_dropdown.grid(column=1, row=5, pady=(0,10))

        self.curr_imp_label = Label(self.instrFrame, text='Impedance')
        self.curr_imp_label.grid(column=1, row=6, sticky='W')

        curr_impedance = ['50' + u'\u03A9', '1M' + u'\u03A9']

        self.curr_channel_impedance = StringVar()
        self.curr_channel_impedance.set('50' + u'\u03A9')

        self.curr_impedance_dropdown = OptionMenu(self.instrFrame, self.curr_channel_impedance, *curr_impedance)
        self.curr_impedance_dropdown.grid(column=1, row=7, padx=5,pady=(0,5), sticky='W')

        # Voltage measurement channel label
        self.voltage_channel_label = Label(self.instrFrame, text='Voltage channel')
        self.voltage_channel_label.grid(column=2, row=4)
        # Voltage measurement channel dropdown
        self.voltage_channel_dropdown = OptionMenu(
            self.instrFrame, self.voltage_channel, *channels)
        self.voltage_channel_dropdown.grid(column=2, row=5, pady=(0,10))
        
        self.volt_imp_label = Label(self.instrFrame, text='Impedance')
        self.volt_imp_label.grid(column=2, row=6, sticky='W')

        volt_impedance = ['50' + u'\u03A9', '1M' + u'\u03A9']

        self.volt_channel_impedance = StringVar()
        self.volt_channel_impedance.set('50' + u'\u03A9')

        self.volt_impedance_dropdown = OptionMenu(self.instrFrame, self.volt_channel_impedance, *volt_impedance)
        self.volt_impedance_dropdown.grid(column=2, row=7, padx=5,pady=(0,5), sticky='W')
        
        # Trigger channel label
        self.trigger_channel_label = Label(self.instrFrame, text='Trigger channel')
        self.trigger_channel_label.grid(column=3, row=4)
        # Trigger channel dropdown
        self.trigger_channel_dropdown = OptionMenu(
            self.instrFrame, self.trigger_channel, *channels)
        self.trigger_channel_dropdown.grid(column=3, row=5, pady=(0,10))
        