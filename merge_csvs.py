import pandas as pd
import os

def merge_csv_files(input_folder, output_file):
    if not os.path.exists(input_folder):
        print(f"Error: {input_folder} directory not found.")
        return

    summary_data = []
    
    # Initialize Excel Writer
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        workbook = writer.book
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })

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
                sheet_name_trunc = sheet_name[:31]
                df.to_excel(writer, sheet_name=sheet_name_trunc, index=False)
                worksheet = writer.sheets[sheet_name_trunc]

                # Format headers
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Adjust column width based on max content length
                for idx, col in enumerate(df.columns):
                    series = df[col]
                    max_len = max((
                        series.astype(str).map(len).max(),
                        len(str(series.name))
                    )) + 1
                    worksheet.set_column(idx, idx, max_len)

        # 2. Create and Write Master Summary Sheet
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        summary_sheet = writer.sheets['Summary']
        
        # Format headers for Summary sheet
        for col_num, value in enumerate(summary_df.columns.values):
            summary_sheet.write(0, col_num, value, header_format)

        for idx, col in enumerate(summary_df.columns):
            series = summary_df[col]
            max_len = max((
                series.astype(str).map(len).max(),
                len(str(series.name))
            )) + 1
            summary_sheet.set_column(idx, idx, max_len)

        # Move 'Summary' to the first position
        workbook.worksheets_objs.insert(0, workbook.worksheets_objs.pop())

    print(f"File created: {output_file}")
    print(summary_df.to_string(index=False))

def main():
    # Configuration
    input_folder = 'nse_sectors'
    output_file = 'NSE_Sectoral_Master_List.xlsx'
    merge_csv_files(input_folder, output_file)

if __name__ == '__main__':
    main()