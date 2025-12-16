# Standings Query Improvements

## Summary
Updated the standings system to properly handle queries like "Are the Oklahoma City Thunder still in the top 3 of the West?" with ESPN API as primary source and comprehensive validation.

## Key Improvements

### 1. Added ESPN API Standings Support
- **Location**: `services/direct_espn_fetcher.py`
- **New Method**: `get_standings(conference: str = None)`
- **Features**:
  - Fetches standings from ESPN API with conference information
  - Handles East/West conference filtering
  - Calculates conference rankings if not provided
  - Returns structured data with team name, wins, losses, win percentage, and conference rank

### 2. Updated Standings Agent
- **Location**: `agents/standings_agent.py`
- **Changes**:
  - Now uses ESPN API as PRIMARY source for standings
  - Falls back to NBA API Library if ESPN fails
  - Improved team name matching for "Oklahoma City Thunder" and variations
  - Automatic conference detection based on team name
  - Enhanced validation of standings data

### 3. Enhanced Validation
- **Conference Rank Validation**: Ensures rank is between 1-15
- **Win/Loss Validation**: Validates wins and losses are non-negative
- **Rank Recalculation**: Automatically recalculates rank if invalid
- **Data Consistency**: Validates that `is_in_top` matches actual rank vs target position

### 4. Improved Team Name Matching
- Handles full team names: "Oklahoma City Thunder"
- Handles abbreviations: "OKC"
- Handles common names: "Thunder"
- Works for all 30 NBA teams

### 5. Response Formatter Updates
- **Location**: `agents/response_formatter_agent.py`
- **Changes**:
  - Uses validated data from intent_data first
  - Properly formats "Yes/No" responses for top N queries
  - Includes rank, record, and win percentage in response

## Query Flow

```
User Query: "Are the Oklahoma City Thunder still in the top 3 of the West?"
    ↓
1. Standings Agent detects team_position_query
    ↓
2. Extracts: team="thunder", position=3, conference="West"
    ↓
3. Tries ESPN API first (PRIMARY)
    ↓
4. Falls back to NBA API Library if needed
    ↓
5. Finds Thunder in Western Conference standings
    ↓
6. Validates data (rank, wins, losses)
    ↓
7. Determines: is_in_top = (actual_rank <= 3)
    ↓
8. Response Formatter creates answer
    ↓
9. Final Answer: "Yes/No, the Oklahoma City Thunder are currently in/not in the top 3..."
```

## Example Response

**If Thunder is ranked 2nd:**
> "Yes, the Oklahoma City Thunder are currently in the top 3 of the Western Conference. They are ranked 2nd with a record of 45-20 (0.692 win percentage)."

**If Thunder is ranked 5th:**
> "No, the Oklahoma City Thunder are not in the top 3 of the Western Conference. They are currently ranked 5th with a record of 40-25 (0.615 win percentage)."

## Testing

Created `validate_standings_query.py` to test:
- ESPN API direct access
- NBA API Library fallback
- Standings Agent processing
- Full pipeline (Agent + Response Formatter)
- Data validation

## API Priority Order

1. **ESPN API** (`DirectESPNFetcher.get_standings()`) - PRIMARY
2. **NBA API Library** (`NBAAPILibrary.get_standings()`) - FALLBACK
3. **Database** - LAST RESORT

## Supported Query Types

- "Are the [Team] still in the top [N] of the [Conference]?"
- "Is [Team] in the top [N]?"
- "Are the [Team] in the top [N] of the West/East?"
- Works with all 30 NBA teams
- Handles conference detection automatically

