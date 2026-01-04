def generate_alerts(df):
    alerts = df[df["anomalie"] == 1].copy()

    def criticite(row):
        if row["panne_predite"] == "Court-circuit":
            return "Critique"
        elif row["panne_predite"] == "Surcharge":
            return "Élevée"
        else:
            return "Modérée"

    alerts["criticite"] = alerts.apply(criticite, axis=1)
    return alerts[["zone", "panne_predite", "criticite"]]