# Hybrid Algorithm for Task Scheduling in Cloud Computing

This project implements and compares several algorithms for task scheduling in cloud computing environments:

1. **Hybrid Algorithm (CGA-SA-IGA)**: A novel approach combining Clone-based Genetic Algorithm (CGA), Simulated Annealing (SA), and Imperialist Genetic Algorithm (IGA)
2. **Conventional Genetic Algorithm (CGA)**: A standard genetic algorithm implementation
3. **Ant Colony Optimization (ACO)**: An implementation of the ant colony optimization metaheuristic

## Project Structure

```
project/
├── data/            # CSV data files with task datasets
├── algorithms/      # Algorithm implementations
│   ├── hybrid_algorithm.py  # Hybrid CGA-SA-IGA implementation
│   ├── genetic_algorithm.py # Standard genetic algorithm
│   └── ant_colony.py        # Ant colony optimization algorithm
├── utils/           # Helper utilities
│   └── data_generator.py    # Generates task datasets
├── visualization/   # Plotting and visualization code
│   └── visualizer.py        # Functions for creating charts
├── results/         # Output directory for results and plots
├── main.py          # Main entry point
├── requirements.txt # Dependencies
└── README.md        # This file
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Generate task datasets and run the experiment:
```bash
python main.py --generate-data --show-plots
```

3. Run with specific options:
```bash
python main.py --task-sizes 100 200 500 --resources 8 --algorithms hybrid ant_colony --generations 100
```

## Command Line Arguments

- `--generate-data`: Generate task datasets before running
- `--task-sizes`: List of task sizes to generate (e.g., `50 100 500`)
- `--resources`: Number of resources to use for scheduling
- `--algorithms`: List of algorithms to run (`hybrid`, `genetic`, `ant_colony`)
- `--generations`: Number of generations/iterations to run
- `--output-dir`: Directory to save results (default: 'results')
- `--show-plots`: Display plots during execution

## Visualization Outputs

The program generates several visualizations:
- Gantt charts of task schedules for each algorithm and dataset size
- Execution time comparison across algorithms and dataset sizes  
- Solution quality (fitness) comparison
- Resource utilization comparison
- Performance metrics by task size (makespan, utilization, deadline violations)

## Dataset Format

The task datasets contain the following information for each task:
- `task_id`: Unique identifier for each task
- `arrival_time`: Time at which the task arrives in the system
- `execution_time`: Time required to execute the task
- `deadline`: Time by which the task should be completed
- `priority`: Priority level of the task (1-5)
- `resource_X`: Resource requirements for each resource type
