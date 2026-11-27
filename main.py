try:
    import pandas as pd 
    import matplotlib.pyplot as plt
    import sqlite3
except ImportError as error:
    print("error loading module.")
    print(error)
    raise SystemExit

file_path = 'data.csv'

#im using functions for each different section of my code so that its earier to read and i can split the project into chunks 


#this is my function to load the csv, it also does some error handling.
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

#this is the cleaning function
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


#here im setting up the connection to the sql database
connection = sqlite3.connect("spending.db")

#just checking if the dataframe is empty or not before inputing the csv data into it.
if df is not None:
    df.to_sql(
        "transactions", #table name
        connection,#database connection
        if_exists="replace",#if data already exists in the table then it will be replaced with the updated csv data. (i had an issue where updating my csv file and the sql data was not being updated)
        index=False #im disabling the index column
    )

    print("CSV data transferred to spending.db.")

    results = connection.execute("SELECT * FROM transactions LIMIT 5").fetchall()

    for row in results:
        print(row)

    #this is my sql query to see which category has the highest spending 
    #im selecting the category and the sum amount and grouping it by the respective category and ordering it by high to low 
    category_query = """
        SELECT category, SUM(amount) AS total_spent 
        FROM transactions
        GROUP BY category
        ORDER BY total_spent DESC
    """

    #here im running the sql query and storing the results in cantegory_reults
    category_results = connection.execute(category_query).fetchall()

    #here im printing the results
    print("\nTotal spending by category:")
    #im using a for loop to iterate through each categorys results,
    for category, total_spent in category_results:
        print(f"{category}: €{total_spent:.2f}")

    #here i am checking which payment method i use most
    #im selecting the payment method and counting the number of transactions of each payment method and storing it in a new column and grouping it my payment bethod and ording it from high to low.
    payment_query = """
        SELECT payment_method, COUNT(*) AS number_of_transactions
        FROM transactions
        GROUP BY payment_method
        ORDER BY number_of_transactions DESC
    """

    #printing the results
    payment_results = connection.execute(payment_query).fetchall()

    #once again im using a for loop to iterate through the different payment methods 
    print("\nTransactions by payment method:")
    for payment_method, count in payment_results:
        print(f"{payment_method}: {count} transactions")


    #here im checking the average spending per category 
    #im using the avg funtion to get teh average per category and group it by category and once again ordering it from high to low.
    average_query = """
        SELECT category, AVG(amount) AS average_spending
        FROM transactions
        GROUP BY category
        ORDER BY average_spending DESC
    """

    #printing the results 
    average_results = connection.execute(average_query).fetchall()

    print("\nAverage spending by category:")
    for category, average_spending in average_results:
        print(f"{category}: €{average_spending:.2f}")

    #here i am checking for any purchases over €50, im returing the shop name and category and the amount and ordering it from high to low.
    large_purchase_query = """
        SELECT shop_name, category, amount
        FROM transactions
        WHERE amount > 50
        ORDER BY amount DESC
    """

    #printing the results of the larg purchases
    large_purchase_results = connection.execute(
        large_purchase_query
    ).fetchall()

    print("\nPurchases over €50:")
    for shop_name, category, amount in large_purchase_results:
        print(f"{shop_name} - {category}: €{amount:.2f}")

#closing teh connection to the database
connection.close()