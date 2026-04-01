import requests
import time
import json
import os
import argparse
import csv
import tempfile
import logging
from datetime import datetime

# Configure logging
log_filename = os.getenv('NSE_LOG_FILE', f"fetch_nse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_nse_token(symbol):
    """
    Fetches the NSE exchange token dynamically using Zerodha's open instrument list.
    """
    base_symbol = symbol.upper().replace('-EQ', '').replace('-BE', '')
    csv_path = os.path.join(tempfile.gettempdir(), "kite_nse_instruments.csv")
    
    download_needed = True
    if os.path.exists(csv_path):
        if (time.time() - os.path.getmtime(csv_path)) < 12 * 3600:
            download_needed = False
            
    if download_needed:
        logger.info("Downloading latest symbol-token mappings...")
        try:
            r = requests.get("https://api.kite.trade/instruments/NSE", timeout=10)
            if r.status_code == 200:
                with open(csv_path, "wb") as f:
                    f.write(r.content)
        except Exception as e:
            logger.error(f"Failed to download symbol mapping: {e}")
            return None

    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("tradingsymbol") == base_symbol and row.get("instrument_type") == "EQ":
                    return row.get("exchange_token")
            f.seek(0)
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("tradingsymbol") == base_symbol:
                    return row.get("exchange_token")
    except Exception as e:
        logger.error(f"Error reading mapping file: {e}")
        
    return None

def fetch_nse_chart_data(symbol, token, from_date, to_date):
    """
    Fetches historical chart data from NSE for a given symbol and token.
    
    Parameters:
    - symbol (str): The stock symbol (e.g., 'TCS-EQ')
    - token (str): The NSE internal token for the symbol (e.g., '11536')
    - from_date (int): Unix timestamp for the start date
    - to_date (int): Unix timestamp for the end date (e.g., 1774951866)
    """
    
    # Base URL for charting API
    url = "https://charting.nseindia.com/v1/charts/symbolHistoricalData"
    
    # Query parameters - 'token' is required here as requested
    params = {
        "token": token,
        "fromDate": str(from_date),
        "toDate": str(to_date),
        "symbol": symbol,
        "symbolType": "Equity",
        "chartType": "D",
        "timeInterval": "1"
    }

    # Browser-like headers are strictly needed to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.nseindia.com/",
        "Origin": "https://www.nseindia.com",
    }

    logger.info(f"Fetching data for {symbol} (Token: {token})...")

    # Creating a session object. NSE India block mechanisms usually require cookies 
    # to be set by an initial visit to the main page.
    session = requests.Session()
    session.headers.update(headers)

    try:
        # Step 1: Hit the main NSE page to acquire necessary session cookies
        # Some WAFs will drop connections, so we use a timeout.
        session.get("https://www.nseindia.com", timeout=15)
    except Exception as e:
        logger.warning(f"Note: Error obtaining initial cookies (this might be benign): {e}")

    # Step 2: Make the actual charting API call
    try:
        response = session.get(url, params=params, timeout=15)
        
        # Check if the request was successful
        if response.status_code == 200:
            logger.info("Successfully retrieved data!")
            return response.json()
        elif response.status_code in [401, 403]:
            logger.error(f"Authentication/Authorization error {response.status_code}.")
            logger.error("NSE blocked the request. You might need refreshed cookies or an advanced mimicking mechanism.")
            return None
        else:
            logger.error(f"Failed with status code: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while calling the API: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch NSE chart data")
    parser.add_argument("--symbol", help="Stock symbol (e.g., TCS-EQ)")
    parser.add_argument("--from-date", type=int, default=0, help="Unix timestamp for start date")
    parser.add_argument("--to-date", type=int, default=int(time.time()), help="Unix timestamp for end date")
    
    args = parser.parse_args()
    
    target_symbol = args.symbol
    if not target_symbol:
        target_symbol = input("Enter the stock symbol (e.g., TCS-EQ): ").strip()
        
    logger.info(f"Resolving internal token for {target_symbol}...")
    target_token = get_nse_token(target_symbol)
    if not target_token:
        logger.error(f"Could not automatically resolve token for {target_symbol}. Exiting.")
        exit(1)

    test_from_date = args.from_date
    test_to_date = args.to_date
    
    # Check for existing data to optimize fetch
    output_dir = "json_data"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{target_symbol}_data.json")
    
    existing_data = None
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            
            if "data" in existing_data and existing_data["data"]:
                # Get the maximum time in milliseconds and convert to seconds
                max_time_ms = max(item["time"] for item in existing_data["data"])
                max_time_sec = int(max_time_ms / 1000)
                
                # Use max_time_sec + 86400 (1 day) as the new from_date
                test_from_date = max_time_sec + 86400
                
                max_date_str = datetime.fromtimestamp(max_time_sec).strftime('%d-%b-%Y')
                new_start_str = datetime.fromtimestamp(test_from_date).strftime('%d-%b-%Y')
                
                logger.info(f"[{target_symbol}] Found existing data up to {max_date_str}.")
                logger.info(f"[{target_symbol}] Updating start date to {new_start_str} instead of starting from 0.")
        except Exception as e:
            logger.error(f"Error reading existing data file {filename}: {e}")

    # Fetch data only if from_date is before or equal to to_date
    if test_from_date <= test_to_date:
        data = fetch_nse_chart_data(
            symbol=target_symbol,
            token=target_token,
            from_date=test_from_date,
            to_date=test_to_date
        )

        if data and "data" in data and data["data"]:
            if existing_data and "data" in existing_data:
                # Merge existing data and new data
                existing_data["data"].extend(data["data"])
                
                # Remove duplicates based on 'time' and keep it sorted
                merged_dict = {item["time"]: item for item in existing_data["data"]}
                existing_data["data"] = [merged_dict[k] for k in sorted(merged_dict.keys())]
                data_to_save = existing_data
                logger.info(f"[{target_symbol}] Successfully merged {len(data['data'])} new records.")
            else:
                data_to_save = data
            
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data_to_save, f, indent=4)
                logger.info(f"[{target_symbol}] Data successfully saved to {filename}")
            except Exception as e:
                logger.error(f"Error saving data to file: {e}")
        elif data:
            logger.info(f"[{target_symbol}] No new records returned from API.")
        else:
            logger.error(f"[{target_symbol}] Failed to fetch data.")
    else:
        logger.info(f"[{target_symbol}] Data is already up to date. No fetch required.")
