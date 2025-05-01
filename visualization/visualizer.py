import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import os

def plot_algorithm_comparison(
    results: Dict[str, List[Tuple[int, float, float]]],
    output_dir: str = None,
    metric: str = 'time',
    show_plot: bool = True
):
    """
    Plot algorithm comparison based on execution time or fitness.
    
    Args:
        results: Dictionary with algorithm name as key and list of (task_count, fitness, exec_time) tuples as value
        output_dir: Directory to save the plots
        metric: 'time' or 'fitness'
        show_plot: Whether to display the plot
    """
    # Create dataframe from results
    data = []
    for algo_name, algo_results in results.items():
        for task_count, fitness, exec_time in algo_results:
            data.append({
                'Algorithm': algo_name,
                'Tasks': task_count,
                'Fitness': fitness,
                'ExecutionTime': exec_time
            })
    
    df = pd.DataFrame(data)
    
    # Create plots
    plt.figure(figsize=(12, 6))
    
    if metric == 'time':
        # Plot execution time vs task count
        pivot_df = df.pivot(index='Tasks', columns='Algorithm', values='ExecutionTime')
        ax = pivot_df.plot(marker='o', linestyle='-')
        plt.title('Algorithm Execution Time Comparison')
        plt.xlabel('Number of Tasks')
        plt.ylabel('Execution Time (seconds)')
        plt.grid(True, linestyle='--', alpha=0.7)
    else:
        # Plot fitness vs task count
        pivot_df = df.pivot(index='Tasks', columns='Algorithm', values='Fitness')
        ax = pivot_df.plot(marker='o', linestyle='-')
        plt.title('Algorithm Solution Quality Comparison')
        plt.xlabel('Number of Tasks')
        plt.ylabel('Fitness (lower is better)')
        plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.legend(title='Algorithm')
    plt.tight_layout()
    
    # Save plot if output_dir provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, f'{metric}_comparison.png'), dpi=300)
    
    if show_plot:
        plt.show()
    else:
        plt.close()

def plot_resource_utilization(
    schedule_results: Dict[str, Dict],
    output_dir: str = None,
    show_plot: bool = True
):
    """
    Plot resource utilization for each algorithm.
    
    Args:
        schedule_results: Dictionary with algorithm name as key and decoded schedule results as value
        output_dir: Directory to save the plots
        show_plot: Whether to display the plot
    """
    plt.figure(figsize=(12, 6))
    
    # Extract resource utilization data
    algorithms = list(schedule_results.keys())
    resources = list(schedule_results[algorithms[0]]['resource_utilization'].keys())
    
    # Create data for plotting
    data = []
    for algo_name, results in schedule_results.items():
        utilization = results['resource_utilization']
        for resource, util_value in utilization.items():
            data.append({
                'Algorithm': algo_name,
                'Resource': resource,
                'Utilization': util_value * 100  # Convert to percentage
            })
    
    df = pd.DataFrame(data)
    
    # Plot as grouped bar chart
    pivot_df = df.pivot(index='Resource', columns='Algorithm', values='Utilization')
    ax = pivot_df.plot(kind='bar', figsize=(12, 6))
    
    plt.title('Resource Utilization Comparison')
    plt.xlabel('Resource')
    plt.ylabel('Utilization (%)')
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.ylim(0, 100)
    
    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', padding=3)
    
    plt.legend(title='Algorithm')
    plt.tight_layout()
    
    # Save plot if output_dir provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, 'resource_utilization.png'), dpi=300)
    
    if show_plot:
        plt.show()
    else:
        plt.close()

def plot_schedule_gantt(
    schedule_result: Dict,
    algorithm_name: str,
    output_dir: str = None,
    show_plot: bool = True
):
    """
    Create a Gantt chart visualization of the task schedule.
    
    Args:
        schedule_result: Decoded schedule result from an algorithm
        algorithm_name: Name of the algorithm
        output_dir: Directory to save the plot
        show_plot: Whether to display the plot
    """
    # Extract schedule data
    schedule = schedule_result['schedule']  # (task_id, resource_id, start_time, finish_time)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get unique resources
    resources = sorted(list(set(item[1] for item in schedule)))
    
    # Colors for tasks
    colors = plt.cm.viridis(np.linspace(0, 1, len(schedule)))
    
    # Plot tasks as horizontal bars
    for i, (task_id, resource_id, start_time, finish_time) in enumerate(schedule):
        y_pos = resources.index(resource_id)
        duration = finish_time - start_time
        
        # Plot the task bar
        ax.barh(
            y_pos, 
            duration, 
            left=start_time, 
            height=0.5, 
            color=colors[i % len(colors)],
            alpha=0.8,
            edgecolor='black',
            linewidth=0.5
        )
        
        # Add task label if the bar is wide enough
        if duration > 5:
            ax.text(
                start_time + duration/2, 
                y_pos,
                f'T{task_id}',
                ha='center', 
                va='center',
                color='white',
                fontweight='bold'
            )
    
    # Set y-axis labels to resource names
    ax.set_yticks(range(len(resources)))
    ax.set_yticklabels([f'Resource {r}' for r in resources])
    
    # Set x-axis as time
    ax.set_xlabel('Time')
    ax.grid(True, axis='x', alpha=0.3)
    
    # Set title
    ax.set_title(f'Task Schedule Gantt Chart - {algorithm_name}')
    
    # Add info about makespan
    makespan = schedule_result['makespan']
    avg_util = schedule_result['avg_utilization'] * 100
    deadline_violations = schedule_result['deadline_violations']
    
    ax.text(
        0.01, -0.1,
        f'Makespan: {makespan:.1f} | Avg Utilization: {avg_util:.1f}% | Deadline Violations: {deadline_violations}',
        transform=ax.transAxes,
        ha='left'
    )
    
    plt.tight_layout()
    
    # Save plot if output_dir provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, f'gantt_{algorithm_name.lower().replace(" ", "_")}.png'), dpi=300)
    
    if show_plot:
        plt.show()
    else:
        plt.close()
        
def plot_metrics_by_task_size(
    results: Dict[str, List[Dict]],
    output_dir: str = None,
    show_plot: bool = True
):
    """
    Plot various metrics by task size for different algorithms.
    
    Args:
        results: Dictionary with algorithm name as key and list of result dictionaries for different task sizes
        output_dir: Directory to save the plots
        show_plot: Whether to display the plot
    """
    # Extract metrics
    data = []
    for algo_name, algo_results in results.items():
        for result in algo_results:
            data.append({
                'Algorithm': algo_name,
                'Tasks': result['num_tasks'],
                'Makespan': result['makespan'],
                'Utilization': result['avg_utilization'] * 100,  # Convert to percentage
                'DeadlineViolations': result['deadline_violations']
            })
    
    df = pd.DataFrame(data)
    
    # Create plots for each metric
    metrics = ['Makespan', 'Utilization', 'DeadlineViolations']
    titles = ['Makespan vs Task Size', 'Resource Utilization vs Task Size', 'Deadline Violations vs Task Size']
    ylabels = ['Makespan (time units)', 'Average Utilization (%)', 'Number of Deadline Violations']
    
    for metric, title, ylabel in zip(metrics, titles, ylabels):
        plt.figure(figsize=(12, 6))
        
        pivot_df = df.pivot(index='Tasks', columns='Algorithm', values=metric)
        ax = pivot_df.plot(marker='o', linestyle='-')
        
        plt.title(title)
        plt.xlabel('Number of Tasks')
        plt.ylabel(ylabel)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(title='Algorithm')
        
        plt.tight_layout()
        
        # Save plot if output_dir provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            plt.savefig(os.path.join(output_dir, f'{metric.lower()}_by_task_size.png'), dpi=300)
        
        if show_plot:
            plt.show()
        else:
            plt.close()
