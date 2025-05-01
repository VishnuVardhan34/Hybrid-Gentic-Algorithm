import random
import time
import copy
from typing import List, Dict, Any, Tuple, Callable

class HESGAScheduler:
    """
    Heterogeneous Earliest Start Time with Genetic Algorithm (HESGA) 
    for task scheduling in cloud computing.
    
    HESGA combines a heuristic-based initial solution generation with 
    genetic algorithm optimization.
    """
    
    def __init__(
        self,
        tasks: List[Dict],
        num_resources: int,
        fitness_function: Callable = None,
        population_size: int = 50,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.2,
        elitism_count: int = 2
    ):
        self.tasks = tasks
        self.num_tasks = len(tasks)
        self.num_resources = num_resources
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        
        # Set fitness function
        self.fitness_function = fitness_function or self._default_fitness
        
    def _generate_heft_priority_list(self) -> List[int]:
        """
        Generate a priority list of tasks using HEFT-like ranking.
        Higher rank = higher priority for execution.
        """
        # Calculate average execution time for each task
        avg_execution_times = []
        for task in self.tasks:
            avg_execution_times.append(task['execution_time'])
        
        # Calculate average communication cost (we'll use resource requirements as proxy)
        avg_comm_costs = []
        for task in self.tasks:
            # Sum of resource requirements as proxy for communication cost
            comm_cost = 0
            for i in range(1, self.num_resources + 1):
                resource_key = f'resource_{i}'
                if resource_key in task:
                    comm_cost += task[resource_key]
            avg_comm_costs.append(comm_cost)
        
        # Calculate upward rank for each task (we'll simplify since we don't have predecessors)
        ranks = []
        for i, task in enumerate(self.tasks):
            # For HEFT, upward rank = task execution time + max(comm cost + successor's rank)
            # Since we don't have predecessors/successors, we'll adapt this:
            rank = avg_execution_times[i] + avg_comm_costs[i] + (task['deadline'] - task['arrival_time'])
            ranks.append((i, rank))
        
        # Sort tasks by rank (highest rank first)
        sorted_tasks = sorted(ranks, key=lambda x: x[1], reverse=True)
        return [task_idx for task_idx, _ in sorted_tasks]
        
    def _generate_individual(self) -> List[float]:
        """Generate a random solution with HEFT-based priorities"""
        # First half: Resource assignment (which resource handles each task)
        resource_assignments = [random.random() for _ in range(self.num_tasks)]
        
        # Second half: Execution priority using HEFT-like ranking with some randomness
        priority_list = self._generate_heft_priority_list()
        
        # Convert priority list to normalized priorities with some randomness
        task_priorities = [0.0] * self.num_tasks
        for i, task_idx in enumerate(priority_list):
            # Normalize priority to [0,1] range with some randomness
            normalized_priority = (len(priority_list) - i) / len(priority_list)
            # Add some randomness (±10%)
            task_priorities[task_idx] = min(1.0, max(0.0, normalized_priority + random.uniform(-0.1, 0.1)))
        
        # Combine resource assignments and priorities
        return resource_assignments + task_priorities
    
    def _decode_individual(self, individual: List[float]) -> List[Tuple[int, int]]:
        """
        Convert an encoded individual to a schedule.
        Returns list of (task_idx, resource_id) tuples
        """
        # First half of individual determines resource assignment
        resource_assignments = [min(int(individual[i] * self.num_resources), self.num_resources - 1) 
                               for i in range(self.num_tasks)]
        
        # Second half determines priority within each resource
        priorities = [(i, individual[i + self.num_tasks]) for i in range(self.num_tasks)]
        sorted_tasks = sorted(priorities, key=lambda x: x[1], reverse=True)  # Higher priority first
        
        # Create schedule
        schedule = [(task_idx, resource_assignments[task_idx]) for task_idx, _ in sorted_tasks]
        return schedule
    
    def _default_fitness(self, individual: List[float]) -> float:
        """
        Default fitness function for a genetic algorithm individual.
        Lower fitness value is better.
        """
        schedule = self._decode_individual(individual)
        
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
    
    def _tournament_selection(self, population: List[List[float]], tournament_size: int = 3) -> List[float]:
        """Select an individual using tournament selection"""
        tournament = random.sample(population, tournament_size)
        winner = min(tournament, key=self.fitness_function)
        return winner[:]
    
    def _crossover(self, parent1: List[float], parent2: List[float]) -> Tuple[List[float], List[float]]:
        """Apply crossover to create two offspring"""
        if random.random() > self.crossover_rate:
            return parent1[:], parent2[:]
        
        # Two-point crossover with separate crossovers for resource assignments and priorities
        child1, child2 = [], []
        
        # Crossover for resource assignments (first half)
        point1 = random.randrange(1, self.num_tasks-1)
        point2 = random.randrange(point1, self.num_tasks)
        
        child1.extend(parent1[:point1])
        child1.extend(parent2[point1:point2])
        child1.extend(parent1[point2:self.num_tasks])
        
        child2.extend(parent2[:point1])
        child2.extend(parent1[point1:point2])
        child2.extend(parent2[point2:self.num_tasks])
        
        # Crossover for priorities (second half)
        point1 = self.num_tasks + random.randrange(1, self.num_tasks-1)
        point2 = self.num_tasks + random.randrange(point1-self.num_tasks, self.num_tasks)
        
        child1.extend(parent1[self.num_tasks:point1])
        child1.extend(parent2[point1:point2])
        child1.extend(parent1[point2:])
        
        child2.extend(parent2[self.num_tasks:point1])
        child2.extend(parent1[point1:point2])
        child2.extend(parent2[point2:])
                
        return child1, child2
    
    def _mutate(self, individual: List[float]) -> List[float]:
        """Apply heterogeneous mutation to an individual"""
        mutated = individual[:]
        
        # Different mutation strategies for resource assignments and priorities
        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                if i < self.num_tasks:  # Resource assignment
                    # Completely random reassignment
                    mutated[i] = random.random()
                else:  # Priority
                    # Apply Gaussian mutation with smaller impact
                    mutated[i] += random.gauss(0, 0.05)
                    # Keep within bounds [0, 1]
                    mutated[i] = max(0, min(1, mutated[i]))
        
        return mutated
    
    def _local_search(self, individual: List[float]) -> List[float]:
        """Apply local search to improve an individual"""
        current = individual[:]
        current_fitness = self.fitness_function(current)
        improved = False
        
        # Try to improve resource assignment for random tasks
        for _ in range(min(5, self.num_tasks // 10)):
            task_idx = random.randrange(self.num_tasks)
            original_value = current[task_idx]
            
            # Try each possible resource
            for r in range(self.num_resources):
                current[task_idx] = (r + 0.5) / self.num_resources  # Ensure it maps to resource r
                new_fitness = self.fitness_function(current)
                
                if new_fitness < current_fitness:
                    current_fitness = new_fitness
                    improved = True
                    break  # Keep the improvement
                
            if not improved:
                # Revert if no improvement
                current[task_idx] = original_value
        
        return current
    
    def run(self, generations: int, verbose: bool = True) -> Tuple[List[float], float, float]:
        """
        Run the HESGA algorithm for task scheduling.
        
        Args:
            generations: Number of generations
            verbose: Whether to print progress information
            
        Returns:
            Tuple of (best_individual, best_fitness, execution_time)
        """
        start_time = time.time()
        
        # Initialize population with HEFT-based individuals
        population = [self._generate_individual() for _ in range(self.population_size)]
        
        # Apply local search to initial population
        for i in range(len(population)):
            if random.random() < 0.5:  # Apply to 50% of initial population
                population[i] = self._local_search(population[i])
        
        # Evaluate initial population
        fitness_values = [self.fitness_function(ind) for ind in population]
        best_individual = population[fitness_values.index(min(fitness_values))]
        best_fitness = min(fitness_values)
        
        local_search_freq = max(1, generations // 5)  # Apply local search periodically
        
        for gen in range(generations):
            # Sort population by fitness
            population = [x for _, x in sorted(zip(fitness_values, population), key=lambda pair: pair[0])]
            
            # Apply local search periodically
            if gen % local_search_freq == 0:
                # Apply local search to best individuals
                for i in range(min(5, len(population))):
                    population[i] = self._local_search(population[i])
            
            # Create new population with elitism
            new_population = population[:self.elitism_count]
            
            # Fill the rest of the population with offspring
            while len(new_population) < self.population_size:
                # Select parents
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                
                # Create offspring through crossover
                offspring1, offspring2 = self._crossover(parent1, parent2)
                
                # Apply mutation
                offspring1 = self._mutate(offspring1)
                offspring2 = self._mutate(offspring2)
                
                # Add to new population
                new_population.append(offspring1)
                if len(new_population) < self.population_size:
                    new_population.append(offspring2)
            
            # Update population
            population = new_population
            
            # Evaluate new population
            fitness_values = [self.fitness_function(ind) for ind in population]
            current_best_index = fitness_values.index(min(fitness_values))
            current_best = population[current_best_index]
            current_best_fitness = fitness_values[current_best_index]
            
            # Update global best if needed
            if current_best_fitness < best_fitness:
                best_individual = current_best
                best_fitness = current_best_fitness
            
            if verbose and (gen % 5 == 0 or gen == generations - 1):
                print(f"Gen {gen}: Best Fitness = {best_fitness:.4f}")
        
        execution_time = time.time() - start_time
        
        if verbose:
            print(f"Optimization completed in {execution_time:.2f} seconds")
            print(f"Best fitness: {best_fitness:.4f}")
        
        return best_individual, best_fitness, execution_time
    
    def decode_solution(self, individual: List[float]) -> Dict[str, Any]:
        """
        Decode the genetic algorithm individual into a human-readable schedule.
        
        Returns a dictionary with:
        - schedule: List of (task_id, resource_id, start_time, finish_time) tuples
        - makespan: Total completion time
        - resource_utilization: Dictionary of resource utilization stats
        """
        schedule = self._decode_individual(individual)
        
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
