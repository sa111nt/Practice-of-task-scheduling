import os
import subprocess

# Configuration
MY_INDEX = "158740"
STUDENT_INDICES = ["156007", "155890","155909", "156027", "158740", "156020", "144678", 
                   "155886", "153918", "155805", "155937", 
                   "155895", "148080", "156143"]

IN_DIR = "instances/in"
OUT_DIR = "instances/out"
ALGORITHM = f"algorithm_{MY_INDEX}.py"

def read_criterion_value(output_file):
    """Reads criterion value from file"""
    try:
        with open(output_file, 'r') as f:
            return float(f.readline().strip())
    except:
        return None

def calculate_time_limit(n):
    """Time limit: n/10 seconds"""
    return n / 10.0

def run_algorithm():
    """Runs algorithm for all instances"""
    
    # Create output directory
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # Table header
    print("\nAlgorithm results (Early Work):")
    print("=" * 140)
    print(f"{'Student':<10}", end="")
    for n in range(50, 501, 50):
        print(f"  {n:>8}  ", end="")
    print("\n" + "=" * 140)
    
    # Process each student
    for student_idx in STUDENT_INDICES:
        print(f"{student_idx:<10}", end="", flush=True)
        
        for n in range(50, 501, 50):
            input_file = os.path.join(IN_DIR, f"in_{student_idx}_{n}.txt")
            output_file = os.path.join(OUT_DIR, f"out_{MY_INDEX}_{student_idx}_{n}.txt")
            
            if not os.path.exists(input_file):
                print(f"{'  MISS  ':>8}", end="", flush=True)
                continue
            
            time_limit = calculate_time_limit(n)
            
            # Run algorithm
            try:
                result = subprocess.run(
                    ['python', ALGORITHM, input_file, output_file, str(time_limit)],
                    timeout=time_limit + 10,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Read result
                    criterion = read_criterion_value(output_file)
                    if criterion is not None:
                        print(f"  {criterion:>8.2f}  ", end="", flush=True)
                    else:
                        print(f"{'ERROR':>8}", end="", flush=True)
                else:
                    print(f"{'ERROR':>8}", end="", flush=True)
                    
            except subprocess.TimeoutExpired:
                print(f"{'TIMEOUT':>8}", end="", flush=True)
            except Exception as e:
                print(f"{'ERROR':>8}", end="", flush=True)
        
        print()  # New line after student
    
    print("=" * 140)
    print(f"\nOutput files saved to: {OUT_DIR}/")
    print("\nCopy results from console to Excel!")

if __name__ == "__main__":
    run_algorithm()