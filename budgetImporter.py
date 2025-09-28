# import pandas as pd
# import gspread
# from google.oauth2.service_account import Credentials
# from gspread_dataframe import set_with_dataframe
# import csv
# import io
# import os

# def upload_chase_transactions_to_gsheet(spreadsheet_name, csv_file_path):
#     """
#     Reads Chase transactions from a CSV, formats them, and appends them
#     to the 'Transactions' sheet of a specified Google Sheet budget template.

#     Args:
#         spreadsheet_name (str): The exact name of your Google Sheet file.
#         csv_file_path (str): The file path to your downloaded Chase CSV.
#     """
#     print("🚀 Starting the transaction upload process...")

#     # --- 1. SETUP & AUTHENTICATION ---
#     # Define the scope of access for the APIs.
#     scopes = [
#         "https://www.googleapis.com/auth/spreadsheets",
#         "https://www.googleapis.com/auth/drive"
#     ]
#     # Path to your service account credentials JSON file.
#     creds_file = 'credentials.json'
#     creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
#     client = gspread.authorize(creds)

#     # Open the Google Sheet by its name.
#     try:
#         spreadsheet = client.open(spreadsheet_name)
#         sheet = spreadsheet.worksheet("Transactions")
#         print(f"✅ Successfully opened spreadsheet: '{spreadsheet_name}'")
#     except gspread.exceptions.SpreadsheetNotFound:
#         print(f"❌ Error: Spreadsheet '{spreadsheet_name}' not found. Please check the name.")
#         return
#     except gspread.exceptions.WorksheetNotFound:
#         print("❌ Error: 'Transactions' worksheet not found in the spreadsheet.")
#         return

#     # --- 2. READ AND PROCESS CHASE CSV ---
#     try:
#         print("Pre-processing CSV to remove extra trailing commas...")

#         # Read all lines from the file into a list
#         with open(csv_file_path, 'r', encoding='utf-8') as f:
#             lines = f.readlines()

#         # The first line is the header
#         header = lines[0]
#         data_rows = lines[1:]

#         # Create a new list to hold the cleaned rows
#         cleaned_rows = []
#         for line in data_rows:
#             # Strip whitespace from the end, then check if the last character is a comma
#             stripped_line = line.strip()
#             if stripped_line.endswith(','):
#                 # If it is, remove that last character
#                 cleaned_line = stripped_line[:-1]
#                 cleaned_rows.append(cleaned_line)
#             else:
#                 cleaned_rows.append(stripped_line)

#         # Combine the header and the cleaned data rows back into a single string
#         # Each line is separated by a newline character
#         cleaned_csv_string = header.strip() + '\n' + '\n'.join(cleaned_rows)

#         # Use io.StringIO to treat the cleaned string as a file for pandas
#         df = pd.read_csv(io.StringIO(cleaned_csv_string))

#         print(f"✅ Successfully cleaned and loaded '{csv_file_path}'.")

#     except FileNotFoundError:
#         print(f"❌ Error: The file '{csv_file_path}' was not found.")
#         return
#     except Exception as e:
#         print(f"❌ An error occurred while processing the CSV: {e}")
#         return


#     # Select and rename columns to match the Google Sheets template.
#     # From: ['Posting Date', 'Description', 'Amount']
#     # To:   ['Date', 'Description', 'Amount']
#     df_formatted = df[['Posting Date', 'Description', 'Amount']].copy()
#     df_formatted.rename(columns={'Posting Date': 'Date', 'Description': 'Description', 'Amount': 'Amount'}, inplace=True)

#     # --- 3. FORMAT DATA FOR GOOGLE SHEETS ---
#     # Convert 'Date' column to datetime objects and then to the desired string format.
#     df_formatted['Date'] = pd.to_datetime(df_formatted['Date']).dt.strftime('%m/%d/%Y')
    
#     # The budget template also needs a 'Category' column. We'll add it but leave it empty.
#     df_formatted['Category'] = ''
    
#     # Reorder columns to match the Google Sheets template exactly: Date, Amount, Description, Category
#     df_formatted = df_formatted[['Date', 'Amount', 'Description', 'Category']]

#     print(f"✅ Formatted {len(df_formatted)} transactions for upload.")


#     # --- 4. APPEND DATA TO GOOGLE SHEETS (EFFICIENT BATCH METHOD) ---
#     print("Preparing batch update to control columns efficiently...")

#     # Get the first empty row number ONCE to avoid API limits
#     try:
#         next_row = len(sheet.get_all_values()) + 1
#     except gspread.exceptions.APIError as e:
#         if 'RESOURCE_EXHAUSTED' in str(e):
#             print("❌ Quota error while getting row count. Please wait a minute and try again.")
#             return
#         else:
#             raise e

#     # This list will hold all the update requests
#     batch_update_data = []

#     # Loop through the dataframe to prepare the data for the batch request
#     for index, row in df_formatted.iterrows():
#         # Determine start column based on Amount (positive=income, negative=expense)
#         if row['Amount'] < 0:
#             # This is an EXPENSE
#             start_column = 'B' # Or your desired expense column
#             # Format for expense row: [Description, Category, Amount]
#             # We use abs() here just to make the number positive in the sheet
#             values_to_append = [row['Date'], abs(row['Amount']), row['Description']]
#         else:
#             # This is an INCOME
#             start_column = 'G' # Or your desired income column
#             # Format for income row: [Description, Amount]
#             values_to_append = [row['Date'], abs(row['Amount']), row['Description']]

#         # Define the range for this specific row (e.g., "B34" or "G35")
#         update_range = f"{start_column}{next_row}"
        
#         # Add the update request to our batch list
#         batch_update_data.append({
#             'range': update_range,
#             'values': [values_to_append],
#         })
        
#         # Increment the row counter for the next item
#         next_row += 1

#     # Only send the request if there's data to update
#     if batch_update_data:
#         print(f"Sending {len(batch_update_data)} transactions in a single batch...")
#         # Send all updates in one API call
#         sheet.batch_update(batch_update_data, value_input_option='USER_ENTERED')
#         print("🎉 Success! All transactions have been appended efficiently.")
#     else:
#         print("No new transactions to upload.")


# # --- SCRIPT EXECUTION ---
# if __name__ == "__main__":
#     # ------------------ USER INPUT ------------------ #
#     YOUR_SPREADSHEET_NAME = "Monthly Budget"
    
#     # --- Auto-find the CSV file ---
#     csv_file_to_use = None
#     # List all files in the current directory
#     for filename in os.listdir('.'):
#         # Check if the file ends with .csv (case-insensitive)
#         if filename.lower().endswith('.csv'):
#             csv_file_to_use = filename
#             print(f"✅ Found CSV file: '{csv_file_to_use}'")
#             break # Stop after finding the first one

#     # ---------------------------------------------- #

#     # Only run the main function if a CSV file was found
#     if csv_file_to_use:
#         upload_chase_transactions_to_gsheet(YOUR_SPREADSHEET_NAME, csv_file_to_use)
#     else:
#         print("❌ Error: No CSV file found in the script's folder.")
#         print("Please add your Chase transactions CSV to the same directory and run again.")


import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import io
import os

def map_credit_card_category(csv_category, sheet_categories):
    """Maps a credit card CSV category to a valid Google Sheet category."""
    csv_category_str = str(csv_category).lower()
    for sheet_cat in sheet_categories:
        if sheet_cat.lower() in csv_category_str:
            return sheet_cat
    return "Other"

def categorize_bank_transaction(row):
    """Applies the detailed categorization logic for checking/savings accounts."""
    amount = row['Amount']
    description = row['Description']

    # Rule for positive amounts (Income)
    if amount >= 0:
        if amount >= 500:
            return "Paycheck"
        else:
            return "Other"
    # Rule for negative amounts (Expenses)
    else:
        if amount <= -300:
            return "Home"
        elif amount > -300 and 'zelle' in description.lower():
            return "Personal"
        else:
            return None # This transaction will be ignored

def upload_transactions_to_gsheet(spreadsheet_name, csv_file_path):
    """
    Reads transactions from a Chase CSV, automatically detects the account type,
    formats and maps categories, and uploads data efficiently.
    """
    print("🚀 Starting the transaction upload process...")

    # --- 1. SETUP & AUTHENTICATION ---
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_file = 'credentials.json'
    creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
    client = gspread.authorize(creds)

    try:
        spreadsheet = client.open(spreadsheet_name)
        sheet = spreadsheet.worksheet("Transactions")
        print(f"✅ Successfully opened spreadsheet: '{spreadsheet_name}'")
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"❌ Error: Spreadsheet '{spreadsheet_name}' not found.")
        return
    except gspread.exceptions.WorksheetNotFound:
        print("❌ Error: 'Transactions' worksheet not found.")
        return

    # --- 2. READ, CLEAN, AND IDENTIFY CSV ---
    try:
        print("Pre-processing CSV to fix formatting...")
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        header_line = lines[0].strip()
        data_rows = lines[1:]
        cleaned_rows = [line.strip().rstrip(',') for line in data_rows]
        cleaned_csv_string = header_line + '\n' + '\n'.join(cleaned_rows)
        
        df = pd.read_csv(io.StringIO(cleaned_csv_string))
        print(f"✅ Successfully loaded and cleaned '{csv_file_path}'.")
    except Exception as e:
        print(f"❌ An error occurred while processing the CSV: {e}")
        return

    # --- 3. PROCESS DATA BASED ON CSV TYPE ---
    checking_savings_cols = ['Details', 'Posting Date', 'Description', 'Amount', 'Type']
    credit_card_cols = ['Transaction Date', 'Post Date', 'Description', 'Category', 'Amount']
    df_formatted = None

    if all(col in df.columns for col in checking_savings_cols):
        print("📂 Detected Checking/Savings account CSV.")
        
        # --- NEW CHECKING/SAVINGS LOGIC ---
        # 1. Ignore transfers
        df_filtered = df[df['Type'] != 'ACCT_XFER'].copy()
        
        # 2. Apply the detailed categorization rules
        df_filtered['Category'] = df_filtered.apply(categorize_bank_transaction, axis=1)
        
        # 3. Drop rows that were marked to be ignored (returned None)
        df_filtered.dropna(subset=['Category'], inplace=True)
        print(f"Found {len(df_filtered)} transactions to record after filtering.")

        df_formatted = df_filtered[['Posting Date', 'Description', 'Amount', 'Category']].copy()
        df_formatted.rename(columns={'Posting Date': 'Date'}, inplace=True)
        # --- END NEW LOGIC ---

    elif all(col in df.columns for col in credit_card_cols):
        print("💳 Detected Credit Card CSV.")
        df_formatted = df[['Post Date', 'Description', 'Amount', 'Category']].copy()
        df_formatted.rename(columns={'Post Date': 'Date'}, inplace=True)
        
        df_formatted['Amount'] = pd.to_numeric(df_formatted['Amount'], errors='coerce')
        df_formatted = df_formatted[df_formatted['Amount'] < 0].copy()
        print(f"Found {len(df_formatted)} expense transactions to record.")
        df_formatted['Amount'] = -df_formatted['Amount']

        google_sheet_categories = [
            "Food", "Gifts", "Health/medical", "Home", "Transportation", 
            "Personal", "Pets", "Utilities", "Travel", "Debt", "Other"
        ]
        df_formatted['Category'] = df_formatted['Category'].apply(
            lambda cat: map_credit_card_category(cat, google_sheet_categories)
        )
        print("✅ Categories mapped successfully.")

    else:
        print("❌ Error: Unrecognized CSV format.")
        return

    df_formatted['Date'] = pd.to_datetime(df_formatted['Date']).dt.strftime('%m/%d/%Y')
    df_formatted.fillna('', inplace=True)
    print(f"✅ Formatted {len(df_formatted)} transactions.")

    # --- 4. EFFICIENT BATCH UPDATE ---
    print("Preparing batch update...")
    try:
        next_row = len(sheet.get_all_values()) + 1
    except gspread.exceptions.APIError as e:
        print(f"❌ Quota error: {e}. Please wait a minute and try again.")
        return

    batch_update_data = []
    for index, row in df_formatted.iterrows():
        if 'Details' in df.columns and row['Amount'] >= 0:
            start_column = 'G' # Income
            values = [row['Date'], row['Amount'], row['Description'], row['Category']]
        else: # Covers bank expenses and all credit card expenses
            start_column = 'B' # Expense
            values = [row['Date'], abs(row['Amount']), row['Description'], row['Category']]
        
        update_range = f"{start_column}{next_row}"
        batch_update_data.append({'range': update_range, 'values': [values]})
        next_row += 1

    if batch_update_data:
        print(f"Sending {len(batch_update_data)} transactions in a single batch...")
        sheet.batch_update(batch_update_data, value_input_option='USER_ENTERED')
        print("🎉 Success! All transactions have been appended.")
    else:
        print("No new transactions to upload.")

# --- SCRIPT EXECUTION ---
if __name__ == "__main__":
    YOUR_SPREADSHEET_NAME = "Monthly Budget"
    
    # Find all CSV files in the current directory
    csv_files_to_process = [
        filename for filename in os.listdir('.') 
        if filename.lower().endswith('.csv')
    ]

    if csv_files_to_process:
        print(f"✅ Found {len(csv_files_to_process)} CSV file(s) to process.")
        # Loop through each found CSV file and process it
        for csv_file in csv_files_to_process:
            print(f"\n--- Processing '{csv_file}' ---")
            upload_transactions_to_gsheet(YOUR_SPREADSHEET_NAME, csv_file)
        print("\n🎉 All CSV files have been processed.")
    else:
        print("❌ Error: No CSV files found in the script's folder.")