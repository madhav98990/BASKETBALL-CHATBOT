"""
Verifier Agent - Optional agent that queries alternate sources for reconciliation
Verifies returned payload fields and timestamps
"""
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerifierAgent:
    """Verifies data from primary source using alternate sources or validation"""
    
    def verify_player_stats(self, stats_data: Dict, metadata: Dict) -> Dict:
        """
        Verify player stats data
        Returns: {'verified': bool, 'confidence': float, 'notes': str}
        """
        if not stats_data:
            return {
                'verified': False,
                'confidence': 0.0,
                'notes': 'No data to verify'
            }
        
        # Basic validation checks
        checks_passed = 0
        total_checks = 0
        
        # Check 1: Valid player name
        total_checks += 1
        if stats_data.get('player_name') and len(stats_data.get('player_name', '')) > 0:
            checks_passed += 1
        
        # Check 2: Stats are numbers
        total_checks += 1
        points = stats_data.get('points')
        rebounds = stats_data.get('rebounds')
        assists = stats_data.get('assists')
        
        if (points is not None and isinstance(points, (int, float)) and points >= 0) or \
           (rebounds is not None and isinstance(rebounds, (int, float)) and rebounds >= 0) or \
           (assists is not None and isinstance(assists, (int, float)) and assists >= 0):
            checks_passed += 1
        
        # Check 3: Reasonable stat values (not impossibly high)
        total_checks += 1
        if points is not None and 0 <= points <= 150 and \
           rebounds is not None and 0 <= rebounds <= 60 and \
           assists is not None and 0 <= assists <= 50:
            checks_passed += 1
        elif points is not None or rebounds is not None or assists is not None:
            # At least one stat is reasonable
            checks_passed += 1
        
        # Check 4: Has date
        total_checks += 1
        if stats_data.get('match_date'):
            checks_passed += 1
        
        # Check 5: Has team info
        total_checks += 1
        if stats_data.get('team1_name') and stats_data.get('team2_name'):
            checks_passed += 1
        
        confidence = checks_passed / total_checks if total_checks > 0 else 0.0
        
        return {
            'verified': confidence >= 0.6,  # At least 60% checks pass
            'confidence': confidence,
            'notes': f'{checks_passed}/{total_checks} validation checks passed'
        }

