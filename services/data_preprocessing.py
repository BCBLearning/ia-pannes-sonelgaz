def preprocess(df):
    df = df.dropna()
    df["puissance"] = df["tension"] * df["courant"] / 1000
    return df