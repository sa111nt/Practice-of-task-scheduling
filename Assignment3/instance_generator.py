#!/usr/bin/env python3
"""
Instance generator for O3|r_j|C_max problem (Open Shop, 3 machines)

Problem:
- 3 machines
- n jobs, each consists of 3 operations (one per machine)
- p_ij - processing time of operation j on machine i
- r_j - release time of job j
- Goal: minimize C_max (makespan)

Output format:
n
p_11 p_12 p_13 r_1
p_21 p_22 p_23 r_2
...
p_n1 p_n2 p_n3 r_n
"""

import random
import os
import argparse


def generate_instance(n: int, 
                      p_min: int = 1, 
                      p_max: int = 20,
                      r_density: float = 0.7,
                      r_spread: float = 0.3) -> list:
    """Generates instance for O3|r_j|C_max problem"""
    tasks = []
    
    # Estimate planning horizon for r_j generation
    # In Open Shop with 3 machines, lower bound for C_max is approximately:
    # max(sum(p_ij) over all j for each machine i, max(sum(p_ij) over i for each j))
    avg_p = (p_min + p_max) / 2
    estimated_horizon = int(n * avg_p * r_spread)
    
    for j in range(n):
        # Generate processing times on each machine
        # Use different strategies to create interesting instances
        
        strategy = random.choice(['uniform', 'one_heavy', 'balanced', 'varied'])
        
        if strategy == 'uniform':
            # All operations approximately equal
            base = random.randint(p_min, p_max)
            p1 = max(p_min, min(p_max, base + random.randint(-2, 2)))
            p2 = max(p_min, min(p_max, base + random.randint(-2, 2)))
            p3 = max(p_min, min(p_max, base + random.randint(-2, 2)))
            
        elif strategy == 'one_heavy':
            # One operation significantly longer than others
            heavy_machine = random.randint(0, 2)
            ops = [random.randint(p_min, p_min + (p_max - p_min) // 3) for _ in range(3)]
            ops[heavy_machine] = random.randint(p_max - (p_max - p_min) // 3, p_max)
            p1, p2, p3 = ops
            
        elif strategy == 'balanced':
            # Balanced operations (sum approximately constant)
            total = random.randint(3 * p_min + 10, 3 * p_max - 10)
            p1 = random.randint(p_min, min(p_max, total - 2 * p_min))
            remaining = total - p1
            p2 = random.randint(p_min, min(p_max, remaining - p_min))
            p3 = max(p_min, min(p_max, remaining - p2))
            
        else:  # varied
            # Completely random
            p1 = random.randint(p_min, p_max)
            p2 = random.randint(p_min, p_max)
            p3 = random.randint(p_min, p_max)
        
        # Generate release time r_j
        if random.random() < (1 - r_density):
            # Some jobs ready from the start
            r = 0
        else:
            # Release time distributed over planning horizon
            # Use different distributions for variety
            dist_type = random.choice(['uniform', 'early', 'spread'])
            
            if dist_type == 'uniform':
                r = random.randint(0, estimated_horizon)
            elif dist_type == 'early':
                # More jobs at the beginning (exponential distribution)
                r = int(random.expovariate(3.0 / estimated_horizon) * estimated_horizon / 3)
                r = min(r, estimated_horizon)
            else:  # spread
                # Uniformly by quantiles
                quantile = j / n
                r = int(quantile * estimated_horizon * random.uniform(0.5, 1.5))
        
        tasks.append((p1, p2, p3, r))
    
    # Shuffle jobs so r_j are not sorted
    random.shuffle(tasks)
    
    return tasks


def write_instance(tasks: list, filename: str):
    """Writes instance to file in required format"""
    n = len(tasks)
    
    with open(filename, 'w') as f:
        f.write(f"{n}\n")
        for p1, p2, p3, r in tasks:
            f.write(f"{p1} {p2} {p3} {r}\n")
    
    print(f"Created file: {filename} ({n} jobs)")


def generate_all_instances(student_id: str, 
                           output_dir: str = ".",
                           sizes: list = None):
    """Generates all required instances (from 50 to 500 with step 50)"""
    if sizes is None:
        sizes = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating instances for student {student_id}")
    print(f"Directory: {output_dir}")
    print("-" * 50)
    
    for n in sizes:
        # Adapt parameters depending on instance size
        # For large instances, slightly modify parameters
        
        if n <= 100:
            p_min, p_max = 1, 20
            r_density = 0.95
            r_spread = 0.25
        elif n <= 300:
            p_min, p_max = 1, 20
            r_density = 0.95
            r_spread = 0.30
        else:
            p_min, p_max = 1, 20
            r_density = 0.95
            r_spread = 0.35
        
        # Generate instance
        tasks = generate_instance(
            n=n,
            p_min=p_min,
            p_max=p_max,
            r_density=r_density,
            r_spread=r_spread
        )
        
        # Form filename
        filename = os.path.join(output_dir, f"in_{student_id}_{n}.txt")
        
        # Write to file
        write_instance(tasks, filename)
        
        # Print statistics
        total_p = sum(p1 + p2 + p3 for p1, p2, p3, r in tasks)
        max_r = max(r for _, _, _, r in tasks)
        avg_r = sum(r for _, _, _, r in tasks) / n
        nonzero_r = sum(1 for _, _, _, r in tasks if r > 0)
        
        print(f"  n={n:3d}: total_p={total_p:6d}, max_r={max_r:4d}, "
              f"avg_r={avg_r:6.1f}, nonzero_r={nonzero_r:3d} ({100*nonzero_r/n:.0f}%)")
    
    print("-" * 50)
    print(f"Done! Created {len(sizes)} instances.")


def validate_instance(filename: str) -> bool:
    """Validates instance file format"""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        n = int(lines[0].strip())
        
        if len(lines) != n + 1:
            print(f"ERROR: Expected {n+1} lines, got {len(lines)}")
            return False
        
        for i, line in enumerate(lines[1:], 1):
            parts = line.strip().split()
            if len(parts) != 4:
                print(f"ERROR: Line {i+1} should contain 4 numbers, got {len(parts)}")
                return False
            
            p1, p2, p3, r = map(int, parts)
            
            if p1 <= 0 or p2 <= 0 or p3 <= 0:
                print(f"ERROR: Line {i+1}: processing times must be > 0")
                return False
            
            if r < 0:
                print(f"ERROR: Line {i+1}: release time must be >= 0")
                return False
        
        print(f"File {filename} is valid ({n} jobs)")
        return True
        
    except Exception as e:
        print(f"ERROR reading file: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Instance generator for O3|r_j|C_max problem"
    )
    parser.add_argument(
        "--student-id", "-s",
        type=str,
        default="158740",
        help="Student index number (default: 158740)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default=".",
        help="Directory for saving files (default: current)"
    )
    parser.add_argument(
        "--sizes", "-n",
        type=str,
        default="50,100,150,200,250,300,350,400,450,500",
        help="Instance sizes separated by comma (default: 50,100,...,500)"
    )
    parser.add_argument(
        "--validate", "-v",
        type=str,
        default=None,
        help="Validate specified file"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random number generator seed (for reproducibility)"
    )
    
    args = parser.parse_args()
    
    # Set seed if specified
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Seed set: {args.seed}")
    
    # Validation mode
    if args.validate:
        validate_instance(args.validate)
    else:
        # Generation mode
        sizes = [int(x.strip()) for x in args.sizes.split(",")]
        generate_all_instances(
            student_id=args.student_id,
            output_dir=args.output_dir,
            sizes=sizes
        )