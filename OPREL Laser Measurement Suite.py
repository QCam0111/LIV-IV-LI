import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from numpy import append, zeros, arange, logspace, flip, log10, size
import os
import pyvisa
# For use when interacting with the temperature controller or oscilloscope
# from pyvisa.constants import Parity, StopBits, VI_ASRL_FLOW_NONE
import Tkinter as tk
from Tkinter import Label, Entry, Button, Radiobutton, LabelFrame, Toplevel, OptionMenu, StringVar, IntVar, END, DISABLED, NORMAL
import tkMessageBox as messagebox
import tkFileDialog as FileDialog
from time import sleep, strftime
import shutil

rm = pyvisa.ResourceManager()

class MeasSelect():

    def __init__(self, parent):
        self.master = parent

        # Assign window title
        self.master.title('Laser Diode Measurement Selection')

        # Create selection buttons
        self.selectedMeasurement = StringVar()

        # Continuous wave (CW) measurement section

        # CW section label
        self.CW_label = Label(self.master, text='Continuous Wave Measurements', font=(
            'Segoe UI Semibold', 12, 'underline'))
        self.CW_label.grid(column=0, row=0, columnspan=3,
                           padx=(5, 0), pady=(5, 5), sticky='W')
        # CW L-I-V measurement button
        self.CW_LIV_radiobutton = Radiobutton(
            self.master, text='CW L - I - V', variable=self.selectedMeasurement, value='CW_LIV', font=('Segoe UI', 10))
        self.CW_LIV_radiobutton.grid(column=0, row=1, padx=(5, 0), sticky='W')
        # CW I-V measurement button
        self.CW_IV_radiobutton = Radiobutton(
            self.master, text='CW I - V', variable=self.selectedMeasurement, value='CW_IV', font=('Segoe UI', 10))
        self.CW_IV_radiobutton.grid(column=1, row=1, padx=(5, 0), sticky='W')
        # CW L-I measurement button
        self.CW_LI_radiobutton = Radiobutton(
            self.master, text='CW L - I', variable=self.selectedMeasurement, value='CW_LI', font=('Segoe UI', 10))
        self.CW_LI_radiobutton.grid(column=2, row=1, padx=(5, 0), sticky='W')

        # Voltage pulsed (VPulse) measurement section

        # VPulse section label
        self.VPulse_label = Label(self.master, text='Voltage Pulsed Measurements', font=(
            'Segoe UI Semibold', 12, 'underline'))
        self.VPulse_label.grid(column=0, row=3, columnspan=3, padx=(
            5, 0), pady=(5, 5), sticky='W')
        # VPulse L-I-V measurement button
        self.VPulse_LIV_radiobutton = Radiobutton(
            self.master, text='Voltage Pulsed L - I - V', variable=self.selectedMeasurement, value='VPulse_LIV', font=('Segoe UI', 10))
        self.VPulse_LIV_radiobutton.grid(
            column=0, row=4, padx=(5, 0), sticky='W')
        # VPulse I-V measurement button
        self.VPulse_IV_radiobutton = Radiobutton(
            self.master, text='Voltage Pulsed I - V', variable=self.selectedMeasurement, value='VPulse_IV', font=('Segoe UI', 10))
        self.VPulse_IV_radiobutton.grid(
            column=1, row=4, padx=(5, 0), sticky='W')
        # VPulse L-I measurement button
        self.VPulse_LI_radiobutton = Radiobutton(
            self.master, text='Voltage Pulsed L - I', variable=self.selectedMeasurement, value='VPulse_LI', font=('Segoe UI', 10))
        self.VPulse_LI_radiobutton.grid(
            column=2, row=4, padx=(5, 0), sticky='W')

        # Current pulsed (IPulse) measurement section

        # IPulse section label
        self.IPulse_label = Label(self.master, text='Current Pulsed Measurements', font=(
            'Segoe UI Semibold', 12, 'underline'))
        self.IPulse_label.grid(column=0, row=5, padx=(
            5, 0), pady=(5, 5), columnspan=3, sticky='W')
        # IPulse L-I-V measurement button
        self.IPulse_LIV_radiobutton = Radiobutton(
            self.master, text='Current Pulsed L - I - V', variable=self.selectedMeasurement, value='IPulse_LIV', font=('Segoe UI', 10))
        self.IPulse_LIV_radiobutton.grid(
            column=0, row=6, padx=(5, 0), sticky='W')
        # IPulse I-V measurement button
        self.IPulse_IV_radiobutton = Radiobutton(
            self.master, text='Current Pulsed V - I', variable=self.selectedMeasurement, value='IPulse_VI', font=('Segoe UI', 10))
        self.IPulse_IV_radiobutton.grid(
            column=1, row=6, padx=(5, 0), sticky='W')
        # IPulse L-I measurement button
        self.IPulse_LI_radiobutton = Radiobutton(
            self.master, text='Current Pulsed L - I', variable=self.selectedMeasurement, value='IPulse_LI', font=('Segoe UI', 10))
        self.IPulse_LI_radiobutton.grid(
            column=2, row=6, padx=(5, 0), sticky='W')

        # Set default value to CW L-I-V
        self.selectedMeasurement.set('CW_LIV')

        # Open measurement button
        self.measure_button = Button(self.master, text='Open Measurement',
                                     command=self.open_measurement_window, font=('Segoe UI', 10))
        self.measure_button.grid(column=2, row=7, padx=(
            10, 20), pady=(5, 10), sticky='W')

    def open_measurement_window(self):
        top = Toplevel(root)
        if 'CW_LIV' == self.selectedMeasurement.get():
            CWLIV_gui = CW_LIV(top)
        elif 'CW_IV' == self.selectedMeasurement.get():
            CWIV_gui = CW_IV(top)
        elif 'CW_LI' == self.selectedMeasurement.get():
            CWLI_gui = CW_LI(top)
        elif 'VPulse_LIV' == self.selectedMeasurement.get():
            VPulseLIV_gui = VPulse_LIV(top)
        elif 'VPulse_IV' == self.selectedMeasurement.get():
            VPulseIV_gui = VPulse_IV(top)
        elif 'VPulse_LI' == self.selectedMeasurement.get():
            VPulseLI_gui = VPulse_LI(top)
        elif 'IPulse_LIV' == self.selectedMeasurement.get():
            IPulseLIV_gui = IPulse_LIV(top)
        elif 'IPulse_VI' == self.selectedMeasurement.get():
            IPulseIV_gui = IPulse_VI(top)
        elif 'IPulse_LI' == self.selectedMeasurement.get():
            IPulseLI_gui = IPulse_LI(top)

class CW_LIV():

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('CW Measurement: L-I-V')

        # Plot frame
        self.plotFrame = LabelFrame(self.master, text='Plot', padx=5, pady=5)
        # Display plot frame
        self.plotFrame.grid(column=0, row=0, rowspan=2)

        self.fig = Figure(figsize=(5, 5), dpi=100)

        y = 0

        self.plot1 = self.fig.add_subplot(111)
        self.plot1.plot(y)

        self.figCanv = FigureCanvasTkAgg(self.fig, master=self.plotFrame)
        self.figCanv.draw()
        self.figCanv.get_tk_widget().grid(column=0, row=0)

class CW_IV():

    """
    Function referenced when: "Start" button is pushed
    Description: Runs an IV sweep using the various input parameters in the main application window
    such as: start voltage, stop voltage, step size, etc.
    """

    def start_iv_sweep(self):
        # Connect to Keithley Source Meter
        self.keithley = rm.open_resource(self.keithley1_addr.get())

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
        name = self.file_name_entry.get()
        filepath = os.path.join(txtDir + '/' + name + '.txt')
        fd = open(filepath, 'w+')
        i = 1

        for i in range(0, len(self.voltage_array)):
            # --------IV file----------
            fd.write(str(round(self.voltage_array[i], 5)) + ' ')
            fd.write(str(self.current[i]))
            fd.writelines('\n')

        fd.close()

        self.generate_graph()

    """
    Function referenced when: The IV sweep has concluded
    Description: The results of the IV sweep will be displayed as a tk widget in the application
    window, and also saved to the user's defined plot directory
    """

    def generate_graph(self):

        if self.figCanv:
            self.figCanv.get_tk_widget().destroy()

        fig1, ax1 = plt.subplots()
        ax1.set_xlabel('Voltage (V)')
        ax1.set_ylabel('Current (A)')
        ax1.set_title('CW I-V', loc='center')
        ax1.set_title(self.file_name_entry.get(), loc='right')

        ax1.plot(self.voltage_array, self.current, '-o')
        # Adjust plot to eliminate Y-axis label cutoff
        plt.gcf().subplots_adjust(left=0.15)
        self.fig = fig1

        self.figCanv = FigureCanvasTkAgg(self.fig, master=self.plotFrame)
        self.figCanv.draw()
        self.figCanv.get_tk_widget().grid(column=0, row=0)

        plotPath = self.plot_dir_entry.get() + '/' + self.file_name_entry.get()

        fig1.savefig(plotPath)

    """
    Function referenced when: setting voltage within the start_iv_sweep function
    Description: Connect to the Keithley, provide what voltage should be set
    read the corresponding current
    """

    def set_voltage(self, voltage):
        keithley = rm.open_resource(self.keithley1_addr.get())
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
    Description: Creates the base geometry and all widgets on the top level
    of the application window
    """

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('CW Measurement: I-V')

        # Plot frame
        self.plotFrame = LabelFrame(self.master, text='Plot', padx=5, pady=5)
        # Display plot frame
        self.plotFrame.grid(column=0, row=0, rowspan=2,
                            padx=(5, 0), pady=(0, 5))

        self.fig = Figure(figsize=(5, 5), dpi=100)

        y = 0

        self.plot1 = self.fig.add_subplot(111)
        self.plot1.plot(y)

        self.figCanv = FigureCanvasTkAgg(self.fig, master=self.plotFrame)
        self.figCanv.draw()
        self.figCanv.get_tk_widget().grid(column=0, row=0)

        # Sweep settings frame
        self.setFrame = LabelFrame(self.master, text='Sweep Settings')
        # Display settings frame
        self.setFrame.grid(column=1, row=0, sticky='W', padx=(10, 5))

        # Create plot directory label, button, and entry box
        # Plot File Label
        self.plot_dir_label = Label(self.setFrame, text='Plot file directory:')
        self.plot_dir_label.grid(column=1, row=0, sticky='W', columnspan=2)
        # Plot directory Entry Box
        self.plot_dir_entry = Entry(self.setFrame, width=30)
        self.plot_dir_entry.grid(column=1, row=1, padx=(3, 0), columnspan=2)
        # Browse button
        self.plot_dir_file = Button(
            self.setFrame, text='Browse', command=self.browse_plot_file)
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
            self.setFrame, text='Browse', command=self.browse_txt_file)
        self.txt_dir_file.grid(column=3, row=3, ipadx=5)

        # Create label for file name entry box
        self.file_name_label = Label(self.setFrame, text='File name:')
        self.file_name_label.grid(column=1, row=4, sticky='W', columnspan=2)
        # File name entry box
        self.file_name_entry = Entry(self.setFrame, width=30)
        self.file_name_entry.grid(
            column=1, row=5, sticky='W', padx=(3, 0), columnspan=3)

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
        # # Stop Button
        # self.stop_button = Button(
        #     self.setFrame, text='Stop', state=DISABLED, command=self.stop_pressed)
        # self.stop_button.grid(column=3, row=11, ipadx=10, pady=5)

        # Device settings frame
        self.devFrame = LabelFrame(self.master, text='Device Settings')
        # Display device settings frame
        self.devFrame.grid(column=1, row=1, sticky='W', padx=(10, 5))

        self.keithley1_label = Label(self.devFrame, text='Keithley 1 Address')
        self.keithley1_label.grid(column=0, row=0, sticky='W')

        self.keithley1_addr = Entry(self.devFrame)
        self.keithley1_addr.grid(column=0, row=1, padx=5, sticky='W')

        self.keithley2_label = Label(self.devFrame, text='Keithley 2 Address')
        self.keithley2_label.grid(column=0, row=2, sticky='W')
        self.keithley2_addr = Entry(self.devFrame)
        self.keithley2_addr.grid(column=0, row=3, padx=5, sticky='W')

        self.tec_label = Label(
            self.devFrame, text='Temperature Controller Address')
        self.tec_label.grid(column=0, row=4)
        self.tec_addr = Entry(self.devFrame)
        self.tec_addr.grid(column=0, row=5, padx=5, pady=(0, 5), sticky='W')

        # Default values
        self.keithley1_addr.insert(0, 'GPIB0::1::INSTR')
        self.keithley2_addr.insert(0, 'GPIB0::2::INSTR')
        self.tec_addr.insert(0, 'ASRL3::INSTR')

class CW_LI():

    """
    Function referenced when: "Start" button is pushed
    Description: Runs an LI sweep using the various input parameters in the main application window
    such as: start current, stop current, step size, etc.
    """

    def start_li_cw(self):
        # Connect to Keithley for applying CW current
        self.keithleySource = rm.open_resource(self.keithleyS_addr.get())

        # # Enable stop button
        # self.stop_button.config(state=NORMAL)

        # Reset GPIB defaults
        self.keithleySource.write("*rst; status:preset; *cls")
        # Select source function mode as current source
        self.keithleySource.write("sour:func curr")
        # Set source level to 0A
        self.keithleySource.write("sour:curr 0")
        # Set sensor to voltage
        self.keithleySource.write("sens:func 'volt'")
        # Set voltage compliance
        compliance = float(self.compliance_entry.get())/1000
        self.keithleySource.write("sens:volt:prot:lev " + str(compliance))
        # Set voltage measure range to auto
        self.keithleySource.write("sens:volt:range:auto on ")

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
        self.voltage = zeros(len(self.current_array), float)
        # Loop number of points
        for i in range(0, len(self.current_array)):
            a = self.set_current(round(self.current_array[i], 3))
            # Delay time between sweeping
            sleep(0.1)
            # --------source-------
            b1 = eval(self.keithleySource.query("read?"))
            self.voltage[i] = b1

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
            # --------IV file----------
            fd.write(str(round(self.current_array[i], 5)) + ' ')
            fd.write(str(self.voltage[i]))
            fd.writelines('\n')

        fd.close()

        self.generate_graph()
    """
    Function referenced when: The LI sweep has concluded
    Description: The results of the LI sweep will be displayed as a tk widget in the application
    window, and also saved to the user's defined plot directory
    """

    def generate_graph(self):

        if self.figCanv:
            self.figCanv.get_tk_widget().destroy()

        fig1, ax1 = plt.subplots()
        ax1.set_xlabel('I (A)')
        ax1.set_ylabel('L (mW)')
        ax1.set_title('CW L-I', loc='center')
        ax1.set_title(self.file_name_entry.get(), loc='right')

        ax1.plot(self.current_array, self.voltage, '-o')
        # Adjust plot to eliminate Y-axis label cutoff
        plt.gcf().subplots_adjust(left=0.15)
        self.fig = fig1

        self.figCanv = FigureCanvasTkAgg(self.fig, master=self.plotFrame)
        self.figCanv.draw()
        self.figCanv.get_tk_widget().grid(column=0, row=0)

        plotPath = self.plot_dir_entry.get() + '/' + self.file_name_entry.get()

        fig1.savefig(plotPath)

    """
    Function referenced when: Setting current within the start_li_sweep function
    Description: Connect to the Keithley, set the current to the value
    passed into the function.
    """

    def set_current(self, current):
        keithley = rm.open_resource(self.keithleyS_addr.get())
        keithley.delay = 0.1    # Necessary for GPIB connection?
        keithley.write("sour:func curr")
        keithley.write("sens:volt:rang:auto on")
        keithley.write("sens:func 'volt'")
        keithley.write("form:elem volt")
        keithley.write("outp on")
        keithley.write("sour:curr:lev " + str(current))
        # For L-I not reading the voltage
        volt = keithley.query('READ?')

        return volt

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
    Description: Creates the base geometry and all widgets on the top level
    of the application window
    """

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('CW Measurement: L-I')

        # Plot frame
        self.plotFrame = LabelFrame(self.master, text='Plot', padx=5, pady=5)
        # Display plot frame
        self.plotFrame.grid(column=0, row=0, rowspan=2)

        self.fig = Figure(figsize=(5, 5), dpi=100)

        y = 0

        self.plot1 = self.fig.add_subplot(111)
        self.plot1.plot(y)

        self.figCanv = FigureCanvasTkAgg(self.fig, master=self.plotFrame)
        self.figCanv.draw()
        self.figCanv.get_tk_widget().grid(column=0, row=0)

        # Sweep settings frame
        self.setFrame = LabelFrame(self.master, text='Sweep Settings')
        # Display settings frame
        self.setFrame.grid(column=1, row=0, sticky='W', padx=(10, 5))

        # Create plot directory label, button, and entry box
        # Plot File Label
        self.plot_dir_label = Label(self.setFrame, text='Plot file directory:')
        self.plot_dir_label.grid(column=1, row=0, sticky='W', columnspan=2)
        # Plot directory Entry Box
        self.plot_dir_entry = Entry(self.setFrame, width=30)
        self.plot_dir_entry.grid(column=1, row=1, padx=(3, 0), columnspan=2)
        # Browse button
        self.plot_dir_file = Button(
            self.setFrame, text='Browse', command=self.browse_plot_file)
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
            self.setFrame, text='Browse', command=self.browse_txt_file)
        self.txt_dir_file.grid(column=3, row=3, ipadx=5)

        # Create label for file name entry box
        self.file_name_label = Label(self.setFrame, text='File name:')
        self.file_name_label.grid(column=1, row=4, sticky='W', columnspan=2)
        # File name entry box
        self.file_name_entry = Entry(self.setFrame, width=30)
        self.file_name_entry.grid(
            column=1, row=5, sticky='W', padx=(3, 0), columnspan=3)

        # Step size label
        self.step_size_label = Label(self.setFrame, text='Step size (mA)')
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
        self.compliance_label = Label(self.setFrame, text='Compliance (mV)')
        self.compliance_label.grid(column=3, row=6, columnspan=2)
        # Compliance entry box
        self.compliance_entry = Entry(self.setFrame, width=5)
        self.compliance_entry.grid(column=3, row=7, columnspan=2)

        # Start current label
        self.start_current_label = Label(self.setFrame, text='Start (A)')
        self.start_current_label.grid(column=1, row=8)
        # Start current entry box
        self.start_current_entry = Entry(self.setFrame, width=5)
        self.start_current_entry.grid(column=1, row=9)

        # Stop current label
        self.stop_current_label = Label(self.setFrame, text='Stop (A)')
        self.stop_current_label.grid(column=2, row=8)
        # Stop current entry box
        self.stop_current_entry = Entry(self.setFrame, width=5)
        self.stop_current_entry.grid(column=2, row=9)

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
        # # Stop Button
        # self.stop_button = Button(
        #     self.setFrame, text='Stop', state=DISABLED, command=self.stop_pressed)
        # self.stop_button.grid(column=3, row=11, ipadx=10, pady=5)

        # Device settings frame
        self.devFrame = LabelFrame(self.master, text='Device Settings')
        # Display device settings frame
        self.devFrame.grid(column=1, row=1, sticky='W', padx=(10, 5), ipady=3)

        self.keithleyS_label = Label(
            self.devFrame, text='Keithley Source Address')
        self.keithleyS_label.grid(column=0, row=0, sticky='W')

        self.keithleyS_addr = Entry(self.devFrame)
        self.keithleyS_addr.grid(column=0, row=1, padx=5, sticky='W')

        self.keithleyM_label = Label(
            self.devFrame, text='Keithley Measurement Address')
        self.keithleyM_label.grid(column=0, row=2, sticky='W')
        self.keithleyM_addr = Entry(self.devFrame)
        self.keithleyM_addr.grid(column=0, row=3, padx=5, sticky='W')

        # Default values
        self.keithleyS_addr.insert(0, 'GPIB0::1::INSTR')
        self.keithleyM_addr.insert(0, 'GPIB0::2::INSTR')

class VPulse_LIV():

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('Pulse Measurement: L-I-V')

        # Plot frame
        self.plotFrame = LabelFrame(self.master, text='Plot', padx=5, pady=5)
        # Display plot frame
        self.plotFrame.grid(column=0, row=0, rowspan=2)

        self.fig = Figure(figsize=(5, 5), dpi=100)

        y = 0

        self.plot1 = self.fig.add_subplot(111)
        self.plot1.plot(y)

        self.figCanv = FigureCanvasTkAgg(self.fig, master=self.plotFrame)
        self.figCanv.draw()
        self.figCanv.get_tk_widget().grid(column=0, row=0)

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
        self.scope.write(":CHANnel%d:IMPedance FIFTy" %
                         self.current_channel.get())
        self.scope.write(":CHANnel%d:IMPedance FIFTy" %
                         self.voltage_channel.get())
        # self.scope.write(":AUToscale")
        self.scope.write(":TIMebase:RANGe 2E-6")
        self.scope.write(":TRIGger:MODE GLITch")
        self.scope.write(":TRIGger:GLITch:SOURce CHANnel%d" %
                         self.current_channel.get())
        self.scope.write(":TRIGger:GLITch:QUALifier RANGe")

        # Define glitch trigger range as: [75% of PW, 125% of PW]
        glitchTriggerLower = float(self.pulse_width_entry.get())*0.75
        glitchTriggerUpper = float(self.pulse_width_entry.get())*1.25

        self.scope.write(":TRIGger:GLITch:RANGe %.6fus,%.6fus" %(glitchTriggerLower,glitchTriggerUpper))

        # Set initial trigger point to 1 mV
        self.scope.write("TRIGger:GLITch:LEVel 1E-3")

        # Channel scales - set each channel to 1mV/div to start
        vertScaleCurrent = 0.001
        vertScaleVoltage = 0.001

        self.scope.write(":CHANNEL%d:SCALe %.3f" %
                         (self.current_channel.get(), vertScaleCurrent))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.current_channel.get())
        self.scope.write(":CHANNEL%d:SCALe %.3f" %
                         (self.voltage_channel.get(), vertScaleVoltage))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.voltage_channel.get())

        # Move each signal down two divisions for a better view on the screen
        self.scope.write(":CHANnel%d:OFFset %.3fV" %
                         (self.current_channel.get(), 2*vertScaleCurrent))
        self.scope.write(":CHANnel%d:OFFset %.3fV" %
                         (self.voltage_channel.get(), 2*vertScaleVoltage))

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
        voltageRangeStop = float(
            self.stop_voltage_entry.get()) + float(self.step_size_entry.get())/1000
        voltageRangeStep = float(self.step_size_entry.get())/1000

        voltageSourceValues = np.arange(
            voltageRangeStart, voltageRangeStop, voltageRangeStep)

        # Lists for data values
        currentData = list()  # To be plotted on y-axis
        voltageData = list()  # To be plotted on x-axis

        i = 1

        voltageData.append(0)
        currentData.append(0)

        for V_s in voltageSourceValues:

            # Handle glitch issues
            if (V_s > 7 and V_s < 7.5) or (V_s > 21.3 and V_s < 21.9) or (V_s > 68 and V_s < 68.5):
                self.pulser.write("OUTPut OFF")
                self.pulser.write("VOLT %.3f" % V_s)
                sleep(1)
            else:
                self.pulser.write("VOLT %.3f" % (V_s))
                self.pulser.write("OUTPut ON")
                sleep(0.1)
                # Read current amplitude from oscilloscope; multiply by 2 to use 50-ohms channel
                current_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                prev_current_amplitude = current_ampl_osc
                # Read photodetector output
                voltage_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
                prev_voltage_amplitude = voltage_ampl_osc
                # Adjust vertical scales if measured amplitude reaches top of screen (99% of display)
                if (current_ampl_osc > 0.99*totalDisplayCurrent):
                    vertScaleCurrent = self.incrOscVertScale(vertScaleCurrent)
                    totalDisplayCurrent = 6*vertScaleCurrent
                    self.scope.write(":CHANNEL%d:SCALe %.3f" % (
                        self.current_channel.get(), float(vertScaleCurrent)))
                    current_ampl_osc = self.scope.query_ascii_values(
                        "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                    voltage_ampl_osc = self.scope.query_ascii_values(
                        "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
                    sleep(0.75)
                if (voltage_ampl_osc > 0.99*totalDisplayVoltage):
                    vertScaleVoltage = self.incrOscVertScale(vertScaleVoltage)
                    totalDisplayVoltage = 6*vertScaleVoltage
                    self.scope.write(":CHANNEL%d:SCALe %.3f" % (
                        self.voltage_channel.get(), float(vertScaleVoltage)))
                    current_ampl_osc = self.scope.query_ascii_values(
                        "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                    voltage_ampl_osc = self.scope.query_ascii_values(
                        "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
                    sleep(0.75)
                # Update trigger cursor to half of measured current amplitude
                self.updateTriggerCursor(
                    current_ampl_osc, self.scope, vertScaleCurrent)
                R_S = 50.0  # AVTECH pulser source resistance
                current_ampl_device = 2*current_ampl_osc
                voltage_ampl_device = voltage_ampl_osc

                voltageData.append(voltage_ampl_device)
                currentData.append(current_ampl_device)

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

    def updateTriggerCursor(self, pulseAmplitude, scope, presentScale):
        new_trigger = 3*pulseAmplitude/4.0
        if (new_trigger < presentScale):
            new_trigger = presentScale
        scope.write(":TRIGger:GLITch:LEVel %.6f" % (new_trigger))

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
        self.pulse_width_label = Label(
            self.pulseFrame, text='Pulse Width (μs)')
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

class VPulse_LI():

    def start_li_pulse(self):
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
                         self.light_channel.get())
        # self.scope.write(":AUToscale")
        self.scope.write(":TIMebase:RANGe 2E-6")
        self.scope.write(":TRIGger:MODE GLITch")
        self.scope.write(":TRIGger:GLITch:SOURce CHANnel%d" %
                         self.current_channel.get())
        self.scope.write(":TRIGger:GLITch:QUALifier RANGe")

        # Define glitch trigger range as: [75% of PW, 125% of PW]
        glitchTriggerLower = float(self.pulse_width_entry.get())*0.75
        glitchTriggerUpper = float(self.pulse_width_entry.get())*1.25

        self.scope.write(":TRIGger:GLITch:RANGe %.6fus,%.6fus" %(glitchTriggerLower,glitchTriggerUpper))

        # Set initial trigger point to 1 mV
        self.scope.write("TRIGger:GLITch:LEVel 1E-3")

        # Channel scales - set each channel to 1mV/div to start
        vertScaleCurrent = 0.001
        vertScaleVoltage = 0.001

        self.scope.write(":CHANNEL%d:SCALe %.3f" %
                         (self.current_channel.get(), vertScaleCurrent))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.current_channel.get())
        self.scope.write(":CHANNEL%d:SCALe %.3f" %
                         (self.light_channel.get(), vertScaleVoltage))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.light_channel.get())

        # Move each signal down two divisions for a better view on the screen
        self.scope.write(":CHANnel%d:OFFset %.3fV" %
                         (self.current_channel.get(), 2*vertScaleCurrent))
        self.scope.write(":CHANnel%d:OFFset %.3fV" %
                         (self.light_channel.get(), 2*vertScaleVoltage))

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
        voltageRangeStop = float(
            self.stop_voltage_entry.get()) + float(self.step_size_entry.get())/1000
        voltageRangeStep = float(self.step_size_entry.get())/1000

        voltageSourceValues = np.arange(
            voltageRangeStart, voltageRangeStop, voltageRangeStep)

        # Lists for data values
        currentData = list()  # To be plotted on y-axis
        voltageData = list()  # To be plotted on x-axis

        i = 1

        voltageData.append(0)
        currentData.append(0)

        for V_s in voltageSourceValues:

            # Handle glitch issues
            if (V_s > 7 and V_s < 7.5) or (V_s > 21.3 and V_s < 21.9) or (V_s > 68 and V_s < 68.5):
                self.pulser.write("OUTPut OFF")
                self.pulser.write("VOLT %.3f" % V_s)
                sleep(1)
            else:
                self.pulser.write("VOLT %.3f" % (V_s))
                self.pulser.write("OUTPut ON")
                sleep(0.1)
                # Read current amplitude from oscilloscope; multiply by 2 to use 50-ohms channel
                current_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                prev_current_amplitude = current_ampl_osc
                # Read photodetector output
                voltage_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.light_channel.get())[0]
                prev_voltage_amplitude = voltage_ampl_osc
                # Adjust vertical scales if measured amplitude reaches top of screen (99% of display)
                if (current_ampl_osc > 0.99*totalDisplayCurrent):
                    vertScaleCurrent = self.incrOscVertScale(vertScaleCurrent)
                    totalDisplayCurrent = 6*vertScaleCurrent
                    self.scope.write(":CHANNEL%d:SCALe %.3f" % (
                        self.current_channel.get(), float(vertScaleCurrent)))
                    current_ampl_osc = self.scope.query_ascii_values(
                        "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                    voltage_ampl_osc = self.scope.query_ascii_values(
                        "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.light_channel.get())[0]
                    sleep(0.75)
                if (voltage_ampl_osc > 0.99*totalDisplayVoltage):
                    vertScaleVoltage = self.incrOscVertScale(vertScaleVoltage)
                    totalDisplayVoltage = 6*vertScaleVoltage
                    self.scope.write(":CHANNEL%d:SCALe %.3f" % (
                        self.light_channel.get(), float(vertScaleVoltage)))
                    current_ampl_osc = self.scope.query_ascii_values(
                        "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                    voltage_ampl_osc = self.scope.query_ascii_values(
                        "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.light_channel.get())[0]
                    sleep(0.75)
                # Update trigger cursor to half of measured current amplitude
                self.updateTriggerCursor(
                    current_ampl_osc, self.scope, vertScaleCurrent)
                R_S = 50.0  # AVTECH pulser source resistance
                current_ampl_device = 2*current_ampl_osc
                voltage_ampl_device = voltage_ampl_osc

                voltageData.append(voltage_ampl_device)
                currentData.append(current_ampl_device)

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
        f.writelines('Current (mA), Light Output\n')
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
        ax1.set_ylabel('Measured device light output')
        ax1.plot(currentData, voltageData, color='blue',
                 label='L-I Characteristic')
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

    def updateTriggerCursor(self, pulseAmplitude, scope, presentScale):
        new_trigger = 3*pulseAmplitude/4.0
        if (new_trigger < presentScale):
            new_trigger = presentScale
        scope.write(":TRIGger:GLITch:LEVel %.6f" % (new_trigger))

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
        self.master.title('Voltage Pulse Measurement: L-I')

        # # Plot frame
        # self.plotFrame = LabelFrame(self.master, text='Plot', padx=5, pady=5)
        # # Display plot frame
        # self.plotFrame.grid(column=0, row=0, rowspan=2)

        # self.fig = Figure(figsize=(5, 5), dpi=100)

        # y = 0

        # self.plot1 = self.fig.add_subplot(111)
        # self.plot1.plot(y)

        # self.figCanv = FigureCanvasTkAgg(self.fig, master=self.plotFrame)
        # self.figCanv.draw()
        # self.figCanv.get_tk_widget().grid(column=0, row=0)

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
        self.pulse_width_label = Label(
            self.pulseFrame, text='Pulse Width (μs)')
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
            self.master, text='Start', command=self.start_li_pulse)
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
        self.light_channel = IntVar()

        # Set current channel to 1
        self.current_channel.set(1)
        # Set light channel to 2
        self.light_channel.set(2)

        # Current measurement channel label
        self.curr_channel_label = Label(self.devFrame, text='Current Channel')
        self.curr_channel_label.grid(column=0, row=4)
        # Current measurement channel dropdown
        self.curr_channel_dropdown = OptionMenu(
            self.devFrame, self.current_channel, *channels)
        self.curr_channel_dropdown.grid(column=0, row=5)

        # Light measurement channel label
        self.light_channel_label = Label(self.devFrame, text='Light Channel')
        self.light_channel_label.grid(column=1, row=4)
        # Light measurement channel dropdown
        self.light_channel_dropdown = OptionMenu(
            self.devFrame, self.light_channel, *channels)
        self.light_channel_dropdown.grid(column=1, row=5)

class IPulse_LIV():

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('Pulse Measurement: L-I-V')

        # Plot frame
        self.plotFrame = LabelFrame(self.master, text='Plot', padx=5, pady=5)
        # Display plot frame
        self.plotFrame.grid(column=0, row=0, rowspan=2)

        self.fig = Figure(figsize=(5, 5), dpi=100)

        y = 0

        self.plot1 = self.fig.add_subplot(111)
        self.plot1.plot(y)

        self.figCanv = FigureCanvasTkAgg(self.fig, master=self.plotFrame)
        self.figCanv.draw()
        self.figCanv.get_tk_widget().grid(column=0, row=0)

class IPulse_VI():

    def start_vi_pulse(self):
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
        # self.scope.write(":AUToscale")
        self.scope.write(":TIMebase:RANGe 2E-6")
        self.scope.write(":TRIGger:MODE GLITch")
        self.scope.write(":TRIGger:GLITch:SOURce CHANnel%d" %
                         self.current_channel.get())
        self.scope.write(":TRIGger:GLITch:QUALifier RANGe")

        # Define glitch trigger range as: [75% of PW, 125% of PW]
        glitchTriggerLower = float(self.pulse_width_entry.get())*0.75
        glitchTriggerUpper = float(self.pulse_width_entry.get())*1.25

        self.scope.write(":TRIGger:GLITch:RANGe %.6fus,%.6fus" %(glitchTriggerLower,glitchTriggerUpper))

        # Set initial trigger point to 1 mV
        self.scope.write("TRIGger:GLITch:LEVel 1E-3")

        # Channel scales - set each channel to 1mV/div to start
        vertScaleCurrent = 0.001
        vertScaleVoltage = 0.001

        self.scope.write(":CHANNEL%d:SCALe %.3f" %
                         (self.current_channel.get(), vertScaleCurrent))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.current_channel.get())
        self.scope.write(":CHANNEL%d:SCALe %.3f" %
                         (self.voltage_channel.get(), vertScaleVoltage))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.voltage_channel.get())

        # Move each signal down two divisions for a better view on the screen
        self.scope.write(":CHANnel%d:OFFset %.3fV" %
                         (self.current_channel.get(), 2*vertScaleCurrent))
        self.scope.write(":CHANnel%d:OFFset %.3fV" %
                         (self.voltage_channel.get(), 2*vertScaleVoltage))

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

        i = 1

        voltageData.append(0)
        currentData.append(0)

        for I_s in currentSourceValues:

            self.pulser.write(":LDI %.3f" % (I_s))
            self.pulser.write("OUTPut ON")
            sleep(0.1)
            # Read current amplitude from oscilloscope; multiply by 2 to use 50-ohms channel
            current_ampl_osc = self.scope.query_ascii_values(
                "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]

            # Read photodetector output
            voltage_ampl_osc = self.scope.query_ascii_values(
                "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]

            # Adjust vertical scales if measured amplitude reaches top of screen (99% of display)
            if (current_ampl_osc > 0.99*totalDisplayCurrent):
                vertScaleCurrent = self.incrOscVertScale(vertScaleCurrent)
                totalDisplayCurrent = 6*vertScaleCurrent
                self.scope.write(":CHANNEL%d:SCALe %.3f" % (
                    self.current_channel.get(), float(vertScaleCurrent)))
                current_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                voltage_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
                sleep(0.75)
                
            if (voltage_ampl_osc > 0.99*totalDisplayVoltage):
                vertScaleVoltage = self.incrOscVertScale(vertScaleVoltage)
                totalDisplayVoltage = 6*vertScaleVoltage
                self.scope.write(":CHANNEL%d:SCALe %.3f" % (
                    self.voltage_channel.get(), float(vertScaleVoltage)))
                current_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                voltage_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.voltage_channel.get())[0]
                sleep(0.75)

            # Update trigger cursor to half of measured current amplitude
            self.updateTriggerCursor(
                current_ampl_osc, self.scope, vertScaleCurrent)

            R_S = 50.0  # AVTECH pulser source resistance

            current_ampl_device = 2*current_ampl_osc
            voltage_ampl_device = voltage_ampl_osc

            voltageData.append(voltage_ampl_device)
            currentData.append(current_ampl_device)

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
                 label='Current Pulsed V-I Characteristic')
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

    def updateTriggerCursor(self, pulseAmplitude, scope, presentScale):
        new_trigger = 3*pulseAmplitude/4.0
        if (new_trigger < presentScale):
            new_trigger = presentScale
        scope.write(":TRIGger:GLITch:LEVel %.6f" % (new_trigger))

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
        self.master.title('Current Pulsed Measurement: V-I')

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
            self.pulseFrame, text='Pulse Width (μs)')
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

        # Start Button
        self.start_button = Button(
            self.master, text='Start', command=self.start_vi_pulse)
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

        # Set current channel to 1
        self.current_channel.set(1)
        # Set light channel to 2
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

class IPulse_LI():

    def start_li_pulse(self):
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
                         self.light_channel.get())
        # self.scope.write(":AUToscale")
        self.scope.write(":TIMebase:RANGe 2E-6")
        self.scope.write(":TRIGger:MODE GLITch")
        self.scope.write(":TRIGger:GLITch:SOURce CHANnel%d" %
                         self.current_channel.get())
        self.scope.write(":TRIGger:GLITch:QUALifier RANGe")

        # Define glitch trigger range as: [75% of PW, 125% of PW]
        glitchTriggerLower = float(self.pulse_width_entry.get())*0.75
        glitchTriggerUpper = float(self.pulse_width_entry.get())*1.25

        self.scope.write(":TRIGger:GLITch:RANGe %.6fus,%.6fus" %(glitchTriggerLower,glitchTriggerUpper))

        # Set initial trigger point to 1 mV
        self.scope.write("TRIGger:GLITch:LEVel 1E-3")

        # Channel scales - set each channel to 1mV/div to start
        vertScaleCurrent = 0.001
        vertScaleVoltage = 0.001

        self.scope.write(":CHANNEL%d:SCALe %.3f" %
                         (self.current_channel.get(), vertScaleCurrent))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.current_channel.get())
        self.scope.write(":CHANNEL%d:SCALe %.3f" %
                         (self.light_channel.get(), vertScaleVoltage))
        self.scope.write(":CHANnel%d:DISPlay ON" % self.light_channel.get())

        # Move each signal down two divisions for a better view on the screen
        self.scope.write(":CHANnel%d:OFFset %.3fV" %
                         (self.current_channel.get(), 2*vertScaleCurrent))
        self.scope.write(":CHANnel%d:OFFset %.3fV" %
                         (self.light_channel.get(), 2*vertScaleVoltage))

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

        i = 1

        voltageData.append(0)
        currentData.append(0)

        for I_s in currentSourceValues:

            self.pulser.write(":LDI %.3f" % (I_s))
            self.pulser.write("OUTPut ON")
            sleep(0.1)
            # Read current amplitude from oscilloscope; multiply by 2 to use 50-ohms channel
            current_ampl_osc = self.scope.query_ascii_values(
                "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]

            # Read photodetector output
            voltage_ampl_osc = self.scope.query_ascii_values(
                "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.light_channel.get())[0]

            # Adjust vertical scales if measured amplitude reaches top of screen (99% of display)
            if (current_ampl_osc > 0.99*totalDisplayCurrent):
                vertScaleCurrent = self.incrOscVertScale(vertScaleCurrent)
                totalDisplayCurrent = 6*vertScaleCurrent
                self.scope.write(":CHANNEL%d:SCALe %.3f" % (
                    self.current_channel.get(), float(vertScaleCurrent)))
                current_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                voltage_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.light_channel.get())[0]
                sleep(0.75)
                
            if (voltage_ampl_osc > 0.99*totalDisplayVoltage):
                vertScaleVoltage = self.incrOscVertScale(vertScaleVoltage)
                totalDisplayVoltage = 6*vertScaleVoltage
                self.scope.write(":CHANNEL%d:SCALe %.3f" % (
                    self.light_channel.get(), float(vertScaleVoltage)))
                current_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.current_channel.get())[0]
                voltage_ampl_osc = self.scope.query_ascii_values(
                    "SINGLE;*OPC;:MEASure:VAMPlitude? CHANNEL%d" % self.light_channel.get())[0]
                sleep(0.75)

            # Update trigger cursor to half of measured current amplitude
            self.updateTriggerCursor(
                current_ampl_osc, self.scope, vertScaleCurrent)

            R_S = 50.0  # AVTECH pulser source resistance

            current_ampl_device = 2*current_ampl_osc
            voltage_ampl_device = voltage_ampl_osc

            voltageData.append(voltage_ampl_device)
            currentData.append(current_ampl_device)

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
        f.writelines('Current (mA), Light Output\n')
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
        ax1.set_ylabel('Measured device light output')
        ax1.plot(currentData, voltageData, color='blue',
                 label='Current Pulsed L-I Characteristic')
        ax1.text(0, 1,'Current Pulsed\nPulse Width: ' + self.pulse_width_entry.get())
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

    def updateTriggerCursor(self, pulseAmplitude, scope, presentScale):
        new_trigger = 3*pulseAmplitude/4.0
        if (new_trigger < presentScale):
            new_trigger = presentScale
        scope.write(":TRIGger:GLITch:LEVel %.6f" % (new_trigger))

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
        self.master.title('Current Pulsed Measurement: L-I')

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
            self.pulseFrame, text='Pulse Width (μs)')
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

        # Start Button
        self.start_button = Button(
            self.master, text='Start', command=self.start_li_pulse)
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
        self.light_channel = IntVar()

        # Set current channel to 1
        self.current_channel.set(1)
        # Set light channel to 2
        self.light_channel.set(2)

        # Current measurement channel label
        self.curr_channel_label = Label(self.devFrame, text='Current Channel')
        self.curr_channel_label.grid(column=0, row=4)
        # Current measurement channel dropdown
        self.curr_channel_dropdown = OptionMenu(
            self.devFrame, self.current_channel, *channels)
        self.curr_channel_dropdown.grid(column=0, row=5)

        # Light measurement channel label
        self.light_channel_label = Label(self.devFrame, text='Light Channel')
        self.light_channel_label.grid(column=1, row=4)
        # Light measurement channel dropdown
        self.light_channel_dropdown = OptionMenu(
            self.devFrame, self.light_channel, *channels)
        self.light_channel_dropdown.grid(column=1, row=5)

# On closing, ensure outputs are turned off
def on_closing():
    if messagebox.askokcancel('Quit', 'Do you want to quit?'):
        root.destroy()


root = tk.Tk()
Selection_GUI = MeasSelect(root)
root.protocol('WM_DELETE_WINDOW', on_closing)
root.mainloop()
