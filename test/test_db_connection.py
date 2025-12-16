"""Quick test for database connection"""
from database.db_connection import db

try:
    db.connect()
    result = db.execute_query('SELECT COUNT(*) as count FROM teams')
    print(f'✅ Database connection successful! Found {result[0]["count"]} teams.')
    
    # Test a few more queries
    players = db.execute_query('SELECT COUNT(*) as count FROM players')
    matches = db.execute_query('SELECT COUNT(*) as count FROM matches')
    print(f'✅ Found {players[0]["count"]} players and {matches[0]["count"]} matches.')
    
except Exception as e:
    print(f'❌ Database connection failed: {e}')

