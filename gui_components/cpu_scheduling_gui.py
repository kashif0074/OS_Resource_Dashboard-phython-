

import tkinter as tk
from tkinter import ttk, messagebox
import collections
import time 


from os_simulations.cpu_scheduling import Process, FCFSScheduler, SJFScheduler, RoundRobinScheduler

class CPUSchedulingFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.scheduler = None
        self.current_time = 0
        self.is_running = False
        self.after_id = None 

        self.processes_data = [] 

        self.create_widgets()
        self.reset_simulation() 

    def create_widgets(self):
        
        config_frame = ttk.LabelFrame(self, text="Configuration", padding="10")
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

       
        process_input_frame = ttk.LabelFrame(config_frame, text="Add Process", padding="10")
        process_input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        ttk.Label(process_input_frame, text="PID:").grid(row=0, column=0, sticky="w", pady=2)
        self.pid_entry = ttk.Entry(process_input_frame, width=10)
        self.pid_entry.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(process_input_frame, text="Arrival Time:").grid(row=1, column=0, sticky="w", pady=2)
        self.arrival_entry = ttk.Entry(process_input_frame, width=10)
        self.arrival_entry.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(process_input_frame, text="Burst Time:").grid(row=2, column=0, sticky="w", pady=2)
        self.burst_entry = ttk.Entry(process_input_frame, width=10)
        self.burst_entry.grid(row=2, column=1, sticky="ew", pady=2)

        add_process_btn = ttk.Button(process_input_frame, text="Add Process", command=self.add_process_gui)
        add_process_btn.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

        
        algo_select_frame = ttk.LabelFrame(config_frame, text="Select Algorithm", padding="10")
        algo_select_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.algorithm_var = tk.StringVar(value="FCFS")
        ttk.Radiobutton(algo_select_frame, text="FCFS (First-Come, First-Served)", variable=self.algorithm_var, value="FCFS", command=self.on_algorithm_change).pack(anchor="w")
        ttk.Radiobutton(algo_select_frame, text="SJF (Shortest Job First)", variable=self.algorithm_var, value="SJF", command=self.on_algorithm_change).pack(anchor="w")
        ttk.Radiobutton(algo_select_frame, text="Round Robin", variable=self.algorithm_var, value="RoundRobin", command=self.on_algorithm_change).pack(anchor="w")

        self.quantum_frame = ttk.Frame(algo_select_frame)
        self.quantum_frame.pack(anchor="w", pady=5)
        ttk.Label(self.quantum_frame, text="Quantum:").pack(side=tk.LEFT)
        self.quantum_entry = ttk.Entry(self.quantum_frame, width=5)
        self.quantum_entry.insert(0, "4")
        self.quantum_entry.pack(side=tk.LEFT, padx=5)
        self.quantum_frame.pack_forget() 

       
        controls_frame = ttk.LabelFrame(config_frame, text="Controls", padding="10")
        controls_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        self.start_pause_btn = ttk.Button(controls_frame, text="Start Simulation", command=self.toggle_simulation)
        self.start_pause_btn.pack(fill=tk.X, pady=2)

        reset_btn = ttk.Button(controls_frame, text="Reset Simulation", command=self.reset_simulation)
        reset_btn.pack(fill=tk.X, pady=2)

      
        process_list_frame = ttk.LabelFrame(self, text="Current Processes (PID, Arrival, Burst)", padding="10")
        process_list_frame.pack(fill=tk.X, padx=10, pady=5)
        self.process_list_label = ttk.Label(process_list_frame, text="No processes added yet.")
        self.process_list_label.pack(fill=tk.X)

       
        viz_frame = ttk.LabelFrame(self, text="Gantt Chart", padding="10")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.gantt_canvas = tk.Canvas(viz_frame, bg="white", height=100, bd=2, relief="groove")
        self.gantt_canvas.pack(fill=tk.X, expand=True)
        self.gantt_canvas.bind("<Configure>", self.on_canvas_resize)


        self.current_time_label = ttk.Label(viz_frame, text="Current Time: 0", font=("Arial", 12, "bold"))
        self.current_time_label.pack(pady=5)

     
        stats_frame = ttk.LabelFrame(self, text="Statistics", padding="10")
        stats_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)

        self.avg_waiting_label = ttk.Label(stats_frame, text="Avg. Waiting Time: 0.00", font=("Arial", 10))
        self.avg_waiting_label.grid(row=0, column=0, sticky="w", pady=2)

        self.avg_turnaround_label = ttk.Label(stats_frame, text="Avg. Turnaround Time: 0.00", font=("Arial", 10))
        self.avg_turnaround_label.grid(row=0, column=1, sticky="w", pady=2)

        self.cpu_util_label = ttk.Label(stats_frame, text="CPU Utilization: 0.00%", font=("Arial", 10))
        self.cpu_util_label.grid(row=0, column=2, sticky="w", pady=2)

        self.context_switches_label = ttk.Label(stats_frame, text="Context Switches: 0", font=("Arial", 10))
        self.context_switches_label.grid(row=0, column=3, sticky="w", pady=2)

    def on_canvas_resize(self, event):
        """Redraws the Gantt chart when the canvas is resized."""
        self.draw_gantt_chart()


    def on_algorithm_change(self):
        """Handles changes in the selected scheduling algorithm."""
        if self.algorithm_var.get() == "RoundRobin":
            self.quantum_frame.pack(anchor="w", pady=5)
        else:
            self.quantum_frame.pack_forget()
        self.reset_simulation() 

    def add_process_gui(self):
        """Gets process data from GUI and adds it to the scheduler."""
        pid = self.pid_entry.get().strip()
        try:
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            if not pid or burst <= 0 or arrival < 0:
                raise ValueError("Invalid input")

           
            if any(p.pid == pid for p in self.processes_data):
                messagebox.showerror("Input Error", f"Process with PID '{pid}' already exists.")
                return

            new_process = Process(pid, arrival, burst)
            self.processes_data.append(new_process)
            self.processes_data.sort(key=lambda p: p.arrival_time) 

            self.update_process_list_display()
            self.reset_simulation()
            self.pid_entry.delete(0, tk.END)
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid PID (text), non-negative Arrival Time, and positive Burst Time.")

    def update_process_list_display(self):
        """Updates the label showing current processes."""
        if not self.processes_data:
            self.process_list_label.config(text="No processes added yet.")
            return

        process_str = ", ".join([f"{p.pid}({p.arrival_time},{p.burst_time})" for p in self.processes_data])
        self.process_list_label.config(text=process_str)

    def toggle_simulation(self):
        """Starts or pauses the simulation."""
        if not self.processes_data:
            messagebox.showinfo("Simulation Info", "Please add processes before starting the simulation.")
            return

        if self.is_running:
            self.pause_simulation()
        else:
            self.start_simulation()

    def start_simulation(self):
        """Starts the simulation loop."""
        if self.scheduler is None:
           
            algo = self.algorithm_var.get()
            if algo == "FCFS":
                self.scheduler = FCFSScheduler()
            elif algo == "SJF":
                self.scheduler = SJFScheduler()
            elif algo == "RoundRobin":
                try:
                    quantum_val = int(self.quantum_entry.get())
                    if quantum_val <= 0:
                        raise ValueError
                    self.scheduler = RoundRobinScheduler(quantum_val)
                except ValueError:
                    messagebox.showerror("Input Error", "Quantum must be a positive integer.")
                    self.reset_simulation()
                    return

           
            for p in self.processes_data:
                self.scheduler.add_process(p)
            self.scheduler.reset_state() 
        self.is_running = True
        self.start_pause_btn.config(text="Pause Simulation")
        self._run_simulation_step()

    def pause_simulation(self):
        """Pauses the simulation loop."""
        self.is_running = False
        self.start_pause_btn.config(text="Start Simulation")
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def reset_simulation(self):
        """Resets the entire simulation state."""
        self.pause_simulation() 
        self.current_time = 0
        self.gantt_canvas.delete("all") 
        self.current_time_label.config(text="Current Time: 0")

        
        self.scheduler = None 
        self.avg_waiting_label.config(text="Avg. Waiting Time: 0.00")
        self.avg_turnaround_label.config(text="Avg. Turnaround Time: 0.00")
        self.cpu_util_label.config(text="CPU Utilization: 0.00%")
        self.context_switches_label.config(text="Context Switches: 0")
        self.update_process_list_display()

    def _run_simulation_step(self):
        """Performs one step of the simulation and schedules the next."""
        if not self.is_running:
            return

      
        if self.scheduler.current_process is None and \
           not self.scheduler.ready_queue and \
           len(self.scheduler.completed_processes) == len(self.processes_data):
            
            self.pause_simulation()
            messagebox.showinfo("Simulation Complete", "All processes have finished execution!")
            return

       
        pid_this_tick, avg_wait, avg_turnaround, cpu_util, context_switches = self.scheduler.step(self.current_time)

        self.draw_gantt_chart()
        self.current_time_label.config(text=f"Current Time: {self.current_time + 1}")
        self.avg_waiting_label.config(text=f"Avg. Waiting Time: {avg_wait:.2f}")
        self.avg_turnaround_label.config(text=f"Avg. Turnaround Time: {avg_turnaround:.2f}")
        self.cpu_util_label.config(text=f"CPU Utilization: {cpu_util:.2f}%")
        self.context_switches_label.config(text=f"Context Switches: {context_switches}")

        self.current_time += 1
        self.after_id = self.after(500, self._run_simulation_step) 

    def draw_gantt_chart(self):
        """Draws the Gantt chart on the canvas."""
        self.gantt_canvas.delete("all")
        if not self.scheduler or not self.scheduler.gantt_chart:
            return

       
        process_colors = {}
        color_idx = 0
        base_colors = ["#FF5733", "#33FF57", "#3357FF", "#FF33F5", "#F5FF33", "#33F5FF"] # Vibrant colors

        def get_process_color(pid):
            nonlocal color_idx
            if pid == 'Idle':
                return "#A9A9A9"
            if pid not in process_colors:
                process_colors[pid] = base_colors[color_idx % len(base_colors)]
                color_idx += 1
            return process_colors[pid]

        x_offset = 0
        cell_width = 30 

       
        required_width = len(self.scheduler.gantt_chart) * cell_width + 50
        
        if required_width > self.gantt_canvas.winfo_width() or self.gantt_canvas.winfo_width() < 1:
            self.gantt_canvas.config(width=required_width)
            
        for item in self.scheduler.gantt_chart:
            color = get_process_color(item['pid'])
            self.gantt_canvas.create_rectangle(
                x_offset, 0, x_offset + cell_width, 50,
                fill=color, outline="black"
            )
            self.gantt_canvas.create_text(
                x_offset + cell_width / 2, 25,
                text=item['pid'], fill="white", font=("Arial", 8, "bold")
            )
           
            self.gantt_canvas.create_text(
                x_offset, 65, 
                text=str(item['time']), anchor="nw", font=("Arial", 7)
            )
            x_offset += cell_width

       
        if self.scheduler.gantt_chart:
            self.gantt_canvas.create_text(
                x_offset, 65,
                text=str(self.current_time), anchor="nw", font=("Arial", 7)
            )