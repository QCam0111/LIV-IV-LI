from Tkinter import LabelFrame
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
