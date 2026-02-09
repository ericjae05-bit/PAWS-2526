import numpy as np
import pandas as pd

from functions import functions as fn


def main():
    """
    Main function to process, analyze and visualize the water system experiment data.
    """
    # Setup file path
    file_path = "./data/data_GdD_WiSe2526.h5"

    # Define lists for controllers, topologies, and disruptions
    controllers = ["ARIMA", "DTW", "PID"]
    topologies = ["Coupled", "Decentral", "Central"]
    disruptions = [
        "BlockageConstant",
        "BlockageCosine",
        "PumpOutage",
        "NoDisruption",
    ]

    # Generate all possible group names
    group_names = fn.generate_group_name(controllers, topologies, disruptions)

    # Define assigned groups (replace with your assigned groups from Moodle)
    considered_groups = [
        "ARIMA_Decentral_BlockageConstant",
        "PID_Central_BlockageConstant",
        "PID_Decentral_BlockageCosine",
        "PID_Decentral_PumpOutage"
    ]

    # Initialize processed data DataFrame
    processed_data = pd.DataFrame(
        columns=[
            "power_mean",
            "power_std",
            "service_loss_mean",
            "service_loss_std",
        ]
    )

    # Outer loop: Iterate through all groups
    for group in group_names:
        # Skip if not in considered groups
        if group not in considered_groups:
            continue

        # Read setpoint metadata for this group
        setpoint = fn.read_metadata(file_path, group, "setpoint")
        if setpoint is None:
            print(f"Warning: No setpoint found for group '{group}'. Skipping this group.")
            continue

        # Initialize lists for service loss and power for this group
        groups_service_loss = []
        groups_power = []

        # Inner loop: Iterate through runs 1 to 10
        for run_id in range(1, 11):
            run = f"run_{run_id:02d}"
            base_path = f"{group}/{run}"

            # Read start time index metadata
            start_time_index = fn.read_metadata(
                file_path, base_path, "analyse_start_time_index"
            )

            # Read measurement data
            tank_pressure = fn.read_data(file_path, f"{base_path}/tank_1_pressure")
            pump_1 = fn.read_data(file_path, f"{base_path}/pump_1_power")
            pump_2 = fn.read_data(file_path, f"{base_path}/pump_2_power")
            time = fn.read_data(file_path, f"{base_path}/time")

            # Check if any data is missing
            if any(x is None for x in (tank_pressure, pump_1, pump_2, time)):
                print(f"Warning: Missing data in {group}, {run}. Appending NaN values.")
                groups_service_loss.append(np.nan)
                groups_power.append(np.nan)
                continue

            # Cap service data
            service_fill = fn.cap_service_data(tank_pressure, setpoint)

            # Check for negative values in pump power
            if not (fn.check_negative_values(pump_1) and fn.check_negative_values(pump_2)):
                print(f"Warning: Negative power values in {group}, {run}")

            # Calculate service fill integral from start_time_index onwards
            service_fill_integral = fn.integral_with_time_step(
                service_fill[start_time_index:],
                time[start_time_index:]
            )

            # Calculate service target integral
            service_target_signal = np.full_like(
                service_fill[start_time_index:], setpoint
            )
            service_target_integral = fn.integral_with_time_step(
                service_target_signal,
                time[start_time_index:]
            )

            # Calculate service loss in percent
            service_loss_percent = fn.calculate_service_loss(
                service_fill_integral, service_target_integral
            )

            # Calculate total energy consumption for both pumps
            total_energy_ws = (
                fn.integral_with_time_step(pump_1, time) +
                fn.integral_with_time_step(pump_2, time)
            )
            total_energy_wh = fn.convert_Ws_to_Wh(total_energy_ws)

            # Append results to lists
            groups_service_loss.append(service_loss_percent)
            groups_power.append(total_energy_wh)

        # Calculate mean and standard deviation for this group
        mean_service_loss, std_service_loss = fn.calculate_mean_and_std(
            groups_service_loss
        )
        mean_power, std_power = fn.calculate_mean_and_std(groups_power)

        # Store results in processed_data DataFrame
        processed_data.loc[group] = [
            mean_power,
            std_power,
            mean_service_loss,
            std_service_loss,
        ]

    # Define archive path
    data_archive_path = "./plotid/data_GdD_plot_WiSe2526.h5"

    # Define metadata for plotting
    metadata = {
        "legend_title": "Configuration",
        "x_label": "Service loss",
        "x_unit": "%",
        "y_label": "Energy consumption",
        "y_unit": "Wh",
    }

    # Save DataFrame with metadata to HDF5
    fn.save_dataframe_in_hdf5_with_metadata(
        processed_data,
        data_archive_path,
        "plotdata",
        metadata,
    )

    # Read plot data back
    plot_data, plot_format_data = fn.read_plot_data(
        data_archive_path, "plotdata"
    )

    # Generate plot
    fig = fn.plot_service_loss_vs_power(plot_data, plot_format_data)

    # Publish plot with source files
    fn.publish_plot(
        fig,
        [data_archive_path, "./main.py", "./functions/functions.py"],
        "./plotid",
    )


if __name__ == "__main__":
    main()