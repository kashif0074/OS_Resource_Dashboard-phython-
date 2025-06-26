

import tkinter as tk
from tkinter import ttk


from gui_components.cpu_scheduling_gui import CPUSchedulingFrame
from gui_components.memory_management_gui import MemoryManagementFrame
from gui_components.deadlock_handling_gui import DeadlockHandlingFrame

class OSResourceDashboardApp:
    """
    Main application class for the OS Resource Management Dashboard.
    Uses Tkinter's Notebook widget to create a tabbed interface.
    """
    def __init__(self, master):
        self.master = master
        master.title("OS Resource Management Dashboard (Python)")
        master.geometry("1000x750") 
        master.minsize(800, 600) 

       
        style = ttk.Style()
       
        style.theme_use('default') 
        
        
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=8, relief='raised')
        style.map('TButton', 
                  foreground=[('active', 'white'), ('!active', 'black')],
                  background=[('active', '#0056b3'), ('!active', '#007bff')] 
                 )
        style.configure('TFrame', background='#f0f0f0') 
        style.configure('TLabelFrame', font=('Arial', 11, 'bold'), background='#e0e0e0', foreground='#333')
        style.configure('TLabel', font=('Arial', 10), background='#f0f0f0')
        style.configure('TRadiobutton', font=('Arial', 10), background='#f0f0f0')
        style.configure('TEntry', padding=5)
        style.configure('TCombobox', padding=5)


      
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        
        self.cpu_frame = CPUSchedulingFrame(self.notebook)
        self.notebook.add(self.cpu_frame, text="CPU Scheduling")

       
        self.memory_frame = MemoryManagementFrame(self.notebook)
        self.notebook.add(self.memory_frame, text="Memory Management")

       
        self.deadlock_frame = DeadlockHandlingFrame(self.notebook)
        self.notebook.add(self.deadlock_frame, text="Deadlock Handling")

if __name__ == "__main__":
    root = tk.Tk()
    app = OSResourceDashboardApp(root)
    root.mainloop()