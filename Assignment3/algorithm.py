from typing import List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Operation:
    """Job operation"""
    job_id: int      # Job ID
    machine_id: int  # Machine ID (0, 1, 2)
    processing_time: int  # Processing time p_ij
    release_time: int  # Job release time r_j


@dataclass
class ScheduledOperation:
    """Scheduled operation"""
    operation: Operation
    start_time: int  # Start time
    end_time: int    # End time


class OpenShopScheduler:
    """Open Shop scheduler"""
    
    def __init__(self, n: int, tasks: List[Tuple[int, int, int, int]]):
        """Initializes scheduler"""
        self.n = n
        self.tasks = tasks
        
        # Create list of all operations
        self.operations: List[Operation] = []
        for job_id, (p1, p2, p3, r) in enumerate(tasks):
            self.operations.append(Operation(job_id, 0, p1, r))
            self.operations.append(Operation(job_id, 1, p2, r))
            self.operations.append(Operation(job_id, 2, p3, r))
        
        # Schedule: machine_id -> list of scheduled operations
        self.schedule: List[List[ScheduledOperation]] = [
            [] for _ in range(3)
        ]
        
        # Machine ready time
        self.machine_ready_time = [0, 0, 0]
        
        # Track scheduled operations
        self.scheduled_ops = set()
        
        # Job completion time
        self.job_completion_time = [0] * n
    
    def calculate_priority(self, op: Operation) -> float:
        """Calculates operation priority for scheduling"""
        job_total_time = sum(
            self.tasks[op.job_id][i] for i in range(3)
        )
        
        # Combined priority:
        # 1. Release time (earlier = higher priority)
        # 2. Processing time (shorter = higher priority)
        # 3. Total job time (shorter = higher priority)
        
        priority = (
            op.release_time * 0.4 +  # Release time
            op.processing_time * 0.3 +  # Operation processing time
            job_total_time * 0.3  # Total job time
        )
        
        return priority
    
    def can_schedule(self, op: Operation, start_time: int) -> bool:
        """Checks if operation can be scheduled at given time"""
        # Check if job is ready
        if start_time < op.release_time:
            return False
        
        end_time = start_time + op.processing_time
        
        # Check conflicts with operations on same machine
        machine_id = op.machine_id
        for scheduled in self.schedule[machine_id]:
            # Check time overlap
            if not (end_time <= scheduled.start_time or 
                   start_time >= scheduled.end_time):
                return False
        
        # Check that other operations of same job are not running at this time
        for other_machine_id in range(3):
            if other_machine_id == machine_id:
                continue
            
            for scheduled in self.schedule[other_machine_id]:
                if scheduled.operation.job_id == op.job_id:
                    # Check time overlap
                    if not (end_time <= scheduled.start_time or 
                           start_time >= scheduled.end_time):
                        return False
        
        return True
    
    def find_earliest_start_time(self, op: Operation) -> int:
        """Finds earliest start time for operation"""
        machine_id = op.machine_id
        
        # Start from machine ready time and job release time
        earliest = max(self.machine_ready_time[machine_id], op.release_time)
        
        # Check all possible start times
        # Find first available window
        max_iterations = 100000
        iteration = 0
        
        while iteration < max_iterations:
            if self.can_schedule(op, earliest):
                return earliest
            
            # Find next potential start time
            next_available = earliest + 1
            
            # Check operations on same machine
            for scheduled in self.schedule[machine_id]:
                if scheduled.end_time > earliest:
                    next_available = max(next_available, scheduled.end_time)
            
            # Check operations of same job on other machines
            for other_machine_id in range(3):
                if other_machine_id == machine_id:
                    continue
                
                for scheduled in self.schedule[other_machine_id]:
                    if scheduled.operation.job_id == op.job_id:
                        if scheduled.end_time > earliest:
                            next_available = max(next_available, scheduled.end_time)
            
            earliest = next_available
            iteration += 1
        
        # If not found, return current time
        return earliest
    
    def schedule_operation(self, op: Operation) -> ScheduledOperation:
        """Schedules operation"""
        start_time = self.find_earliest_start_time(op)
        end_time = start_time + op.processing_time
        
        scheduled = ScheduledOperation(op, start_time, end_time)
        
        # Add to schedule
        machine_id = op.machine_id
        self.schedule[machine_id].append(scheduled)
        self.schedule[machine_id].sort(key=lambda x: x.start_time)
        
        # Update machine ready time (max end time of operations)
        self.machine_ready_time[machine_id] = max(
            self.machine_ready_time[machine_id],
            end_time
        )
        
        # Update job completion time
        self.job_completion_time[op.job_id] = max(
            self.job_completion_time[op.job_id],
            end_time
        )
        
        self.scheduled_ops.add((op.job_id, op.machine_id))
        
        return scheduled
    
    def solve(self) -> int:
        """Solves scheduling problem using list scheduling with priorities"""
        # Sort operations by priority
        unscheduled = [(self.calculate_priority(op), op) for op in self.operations]
        unscheduled.sort(key=lambda x: x[0])
        
        # Schedule operations by priority
        while len(self.scheduled_ops) < len(self.operations):
            # Find first available operation with highest priority
            for priority, op in unscheduled:
                if (op.job_id, op.machine_id) in self.scheduled_ops:
                    continue
                
                # Try to schedule
                self.schedule_operation(op)
                break
        
        # C_max = maximum completion time of all jobs
        return max(self.job_completion_time)
    
    def get_schedule(self) -> List[List[ScheduledOperation]]:
        """Returns schedule"""
        return self.schedule


def solve_open_shop(input_file: str, output_file: str) -> int:
    """Solves O3|r_j|C_max problem for given file"""
    # Read input file
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())
    tasks = []
    
    for i in range(1, n + 1):
        parts = lines[i].strip().split()
        p1, p2, p3, r = map(int, parts)
        tasks.append((p1, p2, p3, r))
    
    # Solve problem
    scheduler = OpenShopScheduler(n, tasks)
    c_max = scheduler.solve()
    schedule = scheduler.get_schedule()
    
    # Write result
    # Output format: 
    # First line: C_max
    # Then for each machine: list of operations in format
    # job_id machine_id start_time end_time
    with open(output_file, 'w') as f:
        f.write(f"{c_max}\n")
        
        for machine_id in range(3):
            for scheduled in schedule[machine_id]:
                f.write(f"{scheduled.operation.job_id} "
                       f"{scheduled.operation.machine_id} "
                       f"{scheduled.start_time} "
                       f"{scheduled.end_time}\n")
    
    return c_max


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python algorithm.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    c_max = solve_open_shop(input_file, output_file)
    print(f"C_max = {c_max}")

