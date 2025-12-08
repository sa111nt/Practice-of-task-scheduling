import sys
import time
import random
from copy import deepcopy

def read_input(filename):
    """Reads input data"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())
    b = list(map(float, lines[1].strip().split()))
    
    tasks = []
    for i in range(n):
        parts = lines[i + 2].strip().split()
        p_j = int(parts[0])
        r_j = int(parts[1])
        d_j = int(parts[2])
        tasks.append({'id': i + 1, 'p': p_j, 'r': r_j, 'd': d_j})
    
    return n, b, tasks

def calculate_early_work(C_j, p_j, d_j, b_k):
    """Calculates early work X_j considering machine speed coefficient"""
    early_part = max(d_j - C_j + p_j * b_k, 0)
    return min(early_part, p_j * b_k)

def calculate_criterion(schedules, b, tasks):
    """Calculates criterion value ∑X_j"""
    task_dict = {task['id']: task for task in tasks}
    total_early_work = 0.0
    
    for machine_idx, schedule in enumerate(schedules):
        current_time = 0.0
        speed_factor = b[machine_idx]
        
        for task_id in schedule:
            if task_id not in task_dict:
                continue
            
            task = task_dict[task_id]
            p_j = task['p']
            r_j = task['r']
            d_j = task['d']
            
            actual_p_j = p_j * speed_factor
            start_time = max(current_time, r_j)
            completion_time = start_time + actual_p_j
            
            X_j = calculate_early_work(completion_time, p_j, d_j, speed_factor)
            total_early_work += X_j
            
            current_time = completion_time
    
    return total_early_work

def calculate_machine_completion_time(schedule, machine_idx, b, task_dict):
    """Calculates completion time for given machine"""
    current_time = 0.0
    speed_factor = b[machine_idx]
    
    for task_id in schedule:
        task = task_dict[task_id]
        actual_p_j = task['p'] * speed_factor
        start_time = max(current_time, task['r'])
        current_time = start_time + actual_p_j
    
    return current_time

def greedy_edf_algorithm(n, b, tasks):
    """
    Earliest Deadline First with intelligent machine selection
    """
    schedules = [[] for _ in range(5)]
    machine_times = [0.0] * 5
    task_dict = {task['id']: task for task in tasks}
    
    # Sort by deadline, then by ready time
    sorted_tasks = sorted(tasks, key=lambda t: (t['d'], t['r'], -t['p']))
    
    for task in sorted_tasks:
        task_id = task['id']
        p_j = task['p']
        r_j = task['r']
        d_j = task['d']
        
        best_machine = -1
        best_score = -float('inf')
        
        for machine_idx in range(5):
            speed_factor = b[machine_idx]
            actual_p_j = p_j * speed_factor
            
            start = max(machine_times[machine_idx], r_j)
            completion = start + actual_p_j
            
            early_work = calculate_early_work(completion, p_j, d_j, speed_factor)
            
            # Score prefers: high early work, fast machines, low load
            score = (early_work * 100 
                    - speed_factor * 50 
                    - machine_times[machine_idx] * 0.5)
            
            if score > best_score:
                best_score = score
                best_machine = machine_idx
        
        schedules[best_machine].append(task_id)
        speed_factor = b[best_machine]
        actual_p_j = p_j * speed_factor
        start = max(machine_times[best_machine], r_j)
        machine_times[best_machine] = start + actual_p_j
    
    return schedules

def greedy_slack_algorithm(n, b, tasks):
    """
    Algorithm based on slack time (time buffer)
    """
    schedules = [[] for _ in range(5)]
    machine_times = [0.0] * 5
    
    # Sort by slack time (smaller slack = higher priority)
    def slack_priority(task):
        slack = task['d'] - task['r'] - task['p']
        return (slack, task['d'], -task['p'])
    
    sorted_tasks = sorted(tasks, key=slack_priority)
    
    for task in sorted_tasks:
        task_id = task['id']
        p_j = task['p']
        r_j = task['r']
        d_j = task['d']
        
        best_machine = -1
        best_early_work = -float('inf')
        
        for machine_idx in range(5):
            speed_factor = b[machine_idx]
            actual_p_j = p_j * speed_factor
            
            start = max(machine_times[machine_idx], r_j)
            completion = start + actual_p_j
            
            early_work = calculate_early_work(completion, p_j, d_j, speed_factor)
            
            # Prefer faster machines for tasks with small slack
            adjusted_early_work = early_work / (speed_factor ** 0.5)
            
            if adjusted_early_work > best_early_work:
                best_early_work = adjusted_early_work
                best_machine = machine_idx
        
        if best_machine == -1:
            best_machine = 0
        
        schedules[best_machine].append(task_id)
        speed_factor = b[best_machine]
        actual_p_j = p_j * speed_factor
        start = max(machine_times[best_machine], r_j)
        machine_times[best_machine] = start + actual_p_j
    
    return schedules

def lpt_algorithm(n, b, tasks):
    """
    Longest Processing Time first
    """
    schedules = [[] for _ in range(5)]
    machine_times = [0.0] * 5
    
    # Sort from longest tasks
    sorted_tasks = sorted(tasks, key=lambda t: (-t['p'], t['d']))
    
    for task in sorted_tasks:
        task_id = task['id']
        p_j = task['p']
        r_j = task['r']
        d_j = task['d']
        
        best_machine = -1
        best_score = -float('inf')
        
        for machine_idx in range(5):
            speed_factor = b[machine_idx]
            actual_p_j = p_j * speed_factor
            
            start = max(machine_times[machine_idx], r_j)
            completion = start + actual_p_j
            
            early_work = calculate_early_work(completion, p_j, d_j, speed_factor)
            
            # For LPT: balance machine load
            score = early_work * 50 - machine_times[machine_idx]
            
            if score > best_score:
                best_score = score
                best_machine = machine_idx
        
        schedules[best_machine].append(task_id)
        speed_factor = b[best_machine]
        actual_p_j = p_j * speed_factor
        start = max(machine_times[best_machine], r_j)
        machine_times[best_machine] = start + actual_p_j
    
    return schedules

def local_search_swap(schedules, b, tasks, time_limit, start_time):
    """
    Local search: swap tasks between machines
    """
    task_dict = {task['id']: task for task in tasks}
    improved = True
    iterations = 0
    
    while improved and time.time() - start_time < time_limit * 0.85:
        improved = False
        iterations += 1
        current_value = calculate_criterion(schedules, b, tasks)
        
        # Try to swap each task
        for from_m in range(5):
            if time.time() - start_time > time_limit * 0.85:
                break
            
            for i in range(len(schedules[from_m])):
                task_id = schedules[from_m][i]
                
                for to_m in range(5):
                    if from_m == to_m:
                        continue
                    
                    # Move task
                    test_schedules = deepcopy(schedules)
                    test_schedules[from_m].pop(i)
                    test_schedules[to_m].append(task_id)
                    
                    new_value = calculate_criterion(test_schedules, b, tasks)
                    
                    if new_value > current_value + 0.01:
                        schedules = test_schedules
                        current_value = new_value
                        improved = True
                        break
                
                if improved:
                    break
            
            if improved:
                break
    
    return schedules

def local_search_reorder(schedules, b, tasks, time_limit, start_time):
    """
    Local search: change task order on the same machine
    """
    task_dict = {task['id']: task for task in tasks}
    improved = True
    iterations = 0
    max_iterations = 50
    
    while improved and iterations < max_iterations and time.time() - start_time < time_limit * 0.9:
        improved = False
        iterations += 1
        current_value = calculate_criterion(schedules, b, tasks)
        
        for machine_idx in range(5):
            if time.time() - start_time > time_limit * 0.9:
                break
            
            schedule = schedules[machine_idx]
            if len(schedule) < 2:
                continue
            
            # Try to swap adjacent tasks
            for i in range(len(schedule) - 1):
                test_schedules = deepcopy(schedules)
                # Swap positions i and i+1
                test_schedules[machine_idx][i], test_schedules[machine_idx][i+1] = \
                    test_schedules[machine_idx][i+1], test_schedules[machine_idx][i]
                
                new_value = calculate_criterion(test_schedules, b, tasks)
                
                if new_value > current_value + 0.01:
                    schedules = test_schedules
                    current_value = new_value
                    improved = True
                    break
            
            if improved:
                break
    
    return schedules

def simulated_annealing(schedules, b, tasks, time_limit, start_time):
    """
    Simulated annealing - allows temporary solution degradation
    """
    task_dict = {task['id']: task for task in tasks}
    current_schedules = deepcopy(schedules)
    best_schedules = deepcopy(schedules)
    
    current_value = calculate_criterion(current_schedules, b, tasks)
    best_value = current_value
    
    temperature = 100.0
    cooling_rate = 0.95
    iterations = 0
    max_iterations = 200
    
    while iterations < max_iterations and time.time() - start_time < time_limit * 0.95:
        iterations += 1
        
        # Random modification
        test_schedules = deepcopy(current_schedules)
        
        if random.random() < 0.5:
            # Move random task to another machine
            from_m = random.randint(0, 4)
            if len(test_schedules[from_m]) > 0:
                to_m = random.randint(0, 4)
                if from_m != to_m:
                    task_idx = random.randint(0, len(test_schedules[from_m]) - 1)
                    task_id = test_schedules[from_m].pop(task_idx)
                    test_schedules[to_m].append(task_id)
        else:
            # Swap order on random machine
            machine_idx = random.randint(0, 4)
            if len(test_schedules[machine_idx]) >= 2:
                i = random.randint(0, len(test_schedules[machine_idx]) - 2)
                test_schedules[machine_idx][i], test_schedules[machine_idx][i+1] = \
                    test_schedules[machine_idx][i+1], test_schedules[machine_idx][i]
        
        new_value = calculate_criterion(test_schedules, b, tasks)
        delta = new_value - current_value
        
        # Accept if better, or with certain probability if worse
        if delta > 0 or random.random() < min(1.0, 2.71828 ** (delta / temperature)):
            current_schedules = test_schedules
            current_value = new_value
            
            if current_value > best_value:
                best_schedules = deepcopy(current_schedules)
                best_value = current_value
        
        temperature *= cooling_rate
    
    return best_schedules

def verify_solution(schedules, n):
    """Verifies if all tasks are in the schedule"""
    all_tasks = []
    for schedule in schedules:
        all_tasks.extend(schedule)
    
    if len(all_tasks) != n:
        return False, f"Number of tasks: {len(all_tasks)} != {n}"
    
    if len(set(all_tasks)) != n:
        return False, "Duplicate tasks found"
    
    if sorted(all_tasks) != list(range(1, n + 1)):
        return False, "Invalid task IDs"
    
    return True, "OK"

def solve_problem(n, b, tasks, time_limit):
    """Main function - hybrid approach with multiple strategies"""
    start_time = time.time()
    
    best_schedules = None
    best_value = -float('inf')
    
    # Strategy 1: EDF (10% of time)
    if time.time() - start_time < time_limit * 0.1:
        schedules1 = greedy_edf_algorithm(n, b, tasks)
        valid, _ = verify_solution(schedules1, n)
        if valid:
            value1 = calculate_criterion(schedules1, b, tasks)
            if value1 > best_value:
                best_value = value1
                best_schedules = schedules1
    
    # Strategy 2: Slack-based (10% of time)
    if time.time() - start_time < time_limit * 0.2:
        schedules2 = greedy_slack_algorithm(n, b, tasks)
        valid, _ = verify_solution(schedules2, n)
        if valid:
            value2 = calculate_criterion(schedules2, b, tasks)
            if value2 > best_value:
                best_value = value2
                best_schedules = schedules2
    
    # Strategy 3: LPT (10% of time)
    if time.time() - start_time < time_limit * 0.3:
        schedules3 = lpt_algorithm(n, b, tasks)
        valid, _ = verify_solution(schedules3, n)
        if valid:
            value3 = calculate_criterion(schedules3, b, tasks)
            if value3 > best_value:
                best_value = value3
                best_schedules = schedules3
    
    # If no solution, use simple one
    if best_schedules is None:
        best_schedules = greedy_edf_algorithm(n, b, tasks)
    
    # Improvement 1: Local Search - Swap (20% of time)
    if time.time() - start_time < time_limit * 0.5:
        best_schedules = local_search_swap(best_schedules, b, tasks, time_limit, start_time)
        best_value = calculate_criterion(best_schedules, b, tasks)
    
    # Improvement 2: Local Search - Reorder (20% of time)
    if time.time() - start_time < time_limit * 0.7:
        best_schedules = local_search_reorder(best_schedules, b, tasks, time_limit, start_time)
        best_value = calculate_criterion(best_schedules, b, tasks)
    
    # Improvement 3: Simulated Annealing (25% of time)
    if time.time() - start_time < time_limit * 0.95:
        best_schedules = simulated_annealing(best_schedules, b, tasks, time_limit, start_time)
    
    # Final verification
    valid, msg = verify_solution(best_schedules, n)
    if not valid:
        print(f"ERROR: {msg}", file=sys.stderr)
        best_schedules = greedy_edf_algorithm(n, b, tasks)
    
    return best_schedules

def write_output(filename, criterion_value, schedules):
    """Writes solution to file"""
    with open(filename, 'w') as f:
        rounded_value = round(criterion_value)
        f.write(f"{rounded_value}\n")
        for schedule in schedules:
            if schedule:
                f.write(" ".join(map(str, schedule)) + "\n")
            else:
                f.write("\n")

def solve(input_file, output_file, time_limit):
    """Main function"""
    n, b, tasks = read_input(input_file)
    
    schedules = solve_problem(n, b, tasks, time_limit)
    
    criterion_value = calculate_criterion(schedules, b, tasks)
    write_output(output_file, criterion_value, schedules)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python algorithm.py <input_file> <output_file> <time_limit>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    time_limit = float(sys.argv[3])
    
    solve(input_file, output_file, time_limit)