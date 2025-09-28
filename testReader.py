# Make sure to change this to the actual name of your CSV file
csv_file_path = "Chase1796_Activity_20250927.CSV" 

print(f"--- Analyzing '{csv_file_path}' ---")

try:
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            print(f"Line {i+1}: {line.strip()}")
            # Stop after the first 10 lines to keep it short
            if i > 10:
                break
except Exception as e:
    print(f"\nAn error occurred while trying to read the file: {e}")

print("\n--- Analysis Complete ---")