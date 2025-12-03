from spade.agent import Agent
from injector import InjectorAgent
from Preprocessor import PreprocessorAgent
from Analyzer import TabAnalyzerAgent
from Analyzer2 import RFAnalyzerAgent
from Analyzer3 import XGBAnalyzerAgent
from Dashboard import DashboardAgent
from Collector import CollectorAgent
from spade.agent import WebApp

AGENT1 = ["agent1@localhost", "1"]
AGENT2 = ["agent2@localhost", "2"]
AGENT3 = ["agent3@localhost", "3"]
AGENT4 = ["agent4@localhost", "4"]
AGENT5 = ["agent5@localhost", "5"]
AGENT6 = ["agent6@localhost", "6"]

async def main():

    # WebApp.add_get("/", controller=WebApp.handle_request, template="/new-test/data/launch.html")
    # WebApp.start(port="10003", templates_path="/new-test/data")

    injector = InjectorAgent(AGENT1[0],AGENT1[1])
    preprocessor = PreprocessorAgent(AGENT2[0],AGENT2[1])
    analyzer1 = TabAnalyzerAgent(AGENT3[0],AGENT3[1])
    analyzer2 = RFAnalyzerAgent(AGENT4[0],AGENT4[1])
    analyzer3 = XGBAnalyzerAgent(AGENT5[0],AGENT5[1])
    collector = CollectorAgent(AGENT6[0],AGENT6[1])

    await injector.start(auto_register=True)
    await preprocessor.start(auto_register=True)
    await analyzer1.start(auto_register=True)
    await analyzer2.start(auto_register=True)
    # await analyzer3.start(auto_register=True)
    await collector.start(auto_register=True)
    print("Agents are running")

    await asyncio.sleep(1000)  # Keep the agents running for a while


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 