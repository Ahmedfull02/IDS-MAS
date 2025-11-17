import pandas as pd
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour, OneShotBehaviour
from spade.message import Message
from aiohttp import web

class InjectorAgent(Agent):
    class InjectBehaviour(PeriodicBehaviour):
        def __init__(self, csv_file, period=5):
            super().__init__(period=period)
            self.data = pd.read_csv(csv_file)
            self.index = 0

        async def run(self):
            if self.index < 20:
                row = self.data.iloc[self.index].to_json()
                msg = Message(to="agent2@localhost")
                msg.body = row
                await self.send(msg)
                print(f"Injected row {self.index}")
                self.index += 1
            else:
                print("All rows injected")
                self.kill()
            
    
    async def setup(self):
        b = self.InjectBehaviour("data/friday.csv", period=5)
        self.add_behaviour(b)  # Inject every 5 seconds
        print(f"InjectorAgent {self.jid} started")
