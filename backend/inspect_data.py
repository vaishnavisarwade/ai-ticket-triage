import pandas as pd

df = pd.read_csv("../data/tickets.csv")

print("Number of tickets:", len(df))
print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst ticket description:")
print(df["Ticket Description"].iloc[0])

print("\nTicket Type value counts:")
print(df["Ticket Type"].value_counts())

print("\nTicket Priority value counts:")
print(df["Ticket Priority"].value_counts())