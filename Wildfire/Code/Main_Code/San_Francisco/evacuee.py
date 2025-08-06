import pandas as pd
import random
import re

# === Load node classification file ===
node_df = pd.read_csv("/Users/stb34/Documents/wildfire/Experiments/San_Francisco/Original_fire_probabality_zone.csv")

# === Parse path file ===
path_file = "/Users/stb34/Documents/wildfire/Experiments/Results/San Francisco_path_objectives.txt"

paths_dict = {}
with open(path_file, "r") as f:
    for line in f:
        if "Path:" in line:
            match = re.match(r"(\d+)\s+Path:\s+(.*)", line.strip())
            if match:
                node_id = int(match.group(1))
                path_nodes = list(map(int, match.group(2).split(',')))
                paths_dict[node_id] = path_nodes

# === Filter eligible evacuee nodes (zone 2 or 3) that have a path ===
eligible_nodes = node_df[node_df['zone'].isin([2, 3])]['node_id'].astype(int)
eligible_with_path = [nid for nid in eligible_nodes if nid in paths_dict]

# === Randomly pick 5 evacuees ===
random.seed(42)
selected_nodes = random.sample(eligible_with_path, min(5, len(eligible_with_path)))

# === Define Evacuee class ===
class Evacuee:
    def __init__(self, evacuee_id, initial_location, request_time):
        self.evacuee_id = evacuee_id
        self.initial_location = initial_location
        self.request_time = request_time
        self.path = []

    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path

    def __repr__(self):
        return (f"Evacuee(ID={self.evacuee_id}, Start={self.initial_location}, "
                f"Time={self.request_time}, Path={self.path})")

# === Create and assign evacuees ===
evacuees = []
for i, node in enumerate(selected_nodes):
    evac = Evacuee(evacuee_id=f"car_{i+1}", initial_location=node, request_time="t0")
    evac.set_path(paths_dict[node])
    evacuees.append(evac)

# === Print result ===
for evac in evacuees:
    print(evac)
