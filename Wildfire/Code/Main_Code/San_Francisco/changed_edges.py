import pandas as pd
import numpy as np
from scipy.stats import beta
from collections import defaultdict

EDGE_FILE = "/Users/stb34/Documents/wildfire/Experiments/San_Francisco/final_edge_weights_directional.csv"
NODE_FILE = "/Users/stb34/Documents/wildfire/Experiments/San_Francisco/Original_fire_probabality_zone.csv"
PATH_FILE = "/Users/stb34/Documents/wildfire/Experiments/Results/San Francisco_path_objectives.txt"

THRESHOLD = 0.5

def update_fire_prob(p_checkpoint, current_time, checkpoint=0):
    delta_t = current_time - checkpoint
    return 1 - (1 - p_checkpoint) ** delta_t

def compute_velocity(d1, d2, delay, alpha=5, beta_param=2):
    distance = d2 - d1
    if distance <= 0 or delay <= 0:
        return 0.0
    vmax = distance / delay
    vmax_kmph = vmax * 3.6
    vmin_kmph = max(0, vmax_kmph - 5)
    vmin = vmin_kmph / 3.6
    x_prime = (d1 + d2) / 2
    z = x_prime / d2 if d2 else 0
    return round((vmax + (vmax - vmin) * (1 - beta.cdf(z, alpha, beta_param))) * 60, 3)

def parse_path_file(path_txt):
    with open(path_txt, "r") as f:
        lines = f.readlines()
    path_blocks, dist_blocks = {}, {}
    for i in range(0, len(lines), 2):
        if "Path:" in lines[i] and "cumDist:" in lines[i + 1]:
            try:
                key = int(lines[i].split()[0])
                path = list(map(int, lines[i].split("Path:")[1].strip().split(",")))
                dists_raw = lines[i + 1].split("cumDist:")[1].strip()
                cum = [tuple(map(float, p.replace("(", "").replace(")", "").split(","))) for p in dists_raw.split("), (")]
                path_blocks[key] = path
                dist_blocks[key] = cum
            except:
                continue
    return path_blocks, dist_blocks

class Evacuee:
    def __init__(self, eid, path, cum):
        self.eid = eid
        self.path = path
        self.cum = cum
        self.location_idx = 0
        self.total_distance = 0.0
        self.finished = False

    def move(self, time_elapsed):
        for i in range(1, len(self.cum)):
            d1, d2 = self.cum[i - 1][0], self.cum[i][0]
            delay = self.cum[i][2]
            speed = compute_velocity(d1, d2, delay)
            if speed == 0:
                break
            travel_time = (d2 - self.total_distance) / speed
            if travel_time <= time_elapsed:
                self.total_distance = d2
                self.location_idx = i
            else:
                break
        if self.location_idx >= len(self.path) - 1:
            self.finished = True

    def current_edge(self):
        if self.finished or self.location_idx >= len(self.path) - 1:
            return None
        return (self.path[self.location_idx], self.path[self.location_idx + 1])

def simulate():
    edge_df = pd.read_csv(EDGE_FILE)
    node_df = pd.read_csv(NODE_FILE)
    path_map, cum_map = parse_path_file(PATH_FILE)
    node_fire_dict = dict(zip(node_df["node_id"], node_df["fire_prob"]))

    evacuees = []
    car_counter = 0
    time_points = [0, 5, 10]

    for t in time_points:
        for key in list(path_map.keys())[:4]:
            path, cum = path_map[key], cum_map[key]
            for _ in range(5):
                evacuees.append(Evacuee(eid=f"car_{car_counter+1}", path=path, cum=cum))
                car_counter += 1

        active_evacuees = [e for e in evacuees if not e.finished]
        for evac in active_evacuees:
            evac.move(time_elapsed=5)

        edge_traffic_count = defaultdict(int)
        for evac in active_evacuees:
            edge = evac.current_edge()
            if edge:
                edge_traffic_count[edge] += 1

        seen = set()
        updated_edges = []
        for _, row in edge_df.iterrows():
            u, v = int(row["From_Node_ID"]), int(row["To_Node_ID"])
            if (u, v) in seen: continue
            seen.add((u, v))

            w1 = row["w1"]
            orig_w2 = row["w2"]
            orig_w3 = row["w3"]

            p1 = node_fire_dict.get(u, 0.0)
            p2 = node_fire_dict.get(v, 0.0)
            p_edge = (p1 + p2) / 2
            updated_p = update_fire_prob(p_edge, current_time=t)
            updated_w2 = round(updated_p * w1, 3)

            traffic_factor = 1 + edge_traffic_count.get((u, v), 0) * 0.05
            updated_w3 = round(orig_w3 * traffic_factor, 3)

            if updated_p > THRESHOLD or edge_traffic_count.get((u, v), 0) > 0:
                updated_edges.append({
                    "From_Node_ID": u,
                    "To_Node_ID": v,
                    "w1": round(w1, 2),
                    "w2": updated_w2,
                    "w3": updated_w3
                })

        pd.DataFrame(updated_edges).to_csv(f"changed_edges_t{t}.csv", index=False)
        print(f"✅ saved changed_edges_t{t}.csv with {len(updated_edges)} entries")

if __name__ == "__main__":
    simulate()
