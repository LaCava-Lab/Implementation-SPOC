import os
import pandas as pd

filename = "spoc_summary.csv"

def build_spoc_summary(spoc_parent_dir, output_filename=filename):
    spoc_outputs_dir = os.path.join(spoc_parent_dir, 'SPOC_outputs')
    summary_csv_path = os.path.join(spoc_parent_dir, output_filename)

    # Collect all CSV files
    csv_files = [
        os.path.join(spoc_outputs_dir, f)
        for f in os.listdir(os.path.join(spoc_outputs_dir))
        if f.endswith(".csv")
    ]

    if not csv_files:
        print("No CSV files found. Exiting.")
        return

    summary_list = []

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            summary_list.append(df)
        except Exception as e:
            print(f"Skipping {csv_file}: {e}")

    # Concatenate
    summary_df = pd.concat(summary_list, ignore_index=True)

    # Sort
    summary_df = summary_df.sort_values(
        by=["spoc_score", "complex_name"],
        ascending=[False, True]
    )

    # Save
    summary_df.to_csv(summary_csv_path, index=False)

    print(f"SPOC summary table written to: {summary_csv_path}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Using: python summary_table.py <spoc_outputs_dir>")
        sys.exit(1)

    spoc_parent_dir = sys.argv[1]
    build_spoc_summary(spoc_parent_dir)