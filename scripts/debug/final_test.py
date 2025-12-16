#!/usr/bin/env python3
"""Final comprehensive test of optimizations"""
import sys
sys.path.append('.')
from agents.player_stats_agent import PlayerStatsAgent
import time

print("=" * 80)
print("FINAL COMPREHENSIVE TEST")
print("=" * 80)

agent = PlayerStatsAgent()

# Test 1: LeBron James (known player, should fail fast)
print("\n[1] Testing LeBron James (known player - should fail fast)...")
start = time.time()
result = agent.process_query("How many points did LeBron James score?")
t1 = time.time() - start
print(f"    Time: {t1:.2f}s")
print(f"    Source: {result.get('source')}")
print(f"    Has error: {'error' in result}")
assert result.get('source') == 'api_unavailable', f"Expected api_unavailable, got {result.get('source')}"
assert t1 < 5, f"Expected < 5s, got {t1}s"
print("    ✓ PASS")

# Test 2: Nikola Jokic (known player, triple-double query)
print("\n[2] Testing Nikola Jokic triple-double (should return error quickly)...")
start = time.time()
result = agent.process_query("How many triple-doubles does Nikola Jokic have?")
t2 = time.time() - start
print(f"    Time: {t2:.2f}s")
print(f"    Source: {result.get('source')}")
print(f"    Has error: {'error' in result}")
assert result.get('source') == 'api_unavailable', f"Expected api_unavailable, got {result.get('source')}"
assert t2 < 15, f"Expected < 15s, got {t2}s"
print("    ✓ PASS")

# Test 3: Unknown player (should fail fast with error)
print("\n[3] Testing unknown player (should fail immediately)...")
start = time.time()
result = agent.process_query("How many points did Zxcvbnm Qwerty score?")
t3 = time.time() - start
print(f"    Time: {t3:.2f}s")
print(f"    Source: {result.get('source')}")
print(f"    Has error: {'error' in result}")
assert result.get('source') == 'player_not_resolved' or 'error' in result, "Expected error for unknown player"
assert t3 < 2, f"Expected < 2s for unknown player, got {t3}s"
print("    ✓ PASS")

print("\n" + "=" * 80)
print("ALL TESTS PASSED")
print("=" * 80)
print(f"\nPerformance Summary:")
print(f"  LeBron James (known):     {t1:.2f}s ✓")
print(f"  Nikola Jokic (known):     {t2:.2f}s ✓")
print(f"  Unknown player:           {t3:.2f}s ✓")
print(f"\n✓ All queries fail fast with clear errors (no database fallback)")
print(f"✓ Known players resolve instantly from map")
print(f"✓ Unknown players return error without expensive search")

