"""Final validation - verify correct answer format"""
from agents.stats_agent import StatsAgent
from agents.response_formatter_agent import ResponseFormatterAgent

question = "Did the New York Knicks win their most recent game?"
print(f"\nQuery: {question}\n")

agent = StatsAgent()
result = agent.process_query(question)

if result and result.get('win_query') and not result.get('error'):
    formatter = ResponseFormatterAgent()
    answer = formatter.format_response(result)
    
    print(f"✅ Final Answer:")
    print(f"   {answer}\n")
    
    # Validate
    checks = {
        'Starts with Yes/No': answer.startswith('Yes.') or answer.startswith('No.'),
        'Contains full team name': 'New York Knicks' in answer or 'Knicks' in answer,
        'Contains opponent': result.get('opponent_name', '') in answer,
        'Contains scores': str(result.get('team_score')) in answer and str(result.get('opponent_score')) in answer,
        'Correct format': 'most recent game' in answer.lower() and 'with a final score of' in answer.lower()
    }
    
    print("Validation:")
    all_pass = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
        if not passed:
            all_pass = False
    
    if all_pass:
        print("\n🎉 VALIDATION PASSED - Answer is correct!")
    else:
        print("\n⚠️  Some checks failed")
else:
    print(f"❌ Error: {result.get('error') if result else 'No result'}")

