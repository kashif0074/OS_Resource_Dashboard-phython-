

import tkinter as tk
from tkinter import ttk, messagebox
from os_simulations.deadlock_handling import DeadlockDetector

class DeadlockHandlingFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.detector = DeadlockDetector()
        self.create_widgets()
        self.update_display() 

    def create_widgets(self):
        
        config_frame = ttk.LabelFrame(self, text="Configuration", padding="10")
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

     
        resource_frame = ttk.LabelFrame(config_frame, text="Manage Resources", padding="10")
        resource_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        ttk.Label(resource_frame, text="Resource ID:").grid(row=0, column=0, sticky="w", pady=2)
        self.resource_id_entry = ttk.Entry(resource_frame, width=10)
        self.resource_id_entry.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(resource_frame, text="Instances:").grid(row=1, column=0, sticky="w", pady=2)
        self.resource_instances_entry = ttk.Entry(resource_frame, width=10)
        self.resource_instances_entry.insert(0, "1")
        self.resource_instances_entry.grid(row=1, column=1, sticky="ew", pady=2)

        add_resource_btn = ttk.Button(resource_frame, text="Add/Update Resource", command=self.add_resource_gui)
        add_resource_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        
        self.resource_list_label = ttk.Label(resource_frame, text="Current Resources:")
        self.resource_list_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        self.update_resource_list_display()


       
        process_frame = ttk.LabelFrame(config_frame, text="Manage Processes", padding="10")
        process_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        ttk.Label(process_frame, text="Process ID:").grid(row=0, column=0, sticky="w", pady=2)
        self.process_id_entry = ttk.Entry(process_frame, width=10)
        self.process_id_entry.grid(row=0, column=1, sticky="ew", pady=2)

        add_process_btn = ttk.Button(process_frame, text="Add Process", command=self.add_process_gui)
        add_process_btn.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        self.process_list_label = ttk.Label(process_frame, text="Current Processes:")
        self.process_list_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        self.update_process_list_display()

       
        ops_frame = ttk.LabelFrame(config_frame, text="Resource Operations", padding="10")
        ops_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        ttk.Label(ops_frame, text="Process:").grid(row=0, column=0, sticky="w", pady=2)
        self.process_selector = ttk.Combobox(ops_frame, state="readonly")
        self.process_selector.grid(row=0, column=1, sticky="ew", pady=2)
        self.process_selector.bind("<<ComboboxSelected>>", self.update_resource_selectors)

        ttk.Label(ops_frame, text="Resource:").grid(row=1, column=0, sticky="w", pady=2)
        self.resource_selector = ttk.Combobox(ops_frame, state="readonly")
        self.resource_selector.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(ops_frame, text="Quantity:").grid(row=2, column=0, sticky="w", pady=2)
        self.quantity_entry = ttk.Entry(ops_frame, width=5)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.grid(row=2, column=1, sticky="ew", pady=2)

        request_btn = ttk.Button(ops_frame, text="Request", command=self.request_resource_gui)
        request_btn.grid(row=3, column=0, columnspan=2, pady=2, sticky="ew")
        
        allocate_btn = ttk.Button(ops_frame, text="Allocate", command=self.allocate_resource_gui)
        allocate_btn.grid(row=4, column=0, columnspan=2, pady=2, sticky="ew")

        release_btn = ttk.Button(ops_frame, text="Release", command=self.release_resource_gui)
        release_btn.grid(row=5, column=0, columnspan=2, pady=2, sticky="ew")
        
       
        state_frame = ttk.LabelFrame(self, text="Current System State", padding="10")
        state_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        state_frame.columnconfigure(0, weight=1)
        state_frame.columnconfigure(1, weight=1)

       
        process_state_viz_frame = ttk.LabelFrame(state_frame, text="Processes State", padding="10")
        process_state_viz_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.process_state_text = tk.Text(process_state_viz_frame, height=10, wrap="word", state="disabled")
        self.process_state_text.pack(fill=tk.BOTH, expand=True)

        
        resource_state_viz_frame = ttk.LabelFrame(state_frame, text="Resources State", padding="10")
        resource_state_viz_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.resource_state_text = tk.Text(resource_state_viz_frame, height=10, wrap="word", state="disabled")
        self.resource_state_text.pack(fill=tk.BOTH, expand=True)

       
        check_deadlock_btn = ttk.Button(self, text="Check for Deadlock", command=self.check_deadlock_gui)
        check_deadlock_btn.pack(pady=10)

        self.deadlock_status_label = ttk.Label(self, text="Deadlock Status: No check yet.", font=("Arial", 12, "bold"))
        self.deadlock_status_label.pack(pady=5)

        self.update_selector_options()


    def update_selector_options(self):
        """Updates the options in the process and resource selectors."""
        process_ids = list(self.detector.processes.keys())
        resource_ids = list(self.detector.resources.keys())

        self.process_selector['values'] = process_ids
        if process_ids and (not self.process_selector.get() or self.process_selector.get() not in process_ids):
            self.process_selector.set(process_ids[0])
        elif not process_ids:
            self.process_selector.set("")

        self.resource_selector['values'] = resource_ids
        if resource_ids and (not self.resource_selector.get() or self.resource_selector.get() not in resource_ids):
            self.resource_selector.set(resource_ids[0])
        elif not resource_ids:
            self.resource_selector.set("")
        
        self.update_display()


    def update_resource_selectors(self, event=None):
        """Updates resource selector based on selected process (if needed, or just refresh all)."""
        
        self.update_selector_options()

    def add_resource_gui(self):
        rid = self.resource_id_entry.get().strip()
        try:
            instances = int(self.resource_instances_entry.get())
            if not rid or instances <= 0:
                raise ValueError
            self.detector.add_resource(rid, instances)
            self.resource_id_entry.delete(0, tk.END)
            self.resource_instances_entry.delete(0, tk.END)
            self.update_selector_options()
            self.update_resource_list_display()
            self.update_display()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid Resource ID (text) and positive Instances (integer).")

    def update_resource_list_display(self):
        resource_str = ", ".join([f"{r.rid}({r.total_instances})" for r in self.detector.resources.values()])
        if not resource_str:
            resource_str = "No resources defined."
        self.resource_list_label.config(text=f"Current Resources: {resource_str}")


    def add_process_gui(self):
        pid = self.process_id_entry.get().strip()
        if not pid:
            messagebox.showerror("Input Error", "Please enter a Process ID.")
            return
        
        success = self.detector.add_process(pid)
        if success:
            self.process_id_entry.delete(0, tk.END)
            self.update_selector_options()
            self.update_process_list_display()
            self.update_display()
        else:
            messagebox.showerror("Error", f"Process '{pid}' already exists.")

    def update_process_list_display(self):
        process_ids = list(self.detector.processes.keys())
        process_str = ", ".join(process_ids)
        if not process_str:
            process_str = "No processes defined."
        self.process_list_label.config(text=f"Current Processes: {process_str}")

    def request_resource_gui(self):
        self._perform_resource_op("request")

    def allocate_resource_gui(self):
        self._perform_resource_op("allocate")

    def release_resource_gui(self):
        self._perform_resource_op("release")

    def _perform_resource_op(self, op_type):
        pid = self.process_selector.get()
        rid = self.resource_selector.get()
        try:
            qty = int(self.quantity_entry.get())
            if not pid or not rid or qty <= 0:
                raise ValueError("Missing or invalid input for PID, Resource, or Quantity.")
            
            success = False
            message = ""
            if op_type == "request":
                success, message = self.detector.request_resource(pid, rid, qty)
            elif op_type == "allocate":
                success, message = self.detector.allocate_resource(pid, rid, qty)
            elif op_type == "release":
                success, message = self.detector.release_resource(pid, rid, qty)
            
            if success:
                self.update_display()
                messagebox.showinfo("Operation Success", message)
            else:
                messagebox.showerror("Operation Failed", message)

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("An Error Occurred", f"An unexpected error occurred: {e}")

    def check_deadlock_gui(self):
        status_message = self.detector.detect_deadlock()
        self.deadlock_status_label.config(text=f"Deadlock Status: {status_message}")
        self.update_display() 

    def update_display(self):
        """Updates the text widgets showing process and resource states."""
        resource_states, process_states = self.detector.get_current_state()

       
        self.process_state_text.config(state="normal")
        self.process_state_text.delete(1.0, tk.END)
        if not process_states:
            self.process_state_text.insert(tk.END, "No processes defined.\n")
        else:
            for pid, p_data in process_states.items():
                alloc_str = ", ".join([f"{r}({q})" for r, q in p_data['allocated'].items()]) if p_data['allocated'] else "None"
                req_str = ", ".join([f"{r}({q})" for r, q in p_data['requested'].items()]) if p_data['requested'] else "None"
                self.process_state_text.insert(tk.END, f"Process {pid}:\n  Allocated: {alloc_str}\n  Requested: {req_str}\n\n")
        self.process_state_text.config(state="disabled")

      
        self.resource_state_text.config(state="normal")
        self.resource_state_text.delete(1.0, tk.END)
        if not resource_states:
            self.resource_state_text.insert(tk.END, "No resources defined.\n")
        else:
            for rid, r_data in resource_states.items():
                self.resource_state_text.insert(tk.END, f"Resource {rid}:\n  Total: {r_data['total']}\n  Available: {r_data['available']}\n  Allocated: {r_data['allocated']}\n  Requested: {r_data['requested']}\n\n")
        self.resource_state_text.config(state="disabled")