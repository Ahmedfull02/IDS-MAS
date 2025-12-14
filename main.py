import click
from slixmpp import JID

from injector import InjectorAgent
from Preprocessor import PreprocessorAgent
from Analyzer import TabAnalyzerAgent
from Analyzer2 import RFAnalyzerAgent
from Analyzer3 import GBAnalyzerAgent
from Dashboard import DashboardAgent
from Collector import CollectorAgent

import spade
from spade.presence import PresenceType, PresenceInfo, Contact

AGENT1 = ["agent1@localhost", "1"]
AGENT2 = ["agent2@localhost", "2"]
AGENT3 = ["agent3@localhost", "3"]
AGENT4 = ["agent4@localhost", "4"]
AGENT5 = ["agent5@localhost", "5"]
AGENT6 = ["agent6@localhost", "6"]
AGENT7 = ["agent7@localhost", "7"]


class WebAgent(agent.Agent):
    
    async def setup(self):
        injector = InjectorAgent(AGENT1[0], AGENT1[1])
        preprocessor = PreprocessorAgent(AGENT2[0], AGENT2[1])
        analyzer1 = TabAnalyzerAgent(AGENT3[0], AGENT3[1])
        analyzer2 = RFAnalyzerAgent(AGENT4[0], AGENT4[1])
        analyzer3 = GBAnalyzerAgent(AGENT5[0], AGENT5[1])
        collector = CollectorAgent(AGENT6[0], AGENT6[1])
        dashboard = DashboardAgent(AGENT7[0], AGENT7[1])

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

        # Create some fake contacts
        self.add_agent(AGENT1[0], PresenceType.AVAILABLE)
        self.add_agent(AGENT2[0], PresenceType.AVAILABLE)
        self.add_agent(AGENT3[0], PresenceType.AVAILABLE)
        self.add_agent(AGENT4[0], PresenceType.AVAILABLE)
        self.add_agent(AGENT5[0], PresenceType.AVAILABLE)
        self.add_agent(AGENT6[0], PresenceType.AVAILABLE)
        

    def add_agent(self, jid, presence, show=None):
        jid = JID(jid)

        contact = Contact(
            jid.bare, name=jid.bare, subscription="both", ask="", groups=[]
        )

        pinfo = PresenceInfo(presence, show=show)
        contact.update_presence("resource", pinfo)

        self.presence.contacts[jid.bare] = contact


async def main(jid, pwd, port):
    a = WebAgent(jid, pwd)
    a.web.port = port

    await a.start(auto_register=True)

    print("Agent web at {}:{}".format(a.web.hostname, a.web.port))
    await spade.wait_until_finished(a)


@click.command()
@click.option("--jid", prompt="Agent JID> ")
@click.option("--pwd", prompt="Password>", hide_input=True)
@click.option("--port", default=10000)
def run(jid, pwd, port):
    spade.run(main(jid, pwd, port))


if __name__ == "__main__":
    run()