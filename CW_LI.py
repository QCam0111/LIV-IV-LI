import pyvisa
from time import sleep, strftime
import numpy as np
from numpy import append, zeros, arange, logspace, log10, size
import os
import shutil
import matplotlib.pyplot as plt
from Tkinter import Label, Entry, Button, LabelFrame, OptionMenu, Radiobutton, StringVar, IntVar, DISABLED, NORMAL

# Import Browse button functions
from Browse_buttons import browse_plot_file, browse_txt_file
# Import Oscilloscope scaling
from Oscilloscope_Scaling import incrOscVertScale

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
        self.scope.write(":CHANnel%d:IMPedance FIFTy" %self.light_channel.get())
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
        name = self.file_name_entry.get()
        filepath = os.path.join(txtDir + '/' + name + '.txt')
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

        plt.tight_layout()
        plt.savefig(self.plot_dir_entry.get() + '/' + self.file_name_entry.get() + ".png")
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
        self.device_dim_label = Label(self.devFrame, text='Dimensions:')
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
        self.keithley_address.set('Choose pulser address.')
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