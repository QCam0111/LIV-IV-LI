import pyvisa
from time import sleep
import numpy as np
from numpy import append, zeros, arange, logspace, log10, size
import os
import shutil
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from Tkinter import Label, Entry, Button, LabelFrame, OptionMenu, Radiobutton, StringVar, IntVar, DISABLED, NORMAL

# Import Browse button functions
from Browse_buttons import browse_plot_file, browse_txt_file

rm = pyvisa.ResourceManager()

class CW_Roll():

    def __init__(self, parent):
        self.master = parent

        # Assign window title and geometry
        self.master.title('CW Measurement: 90% Thermal Rollover I-V')

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