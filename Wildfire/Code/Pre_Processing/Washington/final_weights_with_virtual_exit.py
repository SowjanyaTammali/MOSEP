import pandas as pd
import numpy as np
import random

# === Step 1: Load edge and node files ===
sf_df = pd.read_csv("/Users/stb34/Documents/wildfire/Experiments/Washington/Washington_link.csv")
node_df = pd.read_csv("/Users/stb34/Documents/wildfire/Experiments/Washington/final_node_zone_classification_median_seeded.csv")

# === Step 2: Shift all node IDs by +1 to reserve virtual node 0 ===
sf_df["From_Node_ID"] += 1
sf_df["To_Node_ID"] += 1
node_df["node_id"] += 1

# === Step 3: Create fire_prob lookup ===
fire_prob_map = dict(zip(node_df["node_id"], node_df["fire_prob"]))

# === Step 4: Compute weights ===
sf_df["w1"] = sf_df["Length"]
sf_df["p1"] = sf_df["From_Node_ID"].map(fire_prob_map)
sf_df["p2"] = sf_df["To_Node_ID"].map(fire_prob_map)
sf_df["w2"] = ((sf_df["p1"] + sf_df["p2"]) / 2) * sf_df["Length"]

# BPR delay (w3/w4)
sf_df["Free_Speed_mps"] = sf_df["Free_Speed"] * 1000 / 3600
sf_df["t_ff"] = sf_df["Length"] / sf_df["Free_Speed_mps"]

np.random.seed(42)
sf_df["Flow"] = np.random.uniform(0.1, 0.9, size=len(sf_df)) * sf_df["Capacity"]
alpha, beta = 0.5, 1.8
sf_df["BPR_Delay_sec"] = sf_df["t_ff"] * (1 + alpha * (sf_df["Flow"] / sf_df["Capacity"]) ** beta)
sf_df["w3"] = sf_df["BPR_Delay_sec"] / 60

sf_df["Flow_rev"] = np.random.uniform(0.1, 0.9, size=len(sf_df)) * sf_df["Capacity"]
sf_df["BPR_Delay_rev_sec"] = sf_df["t_ff"] * (1 + alpha * (sf_df["Flow_rev"] / sf_df["Capacity"]) ** beta)
sf_df["w4"] = sf_df["BPR_Delay_rev_sec"] / 60

# === Step 5: Randomly select 5 real nodes as exits ===
random.seed(42)
all_nodes = node_df["node_id"].unique()
exit_nodes = random.sample(list(all_nodes), 5)

# Create virtual exit edges: from selected nodes to node 0 with zero weights
exit_edges = pd.DataFrame({
    "From_Node_ID": exit_nodes,
    "To_Node_ID": [0] * 5,
    "w1": [0.0] * 5,
    "w2": [0.0] * 5,
    "w3": [0.0] * 5,
    "w4": [0.0] * 5
})

# === Step 6: Merge real and virtual edges ===
final_df = pd.concat([
    sf_df[["From_Node_ID", "To_Node_ID", "w1", "w2", "w3", "w4"]],
    exit_edges
], ignore_index=True)

# === Step 7: Save to CSV ===
final_df.to_csv("/Users/stb34/Documents/wildfire/Experiments/Washington/final_edge_weights_with_virtual_exit.csv", index=False)
print("✅ Saved to final_edge_weights_with_virtual_exit.csv")
print("📌 Exit nodes connected to virtual node 0:", exit_nodes)
