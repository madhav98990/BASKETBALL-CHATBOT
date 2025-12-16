"""
Validation script for Jalen Brunson NBA Cup performance queries
Tests various question types to ensure accurate extraction and responses
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import BasketballChatbot

# Test questions based on the articles about Jalen Brunson and NBA Cup
test_queries = [
    # Basic performance questions
    "What did Jalen Brunson do in the NBA Cup?",
    "How did Jalen Brunson perform in the NBA Cup?",
    "Tell me about Jalen Brunson's performance in the NBA Cup",
    "What was Jalen Brunson's performance in the NBA Cup?",
    
    # Specific stat questions
    "How many points did Jalen Brunson score in the NBA Cup?",
    "What were Jalen Brunson's stats in the NBA Cup semifinal?",
    "How many points did Brunson score against Orlando Magic?",
    "What was Brunson's shooting percentage in the NBA Cup game?",
    
    # Game context questions
    "Who did the Knicks play in the NBA Cup semifinal?",
    "What was the score of the NBA Cup semifinal game?",
    "Where was the NBA Cup semifinal played?",
    "Did the Knicks win the NBA Cup semifinal?",
    
    # Achievement questions
    "Was this Brunson's first 40-point game?",
    "Did Brunson receive MVP chants?",
    "What did the coach say about Brunson's performance?",
    "Is Brunson an MVP candidate?",
    
    # Tournament questions
    "Did the Knicks advance to the NBA Cup final?",
    "Who will the Knicks play in the NBA Cup final?",
    "When is the NBA Cup final?",
    
    # Combined questions
    "What did Jalen Brunson do in the NBA Cup semifinal against Orlando?",
    "Tell me about Brunson's 40-point game in the NBA Cup",
    "How did Jalen Brunson help the Knicks reach the NBA Cup final?",
]

# Expected information that should be in responses
expected_info = {
    'points': ['40', 'forty'],
    'opponent': ['orlando', 'magic'],
    'tournament': ['nba cup', 'cup'],
    'result': ['win', 'won', '132-120'],
    'venue': ['las vegas', 't-mobile'],
    'achievements': ['40-point', 'first', 'mvp', 'final'],
    'shooting': ['16-for-27', '16 for 27'],
    'assists': ['6.3', 'assists'],
}

def validate_response(response: str, query: str) -> dict:
    """Validate response contains expected information"""
    response_lower = response.lower()
    query_lower = query.lower()
    
    validation_results = {
        'query': query,
        'response_length': len(response),
        'mentions_brunson': 'brunson' in response_lower or 'jalen' in response_lower,
        'mentions_nba_cup': any(term in response_lower for term in ['nba cup', 'cup']),
        'contains_points': any(term in response_lower for term in expected_info['points']),
        'contains_opponent': any(term in response_lower for term in expected_info['opponent']),
        'contains_result': any(term in response_lower for term in expected_info['result']),
        'contains_venue': any(term in response_lower for term in expected_info['venue']),
        'contains_achievement': any(term in response_lower for term in expected_info['achievements']),
        'contains_shooting': any(term in response_lower for term in expected_info['shooting']),
        'is_meaningful': len(response.strip()) > 50 and 'couldn\'t find' not in response_lower,
        'errors': []
    }
    
    # Check for specific query types
    if 'points' in query_lower or 'score' in query_lower:
        if not validation_results['contains_points']:
            validation_results['errors'].append('Missing points information')
    
    if 'orlando' in query_lower or 'magic' in query_lower:
        if not validation_results['contains_opponent']:
            validation_results['errors'].append('Missing opponent information')
    
    if 'cup' in query_lower or 'tournament' in query_lower:
        if not validation_results['mentions_nba_cup']:
            validation_results['errors'].append('Missing NBA Cup context')
    
    if 'mvp' in query_lower:
        if 'mvp' not in response_lower:
            validation_results['errors'].append('Missing MVP information')
    
    if 'final' in query_lower:
        if 'final' not in response_lower:
            validation_results['errors'].append('Missing final information')
    
    return validation_results

def print_validation_summary(results: list):
    """Print summary of validation results"""
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    total = len(results)
    meaningful = sum(1 for r in results if r['is_meaningful'])
    mentions_brunson = sum(1 for r in results if r['mentions_brunson'])
    mentions_cup = sum(1 for r in results if r['mentions_nba_cup'])
    has_points = sum(1 for r in results if r['contains_points'])
    has_opponent = sum(1 for r in results if r['contains_opponent'])
    has_result = sum(1 for r in results if r['contains_result'])
    has_errors = sum(1 for r in results if r['errors'])
    
    print(f"\nTotal queries tested: {total}")
    print(f"Meaningful responses: {meaningful}/{total} ({meaningful*100//total}%)")
    print(f"Mentions Brunson: {mentions_brunson}/{total} ({mentions_brunson*100//total}%)")
    print(f"Mentions NBA Cup: {mentions_cup}/{total} ({mentions_cup*100//total}%)")
    print(f"Contains points: {has_points}/{total} ({has_points*100//total}%)")
    print(f"Contains opponent: {has_opponent}/{total} ({has_opponent*100//total}%)")
    print(f"Contains result: {has_result}/{total} ({has_result*100//total}%)")
    print(f"Queries with errors: {has_errors}/{total} ({has_errors*100//total}%)")
    
    # Show queries with errors
    if has_errors > 0:
        print("\n" + "-"*80)
        print("QUERIES WITH ERRORS:")
        print("-"*80)
        for result in results:
            if result['errors']:
                print(f"\nQuery: {result['query']}")
                print(f"Errors: {', '.join(result['errors'])}")
                print(f"Response: {result.get('response', 'N/A')[:200]}...")

def main():
    """Run validation tests"""
    print("Initializing chatbot...")
    chatbot = BasketballChatbot()
    
    print(f"\nTesting {len(test_queries)} queries about Jalen Brunson's NBA Cup performance...")
    print("="*80)
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_queries)}")
        print(f"Query: {query}")
        print(f"{'='*80}")
        
        try:
            response = chatbot.process_question(query)
            print(f"\nResponse ({len(response)} chars):")
            print(response)
            
            validation = validate_response(response, query)
            validation['response'] = response
            results.append(validation)
            
            # Print validation for this query
            print(f"\nValidation:")
            print(f"  Mentions Brunson: {validation['mentions_brunson']}")
            print(f"  Mentions NBA Cup: {validation['mentions_nba_cup']}")
            print(f"  Contains points: {validation['contains_points']}")
            print(f"  Contains opponent: {validation['contains_opponent']}")
            print(f"  Contains result: {validation['contains_result']}")
            print(f"  Meaningful: {validation['is_meaningful']}")
            if validation['errors']:
                print(f"  Errors: {', '.join(validation['errors'])}")
            
        except Exception as e:
            print(f"\nERROR processing query: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'query': query,
                'response': '',
                'errors': [f'Exception: {str(e)}'],
                'is_meaningful': False
            })
    
    # Print summary
    print_validation_summary(results)
    
    # Save detailed results to file
    import json
    with open('validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to validation_results.json")

if __name__ == "__main__":
    main()

