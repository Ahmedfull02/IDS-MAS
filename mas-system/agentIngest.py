from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
import asyncio
import aiohttp.web
from spade.message import Message

class WorkerAgent(Agent):
    class WorkBehaviour(CyclicBehaviour):
        async def run(self):
            print(f"Agent {self.agent.jid} is working")
            await self.agent.suspend_behaviour(self)

    async def setup(self):
        b = self.WorkBehaviour(period=10)
        self.add_behaviour(b)
        print(f"Agent {self.jid} started")