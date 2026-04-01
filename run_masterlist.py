import subprocess
import os
import sys
import time
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Process masterlist symbols.")
    parser.add_argument("script", nargs="?", default="fetch_nse_chart.py", help="Target script to run")
    parser.add_argument("-l", "--letter", type=str, help="Only consider symbols starting with this letter")
    args = parser.parse_args()

    masterlist_path = "masterlist.txt"
    target_script = args.script
    
    # Ensure all subprocesses share the same log file for this execution
    if 'NSE_LOG_FILE' not in os.environ:
        os.environ['NSE_LOG_FILE'] = f"fetch_nse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    if not os.path.exists(masterlist_path):
        print(f"Error: '{masterlist_path}' not found in the current directory.")
        sys.exit(1)

    print(f"Reading entries from {masterlist_path}...")
    with open(masterlist_path, "r", encoding="utf-8") as f:
        # Read lines, strip whitespace, and ignore empty lines
        entries = [line.strip() for line in f.readlines() if line.strip()]

    if not entries:
        print("No entries found in the file.")
        sys.exit(0)

    # Check if the first line is a header and skip it
    if "SYMBOL" in entries[0].upper():
        entries = entries[1:]
        print("Skipped header row.")
        
    if args.letter:
        entries = [e for e in entries if e.lower().startswith(args.letter.lower())]
        print(f"Filtered entries starting with '{args.letter}'.")

    if not entries:
        print("No entries to process.")
        sys.exit(0)

    print(f"Total entries to process: {len(entries)}\n")

    for i, symbol in enumerate(entries, 1):
        print(f"[{i}/{len(entries)}] Processing: {symbol}")
        
        try:
            # Call the target script with the symbol as an argument.
            # Adjust the argument flag ('--symbol') if your target script uses a different format.
            result = subprocess.run(
                [sys.executable, target_script, "--symbol", symbol],
                check=True
            )
            print(f"Successfully processed {symbol}.\n")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while processing {symbol}: {e}\n")
        except FileNotFoundError:
            print(f"Error: The script '{target_script}' was not found.")
            print("Make sure it exists in the same directory, or provide the correct script name as an argument.")
            sys.exit(1)
            
        # Optional: Add a small delay between requests to avoid hitting rate limits
        time.sleep(1)

if __name__ == "__main__":
    main()
