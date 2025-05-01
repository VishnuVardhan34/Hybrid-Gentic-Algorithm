import random
import time
import numpy as np
from typing import List, Dict, Any, Tuple, Callable

class AntColonyOptimizer:
    """
    Ant Colony Optimization (ACO) for task scheduling in cloud computing.
    """
    
    def __init__(
        self,
        tasks: List[Dict],
        num_resources: int,
        fitness_function: Callable = None,
        num_ants: int = 30,
        alpha: float = 1.0,  # Pheromone importance
        beta: float = 2.0,   # Heuristic importance
        evaporation_rate: float = 0.5,
        q0: float = 0.9      # Exploration/exploitation parameter
    ):
        self.tasks = tasks
        self.num_tasks = len(tasks)
        self.num_resources = num_resources
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.q0 = q0
        
        # Initialize pheromone matrix 
        # (num_tasks x num_resources matrix representing task-to-resource assignment)
        self.pheromone = np.ones((self.num_tasks, self.num_resources))
        
        # Initialize heuristic matrix (inverse of execution time)
        self.heuristic = np.zeros((self.num_tasks, self.num_resources))
        for i in range(self.num_tasks):
            execution_time = tasks[i]['execution_time']
            for j in range(self.num_resources):
                # Simple heuristic: inverse of execution time
                self.heuristic[i, j] = 1.0 / (execution_time + 1)  # +1 to avoid division by zero
        
        # Set fitness function
        self.fitness_function = fitness_function or self._default_fitness
    
    def _default_fitness(self, schedule: List[Tuple[int, int]]) -> float:
        """
        Default fitness function for a schedule.
        Schedule is a list of (task_idx, resource_id) tuples.
        """
        # Calculate completion times for each task and resource
        resource_finish_times = [0] * self.num_resources
        task_finish_times = [0] * self.num_tasks
        
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
            for i in range(self.num_tasks)
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
    
    def _construct_solution(self) -> List[Tuple[int, int]]:
        """
        Construct a solution using the ACO approach.
        Returns a list of (task_idx, resource_id) tuples representing the schedule.
        """
        # Initialize empty schedule
        schedule = []
        
        # List of unassigned tasks
        unassigned_tasks = list(range(self.num_tasks))
        random.shuffle(unassigned_tasks)  # Randomize initial order
        
        # Sort by arrival time to ensure tasks are considered in arrival order
        unassigned_tasks.sort(key=lambda idx: self.tasks[idx]['arrival_time'])
        
        # Assign each task to a resource
        for task_idx in unassigned_tasks:
            # Calculate selection probabilities for each resource
            probabilities = []
            for resource_id in range(self.num_resources):
                # Calculate probability based on pheromone and heuristic
                p = (self.pheromone[task_idx, resource_id] ** self.alpha) * \
                    (self.heuristic[task_idx, resource_id] ** self.beta)
                probabilities.append(p)
            
            # Normalize probabilities
            total = sum(probabilities)
            if total > 0:
                probabilities = [p / total for p in probabilities]
            else:
                probabilities = [1.0 / self.num_resources] * self.num_resources
            
            # Select resource using the q0 rule (exploitation vs exploration)
            if random.random() < self.q0:
                # Exploitation: choose the best resource
                resource_id = probabilities.index(max(probabilities))
            else:
                # Exploration: choose probabilistically
                resource_id = random.choices(
                    range(self.num_resources), 
                    weights=probabilities, 
                    k=1
                )[0]
            
            # Add to schedule
            schedule.append((task_idx, resource_id))
        
        return schedule
    
    def _update_pheromone(self, schedules: List[List[Tuple[int, int]]], fitnesses: List[float]):
        """
        Update pheromone levels based on the quality of solutions found by ants.
        """
        # Evaporate pheromone
        self.pheromone *= (1 - self.evaporation_rate)
        
        # Add new pheromone based on solution quality
        for schedule, fitness in zip(schedules, fitnesses):
            # Pheromone deposited is inversely proportional to the fitness
            # (since lower fitness is better)
            delta = 1.0 / (fitness + 1)  # +1 to avoid division by zero
            
            for task_idx, resource_id in schedule:
                self.pheromone[task_idx, resource_id] += delta
    
    def run(self, iterations: int, verbose: bool = True) -> Tuple[List[Tuple[int, int]], float, float]:
        """
        Run the ACO algorithm for task scheduling.
        
        Args:
            iterations: Number of iterations
            verbose: Whether to print progress information
            
        Returns:
            Tuple of (best_schedule, best_fitness, execution_time)
        """
        start_time = time.time()
        
        best_schedule = None
        best_fitness = float('inf')
        
        for it in range(iterations):
            # Construct solutions for all ants
            ant_schedules = []
            fitnesses = []
            
            for _ in range(self.num_ants):
                schedule = self._construct_solution()
                fitness = self.fitness_function(schedule)
                
                ant_schedules.append(schedule)
                fitnesses.append(fitness)
                
                # Update best solution
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_schedule = schedule
            
            # Update pheromone levels
            self._update_pheromone(ant_schedules, fitnesses)
            
            if verbose and (it % 5 == 0 or it == iterations - 1):
                print(f"Iteration {it}: Best Fitness = {best_fitness:.4f}")
        
        execution_time = time.time() - start_time
        
        if verbose:
            print(f"Optimization completed in {execution_time:.2f} seconds")
            print(f"Best fitness: {best_fitness:.4f}")
        
        return best_schedule, best_fitness, execution_time
    
    def decode_solution(self, schedule: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        Decode the encoded solution into a human-readable schedule.
        
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
            resource_utilization[f"resource_{resource_id}"] = total_busy_time / makespan
        
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
