from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import asyncio
from  agentIngest import WorkerAgent as AgentComm

AGENT1 = "agent1@localhost"
AGENT2 = "agent2@localhost"
AGENT3 = "agent3@localhost"



class IDSAgent(Agent):
    class CheckWorkersBehaviour(OneShotBehaviour):
        async def run(self):
            print("Checking worker status...")
            
            await asyncio.sleep(5)
            
    async def setup(self):
        self.agent_status = {}
        b = self.CheckWorkersBehaviour()
        self.add_behaviour(b)

        self.web.start(hostname="127.0.0.1", port=10000, templates_path="/mas-system/templates")

        # Serve the HTML page
        async def serve_page(request):
            return {"result": 42}

        # Add a route to check worker status
        async def fetchStatus(request):
            return {"status": self.agent_status}
        
        self.web.add_get("/", serve_page, template='/mas-system/templates/index.html')
        self.web.add_get("/worker_status", fetchStatus, template=None)

async def main():
    
    agent = IDSAgent("main@localhost", "main")
    await agent.start(auto_register=True)
    
    agent1 = AgentComm("agent1@localhost", "1")
    agent2 = AgentComm("agent2@localhost", "2")
    agent3 = AgentComm("agent3@localhost", "3")

    await agent1.start(auto_register=True)
    await agent2.start(auto_register=True)
    await agent3.start(auto_register=True)
    
    await asyncio.sleep(1000)
    await agent1.stop()
    await agent2.stop()
    await agent3.stop()
    
    await asyncio.sleep(1000)  # Keep the agent running

    # await agent.stop()

if __name__ == '__main__':
    asyncio.run(main())