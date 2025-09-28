# Budget Transaction Importer For Myself

A Python script to automate the process of uploading financial transactions from Chase CSV files to a Google Sheets monthly budget template.

note that the script is designed to work for Chase CSVs. I reccommend uploading the last months saving,checking and Credit card transactions. Please note that spending is categorized roughly and may not be entirely accurate. The algorithm is personalized for me, but can serve as an adjustable template for you. Always double check the description on the actual Chase transaction statement if the Budget seems fishy. For example, negative checking/saving transactions greater than $300 and are Zelles, are categorized as "Personal" in order to avoid duplicate transaction on paying credit card fees, which could lead to rare edge cases of transaction being ignored.

## Features

-   **Automatic File Processing**: Scans the folder and processes all `.csv` files in a single run.
-   **Smart CSV Detection**: Intelligently detects the format for Checking/Savings accounts vs. Credit Card accounts.
-   **Custom Categorization**: Applies detailed, custom rules to filter and categorize transactions based on their source and details (e.g., amount, description).
-   **Efficient Uploading**: Uses a single batch request to Google Sheets to upload all data at once, avoiding API rate limits and ensuring fast performance.
-   **Error Handling**: Automatically cleans common CSV formatting errors, such as extra trailing commas.

## Requirements

-   Python 3.6+
-   A Google Cloud Platform project
-   Required Python libraries listed in `requirements.txt`

## Setup Instructions

Follow these steps to configure the script for the first time.

### 1. Google Cloud Project Setup

1.  **Create a Project**: Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2.  **Enable APIs**: In your project's dashboard, go to "APIs & Services" > "Library" and enable the following two APIs:
    -   **Google Drive API**
    -   **Google Sheets API**
3.  **Create Service Account**:
    -   Go to "APIs & Services" > "Credentials".
    -   Click **+ CREATE CREDENTIALS** and select **Service account**.
    -   Give it a name (e.g., "Budget Sheet Importer") and click **CREATE AND CONTINUE**.
    -   Grant it the role of **Project > Editor** and click **DONE**.
4.  **Download JSON Key**:
    -   Click on your newly created service account.
    -   Go to the **KEYS** tab, click **ADD KEY**, and select **Create new key**.
    -   Choose **JSON** and click **CREATE**. A JSON file will be downloaded.
    -   Rename this file to `credentials.json` and place it in the same folder as the script.

### 2. Share Your Google Sheet

1.  **Get Service Account Email**: Open your `credentials.json` file and copy the email address from the `"client_email"` field.
2.  **Share the Sheet**: Open your budget Google Sheet, click the **Share** button, paste the email address, and give it **Editor** permissions.

### 3. Install Python Libraries

1.  Open your terminal, navigate to the project folder, and run the following command:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Ensure your folder contains the `budgetImporter.py`, `credentials.json`, and `requirements.txt` files.
2.  Download your transaction CSV files from Chase and place them in the same folder.
3.  Run the script from your terminal:
    ```bash
    python budgetImporter.py
    ```
The script will automatically find, process, and upload the transactions from all CSV files in the folder.

## Project File Structure

Your project folder should look like this:
/*your folder/
├── budgetImporter.py
├── credentials.json
├── requirements.txt
├── Chase_Checking.csv
└── Chase_CreditCard.csv