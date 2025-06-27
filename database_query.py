import sqlite3
import pandas as pd

#Database to connect to
mlb_db = 'mlb_hit_pitch_stats.db'

#Actually connect to the mlb_hit_pitch_stats.db
conn = sqlite3.connect(mlb_db)

#Function to list all the tables from the MLB hit/pitch database
def list_tables():
    """List all tables in the database."""
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql(query, conn)
    print("\nAvailable Tables:")
    print(tables.to_string(index=False))

#Function to list the column names for a specific table
def show_columns(table_name):
    """List column names for a given table."""
    try:
        #Grab the column names and none of the information from the rows from the table
        df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 0", conn)
        print(f"\nColumns in '{table_name}':")
        #Display to the user the names of the columns in the given table
        print(list(df.columns))
    #Display error to user if the columns names can't be retrieved
    except Exception as e:
        print(f"Error showing columns: {e}")

#Function to let the user run their own queries
def run_query():
    """Run a custom SQL query from user input."""
    try:
        user_query = input("\nEnter your SQL query (in a single line; Press Enter to continue):\n> ")
        # Run the user's query through the SQLite connection
        df = pd.read_sql(user_query, conn)
        print("\nQuery Result:")
        if df.empty:
            print("Query executed successfully but returned no rows.")
        else:
            print(df.to_string(index=False))
    except Exception as e:
        print(f"Query failed: {e}")

#Main query running program
def main():
    print("Query Tool")
    
    #While running
    while True:
        #Show the options
        print("\nOptions:")
        print("1 - List tables")
        print("2 - Show columns in a table")
        print("3 - Run a custom SQL query")
        print("4 - Exit")
        
        choice = input("Select an option (1-4): ")

        #If the user picks 1, list the tables in the mlb db
        if choice == "1":
            list_tables()
        #If the user picks 2, show the column names of the chosen table
        elif choice == "2":
            table_name = input("Enter table name: ").strip()
            show_columns(table_name)
        #If the user picks 3, let their user write their query
        elif choice == "3":
            run_query()
        #If the user picks 4, stop the program
        elif choice == "4":
            break
        #If none of the options above are picked, it's invalid -> let the user know
        else:
            print("Invalid option. Try again.")

    #Close the connection
    conn.close()
    #Tell the user the main query program has exited
    print("Exit complete")

#Run if this file is called
if __name__ == "__main__":
    main()
