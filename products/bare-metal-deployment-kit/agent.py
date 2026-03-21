#!/usr/bin/env python3
"""
Encrypted Monitoring Agent
Sends encrypted status updates about compilation activities.
Can run as daemon or one-shot.
"""

import os
import sys
import time
import json
import socket
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class EncryptedAgent:
 """Lightweight daemon that reports system activity"""

 def __init__(self, config_path: str = "agent_config.json"):
 self.config = self._load_config(config_path)
 self.running = False
 self.thread = None
 self.status_file = Path("agent_status.json")
 self.log_file = Path("agent_log.jsonl")

 def _load_config(self, path: str) -> Dict[str, Any]:
 """Load agent configuration"""
 default = {
 "report_interval": 60,  # seconds
 "log_compilation": True,
 "encrypt_reports": True,
 "daemonize": False,
 "status_dir": "./.agent"
 }
 try:
 if Path(path).exists():
 with open(path) as f:
 user_cfg = json.load(f)
 default.update(user_cfg)
 except Exception:
 pass
 return default

 def start(self) -> None:
 """Start agent as daemon or foreground"""
 if self.config['daemonize']:
 self._daemonize()
 self._run_loop()
 else:
 # Foreground with keyboard interrupt handling
 try:
 self._run_loop()
 except KeyboardInterrupt:
 self.stop()

 def _daemonize(self) -> None:
 """Fork into background (Unix only)"""
 try:
 pid = os.fork()
 if pid > 0:
 # Parent exits
 sys.exit(0)
 except OSError as e:
 print(f"Failed to daemonize: {e}")
 sys.exit(1)

 # Child becomes session leader
 os.setsid()
 # Second fork to prevent reacquiring terminal
 try:
 pid = os.fork()
 if pid > 0:
 sys.exit(0)
 except OSError:
 sys.exit(1)

 # Now we're a proper daemon
 sys.stdout.flush()
 sys.stderr.flush()
 with open('/dev/null', 'rb', 0) as f:
 os.dup2(f.fileno(), sys.stdin.fileno())
 with open('/dev/null', 'ab', 0) as f:
 os.dup2(f.fileno(), sys.stdout.fileno())
 os.dup2(f.fileno(), sys.stderr.fileno())

 def _run_loop(self) -> None:
 """Main agent loop"""
 self.running = True
 self._write_status("starting", {"pid": os.getpid()})

 while self.running:
 try:
 self._collect_and_report()
 time.sleep(self.config['report_interval'])
 except Exception as e:
 self._write_status("error", {"error": str(e)})
 time.sleep(10)  # retry delay

 def _collect_and_report(self) -> None:
 """Gather system info and send report"""
 data = {
 "timestamp": datetime.utcnow().isoformat() + "Z",
 "agent_version": "1.0",
 "hostname": socket.gethostname(),
 "activities": self._scan_activity()
 }

 if self.config['encrypt_reports']:
 data = self._encrypt_data(data)

 self._write_status("active", data)
 self._write_log(data)

 def _scan_activity(self) -> List[Dict[str, Any]]:
 """Scan for recent compilation/link activity"""
 activities = []
 output_dir = Path("output")

 if output_dir.exists():
 for file in output_dir.glob("*"):
 if file.stat().st_mtime > time.time() - 3600:  # last hour
 activities.append({
 "type": "compilation_output",
 "file": str(file),
 "size": file.stat().st_size,
 "mtime": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
 })

 return activities

 def _encrypt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
 """Simple XOR obfuscation (NOT cryptographic)"""
 # In a real agent, use proper encryption (libsodium, age)
 json_str = json.dumps(data)
 # Simple rotation cipher for demo
 encrypted = ''.join(chr(ord(c) + 1) for c in json_str)
 return {
 "encrypted": True,
 "payload": encrypted,
 "method": "rot1_demo"
 }

 def _write_status(self, state: str, data: Dict[str, Any]) -> None:
 """Write current status to file"""
 self.config['status_dir'] = Path(self.config['status_dir'])
 self.config['status_dir'].mkdir(exist_ok=True)
 status_path = self.config['status_dir'] / "status.json"
 status = {
 "state": state,
 "last_update": datetime.utcnow().isoformat() + "Z",
 "data": data
 }
 with open(status_path, 'w') as f:
 json.dump(status, f, indent=2)

 def _write_log(self, data: Dict[str, Any]) -> None:
 """Append to JSONL log"""
 with open(self.log_file, 'a') as f:
 f.write(json.dumps(data) + '\n')

 def stop(self) -> None:
 """Stop agent gracefully"""
 self.running = False
 self._write_status("stopped", {"pid": os.getpid()})


def main():
 """CLI entry point"""
 import argparse

 parser = argparse.ArgumentParser(description="Encrypted Monitoring Agent")
 parser.add_argument("--daemon", action="store_true", help="Run as daemon")
 parser.add_argument("--status", action="store_true", help="Show current status")
 parser.add_argument("--stop", action="store_true", help="Stop running agent")
 parser.add_argument("--config", default="agent_config.json", help="Config file path")
 args = parser.parse_args()

 agent = EncryptedAgent(args.config)

 if args.status:
 status_path = Path(".agent/status.json")
 if status_path.exists():
 with open(status_path) as f:
 print(json.dumps(json.load(f), indent=2))
 else:
 print("Agent not running or no status file")
 sys.exit(0)

 if args.stop:
 # Simple stop: write stopped status (would need PID tracking for real kill)
 agent.stop()
 print("Agent stopped")
 sys.exit(0)

 # Start agent
 if args.daemon:
 agent.config['daemonize'] = True

 print("🔐 Encrypted Monitoring Agent v1.0")
 print(f"PID: {os.getpid()}")
 print(f"Config: {args.config}")
 print("Press Ctrl+C to stop (if running in foreground)")
 print()

 agent.start()


if __name__ == "__main__":
 main()
