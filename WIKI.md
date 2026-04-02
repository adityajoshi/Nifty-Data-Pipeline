# Nifty Data Pipeline - Developer Wiki

Welcome to the Nifty Data Pipeline Developer Wiki! This document provides an in-depth look at the internal workings of the repository, the purpose of each script, and how data flows through the system.

## 1. Overview of the Pipeline

The primary goal of this repository is to track and fetch the constituent stocks for various NSE (National Stock Exchange of India) sectoral and thematic indices, compile them into an Excel workbook for easy reading, and provide tools for analyzing individual stock charts.

There are two main workflows:
1.  **The Index Pipeline (`main.py`)**: Fetches index constituent CSVs and merges them.
2.  **The Charting Pipeline (`run_masterlist.py`)**: Processes a list of stock symbols and fetches historical data for each.

## 2. Core Scripts

### `pull_nse_data.py` (Data Extraction)
- **Purpose**: Downloads the latest CSV list of constituents for predefined Nifty indices directly from the [Nifty Indices website](https://www.niftyindices.com/).
- **How it works**:
  - It iterates over a hardcoded list of `sectors` (e.g., `niftyauto`, `niftybank`).
  - It constructs a URL for each sector (e.g., `https://www.niftyindices.com/IndexConstituent/ind_niftyautolist.csv`).
  - It uses the `requests` library with a spoofed `User-Agent` header to bypass basic 403 Forbidden checks.
  - Downloaded CSVs are saved to the `nse_sectors/` directory with the naming convention `{sector}_constituents.csv`.

### `merge_csvs.py` (Data Consolidation)
- **Purpose**: Aggregates all individual CSV files in the `nse_sectors/` directory into a single Excel workbook named `NSE_Sectoral_Master_List.xlsx`.
- **How it works**:
  - It uses `pandas` and `xlsxwriter`.
  - It loops through all CSV files in the input folder.
  - For each CSV, it writes the data into a distinct Excel sheet named after the sector (truncated to 31 characters, the Excel sheet name limit).
  - It counts the number of stocks in each sector.
  - After processing all CSVs, it creates a `Summary` sheet containing a high-level overview (Sector Index Name and Total Stocks) and moves it to the front of the workbook.

### `main.py` (The Orchestrator)
- **Purpose**: A simple wrapper script to run the index extraction and consolidation in sequence.
- **How it works**:
  - Calls `pull_nse_data.download_sector_csv` for all configured sectors.
  - Calls `merge_csvs.merge_csv_files` to generate the final Excel file.

### `list_constituents.py` (CLI Utility)
- **Purpose**: A command-line utility to quickly print out the constituents of a specific index to the console.
- **How it works**:
  - Reads the local CSV file for the requested sector from `nse_sectors/`.
  - Extracts the `Symbol` column and prints it with an `NSE:` prefix (useful for copy-pasting into tools like TradingView).
  - Can accept a sector name as an argument (e.g., `python list_constituents.py niftybank`) or defaults to printing all of them.

### `fetch_nse_chart.py` (Historical Data Fetcher)
- **Purpose**: Retrieves historical intraday/daily chart data from the NSE charting API and saves it locally.
- **How it works**:
  - **Token Resolution (`get_nse_token`)**: The NSE API requires an internal numeric token, not just the stock symbol. This script downloads an instrument mapping CSV from Kite (Zerodha) to cross-reference the stock symbol (e.g., `TCS-EQ`) and find its internal NSE token. It caches this mapping file in the system temp directory for 12 hours to speed up subsequent runs.
  - **API Request (`fetch_nse_chart_data`)**: Hits `https://charting.nseindia.com/v1/charts/symbolHistoricalData`. It sets up a specific `requests.Session()` with headers to mimic a browser, making an initial call to the main NSE site to acquire session cookies before requesting the chart data.
  - **Caching and Updating**: Data is saved as JSON in a `json_data/` folder. If a file already exists for a symbol, the script smartly extracts the maximum timestamp, sets it as the new start date, fetches only new records, and merges them.

### `run_masterlist.py` (Batch Processor)
- **Purpose**: A generic runner script to execute a target script (usually `fetch_nse_chart.py`) over a list of symbols sequentially.
- **How it works**:
  - Reads a file named `masterlist.txt` located in the root directory.
  - Skips empty lines and the header row (if it contains 'SYMBOL').
  - Has a flag (`-l` or `--letter`) to only process symbols starting with a specific letter.
  - Uses `subprocess.run` to spawn a new process for each symbol, calling the target script with the `--symbol` argument.
  - Logs execution to a central file defined by the `NSE_LOG_FILE` environment variable.

## 3. Directory Structure and Data Flow

1. **`pull_nse_data.py`** -> Downloads -> **`nse_sectors/*.csv`**
2. **`merge_csvs.py`** -> Reads `nse_sectors/*.csv` -> Creates -> **`NSE_Sectoral_Master_List.xlsx`**
3. **`list_constituents.py`** -> Reads -> **`nse_sectors/*.csv`**
4. **`masterlist.txt`** -> Read by -> **`run_masterlist.py`** -> Spawns -> **`fetch_nse_chart.py`** -> Fetches -> **`json_data/*_data.json`**

## 4. Environment & Dependencies
- `pandas`: Essential for CSV/Excel data manipulation.
- `requests`: Used for downloading the CSVs and hitting the NSE charting APIs.
- `xlsxwriter`: The backend engine used by pandas to format and save the final `.xlsx` master list.

All dependencies can be installed via the included `requirements.txt`.
