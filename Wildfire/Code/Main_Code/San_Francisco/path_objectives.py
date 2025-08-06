import pandas as pd
import numpy as np
from scipy.stats import beta

class Evacuee:
    def __init__(self, evac_id, path, distances, delays):
        self.evac_id = evac_id
        self.path = path[::-1]  # reverse path
        self.distances = distances[::-1]  # reverse distances
        self.delays = delays[::-1]  # reverse BPR delays
        self.speeds = self.compute_speeds()

    def compute_speeds(self, alpha=2, beta_param=5):
        speeds = []
        for i in range(len(self.path) - 1):
            u = self.path[i]
            v = self.path[i + 1]
            d_u = self.distances[i]
            d_v = self.distances[i + 1]
            delay = self.delays[i]

            if delay == 0:
                nu_max = 0
            else:
                nu_max = d_u / delay

            nu_min = max(nu_max - 5, 0)
            x = (d_u + d_v) / 2
            d = d_u
            x_norm = min(x / d, 1) if d > 0 else 0

            speed = nu_min + (nu_max - nu_min) * (1 - beta.cdf(x_norm, alpha, beta_param))
            speeds.append(speed)
        return speeds

# === Load paths from the uploaded file ===
path_file = "/Users/stb34/Documents/wildfire/Experiments/Results/San Francisco_path_objectives.txt"
paths_df = pd.read_csv(path_file, sep="\t")

# Convert paths into lists
paths_df["path"] = paths_df["path"].apply(eval)
paths_df["distance"] = paths_df["distance"].apply(eval)
paths_df["BPR_delay"] = paths_df["BPR_delay"].apply(eval)

# Create 5 Evacuee objects
evacuees = []
for i in range(5):
    evac = Evacuee(
        evac_id=i,
        path=paths_df["path"].iloc[i],
        distances=paths_df["distance"].iloc[i],
        delays=paths_df["BPR_delay"].iloc[i]
    )
    evacuees.append(evac)

# Example Output
for evac in evacuees:
    print(f"Evacuee {evac.evac_id}")
    print("  Path:", evac.path)
    print("  Distances:", evac.distances)
    print("  Delays:", evac.delays)
    print("  Speeds:", [round(s, 2) for s in evac.speeds])
    print()
