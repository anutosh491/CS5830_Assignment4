import pandas as pd
import os
import yaml
from sklearn.metrics import r2_score

def compute_r2_scores(ground_truth_dir, predictions_dir, results_dir):
    """Calculate R2 scores between corresponding CSV files in two directories."""
    ground_truth_files = [f for f in os.listdir(ground_truth_dir) if f.endswith('.csv')]
    
    for filename in ground_truth_files:
        gt_path = os.path.join(ground_truth_dir, filename)
        pred_path = os.path.join(predictions_dir, filename.replace('_prepare.csv', '_process.csv'))

        df_gt = pd.read_csv(gt_path).dropna(axis=1, how='all')
        df_pred = pd.read_csv(pred_path).dropna(axis=1, how='all')

        # Identify common columns and months
        common_cols = df_gt.columns.intersection(df_pred.columns)
        df_gt = df_gt.dropna(subset=common_cols)
        df_pred = df_pred.dropna(subset=common_cols)

        common_months = df_gt['Month'].isin(df_pred['Month'])
        df_gt = df_gt[common_months]
        df_pred = df_pred[common_months]

        # Calculate R2 scores for each column
        r2_results = [(col, r2_score(df_gt[col], df_pred[col])) for col in common_cols]
        
        # Determine consistency based on R2 scores
        consistency = "Consistent" if all(score >= 0.9 for _, score in r2_results) else "Inconsistent"

        # Output results to a file
        result_path = os.path.join(results_dir, filename.replace('_prepare.csv', '_r2.txt'))
        with open(result_path, 'w') as result_file:
            result_file.write(f"{consistency}\n")
            result_file.write('\n'.join(f"{col}: {score}" for col, score in r2_results))

def main():
    """Load settings from a YAML file and compute R2 scores."""
    params = yaml.safe_load(open("params.yaml"))
    ground_truth_dir = params["data_prepare"]["dest_folder"]
    predictions_dir = params["data_process"]["dest_folder"]
    results_dir = params["evaluate"]["output"]

    os.makedirs(results_dir, exist_ok=True)
    compute_r2_scores(ground_truth_dir, predictions_dir, results_dir)

if _name_ == "_main_":
    main()
