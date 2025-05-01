import os
import time
import pandas as pd
import argparse
from typing import List, Dict, Any, Tuple

# Import utilities
from utils.data_generator import generate_datasets, generate_task_data

# Import algorithms
from algorithms.hybrid_algorithm import HybridScheduler
from algorithms.ant_colony import AntColonyOptimizer
from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.fcfs_algorithm import FCFSScheduler
from algorithms.hesga_algorithm import HESGAScheduler

# Import visualization tools
from visualization.visualizer import (
    plot_algorithm_comparison,
    plot_resource_utilization,
    plot_schedule_gantt,
    plot_metrics_by_task_size
)
from visualization.vm_assignment import (
    create_vm_assignment_graph,
    generate_process_vm_csv,
    create_multi_algorithm_vm_graph,
    process_vm_summary
)

def load_tasks_from_csv(csv_path: str) -> List[Dict]:
    """
    Load tasks from a CSV file.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        List of task dictionaries
    """
    df = pd.read_csv(csv_path)
    tasks = df.to_dict('records')
    return tasks

def run_experiment(
    task_files: List[str],
    num_resources: int = 5,
    algorithms: List[str] = None,
    generations: int = 50,
    output_dir: str = 'results',
    show_plots: bool = False,
    verbose: bool = True
):
    """
    Run scheduling algorithms on the task datasets and compare results.
    
    Args:
        task_files: List of CSV files containing task data
        num_resources: Number of resources to use
        algorithms: List of algorithms to run (default: all)
        generations: Number of generations/iterations to run
        output_dir: Directory to save results
        show_plots: Whether to display plots during execution
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define available algorithms
    available_algorithms = {
        'hybrid': HybridScheduler,
        'genetic': GeneticAlgorithm,
        'ant_colony': AntColonyOptimizer,
        'fcfs': FCFSScheduler,
        'hesga': HESGAScheduler
    }
    
    # Select algorithms to run
    if algorithms is None:
        algorithms = list(available_algorithms.keys())
    else:
        # Ensure all requested algorithms are available
        for algo in algorithms:
            if algo not in available_algorithms:
                print(f"Warning: Algorithm '{algo}' is not available. Skipping.")
        algorithms = [algo for algo in algorithms if algo in available_algorithms]
    
    # Store results for comparison
    time_results = {algo: [] for algo in algorithms}
    schedule_results = {algo: {} for algo in algorithms}
    all_metrics = {algo: [] for algo in algorithms}
    
    # Process each task file
    for task_file in task_files:
        filename = os.path.basename(task_file)
        task_count = int(filename.split('_')[1].split('.')[0])  # Extract task count from filename
        
        print(f"\n{'='*50}")
        print(f"Processing {filename} ({task_count} tasks)")
        print(f"{'='*50}")
        
        # Load tasks
        tasks = load_tasks_from_csv(task_file)
        
        # Run each algorithm
        for algo_name in algorithms:
            print(f"\nRunning {algo_name} algorithm...")
            
            # Calculate task count to adjust algorithm parameters
            task_count = len(tasks)
            is_large_dataset = task_count > 5000
            
            # For large datasets, use smaller population sizes and fewer iterations
            pop_size = 20 if is_large_dataset else 50
            gen_scaling = max(1, min(5, int(10000 / task_count))) if is_large_dataset else 1
            actual_generations = max(5, generations // gen_scaling) if is_large_dataset else generations
            
            if is_large_dataset and verbose:
                print(f"Large dataset detected. Using optimized parameters: generations={actual_generations}, pop_size={pop_size}")
            
            # Initialize algorithm
            algorithm_class = available_algorithms[algo_name]
            
            if algo_name == 'hybrid':
                scheduler = algorithm_class(
                    tasks=tasks,
                    num_resources=num_resources,
                    pop_size=pop_size,
                    clone_factor=2,
                    mutation_rate=0.2,
                    sa_interval=2,
                    iga_interval=3,
                    sa_top_k=min(5, pop_size // 10)
                )
            elif algo_name == 'genetic':
                scheduler = algorithm_class(
                    tasks=tasks,
                    num_resources=num_resources,
                    population_size=pop_size,
                    crossover_rate=0.8,
                    mutation_rate=0.2,
                    elitism_count=max(1, pop_size // 25)
                )
            elif algo_name == 'ant_colony':
                scheduler = algorithm_class(
                    tasks=tasks,
                    num_resources=num_resources,
                    num_ants=min(30, pop_size),
                    alpha=1.0,
                    beta=2.0,
                    evaporation_rate=0.5,
                    q0=0.9
                )
            elif algo_name == 'fcfs':
                scheduler = algorithm_class(
                    tasks=tasks,
                    num_resources=num_resources
                )
            elif algo_name == 'hesga':
                scheduler = algorithm_class(
                    tasks=tasks,
                    num_resources=num_resources,
                    population_size=pop_size,
                    crossover_rate=0.8,
                    mutation_rate=0.2,
                    elitism_count=max(1, pop_size // 25)
                )
            
            # Run algorithm
            start_time = time.time()
            # Different parameter names and execution patterns for different algorithms
            if algo_name == 'fcfs':
                # FCFS doesn't have generations parameter
                schedule, fitness, exec_time = scheduler.run(verbose=True)
                solution = None  # FCFS returns schedule directly, not encoded solution
            elif algo_name == 'ant_colony':
                # Ant Colony uses 'iterations' parameter
                solution, fitness, exec_time = scheduler.run(iterations=actual_generations, verbose=True)
            else:
                # Other algorithms use 'generations' parameter
                solution, fitness, exec_time = scheduler.run(generations=actual_generations, verbose=True)
            
            # Store results
            time_results[algo_name].append((task_count, fitness, exec_time))
            
            # Decode solution
            if algo_name == 'fcfs':
                # FCFS returns schedule directly
                schedule_data = scheduler.decode_solution(schedule)
            elif algo_name in ['hybrid', 'genetic', 'ant_colony', 'hesga']:
                # These algorithms return encoded solutions that need to be decoded
                schedule_data = scheduler.decode_solution(solution)
            
            schedule_results[algo_name][task_count] = schedule_data
            
            # Store metrics
            metrics = {
                'algorithm': algo_name,
                'num_tasks': task_count,
                'fitness': fitness,
                'execution_time': exec_time,
                'makespan': schedule_data['makespan'],
                'avg_utilization': schedule_data['avg_utilization'],
                'deadline_violations': schedule_data['deadline_violations']
            }
            all_metrics[algo_name].append(metrics)
            
            # Save schedule to CSV
            schedule_df = pd.DataFrame(schedule_data['schedule'], 
                                      columns=['task_id', 'resource_id', 'start_time', 'finish_time'])
            schedule_df.to_csv(os.path.join(output_dir, f'schedule_{algo_name}_{task_count}.csv'), index=False)
            
            # Generate Gantt chart
            plot_schedule_gantt(
                schedule_data,
                f"{algo_name.capitalize()} - {task_count} Tasks",
                output_dir=output_dir,
                show_plot=show_plots
            )
            
            print(f"  Fitness: {fitness:.4f}")
            print(f"  Makespan: {schedule_data['makespan']:.2f}")
            print(f"  Average Utilization: {schedule_data['avg_utilization']*100:.2f}%")
            print(f"  Deadline Violations: {schedule_data['deadline_violations']}")
    
    # Generate comparison plots
    print("\nGenerating comparison plots...")
    
    # Execution time comparison
    plot_algorithm_comparison(
        time_results,
        output_dir=output_dir,
        metric='time',
        show_plot=show_plots
    )
    
    # Fitness comparison
    plot_algorithm_comparison(
        time_results,
        output_dir=output_dir,
        metric='fitness',
        show_plot=show_plots
    )
    
    # Resource utilization comparison for the largest dataset
    largest_task_count = max(int(task_file.split('_')[1].split('.')[0]) for task_file in task_files)
    largest_results = {algo: data[largest_task_count] for algo, data in schedule_results.items()}
    
    plot_resource_utilization(
        largest_results,
        output_dir=output_dir,
        show_plot=show_plots
    )
    
    # Metrics by task size
    plot_metrics_by_task_size(
        all_metrics,
        output_dir=output_dir,
        show_plot=show_plots
    )
    
    # Create VM assignment visualizations for each algorithm and dataset
    print("\nGenerating VM assignment visualizations...")
    
    # Create a directory for VM assignment files
    vm_assignment_dir = os.path.join(output_dir, 'vm_assignments')
    os.makedirs(vm_assignment_dir, exist_ok=True)
    
    # Process each algorithm's schedule results
    for algo_name, algo_results in schedule_results.items():
        for task_count, schedule_data in algo_results.items():
            # Generate CSV file
            csv_file = os.path.join(vm_assignment_dir, f'{algo_name}_{task_count}_vm_assignment.csv')
            generate_process_vm_csv(schedule_data, csv_file)
            
            # Generate individual graph
            graph_file = os.path.join(vm_assignment_dir, f'{algo_name}_{task_count}_vm_graph.png')
            create_vm_assignment_graph(
                schedule_data,
                f"{algo_name.capitalize()} - {task_count} Tasks",
                output_file=graph_file,
                show_plot=False
            )
    
    # Generate comparison graphs for each dataset size
    for task_file in task_files:
        task_count = int(os.path.basename(task_file).split('_')[1].split('.')[0])
        
        # Collect results for this task count across algorithms
        algo_results = {}
        for algo_name, results in schedule_results.items():
            if task_count in results:
                algo_results[algo_name.capitalize()] = results[task_count]
        
        # Create comparison graph
        if algo_results:
            comparison_file = os.path.join(vm_assignment_dir, f'comparison_{task_count}_tasks.png')
            create_multi_algorithm_vm_graph(
                algo_results,
                output_file=comparison_file,
                show_plot=False
            )
    
    # Also generate a summary for each CSV file
    print("\nVM Assignment Summaries:")
    for algo_name, algo_results in schedule_results.items():
        for task_count, _ in algo_results.items():
            csv_file = os.path.join(vm_assignment_dir, f'{algo_name}_{task_count}_vm_assignment.csv')
            print(f"\n{algo_name.upper()} - {task_count} TASKS")
            process_vm_summary(csv_file)
    
    print(f"\nExperiment completed. Results saved to {output_dir}/")
    print(f"VM assignment visualizations saved to {vm_assignment_dir}/")
    

def main():
    parser = argparse.ArgumentParser(description='Run cloud task scheduling algorithms')
    parser.add_argument('--generate-data', action='store_true', help='Generate task datasets before running')
    parser.add_argument('--task-sizes', type=int, nargs='+', default=[50, 100, 200, 500, 1000], help='Task sizes to generate')
    parser.add_argument('--resources', type=int, default=5, help='Number of resources to use')
    parser.add_argument('--algorithms', type=str, nargs='+', choices=['hybrid', 'genetic', 'ant_colony', 'fcfs', 'hesga'], help='Algorithms to run')
    parser.add_argument('--generations', type=int, default=50, help='Number of generations/iterations to run')
    parser.add_argument('--output-dir', type=str, default='results', help='Directory to save results')
    parser.add_argument('--show-plots', action='store_true',
                        help='Show plots (default: false)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output (default: false)')
    
    args = parser.parse_args()
    
    data_dir = 'data'
    
    # Generate data if requested
    if args.generate_data:
        print(f"Generating task datasets with sizes: {args.task_sizes}")
        generate_datasets(data_dir, args.task_sizes, args.resources)
    
    # Find task files
    task_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.startswith('tasks_') and f.endswith('.csv')]
    
    if not task_files:
        print("No task data found. Generating default datasets.")
        task_files = generate_datasets(data_dir, args.task_sizes, args.resources)
    
    # Run experiment
    run_experiment(
        task_files=task_files,
        num_resources=args.resources,
        algorithms=args.algorithms,
        generations=args.generations,
        output_dir=args.output_dir,
        show_plots=args.show_plots,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main()
