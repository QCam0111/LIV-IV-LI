import tkFileDialog as FileDialog
from Tkinter import END

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