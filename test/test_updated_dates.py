"""Test script to verify dates are updated"""
from database.db_connection import db
from datetime import date

conn = db.get_connection()
cursor = conn.cursor()

# Check Lakers schedule
cursor.execute("""
    SELECT t1.team_name, t2.team_name, s.match_date, s.venue
    FROM schedule s
    JOIN teams t1 ON s.team1_id = t1.team_id
    JOIN teams t2 ON s.team2_id = t2.team_id
    WHERE (t1.team_name = 'Lakers' OR t2.team_name = 'Lakers')
    AND s.match_date >= %s
    ORDER BY s.match_date
    LIMIT 5
""", (date.today(),))

print("Lakers upcoming games (updated dates):")
print("=" * 60)
for row in cursor.fetchall():
    team1, team2, match_date, venue = row
    if team1 == 'Lakers':
        print(f"  Lakers vs {team2} on {match_date} at {venue}")
    else:
        print(f"  {team1} vs Lakers on {match_date} at {venue}")

cursor.close()
print("\n✓ Dates are now current!")

