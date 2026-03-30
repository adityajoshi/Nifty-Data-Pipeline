import os
import sys
import pandas as pd
from pull_nse_data import sectors

def list_sector_constituents(sector_name, input_dir='nse_sectors'):
    """
    Reads the CSV file for a given sector and prints the constituents
    with the 'NSE:' prefix.
    """
    filename = f"{sector_name}_constituents.csv"
    filepath = os.path.join(input_dir, filename)

    if not os.path.exists(filepath):
        print(f"Error: Could not find data for sector '{sector_name}' at {filepath}.")
        print(f"Please run pull_nse_data.py first to fetch the data.")
        return

    try:
        df = pd.read_csv(filepath)
        if 'Symbol' not in df.columns:
            print(f"Error: 'Symbol' column not found in {filepath}")
            return

        print(f"\nConstituents for {sector_name}:")
        for symbol in df['Symbol']:
            print(f"NSE:{symbol}")

    except Exception as e:
        print(f"Error reading {filepath}: {e}")

def main():
    if len(sys.argv) > 1:
        # If sector name is provided as an argument
        target_sector = sys.argv[1]
        if target_sector in sectors:
            list_sector_constituents(target_sector)
        else:
            print(f"Error: '{target_sector}' is not a recognized sector.")
            print(f"Available sectors: {', '.join(sectors)}")
    else:
        # If no argument is provided, process all sectors
        for sector in sectors:
            list_sector_constituents(sector)

if __name__ == '__main__':
    main()
