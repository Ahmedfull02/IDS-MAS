from aiohttp import web
from spade.behaviour import CyclicBehaviour
import random
from spade.agent import Agent
from spade.message import Message
import json

class DashboardAgent(Agent):
    results = []
    class DashboardBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                data = json.loads(msg.body) if msg.body is not None else {}
                print(data, 'In dashboard')
                self.agent.add_result(data)

    async def setup(self):
        self.web.add_get("/dashboard", self.launch_controller, template="new-test/data/dashboard.html")
        self.web.start(port=10001, templates_path="data")   
        
        self.web.add_get("/list", self.handle_request, template='new-test/data/list.html')
        self.web.start(port=10001)
        
        print(50*"-")
        print("Dashboard web server started at http://localhost:10001/dashboard")
        print(50*"-")
        
        b = self.DashboardBehaviour()
        self.add_behaviour(b)
        print(f"DashboardAgent {self.jid} started")

    async def launch_controller(self, request):
        return ({"result": 'Agents works'})
    
    async def handle_request(self, request):
        return ({"results": self.results})

    def add_result(self, result):
        self.results.append(result)
    
    def present(self):
        important_columns = [
                'Timestamp', 'Src IP', 'Dst IP', 'Src Port', 'Dst Port', 'Protocol',
                'Flow Duration', 'Total Fwd Packet', 'Total Bwd packets',
                'Total Length of Fwd Packet', 'Total Length of Bwd Packet',
                'Flow Bytes/s', 'Flow Packets/s',
                'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std',
                'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std',
                'FIN Flag Count', 'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count',
                'Subflow Fwd Packets', 'Subflow Fwd Bytes', 'Subflow Bwd Packets', 'Subflow Bwd Bytes',
                'Label'
            ]
        return self.results