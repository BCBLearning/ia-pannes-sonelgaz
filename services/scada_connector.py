from opcua import Client
import pandas as pd

def get_scada_data():
    client = Client("opc.tcp://127.0.0.1:4840")
    client.connect()

    data = {
        "zone": "Nord",
        "tension": client.get_node("ns=2;i=1001").get_value(),
        "courant": client.get_node("ns=2;i=1002").get_value(),
    }

    client.disconnect()

    data["puissance"] = round(data["tension"] * data["courant"] / 1000, 2)
    return pd.DataFrame([data])