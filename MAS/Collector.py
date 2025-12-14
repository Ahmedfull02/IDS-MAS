from aiohttp import web
from spade.behaviour import CyclicBehaviour
import random
from spade.agent import Agent
from spade.message import Message
import json
import datetime
from datetime import timedelta
import asyncio
import os


DASHBOARD_AGENT = "agent7@localhost"

class CollectorAgent(Agent):
    class ReceiveBehaviour(CyclicBehaviour):
        async def on_start(self):
                self.received = []
                
                self.pending_data = {}
                
                self.output_dir = "collected_data"
                os.makedirs(self.output_dir, exist_ok=True)
                print("[Collector] started and waiting for messages...")

        async def run(self):
            msg = await self.receive(timeout=4)
            if msg:
                try:
                    data = json.loads(msg.body)
                    data_id = data.get("id")
                    
                    print(f"[Collector] Received from {msg.sender} for ID {data_id}")
                    
                    if data_id not in self.pending_data:
                        self.pending_data[data_id] = data.copy()
                    else:
                        self.pending_data[data_id].update(data)
                    
                    merged_data = self.pending_data[data_id]
                    has_all_predictions = (
                        "TABPred" in merged_data and 
                        "RFPred" in merged_data and 
                        "GBPred" in merged_data
                    )
                    
                    if has_all_predictions:
                        tab_pred = merged_data.get('TABPred', '')
                        rf_pred = merged_data.get('RFPred', '')
                        gb_pred = merged_data.get('GBPred', '')
                        
                        if tab_pred in ('BENIGN', 'None detected') and rf_pred in ('BENIGN', 'None detected') and gb_pred in ('BENIGN', 'None detected'):
                            merged_data['Label'] = 'BENIGN'
                        else:
                            predictions = [tab_pred, rf_pred, gb_pred]
                            non_benign = [p for p in predictions if p != 'BENIGN' ]
                            
                            if len(non_benign) > 0:
                                from collections import Counter
                                attack_counts = Counter(non_benign)
                                merged_data['Label'] = attack_counts.most_common(1)[0][0]
                            else:
                                merged_data['Label'] = 'Attack'
                        
                        combined_json = json.dumps(merged_data, ensure_ascii=False, separators=(',', ':'))
                        
                        dashboard_msg = Message(to=DASHBOARD_AGENT)
                        dashboard_msg.body = combined_json
                        await self.send(dashboard_msg)
                        
                        print(f"[Collector] ✓ Combined data sent to Dashboard (ID: {data_id})")
                        print(f"[Collector] Label: {merged_data.get('Label')} - TAB: {tab_pred}, RF: {rf_pred}, GB: {gb_pred}")
                        
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{self.output_dir}/combined_data_{data_id}_{timestamp}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(combined_json)
                        print(f"[Collector] Data also saved to {filename}")
                        
                        try:
                            os.remove(filename)
                            print(f"[Collector] File {filename} removed after processing")
                        except OSError as e:
                            print(f"[Collector] Error removing file {filename}: {e}")
                        
                        del self.pending_data[data_id]
                        await asyncio.sleep(2)

                    else:
                        missing = []
                        if "TABPred" not in merged_data:
                            missing.append("TABPred")
                        if "RFPred" not in merged_data:
                            missing.append("RFPred")
                        if "GBPred" not in merged_data:
                            missing.append("GBPred")

                        print(f"[Collector] Waiting for predictions: {', '.join(missing)}")
                        await asyncio.sleep(2)

                        # After 2 seconds, fill missing with NaN
                        for key in ["TABPred", "RFPred", "GBPred"]:
                            if key not in merged_data:
                                merged_data[key] = 'None detected'  # or 'None detected' based on your requirement

                                        
                    self.received.append((str(msg.sender), data_id))
                    print(f"[Collector] Total messages received: {len(self.received)}")
                    
                except json.JSONDecodeError as e:
                    print(f"[Collector] Error parsing JSON: {e}")
                except Exception as e:
                    print(f"[Collector] Error processing message: {e}")
            else:
                # timed out waiting for a message; keep waiting
                print("[Collector] waiting... (no message received in timeout)")

    async def setup(self):
        b = self.ReceiveBehaviour()
        self.add_behaviour(b)
        print(f"\n\n\nCollector Agent {self.jid} started.\n\n\n")