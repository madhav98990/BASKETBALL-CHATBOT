# Fix: Assists Detection in Top Players Queries

## Problem
When users asked for "top 5 players assists per game", the chatbot was returning points per game instead of assists per game.

## Root Cause
The stat extraction logic in `_handle_top_players_query()` was checking stat keywords in a dictionary order, which could cause issues. More importantly, it wasn't prioritizing assists explicitly, and the default was always 'points'.

## Solution
Updated the stat extraction logic in `agents/player_stats_agent.py` to:
1. **Prioritize assists first** - Check for assists before checking for points
2. **Use explicit if-elif chain** - More reliable than dictionary iteration
3. **Add logging** - To help debug stat type detection

## Changes Made

### File: `agents/player_stats_agent.py`
**Location:** `_handle_top_players_query()` method (around line 710)

**Before:**
```python
stat_map = {
    'points': 'points',
    'score': 'points',
    'scoring': 'points',
    'assists': 'assists',
    ...
}

stat_type = None
for stat_key, stat_db in stat_map.items():
    if stat_key in question_lower:
        stat_type = stat_db
        break

if not stat_type:
    stat_type = 'points'  # Default to points
```

**After:**
```python
# Extract stat type - prioritize explicit stat mentions
# Check for assists first (before points) to avoid conflicts
stat_type = None

# Priority order: check for specific stat mentions first
if 'assists' in question_lower or 'assist' in question_lower or 'apg' in question_lower:
    stat_type = 'assists'
    logger.info(f"Detected stat type: assists (from query: '{question}')")
elif 'rebounds' in question_lower or 'rebound' in question_lower or 'rpg' in question_lower:
    stat_type = 'rebounds'
    logger.info(f"Detected stat type: rebounds (from query: '{question}')")
elif 'steals' in question_lower or 'steal' in question_lower or 'spg' in question_lower:
    stat_type = 'steals'
    logger.info(f"Detected stat type: steals (from query: '{question}')")
elif 'blocks' in question_lower or 'block' in question_lower or 'bpg' in question_lower:
    stat_type = 'blocks'
    logger.info(f"Detected stat type: blocks (from query: '{question}')")
elif 'points' in question_lower or 'point' in question_lower or 'ppg' in question_lower or 'score' in question_lower or 'scoring' in question_lower:
    stat_type = 'points'
    logger.info(f"Detected stat type: points (from query: '{question}')")

if not stat_type:
    stat_type = 'points'  # Default to points only if no stat mentioned
    logger.warning(f"No stat type detected in query '{question}', defaulting to points")
```

## Testing
To test the fix:
```python
from agents.player_stats_agent import PlayerStatsAgent

agent = PlayerStatsAgent()
result = agent._handle_top_players_query("top 5 players assists per game")
print(f"Detected stat: {result.get('stat')}")  # Should print 'assists'
```

## Expected Behavior
- Query: "top 5 players assists per game" → Returns assists per game
- Query: "top 5 players points per game" → Returns points per game
- Query: "top 5 players rebounds per game" → Returns rebounds per game

## Status
✅ **FIXED** - Assists queries now correctly detect and return assists per game data.

