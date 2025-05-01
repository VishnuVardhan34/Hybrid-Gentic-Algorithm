import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import random
from typing import List, Dict, Tuple, Any
import seaborn as sns

def create_vm_assignment_graph(
    schedule_data: Dict[str, Any],
    algorithm_name: str,
    output_file: str = None,
    show_plot: bool = True
):
    """
    Generate a graph showing process to VM assignments.
    
    Args:
        schedule_data: Schedule data from algorithm's decode_solution method
        algorithm_name: Name of the algorithm used
        output_file: Output file path to save the graph
        show_plot: Whether to display the plot
    """
    # Extract the schedule and other metadata
    detailed_schedule = schedule_data['schedule']  # (task_id, resource_id, start_time, finish_time)
    makespan = schedule_data['makespan']
    avg_utilization = schedule_data['avg_utilization']
    
    # Group tasks by VM
    vms = {}
    for task_id, vm_id, start_time, finish_time in detailed_schedule:
        if vm_id not in vms:
            vms[vm_id] = []
        vms[vm_id].append((task_id, start_time, finish_time))
    
    # Sort VMs by key
    vm_ids = sorted(vms.keys())
    
    # Prepare figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Set a colorful palette
    palette = sns.color_palette("husl", len(detailed_schedule))
    random.shuffle(palette)  # Shuffle to make adjacent tasks have different colors
    
    # Plot tasks as bars on their assigned VMs
    for vm_idx, vm_id in enumerate(vm_ids):
        tasks = vms[vm_id]
        # Sort tasks by start time
        tasks.sort(key=lambda x: x[1])
        
        for task_id, start_time, finish_time in tasks:
            # Find the index of this task in the original schedule
            task_idx = next(i for i, t in enumerate(detailed_schedule) if t[0] == task_id)
            
            # Plot task as a horizontal bar
            ax.barh(
                vm_id, 
                finish_time - start_time, 
                left=start_time, 
                height=0.6, 
                color=palette[task_idx % len(palette)],
                alpha=0.8,
                edgecolor='black',
                linewidth=0.5
            )
            
            # Add task label if the bar is wide enough
            if finish_time - start_time > makespan * 0.03:
                ax.text(
                    start_time + (finish_time - start_time) / 2, 
                    vm_id,
                    f'T{task_id}',
                    ha='center', 
                    va='center',
                    fontsize=8,
                    fontweight='bold',
                    color='white'
                )
    
    # Set labels and title
    ax.set_title(f'Process to VM Assignment - {algorithm_name}', fontsize=16)
    ax.set_xlabel('Time Units', fontsize=12)
    ax.set_ylabel('Virtual Machine (VM) ID', fontsize=12)
    
    # Set y-axis ticks
    ax.set_yticks(vm_ids)
    ax.set_yticklabels([f'VM {vm_id}' for vm_id in vm_ids])
    
    # Add grid for better readability
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    
    # Add information about the schedule
    info_text = f'Makespan: {makespan:.1f} | Resource Utilization: {avg_utilization*100:.1f}% | Tasks: {len(detailed_schedule)}'
    fig.text(0.5, 0.02, info_text, ha='center', fontsize=12)
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    
    # Save plot if output_file provided
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()

def generate_process_vm_csv(
    schedule_data: Dict[str, Any],
    output_file: str
):
    """
    Generate a CSV file containing process to VM assignments.
    
    Args:
        schedule_data: Schedule data from algorithm's decode_solution method
        output_file: Output file path to save the CSV
    """
    # Extract the schedule
    detailed_schedule = schedule_data['schedule']  # (task_id, resource_id, start_time, finish_time)
    
    # Create DataFrame
    df = pd.DataFrame(detailed_schedule, columns=['process_id', 'vm_id', 'start_time', 'finish_time'])
    
    # Calculate process duration
    df['duration'] = df['finish_time'] - df['start_time']
    
    # Update column names for better clarity
    df = df.rename(columns={
        'process_id': 'ProcessID',
        'vm_id': 'VMID',
        'start_time': 'StartTime',
        'finish_time': 'EndTime',
        'duration': 'ExecutionTime'
    })
    
    # Sort by VM ID and start time
    df = df.sort_values(['VMID', 'StartTime'])
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    
    print(f"Process to VM assignment CSV saved to {output_file}")
    return df

def create_multi_algorithm_vm_graph(
    schedule_results: Dict[str, Dict],
    output_file: str = None,
    show_plot: bool = True
):
    """
    Generate a comparison of VM assignments across different algorithms.
    
    Args:
        schedule_results: Dictionary with algorithm name as key and schedule data as value
        output_file: Output file path to save the graph
        show_plot: Whether to display the plot
    """
    # Determine the number of algorithms
    num_algorithms = len(schedule_results)
    
    # Create a figure with subplots
    fig, axes = plt.subplots(num_algorithms, 1, figsize=(16, 5 * num_algorithms))
    
    # If only one algorithm, wrap axes in a list for consistent indexing
    if num_algorithms == 1:
        axes = [axes]
    
    # Process each algorithm
    for i, (algo_name, schedule_data) in enumerate(schedule_results.items()):
        ax = axes[i]
        
        # Extract the schedule and other metadata
        detailed_schedule = schedule_data['schedule']  # (task_id, resource_id, start_time, finish_time)
        makespan = schedule_data['makespan']
        avg_utilization = schedule_data['avg_utilization']
        
        # Group tasks by VM
        vms = {}
        for task_id, vm_id, start_time, finish_time in detailed_schedule:
            if vm_id not in vms:
                vms[vm_id] = []
            vms[vm_id].append((task_id, start_time, finish_time))
        
        # Sort VMs by key
        vm_ids = sorted(vms.keys())
        
        # Set a colorful palette
        palette = sns.color_palette("husl", len(detailed_schedule))
        random.shuffle(palette)  # Shuffle to make adjacent tasks have different colors
        
        # Plot tasks as bars on their assigned VMs
        for vm_idx, vm_id in enumerate(vm_ids):
            tasks = vms[vm_id]
            # Sort tasks by start time
            tasks.sort(key=lambda x: x[1])
            
            for task_id, start_time, finish_time in tasks:
                # Find the index of this task in the original schedule
                task_idx = next(i for i, t in enumerate(detailed_schedule) if t[0] == task_id)
                
                # Plot task as a horizontal bar
                ax.barh(
                    vm_id, 
                    finish_time - start_time, 
                    left=start_time, 
                    height=0.6, 
                    color=palette[task_idx % len(palette)],
                    alpha=0.8,
                    edgecolor='black',
                    linewidth=0.5
                )
                
                # Add task label if the bar is wide enough
                if finish_time - start_time > makespan * 0.03:
                    ax.text(
                        start_time + (finish_time - start_time) / 2, 
                        vm_id,
                        f'T{task_id}',
                        ha='center', 
                        va='center',
                        fontsize=8,
                        fontweight='bold',
                        color='white'
                    )
        
        # Set labels and title
        ax.set_title(f'{algo_name} - Makespan: {makespan:.1f}, Utilization: {avg_utilization*100:.1f}%', fontsize=14)
        ax.set_xlabel('Time Units', fontsize=10)
        ax.set_ylabel('VM ID', fontsize=10)
        
        # Set y-axis ticks
        ax.set_yticks(vm_ids)
        ax.set_yticklabels([f'VM {vm_id}' for vm_id in vm_ids])
        
        # Add grid for better readability
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save plot if output_file provided
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()

def process_vm_summary(csv_file: str):
    """
    Generate a summary of process to VM assignments from a CSV file.
    
    Args:
        csv_file: Path to the CSV file
    """
    # Load CSV
    df = pd.read_csv(csv_file)
    
    # Calculate statistics
    vm_count = df['VMID'].nunique()
    process_count = df['ProcessID'].nunique()
    avg_processes_per_vm = df.groupby('VMID').size().mean()
    avg_execution_time = df['ExecutionTime'].mean()
    max_execution_time = df['ExecutionTime'].max()
    min_execution_time = df['ExecutionTime'].min()
    
    # Print summary
    print(f"Process to VM Assignment Summary")
    print(f"--------------------------------")
    print(f"Number of VMs: {vm_count}")
    print(f"Number of Processes: {process_count}")
    print(f"Average Processes per VM: {avg_processes_per_vm:.2f}")
    print(f"Average Execution Time: {avg_execution_time:.2f}")
    print(f"Max Execution Time: {max_execution_time:.2f}")
    print(f"Min Execution Time: {min_execution_time:.2f}")
    print(f"--------------------------------")
    
    # VM load balance
    print("\nVM Load Distribution:")
    vm_counts = df.groupby('VMID').size()
    for vm, count in vm_counts.items():
        print(f"VM {vm}: {count} processes ({count/process_count*100:.1f}%)")

if __name__ == "__main__":
    # Example usage (will be replaced by main.py integration)
    pass
