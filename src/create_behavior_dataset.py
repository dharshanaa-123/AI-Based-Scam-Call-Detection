import pandas as pd
import random

data = []

# Generate 500 scam calls
for i in range(500):
    data.append({
        "unknown_number": random.choice([0, 1]),
        "international_number": random.choice([0, 1]),
        "repeated_calls": random.choice([0, 1]),
        "otp_request": random.choice([0, 1]),
        "money_request": random.choice([0, 1]),
        "urgent_language": random.choice([0, 1]),
        "call_duration": random.randint(30, 600),
        "label": "scam"
    })

# Generate 500 genuine calls
for i in range(500):
    data.append({
        "unknown_number": random.choice([0, 1]),
        "international_number": random.choice([0, 1]),
        "repeated_calls": random.choice([0, 1]),
        "otp_request": 0,
        "money_request": 0,
        "urgent_language": random.choice([0, 1]),
        "call_duration": random.randint(30, 600),
        "label": "genuine"
    })

df = pd.DataFrame(data)

# Shuffle the dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save dataset
df.to_csv("data/call_behavior_dataset.csv", index=False)

print("Behavior dataset created successfully!")
print("Total records:", len(df))
print("\nLabel distribution:")
print(df["label"].value_counts())