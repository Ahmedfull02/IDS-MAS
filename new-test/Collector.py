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

# Dashboard agent JID
DASHBOARD_AGENT = "agent7@localhost"

class CollectorAgent(Agent):
    class ReceiveBehaviour(CyclicBehaviour):
        async def on_start(self):
                self.received = []
                # Dictionary to store messages by ID for merging
                self.pending_data = {}
                # Output file path
                self.output_dir = "collected_data"
                os.makedirs(self.output_dir, exist_ok=True)
                print("[Collector] started and waiting for messages...")

        async def run(self):
            # Wait up to 30 seconds for a message
            msg = await self.receive(timeout=2)
            if msg:
                try:
                    data = json.loads(msg.body)
                    data_id = data.get("id")
                    
                    print(f"[Collector] Received from {msg.sender} for ID {data_id}")
                    
                    # Initialize or update the merged data for this ID
                    if data_id not in self.pending_data:
                        self.pending_data[data_id] = data.copy()
                    else:
                        # Merge predictions from this message into existing data
                        self.pending_data[data_id].update(data)
                    
                    # Check if we have all three predictions (TABPred, RFPred, GBPred)
                    merged_data = self.pending_data[data_id]
                    has_all_predictions = (
                        "TABPred" in merged_data and 
                        "RFPred" in merged_data and 
                        "GBPred" in merged_data
                    )
                    
                    if has_all_predictions:
                        # Determine Label: if all predictions are BENIGN, set to BENIGN, else Attack
                        tab_pred = merged_data.get('TABPred', '')
                        rf_pred = merged_data.get('RFPred', '')
                        gb_pred = merged_data.get('GBPred', '')
                        
                        if tab_pred == 'BENIGN' and rf_pred == 'BENIGN' and gb_pred == 'BENIGN':
                            merged_data['Label'] = 'BENIGN'
                        else:
                            # Use the actual attack type from predictions
                            # Priority: if all three agree, use that; if two agree, use majority; otherwise use first non-BENIGN
                            predictions = [tab_pred, rf_pred, gb_pred]
                            non_benign = [p for p in predictions if p != 'BENIGN']
                            
                            if len(non_benign) > 0:
                                # Count occurrences of each attack type
                                from collections import Counter
                                attack_counts = Counter(non_benign)
                                # Get the most common attack type
                                merged_data['Label'] = attack_counts.most_common(1)[0][0]
                            else:
                                # Fallback (shouldn't happen given the else condition)
                                merged_data['Label'] = 'Attack'
                        
                        # All predictions received, format as single-line JSON and send to Dashboard
                        # Format as compact JSON (single line, no indentation)
                        combined_json = json.dumps(merged_data, ensure_ascii=False, separators=(',', ':'))
                        
                        # Send to Dashboard agent
                        dashboard_msg = Message(to=DASHBOARD_AGENT)
                        dashboard_msg.body = combined_json
                        await self.send(dashboard_msg)
                        
                        print(f"[Collector] ✓ Combined data sent to Dashboard (ID: {data_id})")
                        print(f"[Collector] Label: {merged_data.get('Label')} - TAB: {tab_pred}, RF: {rf_pred}, GB: {gb_pred}")
                        
                        # Also save to file for backup
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{self.output_dir}/combined_data_{data_id}_{timestamp}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(combined_json)
                        print(f"[Collector] Data also saved to {filename}")
                        
                        # Remove the file after it's been created and sent
                        try:
                            os.remove(filename)
                            print(f"[Collector] File {filename} removed after processing")
                        except OSError as e:
                            print(f"[Collector] Error removing file {filename}: {e}")
                        
                        # Remove from pending after sending
                        del self.pending_data[data_id]
                    else:
                        missing = []
                        if "TABPred" not in merged_data:
                            missing.append("TABPred")
                        if "RFPred" not in merged_data:
                            missing.append("RFPred")
                        if "GBPred" not in merged_data:
                            missing.append("GBPred")
                        print(f"[Collector] Waiting for predictions: {', '.join(missing)}")
                    
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