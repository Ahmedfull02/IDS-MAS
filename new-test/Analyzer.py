from spade.behaviour import CyclicBehaviour
import random
from spade.agent import Agent
from spade.message import Message
import json


class AnalyzerAgent(Agent):
    class AnalyzeBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                if msg.body is not None:
                    data = json.loads(msg.body)
                else:
                    print("Received message with no body.")
                    return
                # Simulate a model prediction
                benign = self.analyze(data)
                new_msg = Message(to="agent4@localhost")
                
                new_msg.body = json.dumps({**data, "status": "benign" if benign else "malicious"})
                
                print(new_msg.body+ 'In analyzer')
                
                await self.send(new_msg)
                if not benign:
                    print("Detected non-benign data. Stopping system.")
                    self.agent.pause_system()

        def analyze(self, data):
            # Replace with your model logic
            return random.choice([True, False])

    async def setup(self):
        b = self.AnalyzeBehaviour()
        self.add_behaviour(b)
        print(f"AnalyzerAgent {self.jid} started")

    def pause_system(self):
        # Logic to pause the system
        print("System paused. Awaiting user input to continue...")
        # Add mechanism for user to continue the system