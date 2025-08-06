import pandas as pd
import random
from scipy.stats import beta

# === Define Beta CDF-based velocity computation ===
def compute_velocity(d1, d2, delay, alpha=5, beta_param=2):
    distance = d2 - d1
    if distance <= 0 or delay <= 0:
        return 0.0

    V_max = distance / delay  # m/s
    V_max_kmph = V_max * 3.6
    V_min_kmph = max(0, V_max_kmph - 5)
    V_min = V_min_kmph / 3.6

    x_prime = (d1 + d2) / 2
    d = d2 if d2 != 0 else 1  # avoid divide by zero

    z = x_prime / d
    beta_cdf = beta.cdf(z, alpha, beta_param)
    velocity = V_max + (V_max - V_min) * (1 - beta_cdf)
    return float(round(velocity, 3))

# === Evacuee class ===
class Evacuee:
    def __init__(self, evacuee_id, initial_location, request_time):
        self.evacuee_id = evacuee_id
        self.initial_location = initial_location
        self.request_time = request_time
        self.path = []
        self.cumulative = []
        self.velocities = []

    def set_path(self, path):
        self.path = path

    def set_cumulative(self, cumulative):
        self.cumulative = cumulative

    def add_velocity(self, velocity):
        self.velocities.append(velocity)

    def __repr__(self):
        return (f"Evacuee(ID={self.evacuee_id}, Start={self.initial_location}, "
                f"Time={self.request_time}, Path={self.path}, Velocities={self.velocities})")

# === Main Function ===
def main():
    path_file = "/Users/stb34/Documents/wildfire/Experiments/Results/San Francisco_path_objectives.txt"
    with open(path_file, "r") as f:
        lines = f.readlines()

    path_blocks = {}
    dist_blocks = {}

    for line in lines:
        if "Path:" in line and line.split()[0].isdigit():
            key = int(line.split()[0])
            path_str = line.strip().split("Path:")[1].strip()
            path = list(map(int, path_str.split(",")))
            path_blocks[key] = path

        elif "cumDist:" in line and line.split()[0].isdigit():
            key = int(line.split()[0])
            dist_str = line.strip().split("cumDist:")[1].strip()
            points = dist_str.split("), (")
            cum = []
            for p in points:
                p = p.replace("(", "").replace(")", "")
                vals = list(map(float, p.split(",")))
                cum.append(tuple(vals))
            dist_blocks[key] = cum

    evacuees = []

    for idx in list(path_blocks.keys())[:5]:  # Only create 5 evacuees
        path = path_blocks[idx]
        cum = dist_blocks[idx]

        evac = Evacuee(evacuee_id=f"car_{idx}", initial_location=path[0], request_time="t0")
        evac.set_path(path)
        evac.set_cumulative(cum)

        for j in range(len(cum) - 1):
            d1 = cum[j][0]
            d2 = cum[j + 1][0]
            delay = cum[j + 1][2]
            velocity = compute_velocity(d1, d2, delay)
            evac.add_velocity(velocity)

        evacuees.append(evac)

    for evac in evacuees:
        print(evac)

if __name__ == "__main__":
    main()
