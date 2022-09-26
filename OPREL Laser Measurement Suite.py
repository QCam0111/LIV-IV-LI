import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from numpy import append, zeros, arange, logspace, flip, log10
import os
import pyvisa
# For use when interacting with the temperature controller or oscilloscope
# from pyvisa.constants import Parity, StopBits, VI_ASRL_FLOW_NONE
import Tkinter as tk
from Tkinter import Label, Entry, Button, Radiobutton, LabelFrame, Toplevel, OptionMenu, StringVar, IntVar, END, DISABLED, NORMAL
import tkMessageBox as messagebox
import tkFileDialog as FileDialog
from time import sleep

rm = pyvisa.ResourceManager()

class MeasSelect():
    
    def __init__(self, parent):
        self.master = parent

        # Assign window title
        self.master.title('Measurement Selection')

        # Create selection buttons
        self.radiobutton_var = StringVar()

        # Pulsed button selections
        self.pulseLIV_radiobutton = Radiobutton(self.master, text='Pulsed L-I-V', variable=self.radiobutton_var,value='Pulse_LIV')
        self.pulseLIV_radiobutton.grid(column=0, row=0,sticky='W')
        self.pulseIV_radiobutton = Radiobutton(self.master, text='Pulsed I-V', variable=self.radiobutton_var,value='Pulse_IV')
        self.pulseIV_radiobutton.grid(column=0, row=1,sticky='W')
        self.pulseLI_radiobutton = Radiobutton(self.master, text='Pulsed L-I', variable=self.radiobutton_var,value='Pulse_LI')
        self.pulseLI_radiobutton.grid(column=0, row=2,sticky='W')
        # CW button selections
        self.cwLIV_radiobutton = Radiobutton(self.master, text='CW L-I-V', variable=self.radiobutton_var,value='CW_LIV')
        self.cwLIV_radiobutton.grid(column=1, row=0, padx=(10,0), sticky='W')
        self.cwIV_radiobutton = Radiobutton(self.master, text='CW I-V', variable=self.radiobutton_var,value='CW_IV')
        self.cwIV_radiobutton.grid(column=1, row=1, padx=(10,0), sticky='W')
        self.cwLI_radiobutton = Radiobutton(self.master, text='CW L-I', variable=self.radiobutton_var,value='CW_LI')
        self.cwLI_radiobutton.grid(column=1, row=2, padx=(10,0), sticky='W')
        # Set default value to pulsed L-I-V
        self.radiobutton_var.set('Pulse_LIV')

        # Start measurement button
        self.measure_button = Button(self.master, text='Open Measurement', command=self.open_measure_window)
        self.measure_button.grid(column=2, row=0, rowspan=3, padx=(10,10))

    def open_measure_window(self):
        top = Toplevel(root)
        if 'CW_LIV' == self.radiobutton_var.get():
            CWLIV_gui = LIV_CW(top)
        elif 'CW_IV' == self.radiobutton_var.get():
            CWIV_gui = IV_CW(top)
        elif 'CW_LI' == self.radiobutton_var.get():
            CWLI_gui = LI_CW(top)
        elif 'Pulse_LIV' == self.radiobutton_var.get():
            PulseLIV_gui = LIV_Pulse(top)
        elif 'Pulse_IV' == self.radiobutton_var.get():
            PulseIV_gui = IV_Pulse(top)
        elif 'Pulse_LI' == self.radiobutton_var.get():
            PulseLI_gui = LI_Pulse(top)


class LIV_CW():

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

class IV_CW():

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
            voltage_source_pos = logspace(-4, log10(float(self.stop_voltage_entry.get())), int(self.num_of_pts_entry.get())/2)
            voltage_source_neg = -logspace(log10(abs(float(self.start_voltage_entry.get()))), -4, int(self.num_of_pts_entry.get())/2)
            self.voltage_array = append(voltage_source_neg, voltage_source_pos)
        elif 'Linlog' == self.radiobutton_var.get():
            # Set up Linear voltage array
            stepSize = round(float(self.step_size_entry.get())/1000, 3)
            startV = float(self.start_voltage_entry.get())
            stopV = float(self.stop_voltage_entry.get())

            self.voltage_array = arange(startV, -0.5+stepSize, stepSize)
            voltage_linear_pos = arange(0.5+stepSize, stopV+stepSize, stepSize)

            # Log scale
            voltage_log_pos = logspace(-4, log10(0.5), int(self.num_of_pts_entry.get())/2)
            voltage_log_neg = -logspace(log10(0.5), -4, int(self.num_of_pts_entry.get())/2)

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
        self.plotFrame.grid(column=0, row=0, rowspan=2,padx=(5,0),pady=(0,5))

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

class LI_CW():

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
            current_source_pos = logspace(-4, log10(float(self.stop_current_entry.get())), int(self.num_of_pts_entry.get())/2)
            current_source_neg = -logspace(log10(abs(float(self.start_current_entry.get()))), -4, int(self.num_of_pts_entry.get())/2)
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

        self.keithleyS_label = Label(self.devFrame, text='Keithley Source Address')
        self.keithleyS_label.grid(column=0, row=0, sticky='W')

        self.keithleyS_addr = Entry(self.devFrame)
        self.keithleyS_addr.grid(column=0, row=1, padx=5, sticky='W')

        self.keithleyM_label = Label(self.devFrame, text='Keithley Measurement Address')
        self.keithleyM_label.grid(column=0, row=2, sticky='W')
        self.keithleyM_addr = Entry(self.devFrame)
        self.keithleyM_addr.grid(column=0, row=3, padx=5, sticky='W')

        # Default values
        self.keithleyS_addr.insert(0, 'GPIB0::1::INSTR')
        self.keithleyM_addr.insert(0, 'GPIB0::2::INSTR')

class LIV_Pulse():

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

class IV_Pulse():

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('Pulse Measurement: I-V')

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

class LI_Pulse():

    def start_li_pulse(self):
        print('Start')

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
    of the application window.
    """

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('Pulse Measurement: L-I')

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

        # Pulse settings frame
        self.pulseFrame = LabelFrame(self.master, text='Pulse Settings')
        # Display pulse settings frame
        self.pulseFrame.grid(column=1,row=0, sticky='W', padx=(10,5))

        # Create plot directory label, button, and entry box
        # Plot File Label
        self.plot_dir_label = Label(self.pulseFrame, text='Plot file directory:')
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
        self.txt_dir_label = Label(self.pulseFrame, text='Text file directory:')
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
        self.pulse_width_label = Label(self.pulseFrame, text='Pulse Width (μs)')
        self.pulse_width_label.grid(column=3, row=6)
        # Pulse width entry box
        self.pulse_width_entry = Entry(self.pulseFrame, width=5)
        self.pulse_width_entry.grid(column=3, row=7)

        # Start voltage label
        self.start_voltage_label = Label(self.pulseFrame, text='Start (V)')
        self.start_voltage_label.grid(column=1, row=8)
        # Start voltage entry box
        self.start_voltage_entry = Entry(self.pulseFrame, width=5)
        self.start_voltage_entry.grid(column=1, row=9)

        # Stop voltage label
        self.stop_voltage_label = Label(self.pulseFrame, text='Stop (V)')
        self.stop_voltage_label.grid(column=2, row=8)
        # Stop voltage entry box
        self.stop_voltage_entry = Entry(self.pulseFrame, width=5)
        self.stop_voltage_entry.grid(column=2, row=9)

        # Frequency label
        self.frequency_label = Label(self.pulseFrame, text='Frequency (kHz)')
        self.frequency_label.grid(column=3, row=8)
        # Frequency entry box
        self.frequency_entry = Entry(self.pulseFrame, width=5)
        self.frequency_entry.grid(column=3, row=9)

        # Start Button
        self.start_button = Button(
            self.pulseFrame, text='Start', command=self.start_li_pulse)
        self.start_button.grid(column=2, row=10, ipadx=10, pady=5)
        # # Stop Button
        # self.stop_button = Button(
        #     self.setFrame, text='Stop', state=DISABLED, command=self.stop_pressed)
        # self.stop_button.grid(column=3, row=11, ipadx=10, pady=5)

        # Device settings frame
        self.devFrame = LabelFrame(self.master, text='Device Settings')
        # Display device settings frame
        self.devFrame.grid(column=1, row=1, sticky='W', padx=(10, 5))

        self.pulse_label = Label(self.devFrame, text='Pulser Address')
        self.pulse_label.grid(column=0, row=0, sticky='W')
        self.pulse_addr = Entry(self.devFrame)
        self.pulse_addr.grid(column=0, columnspan=2, row=1, padx=5, pady=5, sticky='W')

        self.scope_label = Label(self.devFrame, text='Oscilloscope Address')
        self.scope_label.grid(column=0, row=2, sticky='W')
        self.scope_addr = Entry(self.devFrame)
        self.scope_addr.grid(column=0, columnspan=2, row=3, padx=5, pady=5, sticky='W')

        # Default values
        self.pulse_addr.insert(0, 'GPIB0::1::INSTR')
        self.scope_addr.insert(0, 'USB0::0x0957::0x17A2::MY51450354::INSTR')

        channels = [1,2,3,4]
        currNum = StringVar()

        # Set current channel to 1
        currNum.set('1')

        # Current measurement channel label
        self.curr_channel_label = Label(self.devFrame, text='Current Channel')
        self.curr_channel_label.grid(column=0, row=4)
        # Current measurement channel dropdown
        self.curr_channel_dropdown = OptionMenu(self.devFrame, currNum, *channels)
        self.curr_channel_dropdown.grid(column=0, row=5)

        lightNum = StringVar()
        # Set light channel to 2
        lightNum.set('2')

        # Light measurement channel label
        self.light_channel_label = Label(self.devFrame, text='Light Channel')
        self.light_channel_label.grid(column=1, row=4)
        # Light measurement channel dropdown
        self.light_channel_dropdown = OptionMenu(self.devFrame, lightNum, *channels)
        self.light_channel_dropdown.grid(column=1, row=5)


# On closing, ensure outputs are turned off
def on_closing():
    if messagebox.askokcancel('Quit', 'Do you want to quit?'):
        root.destroy()


root = tk.Tk()
Meas_gui = MeasSelect(root)
root.protocol('WM_DELETE_WINDOW', on_closing)
root.mainloop()