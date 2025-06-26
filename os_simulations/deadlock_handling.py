# os_simulations/deadlock_handling.py

class Resource:
    """
    Represents a system resource type with a total number of instances.
    """
    def __init__(self, rid, total_instances):
        self.rid = rid
        self.total_instances = total_instances

    def __repr__(self):
        return f"Resource(ID={self.rid}, Total={self.total_instances})"

class DeadlockDetector:
    """
    Manages processes, resources, and provides deadlock detection functionality.
    This implementation uses a simplified approach similar to Banker's algorithm
    to check for a safe state, which also implies deadlock detection.
    """
    def __init__(self):
        self.resources = {}    # {rid: Resource_object}
        self.processes = {}    # {pid: {'allocated': {rid: qty}, 'requested': {rid: qty}}}

    def add_resource(self, rid, total_instances):
        """Adds a new resource type with a given number of instances."""
        if rid in self.resources:
            # If resource exists, just update its total instances (or add more)
            self.resources[rid].total_instances += total_instances
        else:
            self.resources[rid] = Resource(rid, total_instances)

    def remove_resource(self, rid):
        """Removes a resource type if it's not currently allocated or requested."""
        if rid not in self.resources:
            return False, f"Resource '{rid}' does not exist."

        # Check if any process is holding or requesting this resource
        for pid, p_state in self.processes.items():
            if (p_state['allocated'].get(rid, 0) > 0) or \
               (p_state['requested'].get(rid, 0) > 0):
                return False, f"Cannot remove resource '{rid}': It is currently held or requested by process '{pid}'."
        
        del self.resources[rid]
        return True, f"Resource '{rid}' removed successfully."

    def add_process(self, pid):
        """Adds a new process to the system."""
        if pid not in self.processes:
            self.processes[pid] = {'allocated': {}, 'requested': {}}
            return True
        return False

    def remove_process(self, pid):
        """Removes a process if it does not hold or request any resources."""
        if pid not in self.processes:
            return False, f"Process '{pid}' does not exist."
        
        p_state = self.processes[pid]
        if any(qty > 0 for qty in p_state['allocated'].values()) or \
           any(qty > 0 for qty in p_state['requested'].values()):
            return False, f"Cannot remove process '{pid}': It holds or requests resources. Release them first."
        
        del self.processes[pid]
        return True, f"Process '{pid}' removed successfully."

    def request_resource(self, pid, rid, quantity):
        """
        A process requests instances of a resource. This adds to the 'requested' state.
        Actual allocation happens separately.
        """
        if pid not in self.processes:
            return False, f"Process '{pid}' does not exist."
        if rid not in self.resources:
            return False, f"Resource '{rid}' does not exist."
        if quantity <= 0:
            return False, "Quantity must be positive."

        self.processes[pid]['requested'][rid] = self.processes[pid]['requested'].get(rid, 0) + quantity
        return True, f"Process '{pid}' requested {quantity} of '{rid}'."

    def allocate_resource(self, pid, rid, quantity):
        """
        Allocates requested resources to a process, if available.
        Moves from 'requested' to 'allocated' state.
        """
        if pid not in self.processes:
            return False, f"Process '{pid}' does not exist."
        if rid not in self.resources:
            return False, f"Resource '{rid}' does not exist."
        if quantity <= 0:
            return False, "Quantity must be positive."

        # Calculate currently available instances of this resource
        currently_allocated_total = sum(p_state['allocated'].get(rid, 0) for p_state in self.processes.values())
        available_instances = self.resources[rid].total_instances - currently_allocated_total

        if quantity > available_instances:
            return False, f"Not enough available instances of '{rid}'. Only {available_instances} left."

        # If process had requested this amount, reduce the requested amount
        requested_qty = self.processes[pid]['requested'].get(rid, 0)
        if requested_qty >= quantity:
            self.processes[pid]['requested'][rid] -= quantity
            if self.processes[pid]['requested'][rid] == 0:
                del self.processes[pid]['requested'][rid]
        
        self.processes[pid]['allocated'][rid] = self.processes[pid]['allocated'].get(rid, 0) + quantity
        return True, f"Process '{pid}' allocated {quantity} of '{rid}'."

    def release_resource(self, pid, rid, quantity):
        """
        A process releases instances of a resource it holds.
        """
        if pid not in self.processes:
            return False, f"Process '{pid}' does not exist."
        if rid not in self.resources:
            return False, f"Resource '{rid}' does not exist."
        if quantity <= 0:
            return False, "Quantity must be positive."

        current_allocated = self.processes[pid]['allocated'].get(rid, 0)
        if quantity > current_allocated:
            return False, f"Process '{pid}' only holds {current_allocated} instances of '{rid}'."
        
        self.processes[pid]['allocated'][rid] -= quantity
        if self.processes[pid]['allocated'][rid] == 0:
            del self.processes[pid]['allocated'][rid]
        return True, f"Process '{pid}' released {quantity} of '{rid}'."

    def detect_deadlock(self):
        """
        Performs a simplified safety algorithm check to detect deadlocks.
        Returns a string indicating "SAFE" or "DEADLOCK DETECTED" with involved processes.
        """
        if not self.processes:
            return "No processes to check."
        if not self.resources:
            return "No resources defined."

        # Deep copy current states to simulate resource allocation
        current_available = {rid: self.resources[rid].total_instances for rid in self.resources}
        for pid, p_state in self.processes.items():
            for rid, qty in p_state['allocated'].items():
                current_available[rid] -= qty

        # Initialize work and finish arrays
        work = {k: v for k, v in current_available.items()}
        finish = {pid: False for pid in self.processes}
        safe_sequence = []

        # Find processes that can finish
        found = True
        while found:
            found = False
            for pid, p_state in self.processes.items():
                if not finish[pid]:
                    can_finish = True
                    # Check if requested resources can be satisfied by current work
                    for rid, req_qty in p_state['requested'].items():
                        if req_qty > work.get(rid, 0): # Use .get to handle cases where resource might not be in work
                            can_finish = False
                            break

                    if can_finish:
                        # If process can finish, release its allocated resources
                        for rid, alloc_qty in p_state['allocated'].items():
                            work[rid] = work.get(rid, 0) + alloc_qty
                        finish[pid] = True
                        safe_sequence.append(pid)
                        found = True

        # Check if all processes finished
        deadlocked_processes = [pid for pid, finished in finish.items() if not finished]

        if not deadlocked_processes:
            return f"System is in a SAFE state. Safe sequence: <{', '.join(safe_sequence)}>"
        else:
            return f"DEADLOCK DETECTED! Involved processes: {', '.join(deadlocked_processes)}"

    def get_current_state(self):
        """Returns the current state of resources and processes for GUI display."""
        resource_usage = {}
        for rid, res_obj in self.resources.items():
            allocated_total = sum(p_state['allocated'].get(rid, 0) for p_state in self.processes.values())
            requested_total = sum(p_state['requested'].get(rid, 0) for p_state in self.processes.values())
            resource_usage[rid] = {
                'total': res_obj.total_instances,
                'available': res_obj.total_instances - allocated_total,
                'allocated': allocated_total,
                'requested': requested_total
            }
        
        # Ensure that process states are returned with default empty dicts if no allocated/requested
        processes_display_state = {
            pid: {
                'allocated': p_state.get('allocated', {}),
                'requested': p_state.get('requested', {})
            } for pid, p_state in self.processes.items()
        }

        return resource_usage, processes_display_state