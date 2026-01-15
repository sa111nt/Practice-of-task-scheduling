#!/usr/bin/env python3
"""
Verifies algorithm execution time.

Checks that algorithm runs in reasonable time.
"""

import sys
import time
from typing import Tuple
from algorithm import solve_open_shop


def verify_time(input_file: str, max_time_seconds: float = 300.0) -> Tuple[bool, float]:
    """Verifies algorithm execution time"""
    output_file = "/tmp/test_output.txt"  # Temporary file
    
    start_time = time.time()
    
    try:
        solve_open_shop(input_file, output_file)
    except Exception as e:
        print(f"Error executing algorithm: {e}")
        return False, 0.0
    
    end_time = time.time()
    actual_time = end_time - start_time
    
    is_within_limit = actual_time <= max_time_seconds
    
    return is_within_limit, actual_time


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verifier_time.py <input_file> [max_time_seconds]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    max_time = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0
    
    is_within_limit, actual_time = verify_time(input_file, max_time)
    
    print(f"Execution time: {actual_time:.3f} seconds")
    
    if is_within_limit:
        print(f"✓ Execution time within limit ({max_time} seconds)")
    else:
        print(f"✗ Execution time exceeds limit ({max_time} seconds)")
        sys.exit(1)

