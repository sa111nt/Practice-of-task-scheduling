import random
import sys

def generate_instance(n, filename):
    """Generates difficult instance of problem Q5|rj|∑Xj"""
    
    # Generate machine speed coefficients
    # Greater diversity = harder problem
    b = [1.0]
    
    # 40% chance for very slow machines
    for i in range(4):
        if random.random() < 0.4:
            b.append(round(random.uniform(1.6, 2.0), 1))
        else:
            b.append(round(random.uniform(1.1, 1.7), 1))
    
    random.shuffle(b)
    
    # Parameters for harder instances
    avg_time = n * 12  # Reduced from 20 to 12 - more conflicts
    
    tasks = []
    
    # Create task "clusters" - groups with similar r_j (resource conflicts)
    num_clusters = max(3, n // 30)
    cluster_centers = sorted([random.randint(0, int(avg_time * 0.6)) 
                              for _ in range(num_clusters)])
    
    for i in range(n):
        # Choose cluster for this task
        cluster = cluster_centers[i % len(cluster_centers)]
        
        # Generate parameters around cluster
        cluster_spread = 100  # Spread around cluster center
        
        # Processing time - varied
        if i % 4 == 0:  # 25% long tasks
            p_j = random.randint(max(40, n // 3), max(80, n))
        elif i % 4 == 1:  # 25% very short tasks
            p_j = random.randint(5, max(15, n // 10))
        else:  # 50% medium tasks
            p_j = random.randint(max(15, n // 8), max(40, n // 2))
        
        # Ready time - around cluster
        r_j = max(0, cluster + random.randint(-cluster_spread, cluster_spread))
        
        # Expected completion deadline - TIGHT DEADLINES
        # Reduced slack = harder problem
        slack_multiplier = random.uniform(1.1, 1.8)  # Was 1.0 to 3.0
        d_j = int(r_j + p_j * slack_multiplier)
        
        # Additional difficulty: some tasks have VERY tight deadlines
        if random.random() < 0.2:  # 20% of tasks with extremely tight deadlines
            slack_multiplier = random.uniform(1.0, 1.3)
            d_j = int(r_j + p_j * slack_multiplier)
        
        tasks.append((p_j, r_j, d_j))
    
    # Random shuffle
    random.shuffle(tasks)
    
    # Write to file
    with open(filename, 'w') as f:
        f.write(f"{n}\n")
        f.write(" ".join(f"{x:.1f}" for x in b) + "\n")
        for p_j, r_j, d_j in tasks:
            f.write(f"{p_j} {r_j} {d_j}\n")
    
    print(f"Generated difficult instance: {filename} (n={n})")
    
    # Optional statistics (set to True to see)
    if False:
        avg_p = sum(t[0] for t in tasks) / len(tasks)
        avg_slack = sum((t[2] - t[1] - t[0]) for t in tasks) / len(tasks)
        avg_r = sum(t[1] for t in tasks) / len(tasks)
        print(f"  Statistics:")
        print(f"    Average p_j: {avg_p:.1f}")
        print(f"    Average slack: {avg_slack:.1f}")
        print(f"    Average r_j: {avg_r:.1f}")
        print(f"    Speed coefficients b: {b}")

if __name__ == "__main__":
    index = "158740"
    
    # Optionally: set seed for reproducibility
    # random.seed(158740)
    
    # Generate 10 instances (n = 50, 100, ..., 500)
    for n in range(50, 501, 50):
        filename = f"in_{index}_{n}.txt"
        generate_instance(n, filename)