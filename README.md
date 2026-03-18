# Nifty Data Pipeline

This project contains tools to automate the fetching, merging, and visualization of stock data for various NSE (National Stock Exchange of India) indices. It provides a robust pipeline to download the constituents of multiple sectoral and thematic indices, compile them into a master Excel file, and includes a web interface for data presentation.

## Features

- **Automated Data Retrieval**: `pull_nse_data.py` downloads the latest constituent lists for a predefined set of Nifty indices (e.g., Nifty Auto, Nifty Bank, Nifty IT, etc.) from the official Nifty Indices website and saves them as CSV files in the `nse_sectors/` directory.
- **Data Consolidation**: `merge_csvs.py` aggregates all downloaded CSV files into a comprehensive Excel workbook (`NSE_Sectoral_Master_List.xlsx`). It generates a summary sheet with the stock counts for each index and separate sheets for each individual index.
- **Web Interface**: Includes a frontend application (HTML, CSS, JavaScript) designed to display and interact with the stock lists.

## Setup & Requirements

- Python 3.x
- [pandas](https://pandas.pydata.org/)
- [requests](https://requests.readthedocs.io/)
- [xlsxwriter](https://xlsxwriter.readthedocs.io/) (for Excel export)

It's recommended to run the project within a virtual environment.

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use .venv\Scripts\activate

# Install dependencies
pip install pandas requests xlsxwriter
```

## Usage

1. **Download Data**: Run the data extraction script to fetch the latest CSVs.
   ```bash
   python pull_nse_data.py
   ```
   This will create a `nse_sectors` folder with individual CSV files for each tracked index.

2. **Merge Data**: Run the consolidation script to create the master Excel file.
   ```bash
   python merge_csvs.py
   ```
   This generates `NSE_Sectoral_Master_List.xlsx` in the root directory.

3. **Web Interface**: Open `index.html` in your browser to view the stock feeds.

## License

This project is licensed under the MIT License.
