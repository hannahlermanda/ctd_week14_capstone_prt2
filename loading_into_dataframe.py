import os
import sqlite3
import pandas as pd

#Files to note
clean_csv_files = 'csv_clean'
db_create = 'mlb_hit_pitch_stats.db'

#Connect to SQLite database
conn = sqlite3.connect(db_create)
cursor = conn.cursor()

#Go through each clean folder (hitting and pitching)
for folder in ['hitting', 'pitching']:
    #Go to the clean folders (csv_clean) with hitting and pitching
    folder_path = os.path.join(clean_csv_files, folder)

    #Iterate through each CSV file in the csv_clean folders
    for filename in os.listdir(folder_path):
        #Make sure it's a CSV
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            #Double check and clean name before officially putting it into the db table names
            table_name = os.path.splitext(filename)[0].lower().replace(" ", "_").replace("-", "_")

            #Display progress to user
            print(f"Importing {file_path} as table '{table_name}'...")

            try:
                #Load CSV into a DataFrame
                df = pd.read_csv(file_path)

                #Double-check column names for inappropriate characters not compatible with SQLite
                df.columns = [col.strip().lower().replace(" ", "_").replace("-", "_") for col in df.columns]

                # Add a new column 'source' indicating whether it's hitting or pitching data
                df['source'] = folder

                #Import DataFrame into SQLite as a table
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                #Let user know of successful import with information about the rows
                print(f"Successfully imported '{table_name}' with {len(df)} rows.\n")

            #Let user know if the import fails
            except Exception as e:
                print(f"Failed to import {filename}: {e}\n")

#Close the connection
conn.close()

#Print success message to user
print(f"All data imported into {db_create}.")
