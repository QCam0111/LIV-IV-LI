import pyvisa
from time import sleep
import numpy as np
from numpy import append, zeros, arange, logspace, log10
import os
import shutil
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Tkinter import Label, Entry, Button, LabelFrame, Radiobutton, StringVar, IntVar, DISABLED, NORMAL

# Import Browse button functions
from Browse_buttons import browse_plot_file, browse_txt_file

rm = pyvisa.ResourceManager()

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