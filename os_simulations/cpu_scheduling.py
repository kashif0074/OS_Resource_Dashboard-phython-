

import collections

class Process:
    """
    Represents a process with its attributes for CPU scheduling.
    """
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = -1      
        self.completion_time = -1  
        self.waiting_time = 0      
        self.turnaround_time = 0   
        self.initial_arrival = arrival_time 

    def __repr__(self):
        return f"Process(PID={self.pid}, Arrival={self.arrival_time}, Burst={self.burst_time}, Remaining={self.remaining_time})"

class BaseScheduler:
    """
    Base class for CPU schedulers. Provides common functionalities.
    """
    def __init__(self):
        self.initial_processes = []  
        self.ready_queue = collections.deque() 
        self.completed_processes = [] 
        self.current_process = None   
        self.gantt_chart = []         
        self.cpu_idle_time = 0
        self.last_activity_time = 0   
        self.total_waiting_time = 0
        self.total_turnaround_time = 0
        self.total_context_switches = 0
        self.total_execution_time = 0 

    def add_process(self, process):
        """Adds a process to the initial list. Resets the scheduler state."""
        self.initial_processes.append(process)
        self.initial_processes.sort(key=lambda x: x.arrival_time) 
        self.reset_state() 

    def reset_state(self):
        """Resets the scheduler to its initial state, re-populating the queue."""
        self.ready_queue = collections.deque()
        self.completed_processes = []
        self.current_process = None
        self.gantt_chart = []
        self.cpu_idle_time = 0
        self.last_activity_time = 0

       
        for p_original in sorted(self.initial_processes, key=lambda x: x.arrival_time):
           
            self.ready_queue.append(Process(p_original.pid, p_original.arrival_time, p_original.burst_time))

        self.total_waiting_time = 0
        self.total_turnaround_time = 0
        self.total_context_switches = 0
        self.total_execution_time = 0

    def _update_waiting_times(self, current_time, process_currently_executing_pid=None):
        """Increments waiting time for processes in the ready queue."""
        for p in self.ready_queue:
            if p.arrival_time <= current_time and p.pid != process_currently_executing_pid:
                p.waiting_time += 1

    def _calculate_metrics(self, current_time_tick):
        """Calculates and updates average waiting time, turnaround time, and CPU utilization."""
        completed_count = len(self.completed_processes)
        if completed_count == 0:
            self.total_waiting_time = 0
            self.total_turnaround_time = 0
            return 0, 0, 0.0

        total_waiting = sum(p.waiting_time for p in self.completed_processes)
        total_turnaround = sum(p.turnaround_time for p in self.completed_processes)

        avg_wait = total_waiting / completed_count
        avg_turnaround = total_turnaround / completed_count

        cpu_utilization = (current_time_tick - self.cpu_idle_time) / current_time_tick * 100 if current_time_tick > 0 else 0

        return avg_wait, avg_turnaround, cpu_utilization

    def step(self, current_time):
        """
        Executes one time unit of the simulation for a generic scheduler.
        Derived classes must override to implement specific scheduling logic.
        """
        raise NotImplementedError("Subclasses must implement 'step' method.")

class FCFSScheduler(BaseScheduler):
    """
    First-Come, First-Served (FCFS) CPU scheduling algorithm.
    Non-preemptive.
    """
    def __init__(self):
        super().__init__()
        

    def step(self, current_time):
        """
        Executes one time unit for FCFS.
        :param current_time: The current time tick.
        :return: (pid_running_this_tick, avg_wait, avg_turnaround, cpu_utilization, num_context_switches)
        """
        pid_this_tick = 'Idle'
        context_switch_occurred = False

        
        for p_original in self.initial_processes:
            if p_original.arrival_time == current_time and \
               p_original.pid not in [qp.pid for qp in self.ready_queue] and \
               p_original.pid not in [cp.pid for cp in self.completed_processes]:
                
                self.ready_queue.append(Process(p_original.pid, p_original.arrival_time, p_original.burst_time))
                
                self.ready_queue = collections.deque(sorted(self.ready_queue, key=lambda x: x.arrival_time))


        if self.current_process is None or self.current_process.remaining_time <= 0:
           
            if self.current_process is not None and self.current_process.remaining_time <= 0:
                
                self.current_process.completion_time = current_time
                self.current_process.turnaround_time = self.current_process.completion_time - self.current_process.initial_arrival
                self.current_process.waiting_time = max(0, self.current_process.turnaround_time - self.current_process.burst_time) # Ensure non-negative
                self.completed_processes.append(self.current_process)
                self.current_process = None 
                context_switch_occurred = True 

           
            if self.ready_queue:
              
                next_process_candidate = None
                for p_in_queue in self.ready_queue:
                    if p_in_queue.arrival_time <= current_time:
                        next_process_candidate = p_in_queue
                        break

                if next_process_candidate:
                   
                    self.ready_queue.remove(next_process_candidate)
                    self.current_process = next_process_candidate
                    if not context_switch_occurred:
                        context_switch_occurred = True
                else:
                    self.current_process = None 
            else:
                self.current_process = None 

        if self.current_process:
            pid_this_tick = self.current_process.pid
            if self.current_process.start_time == -1:
                self.current_process.start_time = current_time
            self.current_process.remaining_time -= 1
            if context_switch_occurred: 
                self.total_context_switches += 1
        else:
            self.cpu_idle_time += 1
        self._update_waiting_times(current_time, pid_this_tick)

       
        self.gantt_chart.append({'pid': pid_this_tick, 'time': current_time})

       
        avg_wait, avg_turnaround, cpu_util = self._calculate_metrics(current_time + 1)
        self.total_execution_time = current_time + 1

        return pid_this_tick, avg_wait, avg_turnaround, cpu_util, self.total_context_switches

class SJFScheduler(BaseScheduler):
    """
    Shortest Job First (SJF) CPU scheduling algorithm.
    Non-preemptive.
    """
    def __init__(self):
        super().__init__()

    def step(self, current_time):
        """
        Executes one time unit for SJF.
        :param current_time: The current time tick.
        :return: (pid_running_this_tick, avg_wait, avg_turnaround, cpu_utilization, num_context_switches)
        """
        pid_this_tick = 'Idle'
        context_switch_occurred = False

       
        for p_original in self.initial_processes:
            if p_original.arrival_time == current_time and \
               p_original.pid not in [qp.pid for qp in self.ready_queue] and \
               p_original.pid not in [cp.pid for cp in self.completed_processes]:
                self.ready_queue.append(Process(p_original.pid, p_original.arrival_time, p_original.burst_time))

        if self.current_process is None or self.current_process.remaining_time <= 0:
            if self.current_process is not None and self.current_process.remaining_time <= 0:
               
                self.current_process.completion_time = current_time
                self.current_process.turnaround_time = self.current_process.completion_time - self.current_process.initial_arrival
                self.current_process.waiting_time = max(0, self.current_process.turnaround_time - self.current_process.burst_time)
                self.completed_processes.append(self.current_process)
                self.current_process = None
                context_switch_occurred = True

           
            ready_and_arrived_processes = [p for p in self.ready_queue if p.arrival_time <= current_time]
            if ready_and_arrived_processes:
                
                ready_and_arrived_processes.sort(key=lambda p: (p.remaining_time, p.arrival_time))
                next_process_candidate = ready_and_arrived_processes[0]

               
                self.ready_queue.remove(next_process_candidate)
                self.current_process = next_process_candidate
                if not context_switch_occurred:
                    context_switch_occurred = True
            else:
                self.current_process = None
        else:
          
            pass

        
        if self.current_process:
            pid_this_tick = self.current_process.pid
            if self.current_process.start_time == -1:
                self.current_process.start_time = current_time
            self.current_process.remaining_time -= 1
            if context_switch_occurred:
                self.total_context_switches += 1
        else:
            self.cpu_idle_time += 1

        self._update_waiting_times(current_time, pid_this_tick)
        self.gantt_chart.append({'pid': pid_this_tick, 'time': current_time})
        avg_wait, avg_turnaround, cpu_util = self._calculate_metrics(current_time + 1)
        self.total_execution_time = current_time + 1

        return pid_this_tick, avg_wait, avg_turnaround, cpu_util, self.total_context_switches

class RoundRobinScheduler(BaseScheduler):
    """
    Round Robin (RR) CPU scheduling algorithm.
    Preemptive, uses a time quantum.
    """
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum
        self.current_quantum_tick = 0 
    def reset_state(self):
        super().reset_state()
        self.current_quantum_tick = 0

    def step(self, current_time):
        """
        Executes one time unit for Round Robin.
        :param current_time: The current time tick.
        :return: (pid_running_this_tick, avg_wait, avg_turnaround, cpu_utilization, num_context_switches)
        """
        pid_this_tick = 'Idle'
        context_switch_occurred = False

       
        for p_original in self.initial_processes:
            if p_original.arrival_time == current_time and \
               p_original.pid not in [qp.pid for qp in self.ready_queue] and \
               p_original.pid not in [cp.pid for cp in self.completed_processes]:
                self.ready_queue.append(Process(p_original.pid, p_original.arrival_time, p_original.burst_time))

       
        if self.current_process:
            if self.current_process.remaining_time <= 0:
               
                self.current_process.completion_time = current_time
                self.current_process.turnaround_time = self.current_process.completion_time - self.current_process.initial_arrival
                self.current_process.waiting_time = max(0, self.current_process.turnaround_time - self.current_process.burst_time)
                self.completed_processes.append(self.current_process)
                self.current_process = None
                self.current_quantum_tick = 0 
                context_switch_occurred = True 

            elif self.current_quantum_tick >= self.quantum:
               
                if self.current_process.pid not in [p.pid for p in self.completed_processes] and \
                   self.current_process.pid not in [p.pid for p in self.ready_queue]:
                    self.ready_queue.append(self.current_process) 
                self.current_process = None
                self.current_quantum_tick = 0
                context_switch_occurred = True

        
        if self.current_process is None and self.ready_queue:
            self.current_process = self.ready_queue.popleft() 
            self.current_quantum_tick = 0 
            if not context_switch_occurred: 
                context_switch_occurred = True


        if self.current_process:
            pid_this_tick = self.current_process.pid
            if self.current_process.start_time == -1:
                self.current_process.start_time = current_time
            self.current_process.remaining_time -= 1
            self.current_quantum_tick += 1
            if context_switch_occurred:
                self.total_context_switches += 1
        else:
            self.cpu_idle_time += 1

        self._update_waiting_times(current_time, pid_this_tick)
        self.gantt_chart.append({'pid': pid_this_tick, 'time': current_time})
        avg_wait, avg_turnaround, cpu_util = self._calculate_metrics(current_time + 1)
        self.total_execution_time = current_time + 1

        return pid_this_tick, avg_wait, avg_turnaround, cpu_util, self.total_context_switches