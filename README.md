# Water Distribution System Resilience Analysis

# Project Overview

This project analyzes the resilience of water distribution systems using experimental data from a test facility at the Institute for Fluid System Technology (FST), TU Darmstadt. The analysis follows the complete data lifecycle: planning, collection, processing, analysis, archiving, and visualization.

# Background

Critical infrastructure systems like water supply networks face various disruptions including pump failures, pipe blockages, and power outages. This project investigates how different network topologies and control strategies perform under various failure scenarios to identify resilient and efficient configurations.

# Experimental Design

The test facility simulates a scaled-down water distribution network with:

- **3 Topologies**: Central, Decentral, Coupled
- **3 Control Strategies**: PID, DTW (Dynamic Time Warping), ARIMA
- **4 Disruption Scenarios**: No Disruption, Constant Blockage, Cosine Blockage, Pump Outage
- **10 Experimental Runs** per configuration

Each combination was tested to measure system performance under different conditions.

# Task Requirements

# Primary Objectives

1. **Data Processing**: Read and clean experimental data from HDF5 files
2. **Data Analysis**: Calculate performance metrics (service loss and energy consumption)
3. **Data Archiving**: Store processed results with metadata for reproducibility
4. **Data Visualization**: Create plots showing trade-offs between resilience and efficiency
5. **Version Control**: Use Git to track all code changes
6. **Documentation**: Provide clear documentation and docstrings

# Performance Metrics

- **Service Loss (%)**: Measures how much tank pressure deviates from target during disruptions. Lower values indicate better resilience.
- **Energy Consumption (Wh)**: Total electrical energy used by pumps. Lower values indicate better efficiency.

# Implementation

# Project Structure
```
pa-ws2526/
├── data/
│   └── data_GdD_WiSe2526.h5          # Input experimental data
├── functions/
│   └── functions.py                   # Utility functions module
├── plotid/                            # Output directory
│   ├── data_GdD_plot_WiSe2526.h5     # Archived processed data
│   └── GdD_WS_2526_XXXXXXX_*/        # Timestamped results
├── main.py                            # Main execution script
└── .git/                              # Version control
```

# Key Functions

# Data Access Functions

- `read_metadata()`: Reads metadata attributes from HDF5 groups/datasets
- `read_data()`: Reads measurement time-series data from HDF5 datasets
- `generate_group_name()`: Creates all possible experimental configuration names

# Data Processing Functions

- `cap_service_data()`: Cleans tank pressure data by capping values at physical limits
- `check_negative_values()`: Validates that power measurements are non-negative
- `integral_with_time_step()`: Calculates integral using trapezoidal rule for non-uniform time steps

# Analysis Functions

- `calculate_service_loss()`: Computes percentage deviation from target service level
- `convert_Ws_to_Wh()`: Converts energy from watt-seconds to watt-hours
- `calculate_mean_and_std()`: Computes statistics over multiple experimental runs

# Archiving Functions

- `save_dataframe_in_hdf5_with_metadata()`: Stores processed data with metadata in HDF5 format
- `read_plot_data()`: Retrieves archived data and formatting information

# Visualization Functions

- `plot_service_loss_vs_power()`: Creates scatter plot with error bars showing performance trade-offs
- `publish_plot()`: Packages plot with source files for reproducibility

# Main Workflow

The main script executes the following workflow:

1. **Setup**: Define file paths and experimental parameters
2. **Generate Group Names**: Create all 36 possible configuration combinations
3. **Filter Assigned Groups**: Process only the 4 assigned experimental configurations
4. **Iterate Through Groups**: For each assigned configuration:
   - Read setpoint metadata
   - Initialize result lists
   - Process 10 experimental runs:
     - Read measurement data (tank pressure, pump power, timestamps)
     - Read analysis start time index
     - Clean data using cap_service_data()
     - Validate power measurements
     - Calculate service fill integral from disruption onset
     - Calculate ideal service target integral
     - Compute service loss percentage
     - Calculate total energy consumption from both pumps
     - Store results for this run
   - Calculate mean and standard deviation over 10 runs
   - Store aggregated results in DataFrame
5. **Archive Results**: Save processed data to HDF5 with metadata
6. **Visualize**: Create plot showing energy consumption vs service loss
7. **Publish**: Package plot with source files and data

# Why This Approach

# Trapezoidal Integration

The trapezoidal rule is used to calculate integrals because:
- Experimental data has non-uniform time steps
- Simple and numerically stable for time-series data
- Accurately captures area under pressure and power curves

# Service Loss Calculation

Service loss is calculated from the disruption start time onwards because:
- Initial stable operation is not relevant to resilience analysis
- Focuses on system response to failures
- Provides fair comparison across different disruption scenarios

# Energy Over Full Time Series

Total energy is calculated over the complete time series because:
- Represents total operational cost
- Includes both normal operation and recovery periods
- Allows comparison of overall efficiency across strategies

# Statistical Aggregation

Mean and standard deviation are computed over 10 runs to:
- Account for experimental variability
- Provide confidence in results
- Enable statistical comparison between configurations

# HDF5 for Archiving

HDF5 format is used for data storage because:
- Supports hierarchical data organization
- Stores metadata alongside data
- Efficient for large numerical datasets
- Standard format in scientific computing

# Results Interpretation

The final plot displays each configuration as a point with error bars:
- X-axis: Service Loss (%) - lower is more resilient
- Y-axis: Energy Consumption (Wh) - lower is more efficient
- **Error bars**: Standard deviation across 10 runs

Ideal configurations appear in the lower-left corner (low service loss, low energy). The plot reveals trade-offs between resilience and efficiency for different topologies and control strategies under various disruption scenarios.

# Dependencies

- Python 3.12
- numpy
- pandas
- h5py
- matplotlib

# Usage
```bash
python main.py
```

This will:
1. Process assigned experimental groups
2. Save processed data to `plotid/data_GdD_plot_WiSe2526.h5`
3. Generate visualization in timestamped subdirectory under `plotid/`

# Version Control

All code changes are tracked using Git with meaningful commit messages. The HDF5 data files are excluded from version control via `.gitignore`.

# Author

Matrikelnummer: 3774919

# Course

Grundlagen der Digitalisierung (GdD)
Wintersemester 2025/2026
TU Darmstadt