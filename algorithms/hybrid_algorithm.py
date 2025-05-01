from typing import List, Callable, Dict, Any, Tuple
import random
import math
import time

# Define types
Solution = List[float]
Population = List[Solution]
Task = Dict[str, Any]

class HybridScheduler:
    """
    Hybrid algorithm combining Clone-based Genetic Algorithm (CGA), 
    Simulated Annealing (SA), and Imperialist Genetic Algorithm (IGA)
    for task scheduling in cloud computing environments.
    """
    
    def __init__(
        self,
        tasks: List[Task],
        num_resources: int,
        fitness_function: Callable = None,
        lower_bound: float = 0.0,
        upper_bound: float = 1.0,
        pop_size: int = 50,
        clone_factor: int = 2,
        mutation_rate: float = 0.2,
        sa_interval: int = 2,
        iga_interval: int = 3,
        sa_top_k: int = 5,
        sa_temp: float = 10.0,
        sa_cooling: float = 0.95,
        sa_iters: int = 10
    ):
        self.tasks = tasks
        self.num_tasks = len(tasks)
        self.num_resources = num_resources
        self.dimension = self.num_tasks * 2  # Resource assignment + execution order
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.pop_size = pop_size
        self.clone_factor = clone_factor
        self.mutation_rate = mutation_rate
        self.sa_interval = sa_interval
        self.iga_interval = iga_interval
        self.sa_top_k = sa_top_k
        self.sa_temp = sa_temp
        self.sa_cooling = sa_cooling
        self.sa_iters = sa_iters
        self.memory = {}
        
        # Set the fitness function to evaluate solutions
        self.fitness_function = fitness_function if fitness_function else self._default_fitness
        
    def _generate_solution(self) -> Solution:
        """Generate a random solution (schedule)"""
        # First half: Resource assignment (which resource handles each task)
        # Second half: Execution priority within each resource
        solution = [random.uniform(self.lower_bound, self.upper_bound) for _ in range(self.dimension)]
        return solution
    
    def _solution_to_schedule(self, solution: Solution) -> List[Tuple[int, int]]:
        """
        Convert a solution vector to an actual schedule.
        Returns list of (task_id, resource_id) tuples
        """
        # First half of solution determines resource assignment
        # Ensure resource_id is always within range [0, num_resources-1]
        resource_assignments = [min(int(solution[i] * self.num_resources), self.num_resources - 1) for i in range(self.num_tasks)]
        
        # Second half determines priority within each resource
        priorities = [(i, solution[i + self.num_tasks]) for i in range(self.num_tasks)]
        sorted_tasks = sorted(priorities, key=lambda x: x[1])
        
        # Create schedule
        schedule = [(task_idx, resource_assignments[task_idx]) for task_idx, _ in sorted_tasks]
        return schedule
    
    def _default_fitness(self, solution: Solution) -> float:
        """
        Default fitness function evaluating a solution based on:
        - Makespan (total completion time)
        - Deadline violations
        - Resource utilization balance
        """
        schedule = self._solution_to_schedule(solution)
        
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
        
    def _simulated_annealing(self, solution: Solution, temp: float, cooling: float, iterations: int) -> Solution:
        """Apply Simulated Annealing to improve a solution with adaptive modifications"""
        current = solution[:]
        current_score = self.fitness_function(current)
        best_solution = current[:]
        best_score = current_score
        
        # Adaptive perturbation strength based on temperature
        initial_temp = temp
        
        for iteration in range(iterations):
            # Calculate adaptive perturbation range that decreases with temperature
            # Start with larger perturbations and gradually refine
            perturbation_range = 0.2 * (temp / initial_temp) + 0.05
            
            # Generate neighbor with adaptive perturbation
            neighbor = current[:]
            
            # Number of dimensions to perturb based on current progress
            # Perturb more dimensions early, fewer dimensions later
            dims_to_perturb = max(1, int((0.2 - 0.1 * (iteration / iterations)) * self.dimension))
            
            # Resource assignments (first half) and priorities (second half) handled differently
            for _ in range(dims_to_perturb):
                # Randomly choose between perturbing resource assignment or priority
                if random.random() < 0.5:  # Perturb resource assignment
                    idx = random.randrange(self.num_tasks)  # First half of solution
                    perturbation = random.uniform(-perturbation_range, perturbation_range)
                    neighbor[idx] = max(self.lower_bound, min(self.upper_bound, neighbor[idx] + perturbation))
                else:  # Perturb priority
                    idx = self.num_tasks + random.randrange(self.num_tasks)  # Second half
                    perturbation = random.uniform(-perturbation_range, perturbation_range)
                    neighbor[idx] = max(self.lower_bound, min(self.upper_bound, neighbor[idx] + perturbation))
            
            # Evaluate neighbor
            neighbor_score = self.fitness_function(neighbor)
            
            # Calculate acceptance probability with a more aggressive formula for worse solutions
            delta = neighbor_score - current_score
            if delta < 0:  # Better solution, always accept
                current = neighbor
                current_score = neighbor_score
                
                # Update best solution if needed
                if neighbor_score < best_score:
                    best_solution = neighbor[:]
                    best_score = neighbor_score
            else:  # Worse solution, accept with probability
                # Modified acceptance probability that decreases more quickly for very bad solutions
                acceptance_prob = math.exp(-(delta) / temp)
                if random.random() < acceptance_prob:
                    current = neighbor
                    current_score = neighbor_score
            
            # Cooling schedule with periodic reheating to escape local optima
            if iteration > 0 and iteration % (iterations // 3) == 0:
                # Slight reheating every third of the way through
                temp = min(initial_temp * 0.5, temp / cooling)
            else:
                # Normal cooling
                temp *= cooling
        
        # Return the best solution found, not just the current one
        return best_solution
    
    def _clone_population(self, population: Population, factor: int) -> Population:
        """Clone individuals in population by the given factor"""
        return [ind[:] for ind in population for _ in range(factor)]
    
    def _mutate_population(self, population: Population) -> Population:
        """Apply mutation to the population"""
        new_pop = []
        
        for ind in population:
            new_ind = ind[:]
            
            # Apply mutation to each gene with probability mutation_rate
            for i in range(len(new_ind)):
                if random.random() < self.mutation_rate:
                    new_ind[i] = max(self.lower_bound, min(self.upper_bound, new_ind[i] + random.uniform(-0.1, 0.1)))
            
            new_pop.append(new_ind)
            
        return new_pop
    
    def _update_iga_memory(self, solution: Solution):
        """Update IGA memory with solution and return if it's a new unique solution"""
        # Use a simplified key for the memory (quantize to reduce precision for better matching)
        key = tuple(int(x * 100) for x in solution)
        
        if key not in self.memory:
            # Store both fitness and the actual solution
            self.memory[key] = {
                'fitness': self.fitness_function(solution),
                'solution': solution[:],
                'access_count': 1,
                'last_updated': 0  # Generation counter
            }
            return True  # New unique solution
        else:
            # Update access count for existing solution
            self.memory[key]['access_count'] += 1
            return False  # Existing solution
            
    def _get_memory_solutions(self, top_k: int = 5) -> List[Solution]:
        """Get top-k solutions from memory based on fitness"""
        if not self.memory:
            return []
            
        # Sort memory items by fitness
        sorted_memory = sorted(
            [(fitness_data['fitness'], fitness_data['solution']) 
             for fitness_data in self.memory.values()],
            key=lambda x: x[0]  # Sort by fitness (first item in tuple)
        )
        
        # Return top-k solutions
        return [solution for _, solution in sorted_memory[:top_k]]
        
    def _inject_memory_solutions(self, population: Population, generation: int):
        """Inject top solutions from memory into the population"""
        if not self.memory or len(population) < 2:
            return population
        
        # Update generation counter for all memory items
        for key in self.memory:
            self.memory[key]['last_updated'] = generation
        
        # Get top solutions from memory
        memory_solutions = self._get_memory_solutions(top_k=min(5, len(population) // 10))
        
        if not memory_solutions:
            return population
            
        # Replace worst solutions in population with memory solutions
        scored_population = [(ind, self.fitness_function(ind)) for ind in population]
        scored_population.sort(key=lambda x: x[1], reverse=True)  # Sort worst to best
        
        # Replace worst solutions with memory solutions
        for i, memory_sol in enumerate(memory_solutions):
            if i < len(scored_population):
                # Replace only if memory solution is better
                memory_fitness = self.fitness_function(memory_sol)
                if memory_fitness < scored_population[i][1]:
                    population[population.index(scored_population[i][0])] = memory_sol[:]
        
        return population
        
    def _clean_memory(self, max_size: int = 100, current_gen: int = 0, retention_gens: int = 20):
        """Clean up memory to prevent excessive growth"""
        if len(self.memory) <= max_size:
            return
            
        # Remove old or rarely accessed memories
        items_to_remove = []
        
        for key, data in self.memory.items():
            # Remove old memories not accessed recently
            if current_gen - data['last_updated'] > retention_gens and data['access_count'] < 3:
                items_to_remove.append(key)
                
        # Remove identified items
        for key in items_to_remove:
            del self.memory[key]
            
        # If still too large, remove worst solutions
        if len(self.memory) > max_size:
            # Sort by fitness (higher is worse)
            sorted_keys = sorted(
                self.memory.keys(),
                key=lambda k: self.memory[k]['fitness'],
                reverse=True
            )
            
            # Remove worst solutions
            for key in sorted_keys[:len(self.memory) - max_size]:
                del self.memory[key]
    
    def run(self, generations: int, verbose: bool = True) -> Tuple[Solution, float, float]:
        """
        Run the hybrid algorithm to find an optimal task schedule.
        
        Args:
            generations: Number of generations to run
            verbose: Whether to print progress information
            
        Returns:
            Tuple of (best_solution, best_fitness, execution_time)
        """
        start_time = time.time()
        
        # Initialize population
        population = [self._generate_solution() for _ in range(self.pop_size)]
        
        # Evaluate initial population
        fitness_values = [self.fitness_function(ind) for ind in population]
        best_solution = population[fitness_values.index(min(fitness_values))]
        best_fitness = min(fitness_values)
        
        # Adaptive parameters
        sa_temp = self.sa_temp
        mutation_rate = self.mutation_rate
        clone_factor = self.clone_factor
        no_improvement_count = 0
        last_best_fitness = best_fitness
        
        # Main loop
        for gen in range(generations):
            # Adjust parameters based on progress
            if gen > 0 and gen % 5 == 0:
                # If no improvement, increase exploration
                if best_fitness >= last_best_fitness:
                    no_improvement_count += 1
                    # Increase temperature to escape local optima
                    sa_temp = min(self.sa_temp * 1.5, sa_temp * 1.2)
                    # Increase mutation rate for more exploration
                    mutation_rate = min(0.4, mutation_rate * 1.1)
                    # Increase clone factor for more diversity
                    clone_factor = min(4, clone_factor + 0.5)
                else:
                    # If improving, reduce exploration
                    no_improvement_count = 0
                    # Gradually reduce temperature
                    sa_temp = max(0.1, sa_temp * 0.9)
                    # Decrease mutation rate for more exploitation
                    mutation_rate = max(0.05, mutation_rate * 0.9)
                    # Decrease clone factor
                    clone_factor = max(1, clone_factor - 0.2)
                    
                last_best_fitness = best_fitness
                
            # If stuck for too long, do a partial reset
            if no_improvement_count >= 3:
                # Reset parameters
                sa_temp = self.sa_temp * 1.5  # Higher temperature
                mutation_rate = 0.3  # Higher mutation
                clone_factor = 3  # More clones
                no_improvement_count = 0
                
                # Replace 30% of the population with new random solutions
                replace_count = max(1, int(0.3 * len(population)))
                for i in range(replace_count):
                    idx = random.randrange(len(population))
                    population[idx] = self._generate_solution()
            
            # CGA: Clone and mutate with adaptive rates
            clones = self._clone_population(population, int(clone_factor))
            
            # Use adaptive mutation rate
            current_mutation_rate = mutation_rate
            mutants = self._mutate_population(clones)
            
            # SA on top K individuals every sa_interval generations
            if gen % self.sa_interval == 0:
                # Sort by fitness
                scored_mutants = [(ind, self.fitness_function(ind)) for ind in mutants]
                scored_mutants.sort(key=lambda x: x[1])
                
                # Apply SA to top K individuals
                improved_count = 0
                for i in range(min(self.sa_top_k, len(scored_mutants))):
                    improved_solution = self._simulated_annealing(
                        scored_mutants[i][0], 
                        sa_temp, 
                        self.sa_cooling, 
                        self.sa_iters
                    )
                    
                    # Calculate improvement
                    original_fitness = scored_mutants[i][1]
                    improved_fitness = self.fitness_function(improved_solution)
                    
                    # Only replace if there was actual improvement
                    if improved_fitness < original_fitness:
                        mutants[mutants.index(scored_mutants[i][0])] = improved_solution
                        improved_count += 1
                
                # If SA is not effective, adjust parameters
                if improved_count == 0 and sa_temp > 1.0:
                    sa_temp *= 1.5  # Increase temperature if no improvements
            
            # IGA memory update and utilization
            if gen % self.iga_interval == 0:
                # Update memory with current solutions
                new_solutions_added = 0
                for ind in mutants:
                    if self._update_iga_memory(ind):
                        new_solutions_added += 1
                
                # Clean memory periodically to prevent excessive growth
                self._clean_memory(max_size=100, current_gen=gen)
                
                # Inject memory solutions back into population
                if gen > 0:  # Don't inject in the first generation
                    mutants = self._inject_memory_solutions(mutants, gen)
            
            # Evaluate and select new population
            scored_mutants = [(ind, self.fitness_function(ind)) for ind in mutants]
            scored_mutants.sort(key=lambda x: x[1])
            
            # Select top individuals for next generation
            population = [ind for ind, _ in scored_mutants[:self.pop_size]]
            current_best_fitness = scored_mutants[0][1]
            
            # Update global best if needed
            if current_best_fitness < best_fitness:
                best_solution = scored_mutants[0][0]
                best_fitness = current_best_fitness
            
            if verbose and (gen % 5 == 0 or gen == generations - 1):
                print(f"Gen {gen}: Best Fitness = {best_fitness:.4f}, "
                      f"Temp = {sa_temp:.2f}, Mut = {mutation_rate:.2f}")
        
        execution_time = time.time() - start_time
        
        if verbose:
            print(f"Optimization completed in {execution_time:.2f} seconds")
            print(f"Best fitness: {best_fitness:.4f}")
            print(f"Memory size: {len(self.memory)} unique solutions")
        
        return best_solution, best_fitness, execution_time
    
    def decode_solution(self, solution: Solution) -> Dict[str, Any]:
        """
        Decode the encoded solution into a human-readable schedule.
        
        Returns a dictionary with:
        - schedule: List of (task_id, resource_id, start_time, finish_time) tuples
        - makespan: Total completion time
        - resource_utilization: Dictionary of resource utilization stats
        """
        schedule = self._solution_to_schedule(solution)
        
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
