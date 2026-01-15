#!/usr/bin/env python3
"""
Verifies correctness of O3|r_j|C_max solution.

Checks:
1. All operations are scheduled
2. Operations don't overlap on same machine
3. Operations of same job don't run simultaneously
4. Start time >= job release time
5. C_max is calculated correctly
"""

import sys
from typing import List, Tuple


def read_input(input_file: str) -> Tuple[int, List[Tuple[int, int, int, int]]]:
    """Reads input file"""
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())
    tasks = []
    
    for i in range(1, n + 1):
        parts = lines[i].strip().split()
        p1, p2, p3, r = map(int, parts)
        tasks.append((p1, p2, p3, r))
    
    return n, tasks


def read_output(output_file: str) -> Tuple[int, List[List[Tuple[int, int, int]]]]:
    """Reads output file"""
    with open(output_file, 'r') as f:
        lines = f.readlines()
    
    c_max = int(lines[0].strip())
    
    schedule = [[], [], []]  # 3 machines
    
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) == 3:
            job_id, start_time, end_time = map(int, parts)
            # Determine machine by operation order
            # This is a simplification - in reality need to track machine
            # But for verification we can use order
            pass
    
    # Alternative approach: parse all operations and group
    operations = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) == 3:
            job_id, start_time, end_time = map(int, parts)
            operations.append((job_id, start_time, end_time))
    
    # Group by machines (assume operations go in machine order)
    # This requires knowledge of which operation is on which machine
    # For simplification, check all operations together
    
    return c_max, operations


def verify_correctness(input_file: str, output_file: str) -> Tuple[bool, List[str]]:
    """Verifies solution correctness"""
    errors = []
    
    try:
        # Read input data
        n, tasks = read_input(input_file)
        
        # Read output data
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) == 0:
            errors.append("Output file is empty")
            return False, errors
        
        c_max = int(lines[0].strip())
        
        # Parse operations
        operations = []
        for line in lines[1:]:
            parts = line.strip().split()
            if len(parts) == 4:
                job_id, machine_id, start_time, end_time = map(int, parts)
                operations.append((job_id, machine_id, start_time, end_time))
            elif len(parts) == 3:
                # Old format without machine_id - determine by processing time
                job_id, start_time, end_time = map(int, parts)
                processing_time = end_time - start_time
                p1, p2, p3, r = tasks[job_id]
                if processing_time == p1:
                    machine_id = 0
                elif processing_time == p2:
                    machine_id = 1
                elif processing_time == p3:
                    machine_id = 2
                else:
                    errors.append(f"Could not determine machine for job {job_id} operation")
                    continue
                operations.append((job_id, machine_id, start_time, end_time))
        
        # Check 1: Should have 3n operations (3 per job)
        if len(operations) != 3 * n:
            errors.append(f"Wrong number of operations: expected {3*n}, got {len(operations)}")
        
        # Check 2: Each job should have exactly 3 operations
        job_ops = {}
        for job_id, machine_id, start_time, end_time in operations:
            if job_id not in job_ops:
                job_ops[job_id] = []
            job_ops[job_id].append((machine_id, start_time, end_time))
        
        for job_id in range(n):
            if job_id not in job_ops:
                errors.append(f"Job {job_id} has no operations")
            elif len(job_ops[job_id]) != 3:
                errors.append(f"Job {job_id} has {len(job_ops[job_id])} operations instead of 3")
        
        # Check 3: Start time >= release time
        for job_id, machine_id, start_time, end_time in operations:
            r_j = tasks[job_id][3]  # Release time
            if start_time < r_j:
                errors.append(f"Job {job_id} operation on machine {machine_id} starts at {start_time}, "
                            f"but job is ready only at {r_j}")
        
        # Check 4: Operations of same job don't overlap
        for job_id in range(n):
            if job_id not in job_ops:
                continue
            
            ops = sorted(job_ops[job_id], key=lambda x: x[1])  # Sort by start_time
            for i in range(len(ops)):
                for j in range(i + 1, len(ops)):
                    machine1, start1, end1 = ops[i]
                    machine2, start2, end2 = ops[j]
                    
                    # Check overlap
                    if not (end1 <= start2 or start1 >= end2):
                        errors.append(f"Job {job_id} operations overlap: "
                                     f"machine {machine1} [{start1}, {end1}) and machine {machine2} [{start2}, {end2})")
        
        # Check 5: C_max should be >= maximum completion time
        max_completion = 0
        for job_id in range(n):
            if job_id in job_ops:
                job_max = max(end_time for _, _, end_time in job_ops[job_id])
                max_completion = max(max_completion, job_max)
        
        if c_max < max_completion:
            errors.append(f"C_max ({c_max}) is less than maximum completion time ({max_completion})")
        
        # Check 6: C_max should equal maximum completion time
        if c_max != max_completion:
            errors.append(f"C_max ({c_max}) is not equal to maximum completion time ({max_completion})")
        
        # Check 7: End time = start time + processing time
        for job_id, machine_id, start_time, end_time in operations:
            if end_time <= start_time:
                errors.append(f"Job {job_id} operation on machine {machine_id}: "
                            f"end_time ({end_time}) <= start_time ({start_time})")
            
            # Check processing time correctness
            processing_time = end_time - start_time
            p1, p2, p3, r = tasks[job_id]
            expected_time = [p1, p2, p3][machine_id]
            
            if processing_time != expected_time:
                errors.append(f"Job {job_id} operation on machine {machine_id}: "
                            f"processing time {processing_time}, expected {expected_time}")
        
        # Check 8: Each job should have exactly one operation on each machine
        job_machine_ops = {}  # job_id -> {machine_id: (start, end)}
        for job_id, machine_id, start_time, end_time in operations:
            if job_id not in job_machine_ops:
                job_machine_ops[job_id] = {}
            
            if machine_id in job_machine_ops[job_id]:
                errors.append(f"Job {job_id} has two operations on machine {machine_id}")
            else:
                job_machine_ops[job_id][machine_id] = (start_time, end_time)
        
        # Check that each job has operations on all 3 machines
        for job_id in range(n):
            if job_id not in job_machine_ops:
                errors.append(f"Job {job_id} has no operations")
            else:
                for machine_id in range(3):
                    if machine_id not in job_machine_ops[job_id]:
                        errors.append(f"Job {job_id} has no operation on machine {machine_id}")
        
        # Check 9: Operations on same machine don't overlap
        machine_ops = {}  # machine_id -> [(job_id, start, end), ...]
        for job_id, machine_id, start_time, end_time in operations:
            if machine_id not in machine_ops:
                machine_ops[machine_id] = []
            machine_ops[machine_id].append((job_id, start_time, end_time))
        
        for machine_id in range(3):
            if machine_id not in machine_ops:
                continue
            
            ops = sorted(machine_ops[machine_id], key=lambda x: x[1])  # Sort by start_time
            for i in range(len(ops)):
                for j in range(i + 1, len(ops)):
                    job1, start1, end1 = ops[i]
                    job2, start2, end2 = ops[j]
                    
                    # Check overlap
                    if not (end1 <= start2 or start1 >= end2):
                        errors.append(f"Operations on machine {machine_id} overlap: "
                                     f"job {job1} [{start1}, {end1}) and job {job2} [{start2}, {end2})")
        
        is_correct = len(errors) == 0
        return is_correct, errors
        
    except Exception as e:
        errors.append(f"Error during verification: {e}")
        return False, errors


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python verifier_correctness.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    is_correct, errors = verify_correctness(input_file, output_file)
    
    if is_correct:
        print("✓ Solution is correct")
    else:
        print("✗ Solution contains errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

