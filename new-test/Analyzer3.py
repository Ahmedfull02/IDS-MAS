from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
import random
from spade.agent import Agent
from spade.message import Message
import json
from pytorch_tabnet.tab_model import TabNetClassifier
import pandas as pd
from spade.template import Template
import pickle as pkl

from sklearn.preprocessing import LabelEncoder
from sklearn.utils.validation import check_is_fitted
from sklearn.exceptions import NotFittedError


MODEL_PATH = "C:\\Users\\YOGA\\Desktop\\master s4 PFE\\project\\IDS-MAS\\new-test\\model\\xgb\\model.pkl"
ENCODER_PATH = "C:\\Users\\YOGA\\Desktop\\master s4 PFE\\project\\IDS-MAS\\new-test\\model\\xgb\\encoder_y.pkl" 
METRICS_PATH = "C:\\Users\\YOGA\\Desktop\\master s4 PFE\\project\\IDS-MAS\\new-test\\model\\xgb\\metric_results.json"
IMPORTANCE_PATH = "C:\\Users\\YOGA\\Desktop\\master s4 PFE\\project\\IDS-MAS\\new-test\\model\\xgb\\importance_df.json"

AGENT6 = "agent6@localhost"

class XGBAnalyzerAgent(Agent):
    class AnalyzeBehaviour(CyclicBehaviour):
        def __init__(self, model_path, y_encoder_path):
            super().__init__()
            self.model_path = model_path
            self.y_encoder_path = y_encoder_path

        async def run(self):
            msg = await self.receive()
            if msg:
                if msg.body is not None:
                    data = json.loads(msg.body)
                else:
                    print("Received message with no body.")
                    return

                # print("\n\n\n\n\n\n")
                # print("In Analyzer Agent")
                # Model prediction
                data_processed = data.get("0")
                encoded_data = data.get("1")
                print(type(encoded_data))
                ed = pd.DataFrame([encoded_data])
                print("\n\n\n\nEncoded data type now is:", type(ed))
                # Importing the model
                model = self.importFile(self.model_path)
                if isinstance(model, TabNetClassifier):
                    print("Model is imported successfully.\n\n")

                try:
                    check_is_fitted(model)
                    print("Model is fitted.")
                except NotFittedError:
                    print("Model is NOT fitted yet.")
                    
                y_encoder = self.importFile(self.y_encoder_path)
                if isinstance(model, LabelEncoder):
                    print("Y encoder is imported successfully.\n\n") 
                
                # Predicting the traffic severity
                prediction = self.predictIncident(model, ed.values)
                
                # Transform results to text
                prediction = self.analyze(y_encoder=y_encoder, prediction=prediction)

                # Send data to dashboard agent 
                new_msg = Message(to=AGENT6)
                print(f"\n\n\n Model XGB \n\n\n")               
                data_processed.update({"XGBPred": prediction})
                new_msg.body = json.dumps(data_processed)
                await self.send(new_msg)

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