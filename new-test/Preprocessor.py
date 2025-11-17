import pandas as pd
import json
from spade.behaviour import CyclicBehaviour
import random
from spade.agent import Agent
from spade.message import Message
import json
import datetime as dt

class PreprocessorAgent(Agent):
    class ProcessBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                data = json.loads(msg.body) if msg.body is not None else {}
                # Preprocess the data
                processed_data = self.preprocess(data)
                # Send to Analyzer
                new_msg = Message(to="agent3@localhost")
                new_msg.body = json.dumps(processed_data)
                print(new_msg.body, 'In preprocessor')
                await self.send(new_msg)

        
        ######## Preprocessing function
        
        
        
        ######## Preprocessing function
        
        
        def preprocess(self, data):
            # Assuming your data is in a DataFrame called df
            important_columns = [
                'Timestamp', 'Src IP', 'Dst IP', 'Src Port', 'Dst Port', 'Protocol',
                'Flow Duration', 'Total Fwd Packet', 'Total Bwd packets',
                'Total Length of Fwd Packet', 'Total Length of Bwd Packet',
                'Flow Bytes/s', 'Flow Packets/s',
                'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std',
                'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std',
                'FIN Flag Count', 'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count',
                'Subflow Fwd Packets', 'Subflow Fwd Bytes', 'Subflow Bwd Packets', 'Subflow Bwd Bytes',
                'Label'
            ]
            # Filter the data to only include necessary fields
            processed_data = {key: data[key] for key in important_columns if key in data}
            processed_data.update({"Timestamp": dt.datetime.now().isoformat()})
            return processed_data

    async def setup(self):
        b = self.ProcessBehaviour()
        self.add_behaviour(b)
        print(f"PreprocessorAgent {self.jid} started")