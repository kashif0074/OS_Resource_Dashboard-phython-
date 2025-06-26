# os_simulations/memory_management.py

class MemoryBlock:
    """
    Represents a contiguous block of memory, either free or allocated.
    """
    def __init__(self, block_id, start_address, size, status='free', process_id=None):
        self.id = block_id
        self.start = start_address
        self.size = size
        self.status = status # 'free' or 'allocated'
        self.process_id = process_id # PID of the process if allocated

    def __repr__(self):
        if self.status == 'allocated':
            return f"MemoryBlock(ID={self.id}, Start={self.start}, Size={self.size}, Status=ALLOCATED, PID={self.process_id})"
        return f"MemoryBlock(ID={self.id}, Start={self.start}, Size={self.size}, Status=FREE)"

class MemoryManager:
    """
    Manages memory allocation and deallocation using various algorithms.
    """
    def __init__(self, total_memory_size):
        self.total_memory_size = total_memory_size
        self.memory_blocks = [] # List of MemoryBlock objects
        self.reset_memory() # Initialize with one large free block

    def reset_memory(self):
        """Resets the memory to a single large free block."""
        self.memory_blocks = [MemoryBlock('free-0', 0, self.total_memory_size, 'free')]
        # Sort by start address to maintain order
        self.memory_blocks.sort(key=lambda b: b.start)

    def allocate(self, process_id, size, algorithm='First Fit'):
        """
        Allocates a block of memory to a process using the specified algorithm.
        Returns True if allocation successful, False otherwise.
        """
        if size <= 0:
            return False # Invalid size

        best_fit_block_index = -1
        min_remaining_size = float('inf')

        # Find suitable block based on algorithm
        for i, block in enumerate(self.memory_blocks):
            if block.status == 'free' and block.size >= size:
                if algorithm == 'First Fit':
                    best_fit_block_index = i
                    break # Found the first suitable block
                elif algorithm == 'Best Fit':
                    if block.size - size < min_remaining_size:
                        min_remaining_size = block.size - size
                        best_fit_block_index = i

        if best_fit_block_index != -1:
            block_to_allocate = self.memory_blocks[best_fit_block_index]
            allocated_block_size = size
            remaining_size = block_to_allocate.size - size

            # Update the existing block to be the allocated portion
            block_to_allocate.size = allocated_block_size
            block_to_allocate.status = 'allocated'
            block_to_allocate.process_id = process_id

            if remaining_size > 0:
                # Create a new free block for the remaining space
                new_free_block = MemoryBlock(
                    block_id=f"free-{block_to_allocate.id}-{block_to_allocate.start + allocated_block_size}",
                    start_address=block_to_allocate.start + allocated_block_size,
                    size=remaining_size,
                    status='free'
                )
                # Insert the new free block right after the allocated one
                self.memory_blocks.insert(best_fit_block_index + 1, new_free_block)
            return True
        return False # No suitable block found

    def deallocate(self, process_id):
        """
        Deallocates memory held by a given process ID.
        Merges adjacent free blocks.
        """
        deallocated_any = False
        # First, mark all blocks allocated to this process as free
        for block in self.memory_blocks:
            if block.process_id == process_id and block.status == 'allocated':
                block.status = 'free'
                block.process_id = None
                deallocated_any = True

        if deallocated_any:
            self._merge_free_blocks()
        return deallocated_any

    def _merge_free_blocks(self):
        """
        Internal helper to merge adjacent free memory blocks.
        Assumes self.memory_blocks is sorted by start address.
        """
        if not self.memory_blocks:
            return

        merged_blocks = []
        # Sort by start address to ensure correct merging
        self.memory_blocks.sort(key=lambda b: b.start)

        # Initialize with the first block
        if self.memory_blocks:
            current_merged_block = self.memory_blocks[0]
            merged_blocks.append(current_merged_block)
        else:
            self.memory_blocks = []
            return


        for i in range(1, len(self.memory_blocks)):
            next_block = self.memory_blocks[i]
            if current_merged_block.status == 'free' and \
               next_block.status == 'free' and \
               current_merged_block.start + current_merged_block.size == next_block.start:
                # Merge: Extend the current merged block's size
                current_merged_block.size += next_block.size
                # Update the ID of the merged block (optional, but good practice for unique IDs)
                current_merged_block.id = f"free-{current_merged_block.start}-{current_merged_block.size}"
            else:
                # Cannot merge, start a new merged block
                merged_blocks.append(next_block)
                current_merged_block = next_block
        self.memory_blocks = merged_blocks

    def get_memory_map_data(self):
        """
        Returns a list of dicts representing the current memory blocks for GUI display.
        [{'start': 0, 'size': 100, 'status': 'free', 'process_id': None}, ...]
        """
        return [{'start': b.start, 'size': b.size, 'status': b.status, 'process_id': b.process_id}
                for b in self.memory_blocks]

    def calculate_stats(self):
        """
        Calculates and returns memory usage statistics.
        Returns a dictionary: {'free_memory', 'allocated_memory', 'free_holes', 'largest_free_block'}
        """
        free_memory = 0
        allocated_memory = 0
        free_holes = 0
        largest_free_block = 0

        for block in self.memory_blocks:
            if block.status == 'free':
                free_memory += block.size
                free_holes += 1
                if block.size > largest_free_block:
                    largest_free_block = block.size
            else:
                allocated_memory += block.size

        return {
            'free_memory': free_memory,
            'allocated_memory': allocated_memory,
            'free_holes': free_holes,
            'largest_free_block': largest_free_block
        }