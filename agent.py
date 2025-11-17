import asyncio
from spade.agent import Agent

class TestAgent(Agent):
    async def setup(self):
        print(f"✓ {self.jid} connected to Openfire successfully!")

async def main():
    print("Testing Openfire connection...\n")
    
    agent1 = TestAgent("agent1@localhost", "1")
    agent2 = TestAgent("agent2@localhost", "2")
    agent3 = TestAgent("agent3@localhost", "03")
    
    agents = [agent1, agent2, agent3]
    
    for agent in agents:
        try:
            await agent.start()
            print(f"✓ Connection of {agent.name} is successful!")
            await asyncio.sleep(2)
            await agent.stop()
            print("✓ Test completed!")
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure Openfire is running")
            print("2. Check account was created correctly")
            print("3. Verify username/password")
    

if __name__ == "__main__":
    asyncio.run(main())