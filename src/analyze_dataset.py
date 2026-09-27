import pandas as pd

# Load the dataset
df = pd.read_csv("data/call_dataset.csv")

# Display basic information
print("Dataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns)

print("\nLabel Counts:")
print(df["label"].value_counts())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nFirst 5 Rows:")
print(df.head())