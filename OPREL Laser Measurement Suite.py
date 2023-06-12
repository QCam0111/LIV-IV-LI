import Tkinter as tk
from Tkinter import Label, Button, Radiobutton, Toplevel, StringVar
import tkMessageBox as messagebox

# Import measurement files
from CW_LIV import CW_LI, CW_IV, CW_LIV
from Voltage_Pulsed_LIV import VPulse_LI, VPulse_IV, VPulse_LIV
from Current_Pulsed_LIV import IPulse_LI, IPulse_IV, IPulse_LIV

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
            self.master, text='Current Pulsed I - V', variable=self.selectedMeasurement, value='IPulse_IV', font=('Segoe UI', 10))
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
        self.measure_button = Button(self.master, text='Open Measurement', command=self.open_measurement_window, font=('Segoe UI', 10))
        self.measure_button.grid(column=2, row=7, padx=(10, 20), pady=(5, 10), sticky='W')

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
        elif 'IPulse_IV' == self.selectedMeasurement.get():
            IPulseIV_gui = IPulse_IV(top)
        elif 'IPulse_LI' == self.selectedMeasurement.get():
            IPulseLI_gui = IPulse_LI(top)
        root.withdraw()

        # When the user closes the measurement window, bring the root window back
        def minimize_root():
            top.destroy()
            root.deiconify()

        top.protocol('WM_DELETE_WINDOW', minimize_root)

# When the user attempts to close the window, double check if they would like to Quit.
def on_closing():
    if messagebox.askokcancel('Quit', 'Do you want to quit?'):
        root.destroy()

root = tk.Tk()

# Place root window in the middle of the user's screen from https://coderslegacy.com/tkinter-center-window-on-screen/

width=475
height=250

# Width of the screen
screen_width = root.winfo_screenwidth()  
# Height of the screen
screen_height = root.winfo_screenheight()
 
# Calculate Starting X and Y coordinates for Window
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)
 
root.geometry('%dx%d+%d+%d' %(width, height, x, y))

Selection_GUI = MeasSelect(root)
root.protocol('WM_DELETE_WINDOW', on_closing)
root.mainloop()
