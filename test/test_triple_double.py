#!/usr/bin/env python3
"""Quick test for triple-double query"""
import sys
sys.path.append('.')
from agents.player_stats_agent import PlayerStatsAgent
import time

agent = PlayerStatsAgent()
question = "How many triple-doubles does Nikola Jokic have?"

print("Testing triple-double query...")
start = time.time()
result = agent._handle_triple_double_query(question)
elapsed = time.time() - start

print(f"Time: {elapsed:.1f}s")
print(f"Source: {result.get('source')}")
print(f"Error: {result.get('error', 'N/A')}")
print(f"Data: {result.get('data')}")
