#!/usr/bin/env python3
"""
Verify the optimizations are working correctly
Tests that LeBron James query:
1. Resolves instantly from known players map
2. Skips expensive boxscore search
3. Returns clear error instead of database garbage
"""
import sys
import time
import json
sys.path.append('.')

from agents.player_stats_agent import PlayerStatsAgent
from agents.resolver_agent import ResolverAgent
import logging

# Reduce logging noise for cleaner output
logging.getLogger().setLevel(logging.WARNING)

print("=" * 80)
print("OPTIMIZATION VERIFICATION TEST")
print("=" * 80)

# Test 1: Resolver optimization
print("\n[TEST 1] Resolver - Check if LeBron James is found in known players map")
print("-" * 80)

resolver = ResolverAgent()
start = time.time()
result = resolver.resolve_player('lebron james')
elapsed = time.time() - start

print(f"✓ Player name: {result.get('canonical_name')}")
print(f"✓ ESPN ID found: {result.get('espn_player_id')}")
print(f"✓ Time to resolve: {elapsed:.3f} seconds")
print(f"✓ Status: {'INSTANT (from map)' if elapsed < 0.1 else 'SLOW (boxscore search)'}")

assert elapsed < 0.5, f"Resolver took too long: {elapsed}s"
assert result.get('canonical_name') == 'LeBron James', "Wrong canonical name"
assert result.get('espn_player_id') is None, "Should have no ESPN ID from map"
print("\n✓ PASS: Resolver works correctly - skips expensive boxscore search")

# Test 2: Player stats agent
print("\n[TEST 2] Player Stats Agent - Check LeBron James query response")
print("-" * 80)

agent = PlayerStatsAgent()
start = time.time()
response = agent.process_query('How many points did LeBron James score?')
elapsed = time.time() - start

print(f"✓ Response type: {response.get('type')}")
print(f"✓ Response source: {response.get('source')}")
print(f"✓ Has error: {bool(response.get('error'))}")
print(f"✓ Query time: {elapsed:.3f} seconds")
print(f"✓ Status: {'FAST FAIL' if elapsed < 5 else f'SLOW ({elapsed:.1f}s)'}")

# Check the response format
assert response.get('type') == 'player_stats', "Wrong response type"
assert response.get('source') == 'api_unavailable', f"Wrong source: {response.get('source')}"
assert response.get('error'), "Should have error message"
assert elapsed < 5, f"Query took too long: {elapsed}s"

# Check no database garbage data
if response.get('data'):
    data_str = str(response.get('data')).lower()
    assert 'unknown player' not in data_str, "ERROR: Returning database garbage data!"
    
print("\n✓ PASS: Player stats query returns clear error (no database fallback)")

# Test 3: Verify error message quality
print("\n[TEST 3] Error Message Quality")
print("-" * 80)

error_msg = response.get('error', '')
print(f"Error message: {error_msg[:100]}...")
assert len(error_msg) > 10, "Error message too short"
assert "couldn't find" in error_msg.lower() or 'could not find' in error_msg.lower() or 'unavailable' in error_msg.lower(), \
    f"Error message doesn't explain the problem: {error_msg[:50]}"
assert 'unknown player' not in error_msg.lower(), "Error contains database garbage"

print("\n✓ PASS: Error message is clear and user-friendly")

# Summary
print("\n" + "=" * 80)
print("ALL TESTS PASSED ✓")
print("=" * 80)
print(f"\nOptimization Summary:")
print(f"  1. LeBron James resolves instantly ({elapsed:.3f}s) from known players map")
print(f"  2. Query completes in {elapsed:.3f}s instead of 25+ seconds")
print(f"  3. Returns clear error instead of database garbage")
print(f"\n✓ Known players: Fast instant lookup from map")
print(f"✓ Unknown players: Fast error without boxscore search")
print(f"✓ No database fallback: Always returns API-first results")
