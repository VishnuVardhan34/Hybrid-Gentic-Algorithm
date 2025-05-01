import time
from typing import List, Dict, Any, Tuple

class FCFSScheduler:
    """
    First Come First Serve (FCFS) algorithm for task scheduling in cloud computing.
    This is a simple baseline algorithm that processes tasks in order of arrival.
    """
    
    def __init__(self, tasks: List[Dict], num_resources: int):
        """
        Initialize the FCFS scheduler.
        
        Args:
            tasks: List of task dictionaries
            num_resources: Number of available resources
        """
        self.tasks = tasks
        self.num_resources = num_resources
        
        # Sort tasks by arrival time
        self.sorted_tasks = sorted(
            [(i, task) for i, task in enumerate(tasks)],
            key=lambda x: x[1]['arrival_time']
        )
    
    def run(self, verbose: bool = True) -> Tuple[List[Tuple[int, int]], float, float]:
        """
        Run the FCFS algorithm.
        
        Args:
            verbose: Whether to print progress information
            
        Returns:
            Tuple of (schedule, fitness, execution_time)
        """
        start_time = time.time()
        
        # Track resource finish times
        resource_finish_times = [0] * self.num_resources
        schedule = []
        
        # Process tasks in order of arrival
        for task_idx, task in self.sorted_tasks:
            # Find the resource that will be available soonest
            earliest_resource = min(range(self.num_resources), key=lambda r: resource_finish_times[r])
            
            # Assign task to this resource
            resource_id = earliest_resource
            
            # Record assignment
            schedule.append((task_idx, resource_id))
            
            # Update resource finish time
            start_time_on_resource = max(resource_finish_times[resource_id], task['arrival_time'])
            resource_finish_times[resource_id] = start_time_on_resource + task['execution_time']
        
        # Calculate fitness (using same metric as other algorithms)
        fitness = self._calculate_fitness(schedule)
        
        execution_time = time.time() - start_time
        
        if verbose:
            print(f"FCFS scheduling completed in {execution_time:.2f} seconds")
            print(f"Fitness: {fitness:.4f}")
        
        return schedule, fitness, execution_time
    
    def _calculate_fitness(self, schedule: List[Tuple[int, int]]) -> float:
        """
        Calculate fitness for a schedule using the same metric as the other algorithms.
        Lower fitness is better.
        """
        # Calculate completion times for each task and resource
        resource_finish_times = [0] * self.num_resources
        task_finish_times = [0] * len(self.tasks)
        
        for task_idx, resource_id in schedule:
            task = self.tasks[task_idx]
            
            # Start time is the max of resource availability and task arrival
            start_time = max(resource_finish_times[resource_id], task['arrival_time'])
            
            # Calculate finish time
            finish_time = start_time + task['execution_time']
            
            # Update resource and task finish times
            resource_finish_times[resource_id] = finish_time
            task_finish_times[task_idx] = finish_time
        
        # Calculate makespan (max completion time across all resources)
        makespan = max(resource_finish_times)
        
        # Calculate deadline violations
        deadline_violations = sum(
            max(0, task_finish_times[i] - self.tasks[i]['deadline']) 
            for i in range(len(self.tasks))
        )
        
        # Calculate resource utilization imbalance
        avg_finish_time = sum(resource_finish_times) / self.num_resources
        resource_imbalance = sum(
            abs(finish_time - avg_finish_time) 
            for finish_time in resource_finish_times
        ) / self.num_resources
        
        # Weighted fitness (lower is better)
        fitness = makespan + 5 * deadline_violations + 2 * resource_imbalance
        
        return fitness
    
    def decode_solution(self, schedule: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        Decode the schedule into a human-readable format.
        
        Returns a dictionary with:
        - schedule: List of (task_id, resource_id, start_time, finish_time) tuples
        - makespan: Total completion time
        - resource_utilization: Dictionary of resource utilization stats
        """
        # Calculate schedule timeline
        resource_finish_times = [0] * self.num_resources
        detailed_schedule = []
        
        for task_idx, resource_id in schedule:
            task = self.tasks[task_idx]
            task_id = task['task_id']
            
            # Start time is the max of resource availability and task arrival
            start_time = max(resource_finish_times[resource_id], task['arrival_time'])
            
            # Calculate finish time
            finish_time = start_time + task['execution_time']
            
            # Update resource finish time
            resource_finish_times[resource_id] = finish_time
            
            # Add to detailed schedule
            detailed_schedule.append((task_id, resource_id, start_time, finish_time))
        
        # Sort by start time
        detailed_schedule.sort(key=lambda x: x[2])
        
        # Calculate makespan and resource utilization
        makespan = max(resource_finish_times)
        total_execution_time = sum(task['execution_time'] for task in self.tasks)
        avg_utilization = total_execution_time / (makespan * self.num_resources)
        
        # Calculate resource-specific utilization
        resource_utilization = {}
        for resource_id in range(self.num_resources):
            resource_tasks = [item for item in detailed_schedule if item[1] == resource_id]
            total_busy_time = sum(finish - start for _, _, start, finish in resource_tasks)
            resource_utilization[f"resource_{resource_id}"] = total_busy_time / makespan if makespan > 0 else 0
        
        # Calculate deadline violations
        task_finish_times = {item[0]: item[3] for item in detailed_schedule}
        deadline_violations = sum(
            1 for task in self.tasks if task_finish_times[task['task_id']] > task['deadline']
        )
        
        return {
            'schedule': detailed_schedule,
            'makespan': makespan,
            'avg_utilization': avg_utilization,
            'resource_utilization': resource_utilization,
            'deadline_violations': deadline_violations
        }
