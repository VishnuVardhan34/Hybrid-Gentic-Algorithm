import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

def create_enhanced_flowchart():
    """
    Create an enhanced flowchart for the hybrid algorithm with better spacing,
    no overlapping boxes, and clear yes/no decision paths.
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(16, 24))
    
    # Define colors
    colors = {
        'start_end': '#4CAF50',  # Green
        'process': '#2196F3',    # Blue
        'decision': '#FFC107',   # Yellow/Amber
        'cga': '#E91E63',        # Pink
        'sa': '#9C27B0',         # Purple
        'iga': '#FF9800',        # Orange
        'arrow': '#000000',      # Black
        'text': '#000000',       # Black
        'background': '#FFFFFF'  # White
    }
    
    # Set background color
    fig.patch.set_facecolor(colors['background'])
    ax.set_facecolor(colors['background'])
    
    # Define box dimensions
    box_width = 0.3
    box_height = 0.05
    decision_width = 0.3
    decision_height = 0.06
    
    # Define spacing
    x_center = 0.5
    y_spacing = 0.035
    
    # Track current y position (start from top)
    y_pos = 0.98
    
    # Dictionary to store key positions
    positions = {}
    
    # Helper functions
    def add_box(label, y, color, width=box_width, height=box_height, x=x_center):
        """Add a process box with the given label at position y"""
        rect = patches.Rectangle((x - width/2, y - height/2), width, height, 
                                linewidth=1, edgecolor='black', facecolor=color, alpha=0.8)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=10, fontweight='bold')
        return y
    
    def add_decision(label, y, color=colors['decision'], width=decision_width, height=decision_height, x=x_center):
        """Add a decision diamond with the given label at position y"""
        diamond = patches.RegularPolygon((x, y), 4, radius=width/1.4, 
                                        orientation=np.pi/4, linewidth=1, 
                                        edgecolor='black', facecolor=color, alpha=0.8)
        ax.add_patch(diamond)
        ax.text(x, y, label, ha='center', va='center', fontsize=10, fontweight='bold')
        return y
    
    def add_arrow(start_y, end_y, start_x=x_center, end_x=x_center, label=None, arrow_color=colors['arrow'], yes_no=None, connection_style='arc3,rad=0.0'):
        """Add an arrow from (start_x, start_y) to (end_x, end_y) with optional label"""
        # Calculate arrow properties
        dx = end_x - start_x
        dy = end_y - start_y
        
        # Create the arrow
        arrow = patches.FancyArrowPatch(
            (start_x, start_y), 
            (end_x, end_y), 
            arrowstyle='->', 
            color=arrow_color, 
            connectionstyle=connection_style, 
            linewidth=1.5,
            zorder=1  # Ensure arrows are drawn below text
        )
        ax.add_patch(arrow)
        
        # Add label if provided
        if label:
            mid_x = start_x + dx/2
            mid_y = start_y + dy/2
            ax.text(mid_x, mid_y, label, ha='center', va='center', fontsize=9, 
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'),
                    zorder=2)  # Ensure text is above arrows
        
        # Add Yes/No for decision branches
        if yes_no:
            # Determine position for yes/no label based on direction
            if abs(dx) > abs(dy):  # Horizontal arrow
                if dx > 0:  # Right branch
                    text_x = start_x + dx/3
                    text_y = start_y + dy/3 - 0.01
                else:  # Left branch
                    text_x = start_x + dx/3
                    text_y = start_y + dy/3 - 0.01
            else:  # Vertical or diagonal arrow
                if dy < 0:  # Downward
                    text_x = start_x + dx/3 + (0.02 if dx >= 0 else -0.02)
                    text_y = start_y + dy/3
                else:  # Upward
                    text_x = start_x + dx/3 + (0.02 if dx >= 0 else -0.02)
                    text_y = start_y + dy/3
            
            # Create a text box with the yes/no label
            ax.text(text_x, text_y, yes_no, ha='center', va='center', fontsize=9, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.9, edgecolor='black', boxstyle='round,pad=0.1'),
                    zorder=3)  # Ensure yes/no labels are on top
    
    # Start node
    y_pos = add_box("Start", y_pos, colors['start_end'])
    positions['start'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    # Initialize parameters
    y_pos = add_box("Initialize Parameters\n(SA Temperature, Mutation Rate, Clone Factor, Memory)", y_pos, colors['process'])
    positions['init_params'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    # Generate initial population
    y_pos = add_box("Generate Initial Population", y_pos, colors['process'])
    positions['init_pop'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    # Evaluate initial solutions
    y_pos = add_box("Evaluate Initial Solutions", y_pos, colors['process'])
    positions['eval_init'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    # Main loop start
    y_pos = add_box("Start Main Loop\n(For each generation)", y_pos, colors['process'])
    positions['main_loop'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    # Adjust parameters
    y_pos = add_box("Adjust Parameters Based on Progress\n(Adaptive Control)", y_pos, colors['process'])
    positions['adjust_params'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    # CGA section - highlighted in pink
    y_pos = add_box("Clone Population\n(Based on Clone Factor)", y_pos, colors['cga'])
    positions['clone_pop'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    y_pos = add_box("Apply Mutation to Clones\n(Based on Mutation Rate)", y_pos, colors['cga'])
    positions['mutate'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    y_pos = add_box("Evaluate Mutated Solutions", y_pos, colors['cga'])
    positions['eval_mutated'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    # SA Decision
    y_pos = add_decision("Apply SA this\ngeneration?", y_pos)
    positions['sa_decision'] = (x_center, y_pos)
    y_pos -= y_spacing * 3
    
    # SA section - right branch - highlighted in purple
    sa_x = x_center + 0.3
    sa_y = y_pos + y_spacing * 1.5
    
    sa_y = add_box("Select Top Solutions for SA", sa_y, colors['sa'], x=sa_x)
    positions['sa_select'] = (sa_x, sa_y)
    sa_y -= y_spacing * 2
    
    sa_y = add_box("Apply Adaptive Perturbation\n(Based on Temperature)", sa_y, colors['sa'], x=sa_x)
    positions['sa_perturb'] = (sa_x, sa_y)
    sa_y -= y_spacing * 2
    
    sa_y = add_box("Accept/Reject Based on\nProbability and Temperature", sa_y, colors['sa'], x=sa_x)
    positions['sa_accept'] = (sa_x, sa_y)
    sa_y -= y_spacing * 2
    
    sa_y = add_box("Update Temperature\n(With Periodic Reheating)", sa_y, colors['sa'], x=sa_x)
    positions['sa_temp'] = (sa_x, sa_y)
    
    # IGA Decision
    y_pos = add_decision("Apply IGA this\ngeneration?", y_pos)
    positions['iga_decision'] = (x_center, y_pos)
    y_pos -= y_spacing * 3
    
    # IGA section - left branch - highlighted in orange
    iga_x = x_center - 0.3
    iga_y = y_pos + y_spacing * 1.5
    
    iga_y = add_box("Update Memory with\nNew Solutions", iga_y, colors['iga'], x=iga_x)
    positions['iga_update'] = (iga_x, iga_y)
    iga_y -= y_spacing * 2
    
    iga_y = add_box("Clean Memory\n(Remove Old/Low Quality)", iga_y, colors['iga'], x=iga_x)
    positions['iga_clean'] = (iga_x, iga_y)
    iga_y -= y_spacing * 2
    
    iga_y = add_box("Inject Solutions from Memory\nto Population", iga_y, colors['iga'], x=iga_x)
    positions['iga_inject'] = (iga_x, iga_y)
    
    # Selection and next generation
    y_pos = add_box("Select Solutions for Next Generation", y_pos, colors['process'])
    positions['select'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    y_pos = add_box("Update Best Solution", y_pos, colors['process'])
    positions['update_best'] = (x_center, y_pos)
    y_pos -= y_spacing * 2
    
    # Termination decision
    y_pos = add_decision("Termination\nCondition Met?", y_pos)
    positions['termination'] = (x_center, y_pos)
    y_pos -= y_spacing * 3
    
    # End node
    y_pos = add_box("Return Best Solution", y_pos, colors['start_end'])
    positions['end'] = (x_center, y_pos)
    
    # Add arrows to connect the nodes
    # Main flow - vertical connections
    add_arrow(positions['start'][1] - box_height/2, positions['init_params'][1] + box_height/2, 
              connection_style='arc3,rad=0')
    add_arrow(positions['init_params'][1] - box_height/2, positions['init_pop'][1] + box_height/2, 
              connection_style='arc3,rad=0')
    add_arrow(positions['init_pop'][1] - box_height/2, positions['eval_init'][1] + box_height/2, 
              connection_style='arc3,rad=0')
    add_arrow(positions['eval_init'][1] - box_height/2, positions['main_loop'][1] + box_height/2, 
              connection_style='arc3,rad=0')
    add_arrow(positions['main_loop'][1] - box_height/2, positions['adjust_params'][1] + box_height/2, 
              connection_style='arc3,rad=0')
    add_arrow(positions['adjust_params'][1] - box_height/2, positions['clone_pop'][1] + box_height/2, 
              connection_style='arc3,rad=0')
    add_arrow(positions['clone_pop'][1] - box_height/2, positions['mutate'][1] + box_height/2, 
              connection_style='arc3,rad=0')
    add_arrow(positions['mutate'][1] - box_height/2, positions['eval_mutated'][1] + box_height/2, 
              connection_style='arc3,rad=0')
    add_arrow(positions['eval_mutated'][1] - box_height/2, positions['sa_decision'][1] + decision_height/2, 
              connection_style='arc3,rad=0')
    
    # SA branch - right side
    # From decision to SA component
    add_arrow(positions['sa_decision'][0], positions['sa_decision'][1], 
              positions['sa_select'][0], positions['sa_select'][1] + box_height/2, 
              yes_no="Yes", connection_style='arc3,rad=0.2')
    
    # Within SA component - vertical connections
    add_arrow(positions['sa_select'][1] - box_height/2, positions['sa_perturb'][1] + box_height/2, 
              start_x=positions['sa_select'][0], end_x=positions['sa_perturb'][0],
              connection_style='arc3,rad=0')
    add_arrow(positions['sa_perturb'][1] - box_height/2, positions['sa_accept'][1] + box_height/2, 
              start_x=positions['sa_perturb'][0], end_x=positions['sa_accept'][0],
              connection_style='arc3,rad=0')
    add_arrow(positions['sa_accept'][1] - box_height/2, positions['sa_temp'][1] + box_height/2, 
              start_x=positions['sa_accept'][0], end_x=positions['sa_temp'][0],
              connection_style='arc3,rad=0')
    
    # From SA back to main flow
    add_arrow(positions['sa_temp'][0], positions['sa_temp'][1] - box_height/2, 
              positions['iga_decision'][0], positions['iga_decision'][1] + decision_height/2,
              connection_style='arc3,rad=-0.2')
    
    # No path from SA decision - direct to IGA decision
    add_arrow(positions['sa_decision'][0], positions['sa_decision'][1], 
              positions['iga_decision'][0], positions['iga_decision'][1] + decision_height/2, 
              yes_no="No", connection_style='arc3,rad=0')
    
    # IGA branch - left side
    # From decision to IGA component
    add_arrow(positions['iga_decision'][0], positions['iga_decision'][1], 
              positions['iga_update'][0], positions['iga_update'][1] + box_height/2, 
              yes_no="Yes", connection_style='arc3,rad=-0.2')
    
    # Within IGA component - vertical connections
    add_arrow(positions['iga_update'][1] - box_height/2, positions['iga_clean'][1] + box_height/2, 
              start_x=positions['iga_update'][0], end_x=positions['iga_clean'][0],
              connection_style='arc3,rad=0')
    add_arrow(positions['iga_clean'][1] - box_height/2, positions['iga_inject'][1] + box_height/2, 
              start_x=positions['iga_clean'][0], end_x=positions['iga_inject'][0],
              connection_style='arc3,rad=0')
    
    # From IGA back to main flow
    add_arrow(positions['iga_inject'][0], positions['iga_inject'][1] - box_height/2, 
              positions['select'][0], positions['select'][1] + box_height/2,
              connection_style='arc3,rad=0.2')
    
    # No path from IGA decision - direct to selection
    add_arrow(positions['iga_decision'][0], positions['iga_decision'][1], 
              positions['select'][0], positions['select'][1] + box_height/2, 
              yes_no="No", connection_style='arc3,rad=0')
    
    # Continue main flow - vertical connections
    add_arrow(positions['select'][1] - box_height/2, positions['update_best'][1] + box_height/2,
              connection_style='arc3,rad=0')
    add_arrow(positions['update_best'][1] - box_height/2, positions['termination'][1] + decision_height/2,
              connection_style='arc3,rad=0')
    
    # Termination decision branches
    add_arrow(positions['termination'][0], positions['termination'][1], 
              positions['end'][0], positions['end'][1] + box_height/2, 
              yes_no="Yes", connection_style='arc3,rad=0')
    
    # Loop back if not terminated - with smoother curves
    add_arrow(positions['termination'][0] + decision_width/2, positions['termination'][1], 
              x_center + 0.45, positions['termination'][1], 
              yes_no="No", connection_style='arc3,rad=0')
    add_arrow(x_center + 0.45, positions['termination'][1], 
              x_center + 0.45, positions['main_loop'][1],
              connection_style='arc3,rad=0')
    add_arrow(x_center + 0.45, positions['main_loop'][1], 
              positions['main_loop'][0], positions['main_loop'][1],
              connection_style='arc3,rad=0')
    
    # Add algorithm component labels
    plt.text(0.2, 0.93, "HYBRID ALGORITHM FLOWCHART", fontsize=18, fontweight='bold', ha='center')
    plt.text(0.2, 0.90, "CGA-SA-IGA", fontsize=16, fontweight='bold', ha='center')
    
    # Add component legend
    legend_x = 0.85
    legend_y_start = 0.93
    legend_y_spacing = 0.03
    legend_box_width = 0.02
    legend_box_height = 0.02
    
    # Add legend title
    plt.text(legend_x - 0.05, legend_y_start + 0.01, "ALGORITHM COMPONENTS", fontsize=12, fontweight='bold', ha='left')
    
    # Add legend items
    components = [
        ("Start/End", colors['start_end']),
        ("Process", colors['process']),
        ("Decision", colors['decision']),
        ("CGA Component", colors['cga']),
        ("SA Component", colors['sa']),
        ("IGA Component", colors['iga'])
    ]
    
    for i, (label, color) in enumerate(components):
        y = legend_y_start - i * legend_y_spacing
        rect = patches.Rectangle((legend_x - 0.1, y - legend_box_height/2), legend_box_width, legend_box_height, 
                                linewidth=1, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        plt.text(legend_x - 0.07, y, label, fontsize=10, va='center')
    
    # Add algorithm description
    description = [
        "ALGORITHM DESCRIPTION:",
        "",
        "This hybrid algorithm combines three optimization techniques:",
        "",
        "1. Clone-based Genetic Algorithm (CGA):",
        "   - Creates multiple clones of solutions",
        "   - Applies mutation to explore solution space",
        "   - Provides population diversity",
        "",
        "2. Simulated Annealing (SA):",
        "   - Improves promising solutions",
        "   - Uses temperature to control acceptance probability",
        "   - Helps escape local optima",
        "",
        "3. Imperialist Genetic Algorithm (IGA):",
        "   - Maintains memory of good solutions",
        "   - Periodically injects memory solutions",
        "   - Preserves high-quality solutions",
        "",
        "The algorithm uses adaptive parameters that adjust",
        "based on optimization progress, allowing it to",
        "balance exploration and exploitation effectively."
    ]
    
    desc_x = 0.85
    desc_y_start = 0.75
    desc_y_spacing = 0.018
    
    for i, line in enumerate(description):
        plt.text(desc_x - 0.1, desc_y_start - i * desc_y_spacing, line, fontsize=9, ha='left')
    
    # Remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Save the figure
    output_dir = os.path.join('results', 'images')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'hybrid_algorithm_flowchart.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    print(f"Enhanced flowchart saved to {output_path}")
    return output_path

if __name__ == "__main__":
    create_enhanced_flowchart()
