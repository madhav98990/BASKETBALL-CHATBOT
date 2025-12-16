"""
Update database dates to current dates
Updates match dates to recent past and schedule dates to upcoming future
"""
import sys
import os
from datetime import datetime, timedelta, date
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import db

def update_dates():
    """Update all dates in the database to be current"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        today = datetime.now().date()
        
        # NBA 2025-26 season: October 2025 to April 2026
        season_start = date(2025, 10, 1)  # Season typically starts in October
        season_end = date(2026, 4, 30)   # Regular season ends in April
        
        # Ensure we're within season dates
        if today < season_start:
            # If before season start, use season start as reference
            reference_date = season_start
        elif today > season_end:
            # If after season end, use season end as reference
            reference_date = season_end
        else:
            reference_date = today
        
        # Update match dates - set to current season (past dates within season)
        print("Updating match dates to current 2025-26 season (past games)...")
        cursor.execute("SELECT match_id, match_date FROM matches ORDER BY match_id")
        matches = cursor.fetchall()
        
        for match_id, old_date in matches:
            # Random date in the season, but in the past (between season start and today)
            if reference_date > season_start:
                days_in_season = (reference_date - season_start).days
                days_ago = random.randint(1, min(days_in_season, 90))  # Last 90 days or season length
                new_date = reference_date - timedelta(days=days_ago)
                # Ensure date is within season
                if new_date < season_start:
                    new_date = season_start + timedelta(days=random.randint(1, 30))
            else:
                new_date = season_start + timedelta(days=random.randint(1, 30))
            
            cursor.execute(
                "UPDATE matches SET match_date = %s WHERE match_id = %s",
                (new_date, match_id)
            )
        
        print(f"Updated {len(matches)} match dates to 2025-26 season")
        
        # Update schedule dates - set to future dates within current season
        print("Updating schedule dates to upcoming games in 2025-26 season...")
        cursor.execute("SELECT schedule_id, match_date FROM schedule ORDER BY schedule_id")
        schedules = cursor.fetchall()
        
        for schedule_id, old_date in schedules:
            # Random date in the future, but within season (next 7-180 days, capped at season end)
            if today < season_end:
                days_ahead = random.randint(7, min(180, (season_end - today).days))
                new_date = today + timedelta(days=days_ahead)
                # Ensure date doesn't exceed season end
                if new_date > season_end:
                    new_date = season_end - timedelta(days=random.randint(1, 7))
            else:
                # If past season end, set to near season end
                new_date = season_end - timedelta(days=random.randint(1, 7))
            
            cursor.execute(
                "UPDATE schedule SET match_date = %s WHERE schedule_id = %s",
                (new_date, schedule_id)
            )
        
        print(f"Updated {len(schedules)} schedule dates to 2025-26 season")
        
        # Commit changes
        conn.commit()
        print("\n✓ All dates updated successfully!")
        print(f"  - Season: 2025-26 NBA Season (Oct 2025 - Apr 2026)")
        print(f"  - Match dates: Past games within current season (ending {reference_date})")
        print(f"  - Schedule dates: Upcoming games within current season (starting {today + timedelta(days=7)})")
        
        # Show some examples
        print("\nExample upcoming games:")
        cursor.execute("""
            SELECT t1.team_name, t2.team_name, s.match_date, s.venue
            FROM schedule s
            JOIN teams t1 ON s.team1_id = t1.team_id
            JOIN teams t2 ON s.team2_id = t2.team_id
            WHERE s.match_date >= %s
            ORDER BY s.match_date
            LIMIT 5
        """, (today,))
        
        for row in cursor.fetchall():
            print(f"  - {row[0]} vs {row[1]} on {row[2]} at {row[3]}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating dates: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Updating Database Dates to Current Dates")
    print("=" * 60)
    print()
    update_dates()

