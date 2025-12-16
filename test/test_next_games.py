"""Test script to verify 'next N games' queries work correctly"""
from agents.schedule_agent import ScheduleAgent
from agents.response_formatter_agent import ResponseFormatterAgent

def test_next_games():
    """Test that queries like 'next 10 lakers games' work correctly"""
    print("Testing 'next N games' functionality")
    print("=" * 60)
    
    schedule_agent = ScheduleAgent()
    formatter = ResponseFormatterAgent()
    
    test_queries = [
        "next 10 lakers games",
        "next 5 warriors games",
        "next 3 celtics games"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        try:
            # Test schedule agent
            result = schedule_agent.process_query(query)
            print(f"Type: {result.get('type')}")
            print(f"Source: {result.get('source')}")
            print(f"Team: {result.get('team')}")
            print(f"Number of games requested: {result.get('num_games')}")
            print(f"Games found: {len(result.get('data', []))}")
            
            if result.get('data'):
                print(f"\nFirst 3 games:")
                for i, game in enumerate(result.get('data', [])[:3], 1):
                    team1 = game.get('team1_name', 'N/A')
                    team2 = game.get('team2_name', 'N/A')
                    date = game.get('match_date', 'N/A')
                    print(f"  {i}. {team1} vs {team2} on {date}")
            
            # Test formatter
            formatted = formatter.format_response(result)
            print(f"\nFormatted response:")
            print(formatted[:500] if len(formatted) > 500 else formatted)
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_next_games()

