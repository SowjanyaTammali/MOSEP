import pandas as pd

def compute_updated_risky_edges(
    node_csv_path: str,
    edge_csv_path: str,
    current_time: int,
    checkpoint_time: int = 0,
    threshold: float = 0.5,
    output_path: str = None
) -> pd.DataFrame:

    node_df = pd.read_csv(node_csv_path)
    edge_df = pd.read_csv(edge_csv_path)


    node_prob_map = dict(zip(node_df["node_id"], node_df["fire_prob"]))


    delta_t = current_time - checkpoint_time
    updated_node_probs = {
        node: 1 - (1 - prob) ** delta_t
        for node, prob in node_prob_map.items()
    }


    updated_edges = []
    for _, row in edge_df.iterrows():
        u = row["From_Node_ID"]
        v = row["To_Node_ID"]
        w1 = row["w1"]
        w3 = row["w3"]

        p1 = updated_node_probs.get(u, 0.0)
        p2 = updated_node_probs.get(v, 0.0)
        p_edge = (p1 + p2) / 2
        w2_updated = p_edge * w1

        if p_edge > threshold:
            updated_edges.append({
                "From_Node_ID": int(u),
                "To_Node_ID": int(v),
                "w1": w1,
                "fire_prob_updated": round(p_edge, 6),
                "w2_updated": round(w2_updated, 6),
                "w3": w3
            })

    result_df = pd.DataFrame(updated_edges)

    if output_path:
        result_df.to_csv(output_path, index=False)
        print(f"Risky edges saved to: {output_path}")

    print(f"Total risky edges found: {len(result_df)}")
    return result_df



if __name__ == "__main__":
    compute_updated_risky_edges(
        node_csv_path="/Users/stb34/Documents/wildfire/Experiments/San_Francisco/Original_fire_probabality_zone.csv",
        edge_csv_path="/Users/stb34/Documents/wildfire/Experiments/San_Francisco/final_edge_weights_directional.csv",
        current_time=5,
        checkpoint_time=0,
        threshold=0.00079,
        output_path="/Users/stb34/Documents/wildfire/Experiments/San_Francisco/Updated_edge_weights_fire_risk.csv"
    )
