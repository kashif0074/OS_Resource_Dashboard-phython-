

import tkinter as tk
from tkinter import ttk, messagebox
from os_simulations.memory_management import MemoryManager

class MemoryManagementFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.memory_manager = MemoryManager(1000) 
        self.create_widgets()
        self.draw_memory_map()
        self.update_stats_display()

    def create_widgets(self):
        
        config_frame = ttk.LabelFrame(self, text="Configuration", padding="10")
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

     
        mem_config_frame = ttk.LabelFrame(config_frame, text="Memory Settings", padding="10")
        mem_config_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        ttk.Label(mem_config_frame, text="Total Memory Units:").grid(row=0, column=0, sticky="w", pady=2)
        self.total_memory_entry = ttk.Entry(mem_config_frame, width=10)
        self.total_memory_entry.insert(0, "1000")
        self.total_memory_entry.grid(row=0, column=1, sticky="ew", pady=2)
        
        set_memory_btn = ttk.Button(mem_config_frame, text="Set & Reset Memory", command=self.set_total_memory)
        set_memory_btn.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        
        algo_select_frame = ttk.LabelFrame(config_frame, text="Select Algorithm", padding="10")
        algo_select_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.algorithm_var = tk.StringVar(value="First Fit")
        ttk.Radiobutton(algo_select_frame, text="First Fit", variable=self.algorithm_var, value="First Fit").pack(anchor="w")
        ttk.Radiobutton(algo_select_frame, text="Best Fit", variable=self.algorithm_var, value="Best Fit").pack(anchor="w")

       
        ops_frame = ttk.LabelFrame(config_frame, text="Memory Operations", padding="10")
        ops_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        ttk.Label(ops_frame, text="Process ID:").grid(row=0, column=0, sticky="w", pady=2)
        self.pid_entry = ttk.Entry(ops_frame, width=15)
        self.pid_entry.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(ops_frame, text="Memory Size:").grid(row=1, column=0, sticky="w", pady=2)
        self.size_entry = ttk.Entry(ops_frame, width=15)
        self.size_entry.grid(row=1, column=1, sticky="ew", pady=2)

        allocate_btn = ttk.Button(ops_frame, text="Allocate Memory", command=self.allocate_memory_gui)
        allocate_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        deallocate_btn = ttk.Button(ops_frame, text="Deallocate Memory (by PID)", command=self.deallocate_memory_gui)
        deallocate_btn.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

       
        viz_frame = ttk.LabelFrame(self, text="Memory Map", padding="10")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.memory_canvas = tk.Canvas(viz_frame, bg="gray", height=200, bd=2, relief="groove")
        self.memory_canvas.pack(fill=tk.X, expand=True)
        self.memory_canvas.bind("<Configure>", self.on_canvas_resize)


       
        stats_frame = ttk.LabelFrame(self, text="Statistics", padding="10")
        stats_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)

        self.free_memory_label = ttk.Label(stats_frame, text="Total Free Memory: 0 units", font=("Arial", 10))
        self.free_memory_label.grid(row=0, column=0, sticky="w", pady=2)

        self.allocated_memory_label = ttk.Label(stats_frame, text="Total Allocated Memory: 0 units", font=("Arial", 10))
        self.allocated_memory_label.grid(row=0, column=1, sticky="w", pady=2)

        self.free_holes_label = ttk.Label(stats_frame, text="Number of Free Holes: 0", font=("Arial", 10))
        self.free_holes_label.grid(row=0, column=2, sticky="w", pady=2)

        self.largest_free_label = ttk.Label(stats_frame, text="Largest Free Block: 0 units", font=("Arial", 10))
        self.largest_free_label.grid(row=0, column=3, sticky="w", pady=2)

    def on_canvas_resize(self, event):
        """Redraws the memory map when the canvas is resized."""
        self.draw_memory_map()

    def set_total_memory(self):
        """Sets the total memory size and resets the memory manager."""
        try:
            new_total_memory = int(self.total_memory_entry.get())
            if new_total_memory <= 0:
                raise ValueError
            self.memory_manager = MemoryManager(new_total_memory)
            self.draw_memory_map()
            self.update_stats_display()
        except ValueError:
            messagebox.showerror("Input Error", "Total Memory must be a positive integer.")

    def allocate_memory_gui(self):
        """Handles memory allocation requests from the GUI."""
        pid = self.pid_entry.get().strip()
        try:
            size = int(self.size_entry.get())
            if not pid or size <= 0:
                raise ValueError("Invalid input")

           
            current_blocks = self.memory_manager.get_memory_map_data()
            if any(block['process_id'] == pid and block['status'] == 'allocated' for block in current_blocks):
                messagebox.showerror("Allocation Error", f"Process '{pid}' already has allocated memory. Deallocate it first if you want to reallocate.")
                return

            algo = self.algorithm_var.get()
            allocated = self.memory_manager.allocate(pid, size, algo)
            if allocated:
                self.draw_memory_map()
                self.update_stats_display()
                self.pid_entry.delete(0, tk.END)
                self.size_entry.delete(0, tk.END)
            else:
                messagebox.showinfo("Allocation Failed", "Could not allocate memory. No suitable free block found.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid Process ID (text) and positive Memory Size (integer).")

    def deallocate_memory_gui(self):
        """Handles memory deallocation requests from the GUI."""
        pid = self.pid_entry.get().strip()
        if not pid:
            messagebox.showerror("Input Error", "Please enter a Process ID to deallocate.")
            return

        deallocated = self.memory_manager.deallocate(pid)
        if deallocated:
            self.draw_memory_map()
            self.update_stats_display()
            self.pid_entry.delete(0, tk.END)
        else:
            messagebox.showinfo("Deallocation Failed", f"Process '{pid}' was not found or had no allocated memory.")

    def draw_memory_map(self):
        """Draws the current memory map on the canvas."""
        self.memory_canvas.delete("all")
        memory_data = self.memory_manager.get_memory_map_data()
        total_memory_size = self.memory_manager.total_memory_size
        canvas_width = self.memory_canvas.winfo_width() 
        if canvas_width == 1: 
             canvas_width = 600

        y_pos = 0
        block_height = self.memory_canvas.winfo_height() 

        
        process_colors = {}
        color_idx = 0
      
        base_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

        def get_process_color(pid):
            nonlocal color_idx
            if pid not in process_colors:
                process_colors[pid] = base_colors[color_idx % len(base_colors)]
                color_idx += 1
            return process_colors[pid]

        for block in memory_data:
            x_start = (block['start'] / total_memory_size) * canvas_width
            x_end = ((block['start'] + block['size']) / total_memory_size) * canvas_width

            if block['status'] == 'free':
                fill_color = "lightgray"
                text = f"FREE\n({block['size']})"
                text_fill = "black"
            else:
                fill_color = get_process_color(block['process_id'])
                text = f"{block['process_id']}\n({block['size']})"
                text_fill = "white"

            self.memory_canvas.create_rectangle(
                x_start, y_pos, x_end, y_pos + block_height,
                fill=fill_color, outline="black", width=1
            )

          
            if block['size'] / total_memory_size * canvas_width > 40: 
                self.memory_canvas.create_text(
                    (x_start + x_end) / 2, y_pos + block_height / 2,
                    text=text, fill=text_fill, font=("Arial", 9, "bold"),
                    justify=tk.CENTER
                )

    def update_stats_display(self):
        """Updates the memory statistics labels."""
        stats = self.memory_manager.calculate_stats()
        self.free_memory_label.config(text=f"Total Free Memory: {stats['free_memory']} units")
        self.allocated_memory_label.config(text=f"Total Allocated Memory: {stats['allocated_memory']} units")
        self.free_holes_label.config(text=f"Number of Free Holes: {stats['free_holes']}")
        self.largest_free_label.config(text=f"Largest Free Block: {stats['largest_free_block']} units")