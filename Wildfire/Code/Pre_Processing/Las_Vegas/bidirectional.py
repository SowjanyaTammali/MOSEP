import pandas as pd

# Load the original edge file
df = pd.read_csv("/Users/stb34/Documents/wildfire/Experiments/Las_Vegas/final_edge_weights_with_virtual_exit.csv")

# Convert node IDs to integers
df["From_Node_ID"] = df["From_Node_ID"].astype(int)
df["To_Node_ID"] = df["To_Node_ID"].astype(int)

# Create forward edge: use w3
forward_df = df[["From_Node_ID", "To_Node_ID", "w1", "w2", "w3"]].copy()
forward_df.rename(columns={"w3": "w3"}, inplace=True)

# Create backward edge: use w4, swap node IDs
reverse_df = df[["From_Node_ID", "To_Node_ID", "w1", "w2", "w4"]].copy()
reverse_df.rename(columns={
    "From_Node_ID": "To_Node_ID",
    "To_Node_ID": "From_Node_ID",
    "w4": "w3"
}, inplace=True)

# Combine forward and reverse
combined_df = pd.concat([forward_df, reverse_df], ignore_index=True)

# Sort to keep rows consecutive for same edge pairs
combined_df = combined_df.sort_values(by=["From_Node_ID", "To_Node_ID"]).reset_index(drop=True)

# Save to file
output_path = "/Users/stb34/Documents/wildfire/Experiments/Las_Vegas/final_edge_weights_directional.csv"
combined_df.to_csv(output_path, index=False)

print("✅ Cleaned directional edge file saved to:", output_path)
