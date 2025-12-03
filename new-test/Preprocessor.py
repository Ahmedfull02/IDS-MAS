import pandas as pd
import json
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
import random
from spade.agent import Agent
from spade.message import Message
import datetime as dt
import functions_to_use as func
import logging
import pickle as pkl
from spade.template import Template

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

AGENT3 = "agent3@localhost"
AGENT4 = "agent4@localhost"
AGENT5 = "agent5@localhost"
AGENT6 = "agent6@localhost"

class PreprocessorAgent(Agent):
    class ProcessBehaviour(CyclicBehaviour):
        def __init__(self, cols_file, encoder):
            super().__init__()
            self.cols_file = cols_file
            self.encoder_path = encoder

        async def run(self):
            msg = await self.receive()  # Wait for a message for 10 seconds
            if msg:
                data_json = msg.body if msg.body is not None else {}
                # logger.info(f'data type before json load: {type(data_json)}')
                # print(type(data_json))
                if isinstance(data_json, str):
                    data_json = json.loads(data_json)

                data_id = data_json.get("id", "N/A")
                print(f"[Preprocessor] Received data for ID {data_id}")

                cleaned_data = self.cleanAgent(data=data_json, cols_file=self.cols_file)
                # print('\n\n\n\n\n\n')
                # print("Cleaned data:", cleaned_data)
                print(f"[Preprocessor] Data cleaned for ID {data_id}")

                data_pd = pd.DataFrame([cleaned_data])

                encoded_data = self.encodeAgent(data_pd, enc=self.encoder_path)
                # encoded_data = encoded_data.to_json(orient='records')  # Convert DataFrame to JSON string
                # print("Encoded data:", encoded_data)
                # print('data type after encoding:', type(encoded_data))
                # print('\n\n\n\n\n\n')
                print(f"[Preprocessor] Data encoded for ID {data_id}")

                # Add Timestamp for dashboard presentation
                now = dt.datetime.now()
                time = now.strftime("%d/%m/%Y %H:%M:%S")
                data_json.update({"Timestamp": time})
                # Prepare data to send to Analyzer agent
                data = json.dumps({0: data_json, 1: encoded_data})
                
                # Send data to Analyzer1
                new_msg1 = Message(to=AGENT3)
                new_msg1.body = data
                
                await self.send(new_msg1)
                print(f"[Preprocessor] ✓ Data sent to TabAnalyzer (ID: {data_id})")
                
                # Send data to Analyzer2
                new_msg2 = Message(to=AGENT4)
                new_msg2.body = data
                
                await self.send(new_msg2)
                print(f"[Preprocessor] ✓ Data sent to RFAnalyzer (ID: {data_id})")
                
                # Send data to Analyzer3
                new_msg3 = Message(to=AGENT5)
                new_msg3.body = data
                
                await self.send(new_msg3)
                print(f"[Preprocessor] ✓ Data sent to XGBAnalyzer (ID: {data_id})")

        def cleanAgent(self, data, cols_file):
            # Assuming your data is in a DataFrame called df
            columns = func.extract_columns(cols_file)
            processed_data = {key: data[key] for key in columns if key in data}
            return processed_data

        def encodeAgent(self, data, enc=None):
            # Pass data directly if it's already a dict, otherwise convert as needed
            with open(enc, "rb") as f:
                label_encoder = pkl.load(f)
            encoded_data = func.encoder(data, label_encoder)
            return encoded_data

    async def setup(self):
        b = self.ProcessBehaviour(
            cols_file="C:\\Users\\YOGA\\Desktop\\master s4 PFE\\project\\IDS-MAS\\new-test\\model\\tabnet\\cols_file.txt",
            encoder="\\Users\\YOGA\\Desktop\\master s4 PFE\\project\\IDS-MAS\\new-test\\model\\tabnet\\encoder_X.pkl",
        )
        self.add_behaviour(b)
        print(f"\n\n\nPreprocessorAgent {self.jid} started\n\n\n")