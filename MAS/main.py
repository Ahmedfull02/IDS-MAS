import asyncio
from spade.agent import Agent

from injector import InjectorAgent
from Preprocessor import PreprocessorAgent
from Analyzer import TabAnalyzerAgent
from Analyzer2 import RFAnalyzerAgent
from Analyzer3 import GBAnalyzerAgent
from Dashboard import DashboardAgent
from Collector import CollectorAgent

AGENT1 = ["agent1@localhost", "1"]
AGENT2 = ["agent2@localhost", "2"]
AGENT3 = ["agent3@localhost", "3"]
AGENT4 = ["agent4@localhost", "4"]
AGENT5 = ["agent5@localhost", "5"]
AGENT6 = ["agent6@localhost", "6"]
AGENT7 = ["agent7@localhost", "7"]

async def main():
    print("--- Initializing Agents ---")
    
    injector = InjectorAgent(AGENT1[0], AGENT1[1])
    preprocessor = PreprocessorAgent(AGENT2[0], AGENT2[1])
    analyzer1 = TabAnalyzerAgent(AGENT3[0], AGENT3[1])
    analyzer2 = RFAnalyzerAgent(AGENT4[0], AGENT4[1])
    analyzer3 = GBAnalyzerAgent(AGENT5[0], AGENT5[1])
    collector = CollectorAgent(AGENT6[0], AGENT6[1])
    dashboard = DashboardAgent(AGENT7[0], AGENT7[1])

    print("--- Starting Agents ---")
    await injector.start(auto_register=True)
    await preprocessor.start(auto_register=True)
    await analyzer1.start(auto_register=True)
    await analyzer2.start(auto_register=True)
    await analyzer3.start(auto_register=True)
    await collector.start(auto_register=True)
    await dashboard.start(auto_register=True)

    print("--- Starting Web Interfaces ---")
    
    await injector.web.start(hostname="127.0.0.1", port=10000)
    await preprocessor.web.start(hostname="127.0.0.1", port=10001)
    await analyzer1.web.start(hostname="127.0.0.1", port=10002)
    await analyzer2.web.start(hostname="127.0.0.1", port=10003)
    await analyzer3.web.start(hostname="127.0.0.1", port=10004)
    await collector.web.start(hostname="127.0.0.1", port=10005)
    await dashboard.web.start(hostname="127.0.0.1", port=10006)

    print("\nAll Agents Running. Access Dashboards here:")
    print(f"Injector:     http://127.0.0.1:10000")
    print(f"Preprocessor: http://127.0.0.1:10001")
    print(f"Analyzer1:    http://127.0.0.1:10002")
    print(f"Analyzer2:    http://127.0.0.1:10003")
    print(f"Analyzer3:    http://127.0.0.1:10004")
    print(f"Collector:    http://127.0.0.1:10005")
    print(f"Dashboard:    http://127.0.0.1:10006")
    print("\nPress Ctrl+C to stop the system.")

    # 4. Keep the script running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all agents...")
        await injector.stop()
        await preprocessor.stop()
        await analyzer1.stop()
        await analyzer2.stop()
        await analyzer3.stop()
        await collector.stop()
        await dashboard.stop()
        print("System stopped.")

if __name__ == "__main__":
    asyncio.run(main())
