import matplotlib.pyplot as plt
import shutil
import os
from datetime import datetime


def tagplot(fig, source_paths, destination_path, id_method="time", prefix="plot"):
    """
    Tags and saves a plot with source files.
    
    Args:
        fig: matplotlib Figure object
        source_paths: list of source file paths
        destination_path: where to save output
        id_method: method to generate ID (only 'time' supported)
        prefix: prefix for output files
    """
    # Generate timestamp ID
    if id_method == "time":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_id = f"{prefix}_{timestamp}"
    else:
        plot_id = prefix
    
    # Create output directory
    output_dir = os.path.join(destination_path, plot_id)
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the plot
    plot_filename = os.path.join(output_dir, f"{plot_id}.png")
    fig.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {plot_filename}")
    
    # Copy source files
    if isinstance(source_paths, str):
        source_paths = [source_paths]
    
    for src in source_paths:
        if os.path.exists(src):
            dest_filename = os.path.basename(src)
            dest_path = os.path.join(output_dir, dest_filename)
            shutil.copy(src, dest_path)
            print(f"Copied: {src} -> {dest_path}")
    
    # Create required_imports.txt (for plotid compatibility)
    imports_file = os.path.join(output_dir, "required_imports.txt")
    with open(imports_file, 'w') as f:
        f.write("numpy\n")
        f.write("pandas\n")
        f.write("matplotlib\n")
        f.write("h5py\n")
    
    # Store the output directory for publish()
    global _last_output_dir
    _last_output_dir = output_dir
    
    return plot_id


# Global variable to track last output
_last_output_dir = None