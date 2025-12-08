import sys 
import subprocess
import time

def validate_time(program_path, input_file, output_file, time_limit):
    """Validates program execution time"""
    try:
        start_time = time.time()
        
        result = subprocess.run(
            ['python', program_path, input_file, output_file, str(time_limit)],
            timeout=time_limit + 5,  # Additional margin
            capture_output=True,
            text=True
        )
        
        elapsed_time = time.time() - start_time
        
        if elapsed_time > time_limit:
            return False, elapsed_time, f"TIME={elapsed_time:.2f}s (exceeded limit {time_limit}s)"
        
        return True, elapsed_time, f"OK: Execution time = {elapsed_time:.2f}s"
    
    except subprocess.TimeoutExpired:
        return False, time_limit + 5, f"TIME={time_limit + 5}s (timeout)"
    except Exception as e:
        return False, 0, f"ERROR: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python verifier_time.py <program> <input> <output> <time_limit_seconds>")
        sys.exit(1)
    
    program_path = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    time_limit = float(sys.argv[4])
    
    valid, elapsed, message = validate_time(program_path, input_file, output_file, time_limit)
    print(message)
    
    sys.exit(0 if valid else 1)