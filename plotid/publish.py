def publish(destination_path):
    """
    Publishes the plot (in our case, just prints confirmation).
    
    Args:
        destination_path: path where files were saved
    """
    from plotid.tagplot import _last_output_dir
    
    if _last_output_dir:
        print(f"\n{'='*60}")
        print(f"Published to: {_last_output_dir}")
        print(f"{'='*60}\n")
    else:
        print(f"Published to: {destination_path}")