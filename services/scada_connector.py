from opcua import Client
import pandas as pd
import time

# --------------------------------------------------
# Connexion SCADA OPC-UA (lecture seule)
# --------------------------------------------------

OPCUA_ENDPOINT = "opc.tcp://127.0.0.1:4840"

# NodeIds EXEMPLE (à adapter au SCADA Sonelgaz)
NODE_TENSION = "ns=2;i=1001"
NODE_COURANT = "ns=2;i=1002"

def get_scada_data():
    """
    Lecture sécurisée des données SCADA via OPC-UA
    Retourne un DataFrame compatible IA
    """

    try:
        client = Client(OPCUA_ENDPOINT, timeout=2)
        client.connect()

        tension = client.get_node(NODE_TENSION).get_value()
        courant = client.get_node(NODE_COURANT).get_value()

        client.disconnect()

        data = {
            "zone": "Poste_Nord_01",
            "tension": float(tension),
            "courant": float(courant),
            "puissance": round((tension * courant) / 1000, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        return pd.DataFrame([data])

    except Exception as e:
        # Sécurité DSI : aucune exception non gérée
        return pd.DataFrame([])