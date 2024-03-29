import pyvisa
from time import sleep
import numpy as np
from numpy import append, zeros, arange, logspace, log10, size
import os
import shutil
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Tkinter import Label, Entry, Button, LabelFrame, OptionMenu, Radiobutton, StringVar, IntVar, DISABLED, NORMAL

# Import Browse button functions
from Browse_buttons import browse_plot_file, browse_txt_file
# Import Oscilloscope scaling and impedance
from Oscilloscope_Scaling import incrOscVertScale, channelImpedance

rm = pyvisa.ResourceManager()

class CW_LI():

    """
    Function referenced when: "Start" button is pushed
    Description: Runs an LI sweep using the various input parameters in the main application window
    such as: start current, stop current, step size, etc.
    """

    def start_li_cw(self):
        # Connect to Keithley for applying CW current
        self.keithleySource = rm.open_resource(self.keithley_address.get())

        # Reset GPIB defaults
        self.keithleySource.write("*rst; status:preset; *cls")
        # Select source function mode as current source
        self.keithleySource.write("sour:func curr")
        # Set source level to 0A
        self.keithleySource.write("sour:curr 0")
        # Set sensor to voltage
        self.keithleySource.write("sens:func 'curr'")
        # Set voltage compliance
        compliance = float(self.compliance_entry.get())/1000
        self.keithleySource.write("sens:curr:prot:lev " + str(compliance))
        # Set voltage measure range to auto
        self.keithleySource.write("sens:curr:range:auto on ")
        
        # Connect to oscilloscope
        self.scope = rm.open_resource(self.scope_address.get())
        # Initialize oscilloscope
        self.scope.write("*RST")
        self.scope.write("*CLS")
        self.scope.write(":CHANnel%d:IMPedance %s" %(self.light_channel.get(), channelImpedance(self.channel_impedance.get())))
        self.scope.write(":TIMebase:RANGe 2E-6")

        # Channel scales - set each channel to 1mV/div to start
        vertScaleLight = 0.001

        self.scope.write(":CHANNEL%d:SCALe %.3f" %(self.light_channel.get(), vertScaleLight))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.light_channel.get())

        # Move signal down two divisions for a better view on the screen
        self.scope.write(":CHANnel%d:OFFset %.3fV" %
                         (self.light_channel.get(), 2*vertScaleLight))

        # Total mV based on 6 divisions to top of display
        totalDisplayCurrent = 6*vertScaleLight

        if 'Lin' == self.radiobutton_var.get():
            # Set up Linear current array
            stepSize = round(float(self.step_size_entry.get())/1000, 10)
            startA = float(self.start_current_entry.get())
            stopA = float(self.stop_current_entry.get())

            self.current_array = arange(startA, stopA, stepSize)
            self.current_array = append(self.current_array, stopA)

            numPtsLin = int((stopA - startA)/stepSize)+1
        elif 'Log' == self.radiobutton_var.get():
            current_source_pos = logspace(-4, log10(
                float(self.stop_current_entry.get())), int(self.num_of_pts_entry.get())/2)
            current_source_neg = - \
                logspace(log10(abs(float(self.start_current_entry.get()))
                               ), -4, int(self.num_of_pts_entry.get())/2)
            self.current_array = append(current_source_neg, current_source_pos)

        # read
        # Create empty space vector
        self.current = zeros(len(self.current_array), float)
        self.light = zeros(len(self.current_array), float)
        # Loop number of points
        for i in range(0, len(self.current_array)):
            a = self.set_current(round(self.current_array[i], 3))
            # Delay time between sweeping
            sleep(0.1)
            # --------source-------
            
            # Read light amplitude from oscilloscope; multiply by 2 to use 50-ohms channel
            self.current[i] = eval(self.keithleySource.query("read?"))
            light_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VMAX? CHANNEL%d" % self.light_channel.get())[0]
            
            # Adjust vertical scales if measured amplitude reaches top of screen (90% of display)
            while (light_ampl_osc > 0.9*totalDisplayCurrent):
                vertScaleLight = incrOscVertScale(vertScaleLight)
                totalDisplayCurrent = 6*vertScaleLight
                self.scope.write(":CHANNEL%d:SCALe %.3f" % (self.light_channel.get(), float(vertScaleLight)))
                light_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VMAX? CHANNEL%d" % self.light_channel.get())[0]
            
            # Store light reading in self.light
            self.light[i] = light_ampl_osc
            # Store current reading in self.current
            self.current[i] = eval(self.keithleySource.query("read?"))

        # finish reading
        # Turn off output
        self.keithleySource.write("outp off")

        # open file and write in data
        txtDir = self.txt_dir_entry.get()
        filename = self.device_name_entry.get() + '_CW-LI_' + self.device_temp_entry.get() + \
            'C_' + self.device_dim_entry.get() + '_' + self.test_laser_button_var.get()
        filepath = os.path.join(txtDir + '/' + filename + '.txt')
        fd = open(filepath, 'w+')
        i = 1

        for i in range(0, len(self.current_array)):
            # --------LI file----------
            fd.write(str(round(self.current_array[i], 5)) + ' ')
            fd.write(str(self.light[i]))
            fd.writelines('\n')

        fd.close()

        # ------------------ Plot measured characteristic ----------------------------------

        fig, ax1 = plt.subplots()
        ax1.set_xlabel('Measured device current (mA)')
        ax1.set_ylabel('Measured device light output (W)')
        ax1.plot(self.current, self.light, color='blue', label='L-I Characteristic')
        ax1.legend(loc='upper left')

        plotString = 'Device Name: ' + self.device_name_entry.get() + '\nTest Type: CW\n' + 'Temperature (' + u'\u00B0' + 'C): ' + self.device_temp_entry.get() + \
            '\n' + 'Device Dimensions: ' + self.device_dim_entry.get() + ' (' + u'\u03BC' + 'm x ' + u'\u03BC' + 'm)\n' + \
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

    """
    Function referenced when: Setting current within the start_li_sweep function
    Description: Connect to the Keithley, set the current to the value
    passed into the function.
    """

    def set_current(self, current):
        keithley = rm.open_resource(self.keithley_address.get())
        keithley.write("sour:func 'curr'")
        keithley.write("sens:volt:rang:auto on")
        keithley.write("sens:func 'curr'")
        keithley.write("form:elem curr")
        keithley.write("outp on")
        keithley.write("sour:curr:lev " + str(current))
        # For L-I not reading the voltage
        volt = keithley.query('READ?')

        return volt

    """
    Function referenced when: Lin radiobutton is selected
    Description: When in linear mode, we use a step size for plotting,
    so disabled the number of points entry box.
    """

    def lin_selected(self):
        self.num_of_pts_entry.config(state=DISABLED)
        self.step_size_entry.config(state=NORMAL)

    """
    Function referenced when: Log radiobutton is selected
    Description: When in logarithmic mode, we use a number of points for plotting,
    so disabled the step size entry box.
    """

    def log_selected(self):
        self.step_size_entry.config(state=DISABLED)
        self.num_of_pts_entry.config(state=NORMAL)

    """
    Function referenced when: Initializing the application window
    Description: Creates the base geometry and all widgets on the top level
    of the application window
    """

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('CW Measurement: L-I')

        """ Sweep settings frame """
        self.setFrame = LabelFrame(self.master, text='Sweep Settings')
        # Display settings frame
        self.setFrame.grid(column=0, row=0, rowspan=2, sticky='W', padx=(10, 5))

        # Create plot directory label, button, and entry box
        # Plot File Label
        self.plot_dir_label = Label(self.setFrame, text='Plot file directory:')
        self.plot_dir_label.grid(column=1, row=0, sticky='W', columnspan=2)
        # Plot directory Entry Box
        self.plot_dir_entry = Entry(self.setFrame, width=30)
        self.plot_dir_entry.grid(column=1, row=1, padx=(3, 0), columnspan=2)
        # Browse button
        self.plot_dir_file = Button(
            self.setFrame, text='Browse', command=lambda:browse_plot_file(self))
        self.plot_dir_file.grid(column=3, row=1, ipadx=5)

        # Create text directory label, button, and entry box
        # Text file label
        self.txt_dir_label = Label(self.setFrame, text='Text file directory:')
        self.txt_dir_label.grid(column=1, row=2, sticky='W', columnspan=2)
        # Text directory entry box
        self.txt_dir_entry = Entry(self.setFrame, width=30)
        self.txt_dir_entry.grid(column=1, row=3, padx=(3, 0), columnspan=2)
        # Browse button
        self.txt_dir_file = Button(
            self.setFrame, text='Browse', command=lambda:browse_txt_file(self))
        self.txt_dir_file.grid(column=3, row=3, ipadx=5)

        # Step size label
        self.step_size_label = Label(self.setFrame, text='Step size (mA)')
        self.step_size_label.grid(column=1, row=4)
        # Step size entry box
        self.step_size_entry = Entry(self.setFrame, width=5)
        self.step_size_entry.grid(column=1, row=5)

        # Number of points label
        self.numPts = IntVar()
        self.num_of_pts_label = Label(self.setFrame, text='# of points')
        self.num_of_pts_label.grid(column=2, row=4)
        # Number of points entry box
        self.num_of_pts_entry = Entry(
            self.setFrame, textvariable=self.numPts, width=5)
        self.num_of_pts_entry.grid(column=2, row=5)

        # Compliance label
        self.compliance_label = Label(self.setFrame, text='Compliance (mV)')
        self.compliance_label.grid(column=3, row=4, columnspan=2)
        # Compliance entry box
        self.compliance_entry = Entry(self.setFrame, width=5)
        self.compliance_entry.grid(column=3, row=5, columnspan=2)

        # Start current label
        self.start_current_label = Label(self.setFrame, text='Start (A)')
        self.start_current_label.grid(column=1, row=6)
        # Start current entry box
        self.start_current_entry = Entry(self.setFrame, width=5)
        self.start_current_entry.grid(column=1, row=7)

        # Stop current label
        self.stop_current_label = Label(self.setFrame, text='Stop (A)')
        self.stop_current_label.grid(column=2, row=6)
        # Stop current entry box
        self.stop_current_entry = Entry(self.setFrame, width=5)
        self.stop_current_entry.grid(column=2, row=7)

        # Linear, Log, Lin-Log buttons
        self.radiobutton_var = StringVar()
        self.lin_radiobutton = Radiobutton(
            self.setFrame, text='Lin', variable=self.radiobutton_var, command=self.lin_selected, value='Lin')
        self.lin_radiobutton.grid(column=1, row=10, padx=(10, 0), sticky='W')

        self.log_radiobutton = Radiobutton(
            self.setFrame, text='Log', variable=self.radiobutton_var, command=self.log_selected, value='Log')
        self.log_radiobutton.grid(column=2, row=10, sticky='W')

        # The default setting for radiobutton is set to linear sweep
        self.radiobutton_var.set('Lin')

        # Disable # of points entry because Lin is selected
        self.num_of_pts_entry.config(state=DISABLED)

        # Start Button
        self.start_button = Button(
            self.setFrame, text='Start', command=self.start_li_cw)
        self.start_button.grid(column=2, row=11, ipadx=10, pady=5)

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
        self.device_dim_label = Label(self.devFrame, text='Device dimensions ' + '(' + u'\u03BC' + 'm x ' + u'\u03BC' + 'm):')
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
        self.instrFrame.grid(column=1, row=1, sticky='N', padx=(10, 5), pady=(5,5))

        # Device addresses
        connected_addresses = list(rm.list_resources())
        # Keithley and scope variables
        self.keithley_address = StringVar()
        self.scope_address = StringVar()

        # If no devices detected
        if size(connected_addresses) is 0:
            connected_addresses = ['No devices detected.']

        # Set the pulser and scope variables to default values
        self.keithley_address.set('Choose keithley address.')
        self.scope_address.set('Choose oscilloscope address.')

        # Keithley address label
        self.keithley_label = Label(self.instrFrame, text='Keithley Address')
        self.keithley_label.grid(column=0, row=0, sticky='W')
        # Keithley address dropdown
        self.keithley_addr = OptionMenu(
            self.instrFrame, self.keithley_address, *connected_addresses)
        self.keithley_addr.grid(column=0, columnspan=2, row=1,
                             padx=5, pady=5, sticky='W')

        # Oscilloscope address label
        self.scope_label = Label(self.instrFrame, text='Oscilloscope Address')
        self.scope_label.grid(column=0, row=2, sticky='W')
        # Oscilloscope address dropdown
        self.scope_addr = OptionMenu(
            self.instrFrame, self.scope_address, *connected_addresses)
        self.scope_addr.grid(column=0, columnspan=2, row=3,
                             padx=5, pady=5, sticky='W')

        # Oscilloscope channel options
        channels = [1, 2, 3, 4]
        self.light_channel = IntVar()

        # Set light channel to 1
        self.light_channel.set(1)

        # Light measurement channel label
        self.light_channel_label = Label(self.instrFrame, text='Light channel')
        self.light_channel_label.grid(column=0, row=4)
        # Light measurement channel dropdown
        self.light_channel_dropdown = OptionMenu(
            self.instrFrame, self.light_channel, *channels)
        self.light_channel_dropdown.grid(column=0, row=5)

        self.imp_label = Label(self.instrFrame, text='Channel Impedance')
        self.imp_label.grid(column=1, row=4, sticky='W')

        # Oscilloscope Channel
        impedance = ['50' + u'\u03A9', '1M' + u'\u03A9']

        self.channel_impedance = StringVar()
        self.channel_impedance.set('50' + u'\u03A9')

        self.channel_impedance_dropdown = OptionMenu(self.instrFrame, self.channel_impedance, *impedance)
        self.channel_impedance_dropdown.grid(column=1, row=5, padx=5,pady=(0,5), sticky='W')

class CW_IV():

    """
    Function referenced when: "Start" button is pushed
    Description: Runs an IV sweep using the various input parameters in the main application window
    such as: start voltage, stop voltage, step size, etc.
    """

    def start_iv_sweep(self):
        # Connect to Keithley Source Meter
        self.keithley = rm.open_resource(self.keithley1_address.get())

        # Reset GPIB defaults
        self.keithley.write("*rst; status:preset; *cls")
        # Select source function mode as voltage source
        self.keithley.write("sour:func volt")
        # Set source level to 10V
        self.keithley.write("sour:volt 0")
        # Set sensor to current
        self.keithley.write("sens:func 'curr'")
        # Set curr compliance
        compliance = float(self.compliance_entry.get())/1000
        self.keithley.write("sens:curr:prot:lev " + str(compliance))
        # Set curr measure range to auto
        self.keithley.write("sens:curr:range:auto on ")

        if 'Lin' == self.radiobutton_var.get():
            # Set up Linear voltage array
            stepSize = round(float(self.step_size_entry.get())/1000, 3)
            startV = float(self.start_voltage_entry.get())
            stopV = float(self.stop_voltage_entry.get())

            self.voltage_array = arange(startV, stopV, stepSize)
            self.voltage_array = append(self.voltage_array, stopV)

            numPtsLin = int((stopV - startV)/stepSize)+1
        elif 'Log' == self.radiobutton_var.get():
            voltage_source_pos = logspace(-4, log10(
                float(self.stop_voltage_entry.get())), int(self.num_of_pts_entry.get())/2)
            voltage_source_neg = - \
                logspace(log10(abs(float(self.start_voltage_entry.get()))
                               ), -4, int(self.num_of_pts_entry.get())/2)
            self.voltage_array = append(voltage_source_neg, voltage_source_pos)
        elif 'Linlog' == self.radiobutton_var.get():
            # Set up Linear voltage array
            stepSize = round(float(self.step_size_entry.get())/1000, 3)
            startV = float(self.start_voltage_entry.get())
            stopV = float(self.stop_voltage_entry.get())

            self.voltage_array = arange(startV, -0.5+stepSize, stepSize)
            voltage_linear_pos = arange(0.5+stepSize, stopV+stepSize, stepSize)

            # Log scale
            voltage_log_pos = logspace(-4, log10(0.5),
                                       int(self.num_of_pts_entry.get())/2)
            voltage_log_neg = - \
                logspace(log10(0.5), -4, int(self.num_of_pts_entry.get())/2)

            self.voltage_array = append(self.voltage_array, voltage_log_neg)
            self.voltage_array = append(self.voltage_array, voltage_log_pos)
            self.voltage_array = append(self.voltage_array, voltage_linear_pos)

        # read
        # Create empty space vector
        self.current = zeros(len(self.voltage_array), float)
        # Loop number of points
        for i in range(0, len(self.voltage_array)):
            a = self.set_voltage(round(self.voltage_array[i], 3))
            # Delay time between sweeping
            sleep(0.1)
            # --------source-------
            b1 = eval(self.keithley.query("read?"))
            self.current[i] = b1

        # finish reading
        # Turn off output
        self.keithley.write("outp off")

        # open file and write in data
        txtDir = self.txt_dir_entry.get()
        filename = self.device_name_entry.get() + '_CW-IV_' + self.device_temp_entry.get() + \
            'C_' + self.device_dim_entry.get() + '_' + self.test_laser_button_var.get()
        filepath = os.path.join(txtDir + '/' + filename + '.txt')
        fd = open(filepath, 'w+')
        i = 1

        for i in range(0, len(self.voltage_array)):
            # --------IV file----------
            fd.write(str(round(self.voltage_array[i], 5)) + ' ')
            fd.write(str(self.current[i]))
            fd.writelines('\n')

        fd.close()

        # ------------------ Plot measured characteristic ----------------------------------

        fig, ax1 = plt.subplots()
        ax1.set_xlabel('Measured device current (mA)')
        ax1.set_ylabel('Measured device voltage (mV)')
        ax1.plot(self.current, self.voltage_array, color='blue', label='I-V Characteristic')
        ax1.legend(loc='upper left')
        
        plotString = 'Device Name: ' + self.device_name_entry.get() + '\nTest Type: CW\n' + 'Temperature (' + u'\u00B0' + 'C): ' + self.device_temp_entry.get() + \
            '\n' + 'Device Dimensions: ' + self.device_dim_entry.get() + ' (' + u'\u03BC' + 'm x ' + u'\u03BC' + 'm)\n' + \
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

    """
    Function referenced when: setting voltage within the start_iv_sweep function
    Description: Connect to the Keithley, provide what voltage should be set
    read the corresponding current
    """

    def set_voltage(self, voltage):
        keithley = rm.open_resource(self.keithley1_address.get())
        keithley.delay = 0.1    # Necessary for GPIB connection?
        keithley.write("sour:func volt")
        keithley.write("sens:curr:rang:auto on")
        keithley.write("sens:func 'curr'")
        keithley.write("form:elem curr")
        keithley.write("outp on")
        keithley.write("sour:volt:lev " + str(voltage))
        curr = keithley.query('READ?')

        return curr

    # Implement multi-threading to allow the use of the main window while running a sweep
    # def stop_pressed(self):
    #     self.keithley.write('outp off')
    #     self.stop_button.config(state=DISABLED)
    #     # Return from function

    """
    Function referenced when: Lin radiobutton is selected
    Description: When in linear mode, we use a step size for plotting,
    so disabled the number of points entry box.
    """

    def lin_selected(self):
        self.num_of_pts_entry.config(state=DISABLED)
        self.step_size_entry.config(state=NORMAL)

    """
    Function referenced when: Log radiobutton is selected
    Description: When in logarithmic mode, we use a number of points for plotting,
    so disabled the step size entry box.
    """

    def log_selected(self):
        self.step_size_entry.config(state=DISABLED)
        self.num_of_pts_entry.config(state=NORMAL)

    """
    Function referenced when: Linlog radiobutton is selected
    Description: When in linear-logarithmic mode, we use both the step size
    and the number of points for plotting, so enable both entries.
    """

    def linlog_selected(self):
        self.step_size_entry.config(state=NORMAL)
        self.num_of_pts_entry.config(state=NORMAL)

    """
    Function referenced when: Initializing the application window
    Description: Creates the base geometry and all widgets on the top level
    of the application window
    """

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('CW Measurement: I-V')

        """ Sweep settings frame """
        self.setFrame = LabelFrame(self.master, text='Sweep Settings')
        # Display settings frame
        self.setFrame.grid(column=0, row=0, sticky='W', rowspan=2, padx=(10, 5), pady=(0,5))

        # Create plot directory label, button, and entry box
        # Plot File Label
        self.plot_dir_label = Label(self.setFrame, text='Plot file directory:')
        self.plot_dir_label.grid(column=1, row=0, sticky='W', columnspan=2)
        # Plot directory Entry Box
        self.plot_dir_entry = Entry(self.setFrame, width=30)
        self.plot_dir_entry.grid(column=1, row=1, padx=(3, 0), columnspan=2)
        # Browse button
        self.plot_dir_file = Button(
            self.setFrame, text='Browse', command=lambda:browse_plot_file(self))
        self.plot_dir_file.grid(column=3, row=1, ipadx=5)

        # Create text directory label, button, and entry box
        # Text file label
        self.txt_dir_label = Label(self.setFrame, text='Text file directory:')
        self.txt_dir_label.grid(column=1, row=2, sticky='W', columnspan=2)
        # Text directory entry box
        self.txt_dir_entry = Entry(self.setFrame, width=30)
        self.txt_dir_entry.grid(column=1, row=3, padx=(3, 0), columnspan=2)
        # Browse button
        self.txt_dir_file = Button(
            self.setFrame, text='Browse', command=lambda:browse_txt_file(self))
        self.txt_dir_file.grid(column=3, row=3, ipadx=5)

        # Step size label
        self.step_size_label = Label(self.setFrame, text='Step size (mV)')
        self.step_size_label.grid(column=1, row=4)
        # Step size entry box
        self.step_size_entry = Entry(self.setFrame, width=5)
        self.step_size_entry.grid(column=1, row=5)

        # Number of points label
        self.numPts = IntVar()
        self.num_of_pts_label = Label(self.setFrame, text='# of points')
        self.num_of_pts_label.grid(column=2, row=4)
        # Number of points entry box
        self.num_of_pts_entry = Entry(
            self.setFrame, textvariable=self.numPts, width=5)
        self.num_of_pts_entry.grid(column=2, row=5)

        # Compliance label
        self.compliance_label = Label(self.setFrame, text='Compliance (mA)')
        self.compliance_label.grid(column=3, row=4, columnspan=2)
        # Compliance entry box
        self.compliance_entry = Entry(self.setFrame, width=5)
        self.compliance_entry.grid(column=3, row=5, columnspan=2)

        # Start voltage label
        self.start_voltage_label = Label(self.setFrame, text='Start (V)')
        self.start_voltage_label.grid(column=1, row=6)
        # Start voltage entry box
        self.start_voltage_entry = Entry(self.setFrame, width=5)
        self.start_voltage_entry.grid(column=1, row=7)

        # Stop voltage label
        self.stop_voltage_label = Label(self.setFrame, text='Stop (V)')
        self.stop_voltage_label.grid(column=2, row=6)
        # Stop voltage entry box
        self.stop_voltage_entry = Entry(self.setFrame, width=5)
        self.stop_voltage_entry.grid(column=2, row=7)

        # Linear, Log, Lin-Log buttons
        self.radiobutton_var = StringVar()
        self.lin_radiobutton = Radiobutton(
            self.setFrame, text='Lin', variable=self.radiobutton_var, command=self.lin_selected, value='Lin')
        self.lin_radiobutton.grid(column=1, row=10, padx=(10, 0), sticky='W')

        self.log_radiobutton = Radiobutton(
            self.setFrame, text='Log', variable=self.radiobutton_var, command=self.log_selected, value='Log')
        self.log_radiobutton.grid(column=2, row=10, sticky='W')

        self.linlog_radiobutton = Radiobutton(
            self.setFrame, text='Lin-log', variable=self.radiobutton_var, command=self.linlog_selected, value='Linlog')
        self.linlog_radiobutton.grid(column=3, row=10, sticky='W')

        # The default setting for radiobutton is set to linear sweep
        self.radiobutton_var.set('Lin')

        # Disable # of points entry because Lin is selected
        self.num_of_pts_entry.config(state=DISABLED)

        # Start Button
        self.start_button = Button(
            self.setFrame, text='Start', command=self.start_iv_sweep)
        self.start_button.grid(column=2, row=11, ipadx=10, pady=5)

        """ Device settings frame """
        self.devFrame = LabelFrame(self.master, text='Device Settings')
        # Display device settings frame
        self.devFrame.grid(column=1, row=0, sticky='W', padx=(10, 5))
        
        # Create label for device name entry box
        self.device_name_label = Label(self.devFrame, text='Device name:')
        self.device_name_label.grid(column=0, row=0, sticky='W')
        # Device name entry box
        self.device_name_entry = Entry(self.devFrame, width=15)
        self.device_name_entry.grid(column=0, row=1, sticky='W', padx=(3, 0))

        # Create label for device dimensions entry box
        self.device_dim_label = Label(self.devFrame, text='Device dimensions ' + '(' + u'\u03BC' + 'm x ' + u'\u03BC' + 'm):')
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
        self.instrFrame.grid(column=1, row=1, sticky='W', padx=(10, 5), pady=(5,5))

        # Device addresses
        connected_addresses = list(rm.list_resources())
        # Pulser and scope variables
        self.keithley1_address = StringVar()
        self.keithley2_address = StringVar()

        # If no devices detected
        if size(connected_addresses) is 0:
            connected_addresses = ['No devices detected.']

        # Set the pulser and scope variables to default values
        self.keithley1_address.set('Choose Source Keithley address.')
        self.keithley2_address.set('Choose Measurement Keithley address.')

        self.keithley1_label = Label(self.instrFrame, text='Source Keithley Address')
        self.keithley1_label.grid(column=0, row=0, sticky='W')

        self.keithley1_addr = OptionMenu(
            self.instrFrame, self.keithley1_address, *connected_addresses)
        self.keithley1_addr.grid(column=0, row=1, padx=5, sticky='W')

        self.keithley2_label = Label(self.instrFrame, text='Measurement Keithley Address')
        self.keithley2_label.grid(column=0, row=2, sticky='W')

        self.keithley2_addr = OptionMenu(
            self.instrFrame, self.keithley2_address, *connected_addresses)
        self.keithley2_addr.grid(column=0, row=3, padx=5, sticky='W')

class CW_LIV():

    """
    Function referenced when: "Start" button is pushed
    Description: Runs an IV sweep using the various input parameters in the main application window
    such as: start voltage, stop voltage, step size, etc.
    """

    def start_liv_sweep(self):
        # Connect to Keithley Source Meter
        self.keithley = rm.open_resource(self.keithley_address.get())

        # # Enable stop button
        # self.stop_button.config(state=NORMAL)

        # Reset GPIB defaults
        self.keithley.write("*rst; status:preset; *cls")
        # Select source function mode as voltage source
        self.keithley.write("sour:func volt")
        # Set source level to 10V
        self.keithley.write("sour:volt 0")
        # Set sensor to current
        self.keithley.write("sens:func 'curr'")
        # Set curr compliance
        compliance = float(self.compliance_entry.get())/1000
        self.keithley.write("sens:curr:prot:lev " + str(compliance))
        # Set curr measure range to auto
        self.keithley.write("sens:curr:range:auto on ")

        # Connect to oscilloscope
        self.scope = rm.open_resource(self.osc_address.get())
        # Initialize oscilloscope
        self.scope.write("*RST")
        self.scope.write("*CLS")

        self.scope.write(":CHANnel%d:IMPedance %s" %(self.light_channel.get(), channelImpedance(self.light_channel_impedance.get())))
        self.scope.write(":TIMebase:RANGe 2E-6")

        # Channel scales - set each channel to 1mV/div to start
        vertScaleLight = 0.001

        self.scope.write(":CHANNEL%d:SCALe %.3f" %
                         (self.light_channel.get(), vertScaleLight))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.light_channel.get())

        # Move signal down two divisions for a better view on the screen
        self.scope.write(":CHANnel%d:OFFset %.3fV" %
                         (self.light_channel.get(), 2*vertScaleLight))

        # Total mV based on 6 divisions to top of display
        totalDisplayCurrent = 6*vertScaleLight

        if 'Lin' == self.radiobutton_var.get():
            # Set up Linear voltage array
            stepSize = round(float(self.step_size_entry.get())/1000, 3)
            startV = float(self.start_voltage_entry.get())
            stopV = float(self.stop_voltage_entry.get())

            self.voltage_array = arange(startV, stopV, stepSize)
            self.voltage_array = append(self.voltage_array, stopV)

            numPtsLin = int((stopV - startV)/stepSize)+1
        elif 'Log' == self.radiobutton_var.get():
            voltage_source_pos = logspace(-4, log10(
                float(self.stop_voltage_entry.get())), int(self.num_of_pts_entry.get())/2)
            voltage_source_neg = - \
                logspace(log10(abs(float(self.start_voltage_entry.get()))
                               ), -4, int(self.num_of_pts_entry.get())/2)
            self.voltage_array = append(voltage_source_neg, voltage_source_pos)

        # read
        # Create empty space vector
        self.current = zeros(len(self.voltage_array), float)
        self.light = zeros(len(self.voltage_array), float)
        # Loop number of points
        for i in range(0, len(self.voltage_array)):
            a = self.set_voltage(round(self.voltage_array[i], 3))
            # Delay time between sweeping
            sleep(0.1)
            # --------source-------
            # Read light amplitude from oscilloscope; multiply by 2 to use 50-ohms channel
            self.current[i] = eval(self.keithley.query("read?"))
            light_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VMAX? CHANNEL%d" % self.light_channel.get())[0]

            # Adjust vertical scales if measured amplitude reaches top of screen (90% of display)
            while (light_ampl_osc > 0.9*totalDisplayCurrent):
                vertScaleLight = incrOscVertScale(vertScaleLight)
                totalDisplayCurrent = 6*vertScaleLight
                self.scope.write(":CHANNEL%d:SCALe %.3f" % (self.light_channel.get(), float(vertScaleLight)))
                light_ampl_osc = self.scope.query_ascii_values("SINGLE;*OPC;:MEASure:VMAX? CHANNEL%d" % self.light_channel.get())[0]
            
            # Store light reading in self.light
            self.light[i] = light_ampl_osc

        # finish reading
        # Turn off output
        self.keithley.write("outp off")

        # open file and write in data
        txtDir = self.txt_dir_entry.get()
        filename = self.device_name_entry.get() + '_CW-LIV_' + self.device_temp_entry.get() + \
            'C_' + self.device_dim_entry.get() + '_' + self.test_laser_button_var.get()
        filepath = os.path.join(txtDir + '/' + filename + '.txt')
        fd = open(filepath, 'w+')
        i = 1
        
        fd.writelines('Device voltage (V)\tDevice current (A)\tPhotodetector current (W)\n')
        for i in range(0, len(self.voltage_array)):
            # --------IV file----------
            fd.write(str(round(self.voltage_array[i], 5)) + '\t')
            fd.write(str(self.current[i]) + '\t')
            fd.write(str(self.light[i]))
            fd.writelines('\n')

        fd.close()

        # ------------------ Plot measured characteristic ----------------------------------

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax2.set_ylabel('Measured device light output (W)', color='red')
        ax1.set_xlabel('Measured device current (A)')
        ax1.set_ylabel('Measured device voltage (V)', color='blue')
        ax1.plot(self.current, self.voltage_array, color='blue', label='I-V Characteristic')
        ax2.plot(self.current, self.light, color='red', label='L-I Characteristic')
        
        plotString = 'Device Name: ' + self.device_name_entry.get() + '\nTest Type: CW\n' + 'Temperature (' + u'\u00B0' + 'C): ' + self.device_temp_entry.get() + \
            '\n' + 'Device Dimensions: ' + self.device_dim_entry.get() + ' (' + u'\u03BC' + 'm x ' + u'\u03BC' + 'm)\n' + \
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

    """
    Function referenced when: setting voltage within the start_iv_sweep function
    Description: Connect to the Keithley, provide what voltage should be set
    read the corresponding current
    """

    def set_voltage(self, voltage):
        keithley = rm.open_resource(self.keithley_address.get())
        keithley.delay = 0.1    # Necessary for GPIB connection?
        keithley.write("sour:func volt")
        keithley.write("sens:curr:rang:auto on")
        keithley.write("sens:func 'curr'")
        keithley.write("form:elem curr")
        keithley.write("outp on")
        keithley.write("sour:volt:lev " + str(voltage))
        curr = keithley.query('READ?')

        return curr

    # Implement multi-threading to allow the use of the main window while running a sweep
    # def stop_pressed(self):
    #     self.keithley.write('outp off')
    #     self.stop_button.config(state=DISABLED)
    #     # Return from function

    """
    Function referenced when: Lin radiobutton is selected
    Description: When in linear mode, we use a step size for plotting,
    so disabled the number of points entry box.
    """

    def lin_selected(self):
        self.num_of_pts_entry.config(state=DISABLED)
        self.step_size_entry.config(state=NORMAL)

    """
    Function referenced when: Log radiobutton is selected
    Description: When in logarithmic mode, we use a number of points for plotting,
    so disabled the step size entry box.
    """

    def log_selected(self):
        self.step_size_entry.config(state=DISABLED)
        self.num_of_pts_entry.config(state=NORMAL)

    """
    Function referenced when: Initializing the application window
    Description: Creates the base geometry and all widgets on the top level
    of the application window
    """

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('CW Measurement: L-I-V')

        """ Sweep settings frame """
        self.setFrame = LabelFrame(self.master, text='Sweep Settings')
        # Display settings frame
        self.setFrame.grid(column=0, row=0, sticky='W', padx=(10, 5), pady=(0,5), rowspan=2)

        # Create plot directory label, button, and entry box
        # Plot File Label
        self.plot_dir_label = Label(self.setFrame, text='Plot file directory:')
        self.plot_dir_label.grid(column=1, row=0, sticky='W', columnspan=2)
        # Plot directory Entry Box
        self.plot_dir_entry = Entry(self.setFrame, width=30)
        self.plot_dir_entry.grid(column=1, row=1, padx=(3, 0), columnspan=2)
        # Browse button
        self.plot_dir_file = Button(
            self.setFrame, text='Browse', command=lambda:browse_plot_file(self))
        self.plot_dir_file.grid(column=3, row=1, ipadx=5)

        # Create text directory label, button, and entry box
        # Text file label
        self.txt_dir_label = Label(self.setFrame, text='Text file directory:')
        self.txt_dir_label.grid(column=1, row=2, sticky='W', columnspan=2)
        # Text directory entry box
        self.txt_dir_entry = Entry(self.setFrame, width=30)
        self.txt_dir_entry.grid(column=1, row=3, padx=(3, 0), columnspan=2)
        # Browse button
        self.txt_dir_file = Button(
            self.setFrame, text='Browse', command=lambda:browse_txt_file(self))
        self.txt_dir_file.grid(column=3, row=3, ipadx=5)

        # Step size label
        self.step_size_label = Label(self.setFrame, text='Step size (mV)')
        self.step_size_label.grid(column=1, row=6)
        # Step size entry box
        self.step_size_entry = Entry(self.setFrame, width=5)
        self.step_size_entry.grid(column=1, row=7)

        # Number of points label
        self.numPts = IntVar()
        self.num_of_pts_label = Label(self.setFrame, text='# of points')
        self.num_of_pts_label.grid(column=2, row=6)
        # Number of points entry box
        self.num_of_pts_entry = Entry(
            self.setFrame, textvariable=self.numPts, width=5)
        self.num_of_pts_entry.grid(column=2, row=7)

        # Compliance label
        self.compliance_label = Label(self.setFrame, text='Compliance (mA)')
        self.compliance_label.grid(column=3, row=6, columnspan=2)
        # Compliance entry box
        self.compliance_entry = Entry(self.setFrame, width=5)
        self.compliance_entry.grid(column=3, row=7, columnspan=2)

        # Start voltage label
        self.start_voltage_label = Label(self.setFrame, text='Start (V)')
        self.start_voltage_label.grid(column=1, row=8)
        # Start voltage entry box
        self.start_voltage_entry = Entry(self.setFrame, width=5)
        self.start_voltage_entry.grid(column=1, row=9)

        # Stop voltage label
        self.stop_voltage_label = Label(self.setFrame, text='Stop (V)')
        self.stop_voltage_label.grid(column=2, row=8)
        # Stop voltage entry box
        self.stop_voltage_entry = Entry(self.setFrame, width=5)
        self.stop_voltage_entry.grid(column=2, row=9)

        # Linear, Log, Lin-Log buttons
        self.radiobutton_var = StringVar()
        self.lin_radiobutton = Radiobutton(
            self.setFrame, text='Lin', variable=self.radiobutton_var, command=self.lin_selected, value='Lin')
        self.lin_radiobutton.grid(column=1, row=10, padx=(10, 0), sticky='W')

        self.log_radiobutton = Radiobutton(
            self.setFrame, text='Log', variable=self.radiobutton_var, command=self.log_selected, value='Log')
        self.log_radiobutton.grid(column=2, row=10, sticky='W')

        # The default setting for radiobutton is set to linear sweep
        self.radiobutton_var.set('Lin')

        # Disable # of points entry because Lin is selected
        self.num_of_pts_entry.config(state=DISABLED)

        # Start Button
        self.start_button = Button(
            self.setFrame, text='Start', command=self.start_liv_sweep)
        self.start_button.grid(column=2, row=11, ipadx=10, pady=5)

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
        self.device_dim_label = Label(self.devFrame, text='Device dimensions ' + '(' + u'\u03BC' + 'm x ' + u'\u03BC' + 'm):')
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
        self.instrFrame.grid(column=1, row=1, sticky='W', padx=(10, 5), pady=(5,5))

        # Device addresses
        connected_addresses = list(rm.list_resources())
        # Pulser and scope variables
        self.keithley_address = StringVar()
        self.osc_address = StringVar()

        # If no devices detected
        if size(connected_addresses) is 0:
            connected_addresses = ['No devices detected.']

        # Set the keithley and scope variables to default values
        self.keithley_address.set('Choose Keithley address.')
        self.osc_address.set('Choose Oscilloscope address.')

        self.keithley_label = Label(self.instrFrame, text='Keithley Address')
        self.keithley_label.grid(column=0, row=0, sticky='W', columnspan=2)

        self.keithley_addr = OptionMenu(self.instrFrame, self.keithley_address, *connected_addresses)
        self.keithley_addr.grid(column=0, row=1, padx=5, sticky='W', columnspan=2)

        self.osc_label = Label(self.instrFrame, text='Oscilloscope Address')
        self.osc_label.grid(column=0, row=2, sticky='W', columnspan=2)

        self.osc_label = Label(self.instrFrame, text='Light Channel')
        self.osc_label.grid(column=0, row=4, sticky='W')

        self.osc_addr = OptionMenu(self.instrFrame, self.osc_address, *connected_addresses)
        self.osc_addr.grid(column=0, row=3, padx=5, sticky='W', columnspan=2)
        
        # Oscilloscope channel options
        channels = [1, 2, 3, 4]

        self.light_channel = IntVar()
        # Set light channel to 1
        self.light_channel.set(1)

        # Light measurement channel dropdown
        self.light_channel_dropdown = OptionMenu(self.instrFrame, self.light_channel, *channels)
        self.light_channel_dropdown.grid(column=0, row=5, padx=5, pady=(0,5), sticky='W')

        self.imp_label = Label(self.instrFrame, text='Channel Impedance')
        self.imp_label.grid(column=1, row=4, sticky='W')

        # Oscilloscope Channel
        impedance = ['50' + u'\u03A9', '1M' + u'\u03A9']

        self.channel_impedance = StringVar()
        self.channel_impedance.set('50' + u'\u03A9')

        self.channel_impedance_dropdown = OptionMenu(self.instrFrame, self.channel_impedance, *impedance)
        self.channel_impedance_dropdown.grid(column=1, row=5, padx=5,pady=(0,5), sticky='W')
