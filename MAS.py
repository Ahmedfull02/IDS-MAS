import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

# Agent 1: Initiator
class Agent1(Agent):
    class SendBehaviour(CyclicBehaviour):
        async def run(self):
            print("Agent1: Sending message to Agent2")
            msg = Message(to="agent2@localhost")
            msg.set_metadata("performative", "inform")
            msg.body = "Hello from Agent1!"
            await self.send(msg)
            print("Agent1: Message sent!")

    async def setup(self):
        print("Agent1 started")
        b = self.SendBehaviour()
        self.add_behaviour(b)

# Agent 2: Middleman
class Agent2(Agent):
    class ReceiveAndForwardBehaviour(CyclicBehaviour):
        async def run(self):
            print("Agent2: Waiting for message...")
            msg = await self.receive(timeout=10)
            if msg:
                print(f"Agent2: Received: {msg.body}")
                print("Agent2: Forwarding to Agent3")
                
                forward_msg = Message(to="agent3@localhost")
                forward_msg.set_metadata("performative", "inform")
                forward_msg.body = f"Agent2 forwarding: {msg.body}"
                await self.send(forward_msg)
                print("Agent2: Message forwarded!")

    async def setup(self):
        print("Agent2 started")
        b = self.ReceiveAndForwardBehaviour()
        self.add_behaviour(b)

# Agent 3: Receiver
class Agent3(Agent):
    class ReceiveBehaviour(OneShotBehaviour):
        async def run(self):
            print("Agent3: Waiting for message...")
            msg = await self.receive(timeout=10)
            if msg:
                print(f"Agent3: Received: {msg.body}")
                print("Agent3: Task completed!")

    async def setup(self):
        print("Agent3 started")
        b = self.ReceiveBehaviour()
        self.add_behaviour(b)

# Main execution
async def main():
    # Create agents with JID and password
    agent1 = Agent1("agent1@localhost", "1")
    agent2 = Agent2("agent2@localhost", "2")
    agent3 = Agent3("agent3@localhost", "3")

    # Start all agents
    await agent1.start()
    await agent2.start()
    await agent3.start()
    agent1.web.start(hostname="127.0.0.1", port="10000")
    agent2.web.start(hostname="127.0.0.2", port="10000")
    agent3.web.start(hostname="127.0.0.3", port="10000")

    print("All agents started. Waiting for communication...")
    
    # Wait for agents to complete their tasks
    await asyncio.sleep(5)

    # # Stop all agents
    # await agent1.stop()
    # await agent2.stop()
    # await agent3.stop()
    print("All agents stopped")

if __name__ == "__main__":
    asyncio.run(main())
