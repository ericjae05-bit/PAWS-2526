from typing import Any, Dict, List, Optional, Tuple, Union

import h5py as h5
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from numpy.typing import NDArray
from plotid.publish import publish
from plotid.tagplot import tagplot

import warnings

def generate_group_name(
    controller: Union[str, List[str]],
    topology: Union[str, List[str]],
    disruption: Union[str, List[str]],
) -> List[str]:
    if isinstance(controller, str):
        controller = [controller]
    if isinstance(topology, str):
        topology = [topology]
    if isinstance(disruption, str):
        disruption = [disruption]

    return [
        f"{c}_{t}_{d}"
        for c in controller
        for t in topology
        for d in disruption 
    ]


def read_metadata(file: str, path: str, attr_key: str) -> Any:
    """
    Reads metadata from a group or dataset in an HDF5 file.
    
    Parameters:
        file (str): Path to the HDF5 file.
        path (str): Path to the group or dataset inside the file.
        attr_key (str): Name of the metadata attribute to read.

    Returns:
        Any: Value of the metadata attribute if it exists, otherwise None.
    """
    try:
        with h5.File(file, "r") as f:
            if path not in f:
                warnings.warn(f"Path '{path}' does not exist in the HDF5 file.")
                return None
            obj = f[path] 
            if attr_key not in obj.attrs:
                warnings.warn(f"Attribute '{attr_key}' does not exist at path '{path}'.")
                return None 
            return obj.attrs[attr_key]
    except OSError:
        warnings.warn("Could not open HDF5 file.")
        return None  
    

def read_data(file: str, path: str) -> Optional[NDArray]:
    """
    Reads a dataset from an HDF5 file and returns it as a 1D numpy array.

    Parameters:
        file (str): Path to the HDF5 file.
        path (str): Path to the dataset inside the HDF5 file.

    Returns:
        Optional[NDArray]: The dataset as a numpy array or None if the path does not exist
                           or is not a dataset.
    """
    try:
        with h5.File(file, "r") as f: 
            if path not in f:
                warnings.warn(f"Dataset '{path}' does not exist.")
                return None
            if not isinstance(f[path], h5.Dataset):
                warnings.warn(f"Path '{path}' is not a dataset.")
                return None
            return np.asarray(f[path])
    except Exception as exc:
        warnings.warn(str(exc)) 
        return None 


def cap_service_data(service_data: NDArray, setpoint: float) -> NDArray:
    """
    Caps service data values according to the setpoint:
        - Values greater than setpoint are set to setpoint.
        - Negative values are set to 0. 
        - All other values remain unchanged.
    
    Parameters:
        service_data (NDArray): Array of service data values.
        setpoint (float): The maximum allowed value (setpoint).
    """
    capped = np.clip(service_data, 0.0, setpoint)
    return capped 


def check_negative_values(array: NDArray) -> bool:
    """
    Checks whether all values in the array are greater than or equal to zero.
    """
    return np.all(array >= 0.0) 


def integral_with_time_step(data: NDArray, time_steps: NDArray) -> float:
    """
    Computes the integral using the trapezoidal rule with given time steps. 
    """
    if len(data) != len(time_steps):
        warnings.warn("Data and time arrays have different lengths.")
        return None
    
    integral = 0.0
    for i in range (len(data) - 1):
        dt = time_steps[i + 1] - time_steps[i]
        integral += 0.5 * (data[i] + data[i + 1]) * dt 
    return float(integral) 


def calculate_service_loss(service_fill: float, service_target: float) -> float:
    """
    Calculates the service loss in percent.

    Parameters:
        service_fill: Actual service level (tank presure).
        service_target: Target service level.

    Return:
        Service loss in percent as a float.
    """
    return 100.0 * (1.0 - (service_fill / service_target)) 


def convert_Ws_to_Wh(energy_in_Ws: float) -> float:
    """
    Converts energy from watt-seconds (Ws) to watt-hours (Wh).

    Parameter:
        Energy_in_Ws: energy value in watt-seconds.

    Return:
        Energy value in watt-hours.
    """
    return energy_in_Ws / 3600.0 


def calculate_mean_and_std(data: List[float]) -> Tuple[float, float]:
    """
    Calculates the mean value and standard deviationof a one-dimensional datalist.

    Parameter:
        data: List of float avlues.
    
    Return:
        Tuple containing (mean, standard deviation)
    """
    arr = np.asarray(data, dtype=float)
    return float(np.mean(arr)), float(np.std(arr))  


def save_dataframe_in_hdf5_with_metadata(
    df: pd.DataFrame,
    hdf5_path: str,
    group_name: str,
    metadata: Dict[str, Any],
) -> None:
    """
    Saves a DataFrame to an HDF5 file under a given group name and 
    stores metadata as attributes of that group.

    Parameters:
        df: DataFrame to be stored.
        hdf5_path_ Path to the HDF5 file.
        group_name: Name of the group inside the HDF5 file.
        metadata: Dictionary containing metadatato be stored as attributes. 
    """
    with pd.HDFStore(hdf5_path, "a") as store:

        if group_name in store:
            store.remove(group_name) 

        store.put(group_name, df, 'table')

        storer = store.get_storer(group_name)

# Current implementation stores metadata items separately, but read_plot_data expects a single metadata attribute
#        for key, value in metadata.items():
#            storer.attrs[key] = value 

        storer.attrs.metadata = metadata 


def read_plot_data(
    file_path: str, group_path: str
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Reads plot data and metadata from a given group inside an HDF5 file.

    Parameters:
        file_path: Path to the HDF5 file.
        group_path: Path to the group inside the HDF5 file.

    Return: 
        Tuple containing ...
        (1) ... a DataFrame with the stored data.
        (2) ... a dictionary with plot labels and legend title.
    """
    with pd.HDFStore(file_path, mode="r") as store: 
        df = store[group_path] 
        metadata = store.get_storer(group_path).attrs.metadata 
    return df, metadata 


def plot_service_loss_vs_power(
    processed_data: pd.DataFrame, plot_format_data: Dict[str, str]
) -> Figure:
    """
    Plots the energy consumption versus service loss with error bars.

    Parameters:
        processed_data: DataFrame containig mean and std values for service loss and power.
        plot_format_data: Dictionary containing labels and legend title for the plot. 

    Return:
        matplotlib Figure object.
    """
    fig, ax = plt.subplots()


    for label in processed_data.index:
        #ax.errorbar(
        #    processed_data.loc[label, "service_loss_mean"],  # ✓ correct x
        #    processed_data.loc[label, "servive_loss_std"],   # ✗ TYPO + WRONG value
        #    xerr=processed_data.loc[label, "power_mean"],     # ✗ WRONG - should be service_loss_std
        #    y_err=processed_data.loc[label, "power_std"],     # ✗ wrong parameter name (should be yerr)
        #    fmt="o",
        #    label=label,
        #)

        ax.errorbar(
            processed_data.loc[label, "service_loss_mean"],      # x values
            processed_data.loc[label, "power_mean"],             # y values
            xerr=processed_data.loc[label, "service_loss_std"],  # x error bars
            yerr=processed_data.loc[label, "power_std"],         # y error bars
            fmt="o",
            label=label,
        )


    ax.set_xlabel(plot_format_data["x_label"])
    ax.set_ylabel(plot_format_data["y_label"])
    ax.legend(title=plot_format_data["legend_title"])
    ax.grid(True)


    return fig 


def publish_plot(
    fig: Figure, source_paths: Union[str, List[str]], destination_path: str
) -> None:
    """
    Publishes a plot along with relevant source data using plotid.
    
    Parameters:
        fig: matplotlib Figure object containing the plot.
        source_paths: Path or list of paths to files required for the plot.
        destination_path: Folder where the plot and source files should be saved.
    """
    tagplot(
        fig,
        source_paths=source_paths,
        destination_path=destination_path,
        id_method="time",
        prefix="GdD_WS_2526_3774919",  # Replace with YOUR Matrikelnummer
    )
    publish(destination_path)