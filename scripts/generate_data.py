import pandas as pd
import numpy as np
import os

os.makedirs("data", exist_ok=True)

def generate_data(n_samples=500):
    zones = ["Nord", "Sud", "Est", "Ouest", "Centre"]
    data = []
    for _ in range(n_samples):
        tension = np.random.normal(230, 5)
        courant = np.random.normal(10, 2)
        panne = np.random.rand() < 0.08
        type_panne = "OK"
        if panne:
            type_panne = np.random.choice(["Court-circuit","Surcharge","Ligne coupée"])
            tension -= np.random.uniform(30,60)
            courant += np.random.uniform(3,8)
        puissance = round(tension * courant / 1000, 2)
        data.append({
            "zone": np.random.choice(zones),
            "tension": round(tension,2),
            "courant": round(courant,2),
            "puissance": puissance,
            "panne": int(panne),
            "type_panne": type_panne
        })
    df = pd.DataFrame(data)
    df.to_csv("data/data.csv", index=False)
    return df

if __name__ == "__main__":
    generate_data()