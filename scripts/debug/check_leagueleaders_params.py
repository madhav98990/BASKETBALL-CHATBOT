"""Check LeagueLeaders parameters"""
from nba_api.stats.endpoints import leagueleaders
import inspect

sig = inspect.signature(leagueleaders.LeagueLeaders)
print("LeagueLeaders Parameters:")
for name, param in sig.parameters.items():
    if name != 'self':
        default = param.default if param.default != inspect.Parameter.empty else "required"
        print(f"  {name}: {default}")

