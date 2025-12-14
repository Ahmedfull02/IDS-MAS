import asyncio
import sys
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class MyAgent(Agent):
    class MyBehaviour(CyclicBehaviour):
        async def run(self):
            print("[Agent] I am alive and running...")
            # This sleep simulates work being done
            await asyncio.sleep(3)

    async def setup(self):
        print("Agent starting . . .")
        
        # 1. Start the built-in web dashboard on port 10000
        await self.web.start(port=10000)
        print("Web dashboard enabled: http://localhost:10000")
        
        # 2. Add the behavior
        b = self.MyBehaviour()
        self.add_behaviour(b)

async def main():
    # --- ENTER REAL CREDENTIALS HERE ---
    JID = "admin@localhost"
    PASSWORD = "admin"

    if JID == "your_username@xmpp.server":
        print("ERROR: Please update the JID and PASSWORD with real XMPP credentials.")
        return

    # Create the agent
    dummy_agent = MyAgent(JID, PASSWORD)
    
    # Start the agent
    await dummy_agent.start()
    print("Agent started. Press Ctrl+C to quit.")

    # Keep the script running so the agent stays alive
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping agent...")
        await dummy_agent.stop()

if __name__ == "__main__":
    # Windows fix for Python 3.8+
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())