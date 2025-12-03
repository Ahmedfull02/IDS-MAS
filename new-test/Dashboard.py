from aiohttp import web
from spade.behaviour import CyclicBehaviour
import random
from spade.agent import Agent
from spade.message import Message
import json
import datetime
from datetime import timedelta
import os


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
                
                print(f"[Dashboard] ✓ Data processed and added to results (ID: {data.get('id', 'N/A')})")
                
    async def setup(self):
        # Initialize MODELS once during setup
        self._load_models_data()
        
        # Add static route for model images - must be done before start()
        model_path = os.path.join(os.getcwd(), 'new-test', 'model')
        if os.path.exists(model_path):
            from aiohttp import web
            self.web.app.router.add_static('/model', path=model_path, name='model_static')
            print(f"[Dashboard] Static route added for model images: /model -> {model_path}")
        else:
            print(f"[Dashboard] Warning: Model path not found: {model_path}")
        
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

    def _load_models_data(self):
        """Load models data once during setup"""
        # Load metrics and check for images
        rfMetricsPath = './new-test/model/RF/metric_results.json'
        xgbMetricsPath = './new-test/model/xgb/metric_results.json'
        tabMetricsPath = './new-test/model/tabnet/metric_results.json'
        
        # Load metrics
        rfMetrics = {}
        xgbMetrics = {}
        tabMetrics = {}
        
        def clean_metrics(metrics_dict):
            """Clean metrics by removing leading/trailing spaces from values"""
            cleaned = {}
            for key, value in metrics_dict.items():
                if isinstance(value, str):
                    cleaned[key] = value.strip()
                else:
                    cleaned[key] = value
            return cleaned
        
        try:
            with open(rfMetricsPath, "r", encoding="utf-8") as f:
                rfMetrics = clean_metrics(json.load(f))
        except Exception as e:
            print(f"[Dashboard] Error loading RF metrics: {e}")
        
        try:
            with open(xgbMetricsPath, "r", encoding="utf-8") as f:
                xgbMetrics = clean_metrics(json.load(f))
        except Exception as e:
            print(f"[Dashboard] Error loading GB metrics: {e}")
        
        try:
            with open(tabMetricsPath, "r", encoding="utf-8") as f:
                tabMetrics = clean_metrics(json.load(f))
        except Exception as e:
            print(f"[Dashboard] Error loading TabNet metrics: {e}")
        
        # Helper function to check if image exists and return web-accessible path
        def check_image_path(image_path):
            if image_path is None:
                return None
            # Convert relative path to absolute for file checking
            # Remove '../' prefix and convert to web path
            web_path = image_path.replace('../model/', '/model/')
            file_path = os.path.join('new-test', image_path.replace('../model/', 'model/'))
            if os.path.exists(file_path):
                return web_path  # Return web-accessible path
            return None
        
        # Build models data with metrics and image paths
        self.MODELS = [
            {
                "id": "rf",
                "name": "Random Forest",
                "type": "Ensemble Learning",
                "status": "Trained",
                "description": "Random Forest is an ensemble learning method that operates by constructing multiple decision trees during training and outputting the class that is the mode of the classes (classification) or mean prediction (regression) of the individual trees. It's highly effective for network intrusion detection due to its ability to handle high-dimensional data and resistance to overfitting.",
                "metrics": rfMetrics,
                "images": {
                    "confusionMatrix": check_image_path("../model/RF/cm.png"),
                    "rocCurve": check_image_path("../model/RF/roc.png"),
                    "accLoss": None,
                },
            },
            {
                "id": "gb",
                "name": "XGBoost",
                "type": "Gradient Boosting",
                "status": "Trained",
                "description": "Gradient Boosting is an ensemble learning technique that builds models sequentially by adding weak learners—typically decision trees—to correct the errors of prior models. It optimizes a chosen loss function via gradient-based methods, supports regression, classification, and ranking, and often achieves strong performance on structured/tabular data. Regularization and subsampling variants help improve generalization and prevent overfitting..",
                "metrics": xgbMetrics,
                "images": {
                    "confusionMatrix": check_image_path("../model/xgb/cm.png"),
                    "rocCurve": None,
                    "accLoss": None,
                },
            },
            {
                "id": "tabnet",
                "name": "TabNet",
                "type": "Deep Learning",
                "status": "Trained",
                "description": "TabNet is a novel deep learning architecture specifically designed for tabular data. It uses sequential attention to choose which features to reason from at each decision step, enabling interpretability and more efficient learning. TabNet outperforms or matches other models on various datasets while providing interpretable feature attributions and achieving excellent performance without requiring extensive preprocessing or feature engineering.",
                "metrics": tabMetrics,
                "images": {
                    "confusionMatrix": check_image_path("../model/tabnet/cm.png"),
                    "rocCurve": None,
                    "accLoss": check_image_path("../model/tabnet/acc_loss_epoch.png"),
                },
            },
        ]
        
        print(f"[Dashboard] Models data loaded with metrics")
        # Debug: Print image paths
        for model in self.MODELS:
            print(f"[Dashboard] {model['name']} images: {model['images']}")

    async def launch_controller(self, request):
        return {"result": "Agents works"}

    async def handle_request(self, request, att_types=None, time=None, att_over_time=None, protocol_usage=None):
        # Use instance variables instead of defaults
        if att_types is None:
            att_types = self.ATT_TYPES
        if time is None:
            time = self.SERVER_START
        if att_over_time is None:
            att_over_time = self.ATT_OVER_TIME
        if protocol_usage is None:
            protocol_usage = self.PROTOCOL_USAGE
            
        # Data times
        now = datetime.datetime.now()
        elapsed = now - time  # timedelta
        total_seconds = int(elapsed.total_seconds())
        elapsed_time = self.to_minutes_seconds(total_seconds)
        time_str = time.strftime("%d/%m/%Y %H:%M:%S")
        
        print(f"[Dashboard] Handling request - Results count: {len(self.results)}")
               
        return {
            "results": self.results, # Rows of trafic
            "server_start_time": time_str,
            "elapsed_time": elapsed_time,
            "attacks": att_types, #Attacks per type presented in pie chart
            "attacks_per_time": att_over_time,
            "protocol_usage": protocol_usage,
            "models": self.MODELS
            }

    def add_result(self, result):
        self.results.append(result)

    def to_minutes_seconds(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

