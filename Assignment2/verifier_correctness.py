import sys

def read_input(input_file):
    """Reads input data"""
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())
    b = list(map(float, lines[1].strip().split()))
    
    tasks = []
    for i in range(2, n + 2):
        parts = lines[i].strip().split()
        p_j = int(parts[0])
        r_j = int(parts[1])
        d_j = int(parts[2])
        tasks.append((p_j, r_j, d_j))
    
    return n, b, tasks

def read_output(output_file):
    """Reads solution"""
    with open(output_file, 'r') as f:
        lines = f.readlines()
    
    criterion_value = float(lines[0].strip())
    
    schedules = []
    for i in range(1, 6):
        line = lines[i].strip()
        if line:
            schedule = list(map(int, line.split()))
        else:
            schedule = []
        schedules.append(schedule)
    
    return criterion_value, schedules

def validate_solution(input_file, output_file):
    """Validates solution correctness"""
    try:
        n, b, tasks = read_input(input_file)
        criterion_value, schedules = read_output(output_file)
        
        # Check if each task appears exactly once
        all_tasks = []
        for schedule in schedules:
            all_tasks.extend(schedule)
        
        if len(all_tasks) != n:
            return False, f"ERROR: Number of tasks in solution ({len(all_tasks)}) != n ({n})"
        
        if sorted(all_tasks) != list(range(1, n + 1)):
            return False, "ERROR: Not all tasks appear exactly once"
        
        # Calculate actual criterion value
        total_early_work = 0.0
        
        for machine_idx, schedule in enumerate(schedules):
            current_time = 0.0
            speed_factor = b[machine_idx]
            
            for task_id in schedule:
                task_idx = task_id - 1
                p_j, r_j, d_j = tasks[task_idx]
                
                # Actual processing time on this machine
                actual_p_j = p_j * speed_factor
                
                # Task cannot start before r_j
                start_time = max(current_time, r_j)
                completion_time = start_time + actual_p_j
                
                # Calculate X_j = min{max{d_j - C_j + p_j * b_k, 0}, p_j * b_k}
                early_part = max(d_j - completion_time + p_j * speed_factor, 0)
                X_j = min(early_part, p_j * speed_factor)
                
                total_early_work += X_j
                current_time = completion_time
        
        # Round to integer value (as in algorithm)
        rounded_total = round(total_early_work)
        
        # Compare with given value
        if rounded_total != criterion_value:
            return False, f"ERROR: Criterion value mismatch. Calculated: {rounded_total}, Given: {criterion_value}"
        
        return True, f"OK: Criterion value = {criterion_value}"
    
    except Exception as e:
        return False, f"ERROR: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python verifier_correctness.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    valid, message = validate_solution(input_file, output_file)
    print(message)
    
    sys.exit(0 if valid else 1)