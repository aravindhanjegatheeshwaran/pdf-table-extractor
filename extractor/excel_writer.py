import pandas as pd
import os

def save_to_excel(dataframes_dict, output_path):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet, df in dataframes_dict.items():
                safe_sheet_name = str(sheet)[:31]
                df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

        print(f"Excel written successfully to {output_path}")
    except Exception as e:
        print(f"Failed to write Excel: {e}")
