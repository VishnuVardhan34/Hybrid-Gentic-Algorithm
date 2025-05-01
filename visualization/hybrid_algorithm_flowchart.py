import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.path import Path

def create_flowchart(output_file="hybrid_algorithm_flowchart.png"):
    """
    Create a detailed flowchart of the hybrid algorithm execution
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(16, 24))
    
    # Set background color
    fig.patch.set_facecolor('#F5F5F5')
    
    # Define colors
    colors = {
        'start_end': '#4CAF50',      # Green
        'process': '#2196F3',        # Blue
        'decision': '#FFC107',       # Yellow
        'cga': '#E91E63',            # Pink
        'sa': '#9C27B0',             # Purple
        'iga': '#FF9800',            # Orange
        'evaluation': '#795548',     # Brown
        'memory': '#607D8B',         # Blue Grey
        'text': '#212121',           # Dark Grey
        'arrow': '#757575'           # Grey
    }
    
    # Define styles
    box_style = {
        'boxstyle': 'round,pad=0.5',
        'facecolor': 'white',
        'edgecolor': 'black',
        'linewidth': 1,
        'alpha': 0.9
    }
    
    arrow_style = {
        'arrowstyle': '->',
        'linewidth': 1.5,
        'color': colors['arrow']
    }
    
    # Define positions
    y_spacing = 1.0
    y_start = 22
    x_center = 8
    
    # Dictionary to store positions
    positions = {}
    
    # Start node
    y = y_start
    positions['start'] = (x_center, y)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 1.5, y - 0.4), 3, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.4),
        facecolor=colors['start_end'], alpha=0.8
    ))
    ax.text(x_center, y, 'Start', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Parameter initialization
    y -= y_spacing
    positions['init'] = (x_center, y)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['process'], alpha=0.8
    ))
    ax.text(x_center, y, 'Initialize Parameters', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Add detailed info about initialization
    ax.text(x_center + 3.5, y, 
            'SA Temperature, Mutation Rate,\nClone Factor, Memory Dictionary', 
            ha='left', va='center', fontsize=10, color=colors['text'],
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
    
    # Generate population
    y -= y_spacing
    positions['population'] = (x_center, y)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['process'], alpha=0.8
    ))
    ax.text(x_center, y, 'Generate Initial Population', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Evaluate initial population
    y -= y_spacing
    positions['evaluate_init'] = (x_center, y)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['evaluation'], alpha=0.8
    ))
    ax.text(x_center, y, 'Evaluate Initial Population', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Begin generation loop
    y -= y_spacing
    positions['begin_loop'] = (x_center, y)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['process'], alpha=0.8
    ))
    ax.text(x_center, y, 'Begin Generation Loop', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Adjust parameters
    y -= y_spacing
    positions['adjust_params'] = (x_center, y)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['process'], alpha=0.8
    ))
    ax.text(x_center, y, 'Adjust Adaptive Parameters', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Add detailed info about adaptive parameters
    ax.text(x_center + 3.5, y, 
            'Based on improvement:\n'+
            '• If improving: ↓ temperature, ↓ mutation\n'+
            '• If stagnant: ↑ temperature, ↑ mutation\n'+
            '• If stuck: partial population reset', 
            ha='left', va='center', fontsize=10, color=colors['text'],
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
    
    # CGA: Clone
    y -= y_spacing
    positions['cga_clone'] = (x_center, y)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['cga'], alpha=0.8
    ))
    ax.text(x_center, y, 'CGA: Clone Population', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # CGA: Mutate
    y -= y_spacing
    positions['cga_mutate'] = (x_center, y)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['cga'], alpha=0.8
    ))
    ax.text(x_center, y, 'CGA: Mutate Clones', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # SA check
    y -= y_spacing
    positions['sa_check'] = (x_center, y)
    ax.add_patch(patches.Polygon(
        [[x_center - 2, y - 0.4], [x_center + 2, y - 0.4], 
         [x_center + 2, y + 0.4], [x_center - 2, y + 0.4]],
        facecolor=colors['decision'], alpha=0.8
    ))
    ax.text(x_center, y, 'Gen % SA interval == 0?', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # SA: No branch
    positions['sa_no'] = (x_center + 4, y)
    ax.text(x_center + 2.5, y, 'No', ha='center', va='center', 
            fontsize=10, fontweight='bold', color=colors['text'])
    
    # SA: Yes path
    y_sa = y - y_spacing
    positions['sa_yes'] = (x_center, y_sa)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y_sa - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['sa'], alpha=0.8
    ))
    ax.text(x_center, y_sa, 'SA: Select Top K Solutions', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # SA: Apply SA
    y_sa -= y_spacing
    positions['sa_apply'] = (x_center, y_sa)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y_sa - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['sa'], alpha=0.8
    ))
    ax.text(x_center, y_sa, 'SA: Apply Simulated Annealing', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Add detailed info about SA
    ax.text(x_center + 3.5, y_sa, 
            'For each solution:\n'+
            '• Generate neighbor with adaptive perturbation\n'+
            '• Accept if better or probabilistically\n'+
            '• Periodic reheating to escape local optima\n'+
            '• Return best solution found', 
            ha='left', va='center', fontsize=10, color=colors['text'],
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
    
    # SA: Replace solutions
    y_sa -= y_spacing
    positions['sa_replace'] = (x_center, y_sa)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y_sa - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['sa'], alpha=0.8
    ))
    ax.text(x_center, y_sa, 'SA: Replace with Improved Solutions', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Point where SA path rejoins
    y_rejoin = y_sa - y_spacing
    positions['sa_rejoin'] = (x_center, y_rejoin)
    
    # IGA check
    positions['iga_check'] = (x_center, y_rejoin)
    ax.add_patch(patches.Polygon(
        [[x_center - 2, y_rejoin - 0.4], [x_center + 2, y_rejoin - 0.4], 
         [x_center + 2, y_rejoin + 0.4], [x_center - 2, y_rejoin + 0.4]],
        facecolor=colors['decision'], alpha=0.8
    ))
    ax.text(x_center, y_rejoin, 'Gen % IGA interval == 0?', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # IGA: No branch
    positions['iga_no'] = (x_center + 4, y_rejoin)
    ax.text(x_center + 2.5, y_rejoin, 'No', ha='center', va='center', 
            fontsize=10, fontweight='bold', color=colors['text'])
    
    # IGA: Yes path
    y_iga = y_rejoin - y_spacing
    positions['iga_yes'] = (x_center, y_iga)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y_iga - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['iga'], alpha=0.8
    ))
    ax.text(x_center, y_iga, 'IGA: Update Memory with Solutions', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # IGA: Clean memory
    y_iga -= y_spacing
    positions['iga_clean'] = (x_center, y_iga)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y_iga - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['iga'], alpha=0.8
    ))
    ax.text(x_center, y_iga, 'IGA: Clean Memory', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Add detailed info about memory cleaning
    ax.text(x_center + 3.5, y_iga, 
            'Remove entries based on:\n'+
            '• Age (not recently updated)\n'+
            '• Access count (rarely used)\n'+
            '• Quality (worst solutions)\n'+
            '• Maintain max size limit', 
            ha='left', va='center', fontsize=10, color=colors['text'],
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
    
    # IGA: Inject solutions
    y_iga -= y_spacing
    positions['iga_inject'] = (x_center, y_iga)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y_iga - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['iga'], alpha=0.8
    ))
    ax.text(x_center, y_iga, 'IGA: Inject Memory Solutions', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Point where IGA path rejoins
    y_rejoin_iga = y_iga - y_spacing
    positions['iga_rejoin'] = (x_center, y_rejoin_iga)
    
    # Evaluate and select
    positions['evaluate'] = (x_center, y_rejoin_iga)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y_rejoin_iga - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['evaluation'], alpha=0.8
    ))
    ax.text(x_center, y_rejoin_iga, 'Evaluate & Select New Population', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Update best solution
    y_update = y_rejoin_iga - y_spacing
    positions['update_best'] = (x_center, y_update)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y_update - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['process'], alpha=0.8
    ))
    ax.text(x_center, y_update, 'Update Best Solution', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Check termination
    y_terminate = y_update - y_spacing
    positions['terminate_check'] = (x_center, y_terminate)
    ax.add_patch(patches.Polygon(
        [[x_center - 2, y_terminate - 0.4], [x_center + 2, y_terminate - 0.4], 
         [x_center + 2, y_terminate + 0.4], [x_center - 2, y_terminate + 0.4]],
        facecolor=colors['decision'], alpha=0.8
    ))
    ax.text(x_center, y_terminate, 'Generation < Max Generations?', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Continue loop
    positions['continue'] = (x_center - 4, y_terminate)
    ax.text(x_center - 2.5, y_terminate, 'Yes', ha='center', va='center', 
            fontsize=10, fontweight='bold', color=colors['text'])
    
    # End loop
    y_end = y_terminate - y_spacing
    positions['end_loop'] = (x_center, y_end)
    ax.text(x_center + 2.5, y_terminate, 'No', ha='center', va='center', 
            fontsize=10, fontweight='bold', color=colors['text'])
    
    # Return result
    positions['return'] = (x_center, y_end)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 2.5, y_end - 0.4), 5, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.2),
        facecolor=colors['process'], alpha=0.8
    ))
    ax.text(x_center, y_end, 'Return Best Solution', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # End node
    y_end -= y_spacing
    positions['end'] = (x_center, y_end)
    ax.add_patch(patches.FancyBboxPatch(
        (x_center - 1.5, y_end - 0.4), 3, 0.8, 
        boxstyle=patches.BoxStyle("Round", pad=0.4),
        facecolor=colors['start_end'], alpha=0.8
    ))
    ax.text(x_center, y_end, 'End', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    # Add arrows
    add_arrow(ax, positions['start'], positions['init'], arrow_style)
    add_arrow(ax, positions['init'], positions['population'], arrow_style)
    add_arrow(ax, positions['population'], positions['evaluate_init'], arrow_style)
    add_arrow(ax, positions['evaluate_init'], positions['begin_loop'], arrow_style)
    add_arrow(ax, positions['begin_loop'], positions['adjust_params'], arrow_style)
    add_arrow(ax, positions['adjust_params'], positions['cga_clone'], arrow_style)
    add_arrow(ax, positions['cga_clone'], positions['cga_mutate'], arrow_style)
    add_arrow(ax, positions['cga_mutate'], positions['sa_check'], arrow_style)
    
    # SA branch
    add_arrow(ax, positions['sa_check'], positions['sa_yes'], arrow_style, text='Yes')
    add_arrow(ax, positions['sa_yes'], positions['sa_apply'], arrow_style)
    add_arrow(ax, positions['sa_apply'], positions['sa_replace'], arrow_style)
    add_arrow(ax, positions['sa_replace'], positions['sa_rejoin'], arrow_style)
    
    # SA bypass
    add_curved_arrow(ax, positions['sa_check'], positions['sa_rejoin'], arrow_style)
    
    # IGA branch
    add_arrow(ax, positions['iga_check'], positions['iga_yes'], arrow_style, text='Yes')
    add_arrow(ax, positions['iga_yes'], positions['iga_clean'], arrow_style)
    add_arrow(ax, positions['iga_clean'], positions['iga_inject'], arrow_style)
    add_arrow(ax, positions['iga_inject'], positions['iga_rejoin'], arrow_style)
    
    # IGA bypass
    add_curved_arrow(ax, positions['iga_check'], positions['iga_rejoin'], arrow_style)
    
    # Continue flow
    add_arrow(ax, positions['evaluate'], positions['update_best'], arrow_style)
    add_arrow(ax, positions['update_best'], positions['terminate_check'], arrow_style)
    
    # Loop back
    add_curved_arrow_back(ax, positions['terminate_check'], positions['adjust_params'], arrow_style)
    
    # Finish flow
    add_arrow(ax, positions['terminate_check'], positions['return'], arrow_style)
    add_arrow(ax, positions['return'], positions['end'], arrow_style)
    
    # Add title
    ax.text(x_center, y_start + 1.5, 'Hybrid Algorithm (CGA-SA-IGA) Flowchart', 
            ha='center', va='center', fontsize=20, fontweight='bold')
    
    # Add component legend
    legend_x = 1
    legend_y = 2
    legend_spacing = 0.7
    
    # Legend boxes
    component_colors = {
        'Start/End': colors['start_end'],
        'Process': colors['process'],
        'Decision': colors['decision'],
        'CGA Component': colors['cga'],
        'SA Component': colors['sa'],
        'IGA Component': colors['iga'],
        'Evaluation': colors['evaluation']
    }
    
    for i, (name, color) in enumerate(component_colors.items()):
        y_pos = legend_y + i * legend_spacing
        if name == 'Decision':
            ax.add_patch(patches.Polygon(
                [[legend_x, y_pos - 0.3], [legend_x + 1, y_pos - 0.3], 
                 [legend_x + 1, y_pos + 0.3], [legend_x, y_pos + 0.3]],
                facecolor=color, alpha=0.8
            ))
        else:
            ax.add_patch(patches.FancyBboxPatch(
                (legend_x, y_pos - 0.3), 1, 0.6, 
                boxstyle=patches.BoxStyle("Round", pad=0.2),
                facecolor=color, alpha=0.8
            ))
        ax.text(legend_x + 1.5, y_pos, name, ha='left', va='center', 
                fontsize=10, color=colors['text'])
    
    # Set limits
    ax.set_xlim(0, 16)
    ax.set_ylim(y_end - 1, y_start + 2)
    
    # Remove axes
    ax.set_axis_off()
    
    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Flowchart created and saved as {output_file}")
    return output_file

def add_arrow(ax, start_pos, end_pos, style, text=None):
    """Add an arrow between two positions"""
    arrow = patches.FancyArrowPatch(
        start_pos, end_pos, 
        connectionstyle="arc3,rad=0.0", 
        **style
    )
    ax.add_patch(arrow)
    
    # Add text if provided
    if text:
        # Calculate position
        mid_x = (start_pos[0] + end_pos[0]) / 2
        mid_y = (start_pos[1] + end_pos[1]) / 2
        offset_x = 0.3
        
        # Add text
        ax.text(mid_x + offset_x, mid_y, text, 
                ha='center', va='center', fontsize=10, fontweight='bold')

def add_curved_arrow(ax, start_pos, end_pos, style):
    """Add a curved arrow between two positions"""
    arrow = patches.FancyArrowPatch(
        start_pos, end_pos, 
        connectionstyle="arc3,rad=0.3", 
        **style
    )
    ax.add_patch(arrow)

def add_curved_arrow_back(ax, start_pos, end_pos, style):
    """Add a curved arrow going back up from bottom to top"""
    arrow = patches.FancyArrowPatch(
        start_pos, end_pos, 
        connectionstyle="arc3,rad=-0.5", 
        **style
    )
    ax.add_patch(arrow)

if __name__ == "__main__":
    create_flowchart("hybrid_algorithm_flowchart.png")
