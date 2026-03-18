import pandas as pd
import os

# Configuration
input_folder = 'nse_sectors'
output_file = 'NSE_Sectoral_Master_List.xlsx'

if not os.path.exists(input_folder):
    print(f"Error: {input_folder} directory not found.")
else:
    summary_data = []
    
    # Initialize Excel Writer
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # 1. Process all CSVs and store counts
        for file in sorted(os.listdir(input_folder)):
            if file.endswith('.csv'):
                file_path = os.path.join(input_folder, file)
                sheet_name = file.replace('_constituents.csv', '')
                
                df = pd.read_csv(file_path)
                
                # Add to Summary List
                summary_data.append({
                    'Sector Index': sheet_name.upper(),
                    'Total Stocks': len(df)
                })
                
                # Write individual sector sheet
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

        # 2. Create and Write Master Summary Sheet
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Move 'Summary' to the first position
        workbook = writer.book
        summary_sheet = writer.sheets['Summary']
        workbook.worksheets_objs.insert(0, workbook.worksheets_objs.pop())

    print(f"File created: {output_file}")
    print(summary_df.to_string(index=False))