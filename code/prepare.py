import pandas as pd
import os
import yaml

def process_monthly_data(source_dir, output_dir):
    """Process each CSV file to extract monthly data and save modified versions."""
    csv_files = [f for f in os.listdir(source_dir) if f.endswith('.csv')]  # List all CSV files in the directory
    
    for filename in csv_files:
        file_path = os.path.join(source_dir, filename)
        df = pd.read_csv(file_path)
        df['DATE'] = pd.to_datetime(df['DATE'])
        df['Month'] = df['DATE'].dt.month  # Extract month from DATE column

        # Identify and transform column names based on specific conditions
        monthly_cols = [col for col in df.columns if 'Monthly' in col]
        params = []
        for col in monthly_cols:
            new_col_name = col.replace('Monthly', '')
            if 'WetBulb' not in new_col_name and 'Departure' not in new_col_name:
                new_col_name = new_col_name.replace('Temperature', 'DryBulbTemperature')
            params.append(new_col_name)

        # Prepare and save the modified DataFrame
        monthly_data = df.dropna(how='all', subset=monthly_cols)[['Month'] + monthly_cols]
        output_csv_path = os.path.join(output_dir, filename.replace('.csv', '_prepare.csv'))
        monthly_data.to_csv(output_csv_path, index=False)

        # Save the list of transformed column names to a text file
        params_file_path = os.path.join(output_dir, filename.replace('.csv', '.txt'))
        with open(params_file_path, 'w') as file:
            file.write(','.join(params))

def main():
    """Load configurations and process the CSV files."""
    config = yaml.safe_load(open("params.yaml"))
    input_dir = config["data_source"]["temp_dir"]
    output_dir = config["data_prepare"]["dest_folder"]
    
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
    process_monthly_data(input_dir, output_dir)

if _name_ == "_main_":
    main()
