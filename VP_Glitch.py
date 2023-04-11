import pyvisa
import Tkinter as tk
from Tkinter import Label, Entry, Button


rm = pyvisa.ResourceManager()
print(rm.list_resources())

class GlitchSelect():

    def __init__(self, parent):
        self.master = parent

        # Assign window title
        self.master.title('Glitch Discovery')
        
        self.start_label = Label(self.master, text='Start Voltage')
        self.start_label.grid(column=0, row=0)

        self.start_entry = Entry(self.master, width=5)
        self.start_entry.grid(column=0, row=1, pady=(0,10))

        self.step_label = Label(self.master, text='Step')
        self.step_label.grid(column=1, row=0)

        self.step_entry = Entry(self.master, width=5)
        self.step_entry.grid(column=1, row=1, pady=(0,10)) 

        self.inc_button = Button(self.master, text='Inc', command=self.inc_voltage)
        self.inc_button.grid(column=0, row=2, ipadx=10, pady=5)

        self.dec_button = Button(self.master, text='Dec', command=self.dec_voltage)
        self.dec_button.grid(column=1, row=2, ipadx=10, pady=5)

        self.start_button = Button(self.master, text='Start', command=self.start_voltage)
        self.start_button.grid(column=1, row=3, ipadx=10, pady=5)

    def inc_voltage(self):
        
        self.pulser = rm.open_resource('GPIB1::3::INSTR')

        current_voltage = self.pulser.query('VOLT?')

        new_voltage = float(current_voltage) + float(self.step_entry.get())

        self.pulser.write("VOLT %.3f" %(new_voltage))

    def dec_voltage(self):
        
        self.pulser = rm.open_resource('GPIB1::3::INSTR')

        current_voltage = self.pulser.query('VOLT?')

        new_voltage = float(current_voltage) - float(self.step_entry.get())

        self.pulser.write("VOLT %.3f" %(new_voltage))

    def start_voltage(self):
        
        self.pulser = rm.open_resource("GPIB1::3::INSTR")

        self.pulser.write("OUTPut:IMPedance 50")
        self.pulser.write("SOURce INTernal")

        self.pulser.write("VOLT " + self.start_entry.get())
        self.pulser.write("OUTPut ON")


root = tk.Tk()

Glitch_GUI = GlitchSelect(root)
root.mainloop()