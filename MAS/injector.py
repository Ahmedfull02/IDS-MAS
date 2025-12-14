import pandas as pd
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour, OneShotBehaviour
from spade.message import Message
from aiohttp import web
import functions_to_use as f
from spade.template import Template
import random

AGENT2 = "agent2@localhost"

class InjectorAgent(Agent):
    class InjectBehaviour(PeriodicBehaviour):
        def __init__(self, csv_file, period=1):
            super().__init__(period=period)
            self.data = pd.read_csv(csv_file)
            
            self.index = 0

        async def run(self):
            if self.index < len(self.data): # len(self.data)
                row = f.read_data_row(self.data, self.index)
                msg = Message(to=AGENT2)
                msg.set_metadata("performative", "inform")
                row.update({'id':self.index})
                msg.body = row.to_json()
                await self.send(msg)
                
                print(f"[Injector] ✓ Row {self.index} injected and sent to Preprocessor")
                self.index += 1
            else:
                print(f"[Injector] All rows injected (total: {self.index})")
                self.kill()

    async def setup(self):
        b = self.InjectBehaviour("data/dataset.csv", period=2)
        self.add_behaviour(b)  # Inject every 1 second
        print(f"\n\n\nInjectorAgent {self.jid} started\n\n\n")
