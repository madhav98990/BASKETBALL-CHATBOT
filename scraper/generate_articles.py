"""
Generate synthetic basketball articles from NBA database
This helps reach 1000 articles when scraping alone isn't sufficient
"""
import os
import sys
import random
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import db
from config import ARTICLES_DIR

# Article templates for different types
MATCH_ARTICLE_TEMPLATES = [
    """{team1} Defeat {team2} in Thrilling {score1}-{score2} Victory

In a highly anticipated matchup between the {team1} and {team2}, {team1} came out on top with a final score of {score1}-{score2}. The game was a back-and-forth battle that kept fans on the edge of their seats until the final buzzer.

{top_player} led the way for {team1}, scoring {points} points and adding {rebounds} rebounds and {assists} assists. His performance was crucial in securing the victory for his team. {team2} put up a strong fight, with {opponent_player} contributing {opponent_points} points, but it wasn't enough to overcome {team1}'s balanced attack.

The game featured several key moments, including a crucial {quarter} quarter run by {team1} that shifted the momentum in their favor. Both teams displayed excellent defensive intensity throughout the contest, making it a true showcase of NBA-level basketball.

With this win, {team1} improves their record and continues to build momentum as the season progresses. The loss is a setback for {team2}, but they showed resilience and will look to bounce back in their next matchup.""",

    """{team2} Falls Short Against {team1} in {score1}-{score2} Defeat

The {team2} couldn't overcome a strong performance from the {team1}, falling {score1}-{score2} in a hard-fought contest. Despite a valiant effort, {team2} struggled to contain {team1}'s offensive firepower throughout the game.

{top_player} was the standout performer for {team1}, putting up an impressive stat line of {points} points, {rebounds} rebounds, and {assists} assists. His ability to impact the game on both ends of the floor was evident as he made key plays down the stretch.

For {team2}, {opponent_player} tried to keep his team in the game with {opponent_points} points, but the team's overall execution wasn't enough to secure the victory. The game highlighted some areas where {team2} will need to improve as they continue through the season.

The matchup showcased the competitive nature of the NBA, with both teams fighting until the final seconds. {team1} will look to build on this performance, while {team2} will need to regroup and address their weaknesses before their next game.""",

    """{team1} Secure {score1}-{score2} Win Over {team2} Behind {top_player}'s Stellar Performance

{top_player} delivered a masterful performance, leading the {team1} to a {score1}-{score2} victory over the {team2}. The game was a testament to {top_player}'s ability to take over when his team needs him most.

Finishing with {points} points, {rebounds} rebounds, and {assists} assists, {top_player} was the driving force behind {team1}'s success. His efficiency and decision-making were on full display as he orchestrated the offense and made timely defensive plays.

The {team2} received solid contributions from {opponent_player}, who scored {opponent_points} points, but the team struggled to find consistent scoring options throughout the game. This loss will serve as a learning opportunity for {team2} as they work to improve their offensive cohesion.

The victory is significant for {team1}, demonstrating their ability to execute their game plan and come away with wins against quality opponents. As the season continues, both teams will look to build on the lessons learned from this competitive matchup."""
]

PLAYER_PERFORMANCE_TEMPLATES = [
    """{player_name} Dominates with {points} Points in {team} Victory

{player_name} put on a show for {team} fans, scoring {points} points in a commanding performance. The {position} was unstoppable, showcasing his offensive versatility and ability to score from anywhere on the court.

In addition to his scoring, {player_name} contributed {rebounds} rebounds and {assists} assists, demonstrating his all-around impact on the game. His performance was a key factor in {team}'s success, as he consistently made plays when his team needed them most.

The game highlighted {player_name}'s growth and development as a player. His ability to read defenses and make the right decisions has made him one of the most valuable players on the {team} roster. This type of performance is what makes {player_name} a standout in the league.

With performances like this, {player_name} continues to establish himself as a force to be reckoned with. His consistency and work ethic have been evident throughout the season, and this game was just another example of his commitment to excellence.""",

    """{player_name} Leads {team} with Impressive {points}-Point Outing

{player_name} was the catalyst for {team}'s success, leading the team with {points} points in a standout performance. The {position} displayed his full offensive arsenal, scoring efficiently and creating opportunities for his teammates.

Beyond scoring, {player_name} made his presence felt on the boards with {rebounds} rebounds and facilitated the offense with {assists} assists. His ability to impact multiple facets of the game makes him an invaluable asset to the {team}.

The performance showcased {player_name}'s basketball IQ and understanding of the game. He consistently made the right reads and put his team in positions to succeed. This type of leadership on the court is what separates great players from good ones.

As the season progresses, {player_name} will continue to be a key piece of {team}'s success. His ability to elevate his game when needed and make those around him better is what makes him special."""
]

TEAM_ANALYSIS_TEMPLATES = [
    """{team} Show Strong Form in Recent Stretch

The {team} have been showing impressive form in their recent games, demonstrating the depth and talent that makes them a competitive force in the league. The team's chemistry and execution have been on full display as they continue to build momentum.

Key players have stepped up when needed, and the team's coaching staff has done an excellent job of putting players in positions to succeed. The {team}'s ability to adapt and make in-game adjustments has been a significant factor in their recent success.

The team's defensive intensity has been particularly noteworthy, as they've been able to disrupt opponents' offensive flow and create transition opportunities. This commitment to defense has translated into wins and has given the team confidence moving forward.

As the season continues, the {team} will look to maintain this level of play and continue building on their strengths. The team's recent performances suggest they have the potential to be a factor as the season progresses.""",

    """{team} Face Challenges but Show Resilience

The {team} have encountered some challenges recently, but the team has shown resilience and determination in working through adversity. Despite facing obstacles, the team continues to compete hard and look for ways to improve.

The coaching staff and players have been working together to identify areas for improvement and implement solutions. This collaborative approach has been important in helping the team navigate through difficult stretches and maintain a positive outlook.

While results may not always reflect the effort, the {team} are committed to the process and believe in their ability to turn things around. The team's work ethic and dedication to improvement are evident in their approach to each game.

Moving forward, the {team} will continue to focus on execution and making incremental improvements. The team's resilience and commitment to growth will be key factors in their ability to overcome challenges and find success."""
]

def get_match_data(conn):
    """Get match data from database"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.match_id, m.match_date, m.venue,
               t1.team_name as team1_name, t2.team_name as team2_name,
               m.team1_score, m.team2_score
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        ORDER BY m.match_date DESC
        LIMIT 100
    """)
    return cursor.fetchall()

def get_player_stats_for_match(conn, match_id, team_id):
    """Get top player stats for a match"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.player_name, ps.points, ps.rebounds, ps.assists, p.position
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.player_id
        WHERE ps.match_id = %s AND p.team_id = %s
        ORDER BY ps.points DESC
        LIMIT 1
    """, (match_id, team_id))
    result = cursor.fetchone()
    if result:
        return {
            'name': result[0],
            'points': result[1],
            'rebounds': result[2],
            'assists': result[3],
            'position': result[4]
        }
    return None

def get_team_players(conn, team_id):
    """Get players for a team"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT player_name, position
        FROM players
        WHERE team_id = %s
        LIMIT 4
    """, (team_id,))
    return cursor.fetchall()

def generate_match_article(conn, match_data):
    """Generate an article about a match"""
    match_id, match_date, venue, team1, team2, score1, score2 = match_data
    
    # Get top players
    team1_id = get_team_id(conn, team1)
    team2_id = get_team_id(conn, team2)
    
    player1 = get_player_stats_for_match(conn, match_id, team1_id)
    player2 = get_player_stats_for_match(conn, match_id, team2_id)
    
    if not player1 or not player2:
        return None
    
    template = random.choice(MATCH_ARTICLE_TEMPLATES)
    
    # Determine winner
    if score1 > score2:
        winner = team1
        loser = team2
        top_player = player1
        opponent_player = player2
    else:
        winner = team2
        loser = team1
        top_player = player2
        opponent_player = player1
    
    quarter = random.choice(['first', 'second', 'third', 'fourth'])
    
    article = template.format(
        team1=winner,
        team2=loser,
        score1=max(score1, score2),
        score2=min(score1, score2),
        top_player=top_player['name'],
        points=top_player['points'],
        rebounds=top_player['rebounds'],
        assists=top_player['assists'],
        opponent_player=opponent_player['name'],
        opponent_points=opponent_player['points'],
        quarter=quarter
    )
    
    return article

def generate_player_article(conn, match_data):
    """Generate an article about a player's performance"""
    match_id, match_date, venue, team1, team2, score1, score2 = match_data
    
    team1_id = get_team_id(conn, team1)
    team2_id = get_team_id(conn, team2)
    
    # Randomly pick a team
    team_id = random.choice([team1_id, team2_id])
    team_name = team1 if team_id == team1_id else team2
    
    player = get_player_stats_for_match(conn, match_id, team_id)
    if not player:
        return None
    
    template = random.choice(PLAYER_PERFORMANCE_TEMPLATES)
    
    article = template.format(
        player_name=player['name'],
        team=team_name,
        points=player['points'],
        rebounds=player['rebounds'],
        assists=player['assists'],
        position=player['position']
    )
    
    return article

def generate_team_article(conn, team_name):
    """Generate an article about a team"""
    template = random.choice(TEAM_ANALYSIS_TEMPLATES)
    article = template.format(team=team_name)
    return article

def get_team_id(conn, team_name):
    """Get team ID from team name"""
    cursor = conn.cursor()
    cursor.execute("SELECT team_id FROM teams WHERE team_name = %s", (team_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def generate_articles():
    """Generate articles from database"""
    try:
        conn = db.get_connection()
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return
    
    print("Generating articles from NBA database...")
    
    # Get match data
    matches = get_match_data(conn)
    print(f"Found {len(matches)} matches in database")
    
    # Get current article count
    if os.path.exists(ARTICLES_DIR):
        existing_articles = [f for f in os.listdir(ARTICLES_DIR) if f.startswith('article_') and f.endswith('.txt')]
        start_num = len(existing_articles)
    else:
        os.makedirs(ARTICLES_DIR, exist_ok=True)
        start_num = 0
    
    target_articles = 1000
    articles_needed = target_articles - start_num
    
    if articles_needed <= 0:
        print(f"Already have {start_num} articles. Target reached!")
        conn.close()
        return
    
    print(f"Generating {articles_needed} articles to reach {target_articles} total...")
    
    article_num = start_num
    generated = 0
    
    # Generate match articles
    for match in matches:
        if generated >= articles_needed:
            break
        
        # Generate match article
        article = generate_match_article(conn, match)
        if article:
            filename = f"article_{article_num}.txt"
            filepath = os.path.join(ARTICLES_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(article)
            article_num += 1
            generated += 1
        
        # Generate player performance article (50% chance)
        if random.random() < 0.5 and generated < articles_needed:
            article = generate_player_article(conn, match)
            if article:
                filename = f"article_{article_num}.txt"
                filepath = os.path.join(ARTICLES_DIR, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(article)
                article_num += 1
                generated += 1
    
    # Generate team analysis articles if still needed
    if generated < articles_needed:
        cursor = conn.cursor()
        cursor.execute("SELECT team_name FROM teams")
        teams = cursor.fetchall()
        
        for team in teams:
            if generated >= articles_needed:
                break
            
            article = generate_team_article(conn, team[0])
            if article:
                filename = f"article_{article_num}.txt"
                filepath = os.path.join(ARTICLES_DIR, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(article)
                article_num += 1
                generated += 1
    
    conn.close()
    print(f"\nGenerated {generated} new articles!")
    print(f"Total articles: {article_num}")
    print(f"Articles saved to: {ARTICLES_DIR}")

if __name__ == "__main__":
    generate_articles()

