try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError as error:
    print("error loading module.")
    print(error)
    raise SystemExit

file_path = 'data.csv'

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        print("Data loaded successfully.")
        return df
    except FileNotFoundError:
        print("Error: The file was not found.")
        return None
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        return None
    except pd.errors.ParserError:
        print("Error: The file could not be parsed.")
        return None


def clean_data(df):
    if df is not None:
        #here im changing the amount column value to a float and removing € sign from it
        df["amount"] = (
            df["amount"]
            .astype("string")#temporarily change the colum to a string so i can strip the € sign
            .str.replace("€", "", regex=False) #replacing the euro sign with whitespace
            .str.strip()
            .astype(float)#change the column type back to float
        )

        #just checking if the amounts column is cleaned up
        print(df["amount"].head())

        df["date"] = pd.to_datetime(
            df["date"],
            #this is the date format that i have set 
            format="%d/%m/%Y",
            #if there is any invalid dates it will be set to Nat instead if raising an error. 
            errors="coerce"
        )

        #im changing the transaction_time to a pandas datetime.
        df["transaction_time"] = pd.to_datetime(
            #again im temporarily changing the column to a string so i can strip any whitespace
            df["transaction_time"].astype("string").str.strip(),
            #this is the format of the time i have set. 
            format="%H:%M",
            #if there are any invalid times it will be set to NaT  instead of raising an error.
            errors="coerce"
        ).dt.time

        #here im checking if there are any invalid dates
        if df["date"].isna().any():
            print("Some dates are invalid.")

        #checking for any invalid transaction times. 
        if df["transaction_time"].isna().any():
            print("Some transaction times are invalid.")

        #here i am checking if there are any invalid amounts
        if df["amount"].isna().any():
            print("Some amounts are invalid.")

        print(df.head())
        print(df.info())

    return df

df = load_data(file_path)
df = clean_data(df)