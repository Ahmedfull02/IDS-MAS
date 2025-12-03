from aiohttp import web
from spade.behaviour import CyclicBehaviour
import random
from spade.agent import Agent
from spade.message import Message
import json
import datetime
from datetime import timedelta
import asyncio

class CollectorAgent(Agent):
    class ReceiveBehaviour(CyclicBehaviour):
        async def on_start(self):
                self.received = []
                print("[Collector] started and waiting for messages...")

        async def run(self):
            # Wait up to 30 seconds for a message
            msg = await self.receive(timeout=30)
            if msg:
                print(f"[Collector] Received from {msg.sender}: {msg.body}")
                self.received.append((str(msg.sender), msg.body))

                # Stop after 3 messages (or however many senders)
                if len(self.received) >= 3:
                    print("[Collector] Collected all messages. Stopping...")
                    # stop the collector agent after a short delay to allow console output
                    await asyncio.sleep(0.5)
                    await self.agent.stop()
            else:
                # timed out waiting for a message; keep waiting or stop depending on your needs
                print("[Collector] waiting... (no message received in timeout)")

    async def setup(self):
        b = self.CollectBehaviour()
        self.add_behaviour(b)
        print(f"\n\n\nCollector Agent {self.jid} started.\n\n\n")