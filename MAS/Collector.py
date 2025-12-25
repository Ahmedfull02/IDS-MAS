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
# How long to wait for all agents before forcing a result (in seconds)
MAX_WAIT_SECONDS = 10 

class CollectorAgent(Agent):
    class ReceiveBehaviour(CyclicBehaviour):
        async def on_start(self):
            self.received = []
            # Structure: { "data_id": { ...data..., "seen": datetime } }
            self.pending_data = {}
            
            self.output_dir = "collected_data"
            os.makedirs(self.output_dir, exist_ok=True)
            print("[Collector] started and waiting for messages...")
        async def run(self):
            # 1. Check for timeouts at the start of every cycle
            await self.check_timeouts()

            # 2. Wait for messages
            msg = await self.receive(timeout=1) # Reduced timeout to check for internal timeouts more often
            
            if msg:
                try:
                    data = json.loads(msg.body)
                    data_id = data.get("id")
                    
                    print(f"[Collector] Received from {msg.sender} for ID {data_id}")
                    
                    # Update pending data
                    if data_id not in self.pending_data:
                        self.pending_data[data_id] = data.copy()
                        # Stamp the arrival time of the first piece of data for this ID
                        self.pending_data[data_id]["seen"] = datetime.datetime.now()
                    else:
                        self.pending_data[data_id].update(data)
                    
                    merged_data = self.pending_data[data_id]
                    
                    # Check if we have ALL predictions
                    has_all_predictions = (
                        "TABPred" in merged_data and 
                        "RFPred" in merged_data and 
                        "GBPred" in merged_data
                    )
                    
                    if has_all_predictions:
                        await self.process_and_send(data_id, merged_data)
                    else:
                        # Log what is missing
                        missing = []
                        if "TABPred" not in merged_data: missing.append("TABPred")
                        if "RFPred" not in merged_data: missing.append("RFPred")
                        if "GBPred" not in merged_data: missing.append("GBPred")
                        print(f"[Collector] Waiting for predictions for {data_id}: {', '.join(missing)}")
                                        
                    self.received.append((str(msg.sender), data_id))
                    
                except json.JSONDecodeError as e:
                    print(f"[Collector] Error parsing JSON: {e}")
                except Exception as e:
                    print(f"[Collector] Error processing message: {e}")
            else:
                
                pass
        async def process_and_send(self, data_id, merged_data):
            # Remove the timestamp marker so it isn't sent to dashboard
            if "seen" in merged_data:
                del merged_data["seen"]

            # Safe get for predictions (defaults to 'N/A' if agent was down)
            tab_pred = merged_data.get('TABPred', 'N/A')
            rf_pred = merged_data.get('RFPred', 'N/A')
            gb_pred = merged_data.get('GBPred', 'N/A')
            
            # BENIGN LOGIC:
            # We treat 'N/A' as neutral/benign for the sake of the 'all benign' check
            benign_indicators = ('BENIGN', 'None detected', 'N/A')
            
            if tab_pred in benign_indicators and rf_pred in benign_indicators and gb_pred in benign_indicators:
                merged_data['Label'] = 'BENIGN'
            else:
                predictions = [tab_pred, rf_pred, gb_pred]
                # Filter out BENIGN and N/A to count actual votes
                non_benign = [p for p in predictions if p not in benign_indicators]
                
                if len(non_benign) > 0:
                    from collections import Counter
                    attack_counts = Counter(non_benign)
                    merged_data['Label'] = attack_counts.most_common(1)[0][0]
                else:
                    # If we only had "N/A" and "BENIGN" mixed but didn't trigger the first check
                    merged_data['Label'] = 'BENIGN'

            # --- Serialize and Send ---
            combined_json = json.dumps(merged_data, ensure_ascii=False, separators=(',', ':'))
            
            dashboard_msg = Message(to=DASHBOARD_AGENT)
            dashboard_msg.body = combined_json
            await self.send(dashboard_msg)
            
            print(f"[Collector] ✓ Processed ID: {data_id} (Reason: {'COMPLETE' if 'TABPred' in merged_data and 'RFPred' in merged_data and 'GBPred' in merged_data else 'PARTIAL/TIMEOUT'})")
            print(f"[Collector] Label: {merged_data.get('Label')} - TAB: {tab_pred}, RF: {rf_pred}, GB: {gb_pred}")
            
            # --- Save to File ---
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/combined_data_{data_id}_{timestamp}.json"
            
            # Write and then Delete
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(combined_json)
            
            try:
                os.remove(filename)
            except OSError as e:
                print(f"[Collector] Error removing file {filename}: {e}")
            
            # --- Cleanup Memory ---
            if data_id in self.pending_data:
                del self.pending_data[data_id]

        async def check_timeouts(self):
            now = datetime.datetime.now()
            # Create a list of IDs to process to avoid modifying dict while iterating
            timed_out_ids = []
            
            for data_id, data in self.pending_data.items():
                first_seen = data.get("seen")
                if first_seen and (now - first_seen) > timedelta(seconds=MAX_WAIT_SECONDS):
                    timed_out_ids.append(data_id)
            
            for data_id in timed_out_ids:
                print(f"[Collector] ID {data_id} timed out. Processing partial data.")
                await self.process_and_send(data_id, self.pending_data[data_id])

        

    async def setup(self):
        b = self.ReceiveBehaviour()
        self.add_behaviour(b)
        print(f"\n\n\nCollector Agent {self.jid} started.\n\n\n")