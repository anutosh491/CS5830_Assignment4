import pandas as pd
import os
import yaml

def aggregate_data(input_dir, output_dir, cols_dir):
    """Aggregate daily data to monthly averages and map them to corresponding monthly columns."""
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    for filename in csv_files:
        # Read the CSV file and convert DATE column to datetime
        df = pd.read_csv(os.path.join(input_dir, filename))
        df['DATE'] = pd.to_datetime(df['DATE'])
        df['Month'] = df['DATE'].dt.month  # Extract month from the DATE column

        # Identify daily and monthly parameters
        daily_cols = [col for col in df.columns if 'Daily' in col]
        monthly_cols = [col for col in df.columns if 'Monthly' in col]

        # Read the mapping from the associated text file
        mapping_file = os.path.join(cols_dir, filename.replace('.csv', '.txt'))
        with open(mapping_file, 'r') as file:
            monthly_params = file.read().split(',')

        # Determine which daily columns correspond to monthly columns
        retain_cols = []
        rename_mapping = {}
        for daily_col in daily_cols:
            for month_param in monthly_params:
                if month_param in daily_col.replace('Average', '') or ('Average' in daily_col and month_param.replace('Mean', '').replace('Average', '') in daily_col.replace('Average', '')):
                    retain_cols.append(daily_col)
                    rename_mapping[daily_col] = month_param.replace('Mean', '').replace('Average', '')

        # Filter the data and aggregate by month
        df_filtered = df.dropna(how='all', subset=retain_cols)[['Month'] + retain_cols]
        df_filtered = df_filtered.astype({col: float for col in df_filtered.columns if col != 'Month'})
        df_monthly = df_filtered.groupby('Month').mean().reset_index().rename(columns=rename_mapping)

        # Write the aggregated data to a CSV file
        output_file_path = os.path.join(output_dir, filename.replace('.csv', '_process.csv'))
        df_monthly.to_csv(output_file_path, index=False)

def main():
    """Load settings from a YAML file and process the CSV files accordingly."""
    config = yaml.safe_load(open("params.yaml"))
    input_dir = config["data_source"]["temp_dir"]
    cols_dir = config["data_prepare"]["dest_folder"]
    output_dir = config["data_process"]["dest_folder"]

    os.makedirs(output_dir, exist_ok=True)
    aggregate_data(input_dir, output_dir, cols_dir)

if _name_ == "_main_":
    main()
