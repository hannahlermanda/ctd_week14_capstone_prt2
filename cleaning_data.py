import os
import pandas as pd
import numpy as np

#Folders with the raw CSVs
raw_csv = {
    'hitting': 'csv/hitting',
    'pitching': 'csv/pitching'
}
clean_csv = 'csv_clean'

#Make a folder for the clean csvs if they don't already exists
for category in raw_csv:
    os.makedirs(os.path.join(clean_csv, category), exist_ok=True)

#Cleaning dataframe function
def clean_dataframe(df):
    #Get the original number of rows and columns BEFORE cleaning
    dirty_csv_stats = df.shape

    #Remove columns that are empty (have a value of Na across the column)
    df = df.dropna(axis=1, how='all')

    #Remove empty rows (have a value of Na across the row)
    df = df.dropna(axis=0, how='all')

    #Drop exact duplicates
    df = df.drop_duplicates()

    #Strip unnecessary whitespace from the column headers in the dataframe
    df.columns = [col.strip() for col in df.columns]

    #Split columns with values like "# (#.#)"
    new_columns = {}
    for col in df.columns:
        if df[col].dtype == object:
            split_values = df[col].dropna().astype(str).str.extract(r'^([\d\.\-]+) \(([\d\.\-]+)\)$', expand=True)
            if not split_values.isnull().all().all():
                #If pattern matched for at least some rows, create new columns
                base_name = col.split('(')[0].strip()
                alt_name = col[col.find("(")+1:col.find(")")] if "(" in col and ")" in col else "Raw"
                alt_name = alt_name.replace(" ", "_")
                new_columns[base_name] = pd.to_numeric(split_values[0], errors='coerce')
                new_columns[alt_name] = pd.to_numeric(split_values[1], errors='coerce')
            else:
                #Keep the original column as-is if no match
                new_columns[col] = df[col]
        else:
            new_columns[col] = df[col]
    df = pd.DataFrame(new_columns)

    #Convert string numeric columns to int or float properly
    for col in df.columns:
        if df[col].dtype == object:
            #Remove commas and strip whitespace
            df[col] = df[col].str.replace(',', '').str.strip()
            #Attempt numeric conversion if the column looks numeric
            sample = df[col].dropna().head(20).astype(str)
            if all(any(char.isdigit() for char in val) for val in sample):
                df[col] = pd.to_numeric(df[col], errors='coerce')
                #If all non-NaN values are whole numbers, convert to integer type
                if (df[col].dropna() % 1 == 0).all():
                    df[col] = df[col].astype('Int64')

    #Fill in the appropriate spaces in the rank column
    if 'Rank' in df.columns:
        try:
            #Convert all rows in 'Rank' to numbers or coercing errors to NaN
            df['Rank'] = pd.to_numeric(df['Rank'], errors='coerce')
            #Start off with a fixed ranked empty list and don't determine a last rank at the beginning
            fixed_ranks = []
            last_rank = None

            #For the values in the rank column of the dataframe (Iterate)
            for val in df['Rank']:
                #If the value we are currently iterating on is not NaN
                if not np.isnan(val):
                    #If not, convert the current value into the 'last' valid rank 
                    last_rank = int(val)
                    #Add the valid rank to the list of fixed ranks
                    fixed_ranks.append(last_rank)
                else:
                    #If the last_rank recorded is NaN BUT we have a recorded last_rank
                    if last_rank is not None:
                        #Add 1 to the current last_rank
                        last_rank += 1
                        #Append the new last rank onto the fixed ranks
                        fixed_ranks.append(last_rank)
                    else:
                        #If the first ranked value is missing, keep it as NaN
                        fixed_ranks.append(np.nan)
            #After iteration through the rank column, have the fixed_ranks be the new rank column
            df['Rank'] = fixed_ranks

        except Exception as e:
            print(f"Could not fix missing ranks due to error: {e}")

    print(f"Cleaned: {dirty_csv_stats} -> {df.shape}")
    #Return the dataframe with the updated ranks
    return df

#Process all CSV files in the raw csv
for category, raw_path in raw_csv.items():
    #For each file in raw csvs
    for filename in os.listdir(raw_path):
        #If the file ends with .csv
        if filename.endswith(".csv"):
            #Join the raw_path and filename?
            file_path = os.path.join(raw_path, filename)
            print(f"Processing {file_path}")
            try:
                #Read the original (raw) csv file into a dataframe
                df = pd.read_csv(file_path)

                #Show original
                print("Before cleaning:")
                print(df.head(2))

                #The new cleaned dataframes after the clean_dataframe function is run
                cleaned_df = clean_dataframe(df)

                #Verify cleaning
                print("After cleaning:")
                print(cleaned_df.head(2))

                #Save the clean csv to the clean folder 
                save_path = os.path.join(clean_csv, category, filename)
                cleaned_df.to_csv(save_path, index=False)
                print(f"Saved cleaned file: {save_path}\n")

            #State an error to the user if file processing fails
            except Exception as e:
                print(f"Error processing {filename}: {e}\n")
