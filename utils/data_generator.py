import csv
import random
import os
from typing import List, Dict, Tuple

def generate_task_data(
    num_tasks: int, 
    num_resources: int, 
    arrival_time_range: Tuple[int, int] = (0, 100),
    execution_time_range: Tuple[int, int] = (5, 50),
    deadline_range: Tuple[int, int] = (20, 200),
    resource_requirement_range: Tuple[int, int] = (1, 10),
    filename: str = None
) -> List[Dict]:
    """
    Generate task data for cloud computing scheduling simulations.
    
    Args:
        num_tasks: Number of tasks to generate
        num_resources: Number of cloud resources available
        arrival_time_range: Range for task arrival times (min, max)
        execution_time_range: Range for task execution times (min, max)
        deadline_range: Range for task deadlines (min, max)
        resource_requirement_range: Range for resource requirements (min, max)
        filename: Optional filename to save the data as CSV
        
    Returns:
        List of task dictionaries with task properties
    """
    tasks = []
    
    for task_id in range(1, num_tasks + 1):
        arrival_time = random.randint(*arrival_time_range)
        execution_time = random.randint(*execution_time_range)
        deadline = arrival_time + execution_time + random.randint(10, deadline_range[1] - execution_time)
        priority = random.randint(1, 5)  # 1 to 5, where 5 is highest priority
        
        # Resource requirements (CPU, memory, etc.)
        resource_reqs = {}
        for res_id in range(1, num_resources + 1):
            resource_reqs[f"resource_{res_id}"] = random.randint(*resource_requirement_range)
            
        task = {
            "task_id": task_id,
            "arrival_time": arrival_time,
            "execution_time": execution_time,
            "deadline": deadline,
            "priority": priority
        }
        
        # Add resource requirements to the task
        task.update(resource_reqs)
        tasks.append(task)
    
    # Sort by arrival time
    tasks.sort(key=lambda x: x["arrival_time"])
    
    # Save to CSV if filename provided
    if filename:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', newline='') as csvfile:
            if tasks:
                fieldnames = tasks[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(tasks)
    
    return tasks

def generate_datasets(
    output_dir: str,
    sizes: List[int] = [50, 100, 200, 500, 1000, 10000, 100000],
    num_resources: int = 5
) -> List[str]:
    """
    Generate multiple datasets of different sizes and save them to CSV files.
    Optimized to handle large datasets efficiently.
    
    Args:
        output_dir: Directory to save the datasets
        sizes: List of task sizes to generate
        num_resources: Number of resources to consider
        
    Returns:
        List of paths to the generated CSV files
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []
    
    for size in sizes:
        filename = os.path.join(output_dir, f"tasks_{size}.csv")
        
        # Check if file already exists
        if os.path.exists(filename):
            print(f"Dataset with {size} tasks already exists: {filename}")
            generated_files.append(filename)
            continue
        
        # For very large datasets, use batch processing
        if size > 10000:
            print(f"Generating large dataset with {size} tasks (batch processing)...")
            # Open file and write header
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = [
                    'task_id', 'arrival_time', 'execution_time', 'deadline', 'priority'
                ] + [f'resource_{i}' for i in range(1, num_resources + 1)]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Process in batches of 10,000
                batch_size = 10000
                for batch_start in range(1, size + 1, batch_size):
                    batch_end = min(batch_start + batch_size - 1, size)
                    print(f"  Processing tasks {batch_start}-{batch_end}...")
                    
                    batch_tasks = []
                    for task_id in range(batch_start, batch_end + 1):
                        arrival_time = random.randint(*arrival_time_range)
                        execution_time = random.randint(*execution_time_range)
                        deadline = arrival_time + execution_time + random.randint(10, deadline_range[1] - execution_time)
                        priority = random.randint(1, 5)  # 1 to 5, where 5 is highest priority
                        
                        # Resource requirements (CPU, memory, etc.)
                        resource_reqs = {}
                        for res_id in range(1, num_resources + 1):
                            resource_reqs[f"resource_{res_id}"] = random.randint(*resource_requirement_range)
                            
                        task = {
                            "task_id": task_id,
                            "arrival_time": arrival_time,
                            "execution_time": execution_time,
                            "deadline": deadline,
                            "priority": priority
                        }
                        
                        # Add resource requirements to the task
                        task.update(resource_reqs)
                        batch_tasks.append(task)
                    
                    # Sort batch by arrival time
                    batch_tasks.sort(key=lambda x: x["arrival_time"])
                    
                    # Write batch to file
                    writer.writerows(batch_tasks)
        else:
            # For smaller datasets, use the standard approach
            generate_task_data(
                num_tasks=size,
                num_resources=num_resources,
                arrival_time_range=arrival_time_range,
                execution_time_range=execution_time_range,
                deadline_range=deadline_range,
                resource_requirement_range=resource_requirement_range,
                filename=filename
            )
            
        generated_files.append(filename)
        print(f"Generated dataset with {size} tasks: {filename}")
    
    return generated_files

# Define parameter ranges as module-level constants for consistency
arrival_time_range = (0, 100)
execution_time_range = (5, 50)
deadline_range = (20, 200)
resource_requirement_range = (1, 10)

if __name__ == "__main__":
    # Example usage
    output_dir = "../data"
    generate_datasets(output_dir)
