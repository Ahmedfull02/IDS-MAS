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
            sampled_df = self.data.groupby('Label', group_keys=False).apply(lambda x: x.sample(min(len(x), 1000)))
            self.data = sampled_df
            self.index = 0

        async def run(self):
            if self.index < len(self.data): # len(self.data)
                row = f.read_data_row(self.data, self.index)
                msg = Message(to=AGENT2)
                msg.set_metadata("performative", "inform")
                row.update({'id':self.index})
                msg.body = row.to_json()
                await self.send(msg)
                # print(f"Injected row {self.index}")
                self.index += 1
                print('\n\n\nThis Row is Injected.\n\n\n')
            else:
                print("All rows injected")
                self.kill()

    async def setup(self):
        b = self.InjectBehaviour("data/Friday.csv", period=5)
        self.add_behaviour(b)  # Inject every 1 second
        print(f"\n\n\nInjectorAgent {self.jid} started\n\n\n")
