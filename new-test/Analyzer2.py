from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
import random
from spade.agent import Agent
from spade.message import Message
import json
import pandas as pd
from spade.template import Template
import pickle as pkl

from sklearn.preprocessing import LabelEncoder
from sklearn.utils.validation import check_is_fitted
from sklearn.exceptions import NotFittedError


MODEL_PATH = "C:\\Users\\YOGA\\Desktop\\master s4 PFE\\project\\IDS-MAS\\new-test\\model\\rf\\model.pkl"
ENCODER_PATH = "C:\\Users\\YOGA\\Desktop\\master s4 PFE\\project\\IDS-MAS\\new-test\\model\\rf\\encoder_y.pkl" 
METRICS_PATH = "C:\\Users\\YOGA\\Desktop\\master s4 PFE\\project\\IDS-MAS\\new-test\\model\\rf\\metric_results.json"
IMPORTANCE8PATH = "C:\\Users\\YOGA\\Desktop\\master s4 PFE\\project\\IDS-MAS\\new-test\\model\\rf\\importance_df.json"

AGENT6 = "agent6@localhost"

class RFAnalyzerAgent(Agent):
    class AnalyzeBehaviour(CyclicBehaviour):
        def __init__(self, model_path, y_encoder_path):
            super().__init__()
            self.model_path = model_path
            self.y_encoder_path = y_encoder_path
            # Importing the model
            self.model = self.importFile(self.model_path)
            self.y_encoder = self.importFile(self.y_encoder_path)
                    
                
        async def run(self):
            msg = await self.receive()
            if msg:
                if msg.body is not None:
                    data = json.loads(msg.body)
                else:
                    print("[RFAnalyzer] Received message with no body.")
                    return

                # Model prediction
                data_processed = data.get("0")
                encoded_data = data.get("1")
                data_id = data_processed.get("id", "N/A")
                
                print(f"[RFAnalyzer] Received data for ID {data_id}")
                
                ed = pd.DataFrame([encoded_data])
                              
                # Predicting the traffic severity
                prediction = self.predictIncident(self.model, ed.values)
                
                # Transform results to text
                prediction = self.analyze(y_encoder=self.y_encoder, prediction=prediction)
                
                print(f"[RFAnalyzer] Prediction: {prediction} for ID {data_id}")

                # Send data to dashboard agent 
                new_msg = Message(to=AGENT6)
                data_processed.update({"RFPred": prediction})
                new_msg.body = json.dumps(data_processed)
                await self.send(new_msg)
                
                print(f"[RFAnalyzer] ✓ Prediction sent to Collector (ID: {data_id}, Prediction: {prediction})")

        def importFile(self, model_path):
            with open(model_path, "rb") as file:
                model = pkl.load(file)
            return model

        def predictIncident(self, model, data):
            prediction = model.predict(data)
            return prediction

        def analyze(self, y_encoder, prediction):
            # Replace with your model logic
            pred = y_encoder.inverse_transform(prediction)
            pred = pred[0]
            return pred

    async def setup(self):
        b = self.AnalyzeBehaviour(MODEL_PATH,ENCODER_PATH)
        self.add_behaviour(b)
        print(f"\n\n\nAnalyzerAgent {self.jid} started\n\n\n")