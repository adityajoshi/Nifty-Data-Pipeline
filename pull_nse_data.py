import pandas as pd
import requests
import io
import os

# Define the sectors/indices you want to download
sectors = [
    'niftyauto','niftybank','NiftyCement_','niftyChemicals_','niftyfinance',
    'niftyfinancialservices25-50','niftyfinancialservicesexbank_','niftyfmcg',
    'niftyhealthcare','niftyit','niftymedia',
    'niftymetal','niftypharma','nifty_privatebank',
    'niftypsubank','niftyrealty','niftyconsumerdurables',
    'niftyoilgas','nifty500Healthcare_','niftymidsmallfinancailservice_',
    'niftymidsmallhealthcare_','niftymidsmallitAndtelecom_'
]

def download_sector_csv(index_name):
    # Standard URL pattern for Nifty Indices CSVs
    url = f"https://www.niftyindices.com/IndexConstituent/ind_{index_name}list.csv"
    
    # User-Agent is often required to avoid 403 Forbidden errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
            filename = f"{index_name}_constituents.csv"
            df.to_csv(filename, index=False)
            print(f"Successfully downloaded: {filename}")
        else:
            print(f"Failed to download {index_name}: Status Code {response.status_code}")
    except Exception as e:
        print(f"Error downloading {index_name}: {e}")

# Create a folder for downloads
if not os.path.exists('nse_sectors'):
    os.makedirs('nse_sectors')
os.chdir('nse_sectors')

for sector in sectors:
    download_sector_csv(sector)