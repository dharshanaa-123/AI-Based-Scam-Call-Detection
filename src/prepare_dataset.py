import pandas as pd

def read_conversations(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split conversations using blank lines
    conversations = content.split("\n\n")

    # Remove empty conversations
    conversations = [conversation.strip() for conversation in conversations if conversation.strip()]

    return conversations


# Read individual conversations
scam_conversations = read_conversations("data/English_Scam.txt")
nonscam_conversations = read_conversations("data/English_NonScam.txt")

# Create separate labels
scam_data = pd.DataFrame({
    "text": scam_conversations,
    "label": "scam"
})

nonscam_data = pd.DataFrame({
    "text": nonscam_conversations,
    "label": "non-scam"
})

# Combine both datasets
df = pd.concat([scam_data, nonscam_data], ignore_index=True)

# Save dataset
df.to_csv("data/call_dataset.csv", index=False)

print("Dataset created successfully!")
print("Total conversations:", len(df))
print("\nLabel distribution:")
print(df["label"].value_counts())