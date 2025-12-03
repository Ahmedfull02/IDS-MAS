from aiohttp import web
from spade.behaviour import CyclicBehaviour
import random
from spade.agent import Agent
from spade.message import Message
import json
import datetime
from datetime import timedelta


class DashboardAgent(Agent):
    results = []
    SERVER_START = datetime.datetime.now()
    ATT_TYPES = {'BENIGN':0, 'Botnet':0, 'DDoS':0, 'DoS':0,
                    'FTP-Patator':0, 'Heartbleed':0,
                    'Infiltration':0, 'Port Scanning':0, 
                    'SSH-Patator':0, 'Web Attacks':0
                }
    ATT_OVER_TIME = {0:{},1:{}} # 0 : normal traffic 1: attack
    PROTOCOL_USAGE = {0:{},1:{}} # 0 : normal traffic 1: attack
    
    MODELS = []
    class DashboardBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                data = json.loads(msg.body) if msg.body is not None else {}
                print(data, "In dashboard")
                self.agent.add_result(data)
########################################################################################
####                                                                                ####    
####                         Dashboard variables                                    ####
####                                                                                ####
########################################################################################
                # ATTACKS types
                attack = data['Label']
                counter = self.agent.ATT_TYPES[attack]+1
                self.agent.ATT_TYPES[attack] = counter
                
                # ATTACKS Over Time
                time_attack = data['Timestamp']
                print(f"\n\n\n time attack : {time_attack}\n\n\n") # str
                print(f"\n\n\n time type : {type(time_attack)}\n\n\n")
                time_attack = datetime.datetime.strptime(time_attack, "%d/%m/%Y %H:%M:%S")
                print(f"\n\n\n time type : {type(time_attack)}\n\n\n")
                time_attack = datetime.datetime.strftime(time_attack,"%H:%M")
                
                print(f'\n\n\nATTACK time: {time_attack}\n\n\n')
                print(f'\n\n\nATTACK TYPE: {attack}\n\n\n')
                 
                if attack == 'BENIGN':
                    if time_attack in self.agent.ATT_OVER_TIME[0]:
                        self.agent.ATT_OVER_TIME[0][time_attack] += 1
                    else:
                        self.agent.ATT_OVER_TIME[0][time_attack] = 1
                else:
                    if time_attack in self.agent.ATT_OVER_TIME[1]:
                        self.agent.ATT_OVER_TIME[1][time_attack] += 1
                    else:
                        self.agent.ATT_OVER_TIME[1][time_attack] = 1
                        
                # Protocole Usage
                protocol = data['Protocol']
                if attack == 'BENIGN':
                    if protocol in self.agent.PROTOCOL_USAGE[0]:
                        self.agent.PROTOCOL_USAGE[0][protocol] += 1
                    else:
                        self.agent.PROTOCOL_USAGE[0][protocol] = 1
                else:
                    if protocol in self.agent.PROTOCOL_USAGE[1]:
                        self.agent.PROTOCOL_USAGE[1][protocol] += 1
                    else:
                        self.agent.PROTOCOL_USAGE[1][protocol] = 1
                        
                print(f'\n\n\Protocole usage: {self.agent.PROTOCOL_USAGE}\n\n\n')
                
########################################################################################
####                                                                                ####    
####                         Models info data                                       ####
####                                                                                ####
########################################################################################
                # self.agent.MODELS = [
                #     {
                #         "id": "rf",
                #         "name": "Random Forest",
                #         "type": "Ensemble Learning",
                #         "status": "Trained",
                #         "description": "Random Forest is an ensemble learning method that operates by constructing multiple decision trees during training and outputting the class that is the mode of the classes (classification) or mean prediction (regression) of the individual trees. It's highly effective for network intrusion detection due to its ability to handle high-dimensional data and resistance to overfitting.",
                #         "metrics": {},
                #         "images": {
                #             "confusionMatrix": "../model/RF/cm.png",
                #             "rocCurve": "../model/RF/roc.png",
                #             "accLoss": None,
                #         },
                #     },
                #     {
                #         "id": "xgb",
                #         "name": "XGBoost",
                #         "type": "Gradient Boosting",
                #         "status": "Trained",
                #         "description": "XGBoost (eXtreme Gradient Boosting) is an optimized distributed gradient boosting library designed to be highly efficient, flexible and portable. It implements machine learning algorithms under the Gradient Boosting framework, providing a parallel tree boosting that solves many data science problems in a fast and accurate way. It's particularly effective for structured/tabular data and has become a go-to method for winning machine learning competitions.",
                #         "metrics": {},
                #         "images": {
                #             "confusionMatrix": "../model/xgb/cm.png",
                #             "rocCurve": None,
                #             "accLoss": None,
                #         },
                #     },
                #     {
                #         "id": "tabnet",
                #         "name": "TabNet",
                #         "type": "Deep Learning",
                #         "status": "Trained",
                #         "description": "TabNet is a novel deep learning architecture specifically designed for tabular data. It uses sequential attention to choose which features to reason from at each decision step, enabling interpretability and more efficient learning. TabNet outperforms or matches other models on various datasets while providing interpretable feature attributions and achieving excellent performance without requiring extensive preprocessing or feature engineering.",
                #         "metrics": {},
                #         "images": {
                #             "confusionMatrix": "../model/tabnet/cm.png",
                #             "rocCurve": None,
                #             "accLoss": "../model/tabnet/acc_loss_epoch.png",
                #         },
                #     },
                # ]
                # rfMetricsPath = './new-test/model/RF/metric_results.json'
                # xgbMetricsPath = './new-test/model/xgb/metric_results.json'
                # tabMetricsPath = './new-test/model/tab/metric_results.json'
                
                # with open(rfMetricsPath, "r", encoding="utf-8") as f:
                #     rfMetrics = json.load(f)
                    
                # with open(xgbMetricsPath, "r", encoding="utf-8") as f:
                #     xgbMetrics = json.load(f)
                # with open(tabMetricsPath, "r", encoding="utf-8") as f:
                #     tabMetrics = json.load(f)
                    
                # self.agent.MODELS[0].update({"metrics":rfMetrics})
                # self.agent.MODELS[1].update('"metrics":xgbMetrics')
                # self.agent.MODELS[2].update('"metrics":tabMetrics')
                
                # print(self.agent.MODELS)
                
    async def setup(self):
        self.web.add_get("/dashboard",self.handle_request,template="new-test/data/dashboard.html",)
        self.web.start(port=10001, templates_path="data")

        self.web.add_get("/list", self.handle_request, template="new-test/data/list.html")
        self.web.start(port=10000)
        
        self.web.add_get("/models", self.handle_request, template="new-test/data/models.html")
        self.web.start(port=10002)
        

        print(50 * "-")
        print("Dashboard web server started at http://localhost:10000/dashboard")
        print(50 * "-")

        b = self.DashboardBehaviour()
        self.add_behaviour(b)
        print(f"DashboardAgent {self.jid} started")

    async def launch_controller(self, request):
        return {"result": "Agents works"}

    async def handle_request(self, request, att_types=ATT_TYPES, time=SERVER_START,att_over_time = ATT_OVER_TIME, protocol_usage=PROTOCOL_USAGE):
        # Data times
        now = datetime.datetime.now()
        elapsed = now - time  # timedelta
        total_seconds = int(elapsed.total_seconds())
        elapsed_time = self.to_minutes_seconds(total_seconds)
        time = time.strftime("%d/%m/%Y %H:%M:%S")
               
        return {
            "results": self.results, # Rows of trafic
            "server_start_time":time,
            "elapsed_time":elapsed_time,
            "attacks":att_types, #Attacks per type presented in pie chart
            "attacks_per_time":att_over_time,
            "protocol_usage":protocol_usage,
            "models":self.MODELS
            }

    def add_result(self, result):
        self.results.append(result)

    def to_minutes_seconds(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

