import os
import pull_nse_data
import merge_csvs

def run_pipeline():
    output_dir = 'nse_sectors'
    output_file = 'NSE_Sectoral_Master_List.xlsx'

    print("--- Starting Nifty Data Pipeline ---")

    print("\n[1/2] Fetching NSE sector data...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for sector in pull_nse_data.sectors:
        pull_nse_data.download_sector_csv(sector, output_dir)

    print("\n[2/2] Merging CSVs into Master Excel...")
    merge_csvs.merge_csv_files(output_dir, output_file)

    print("\n--- Pipeline Completed Successfully! ---")

if __name__ == '__main__':
    run_pipeline()
