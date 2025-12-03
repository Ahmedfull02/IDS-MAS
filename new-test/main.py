from spade.agent import Agent
from injector import InjectorAgent
from Preprocessor import PreprocessorAgent
from Analyzer import TabAnalyzerAgent
from Dashboard import DashboardAgent
from spade.agent import WebApp


async def main():

    # WebApp.add_get("/", controller=WebApp.handle_request, template="/new-test/data/launch.html")
    # WebApp.start(port="10003", templates_path="/new-test/data")

    injector = InjectorAgent("agent1@localhost", "1")
    preprocessor = PreprocessorAgent("agent2@localhost", "2")
    analyzer = TabAnalyzerAgent("agent3@localhost", "3")
    dashboard = DashboardAgent("agent4@localhost", "4")

    await injector.start(auto_register=True)
    await preprocessor.start(auto_register=True)
    await analyzer.start(auto_register=True)
    await dashboard.start(auto_register=True)
    print("Agents are running")

    await asyncio.sleep(1000)  # Keep the agents running for a while


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 