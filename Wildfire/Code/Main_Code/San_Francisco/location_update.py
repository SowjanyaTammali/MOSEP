import pandas as pd
import random
from scipy.stats import beta

# --- Fire Risk Update ---
def update_fire_prob(p_checkpoint, current_time, checkpoint=0):
    delta_t = current_time - checkpoint
    return 1 - (1 - p_checkpoint) ** delta_t

# --- Velocity calculation using Beta CDF ---
def compute_velocity(d1, d2, delay, alpha=5, beta_param=2):
    distance = d2 - d1
    if distance == 0 or delay == 0:
        return 0.0
    v_max = distance / delay  # m/s
    v_max_mmin = v_max * 60
    v_min_kmph = max(0, v_max * 3.6 - 5)
    v_min_mmin = v_min_kmph / 3.6 * 60
    x_prime = (d1 + d2) / 2
    z = x_prime / d2 if d2 else 0
    return round(v_max_mmin + (v_max_mmin - v_min_mmin) * (1 - beta.cdf(z, alpha, beta_param)), 3)

# --- Evacuee Class ---
class Evacuee:
    def __init__(self, eid, path, cum):
        self.eid = eid
        self.path = path
        self.cum = cum
        self.location_idx = 0
        self.ros = round(0.0674 * 60, 2)  # m/min
        self.fire_prob = 0.0
        self.total_distance = 0.0
        self.velocities = []
        self.updated_path = None

    def move(self, time_elapsed):
        distance_covered = 0.0
        for i in range(1, len(self.cum)):
            d1 = self.cum[i-1][0]
            d2 = self.cum[i][0]
            delay = self.cum[i][2]
            speed = compute_velocity(d1, d2, delay)
            time_to_travel = (d2 - d1) / speed if speed > 0 else float("inf")
            if distance_covered + (d2 - d1) <= time_elapsed * speed:
                distance_covered = d2
                self.location_idx = i
                self.velocities.append(speed)
            else:
                break
        self.total_distance = round(distance_covered, 2)

    def update_risk(self, current_time, threshold=0.5):
        self.fire_prob = update_fire_prob(0.1, current_time)
        if self.fire_prob > threshold:
            self.updated_path = self.path[::-1]  # just to simulate path update
            return True
        return False

    def status(self):
        node = self.path[self.location_idx] if self.location_idx < len(self.path) else self.path[-1]
        return {
            "Evacuee_ID": self.eid,
            "Current_Node": node,
            "Distance_Covered": self.total_distance,
            "Speed": self.velocities[-1] if self.velocities else 0.0,
            "ROS": self.ros,
            "Fire_Risk": round(self.fire_prob, 3),
            "Updated_Path": self.updated_path
        }

# --- Parse Path File ---
def parse_path_file(path_txt):
    with open(path_txt, "r") as f:
        lines = f.readlines()
    path_blocks, dist_blocks = {}, {}
    for line in lines:
        if "Path:" in line and line.split()[0].isdigit():
            key = int(line.split()[0])
            path = list(map(int, line.strip().split("Path:")[1].strip().split(",")))
            path_blocks[key] = path
        elif "cumDist:" in line and line.split()[0].isdigit():
            key = int(line.split()[0])
            dists_raw = line.strip().split("cumDist:")[1].strip()
            points = dists_raw.split("), (")
            cum = []
            for p in points:
                p = p.replace("(", "").replace(")", "")
                vals = list(map(float, p.split(",")))
                cum.append(tuple(vals))
            dist_blocks[key] = cum
    return path_blocks, dist_blocks

# --- Main Simulation ---
def simulate_evacuees(path_txt):
    path_map, cum_map = parse_path_file(path_txt)
    evacuees = []
    count = 1

    for key in list(path_map.keys())[:4]:
        path, cum = path_map[key], cum_map[key]
        for _ in range(5):
            evacuees.append(Evacuee(f"car_{count}", path, cum))
            count += 1

    for t in [0, 5, 15]:
        print(f"\n====== Timestamp t = {t} minutes ======")
        for evac in evacuees:
            evac.move(t)
            evac.update_risk(current_time=t)
            print(evac.status())

# --- Entry Point ---
if __name__ == "__main__":
    simulate_evacuees("/Users/stb34/Documents/wildfire/Experiments/Results/San Francisco_path_objectives.txt")
