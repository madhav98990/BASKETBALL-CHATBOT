-- PostgreSQL Schema for Fictional NBA Database
-- This creates a complete NBA database with teams, players, matches, stats, and schedules

-- Drop existing tables if they exist
DROP TABLE IF EXISTS team_news CASCADE;
DROP TABLE IF EXISTS season_averages CASCADE;
DROP TABLE IF EXISTS injuries CASCADE;
DROP TABLE IF EXISTS standings CASCADE;
DROP TABLE IF EXISTS live_games CASCADE;
DROP TABLE IF EXISTS player_stats CASCADE;
DROP TABLE IF EXISTS schedule CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS teams CASCADE;

-- Teams Table (All 30 NBA Teams)
CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL UNIQUE,
    city VARCHAR(100) NOT NULL,
    conference VARCHAR(10) NOT NULL CHECK (conference IN ('East', 'West')),
    division VARCHAR(20) NOT NULL
);

-- Players Table
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    team_id INTEGER NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    position VARCHAR(10) NOT NULL CHECK (position IN ('PG', 'SG', 'SF', 'PF', 'C'))
);

-- Matches Table (Past games with scores)
CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    team1_id INTEGER NOT NULL REFERENCES teams(team_id),
    team2_id INTEGER NOT NULL REFERENCES teams(team_id),
    team1_score INTEGER NOT NULL,
    team2_score INTEGER NOT NULL,
    match_date DATE NOT NULL,
    venue VARCHAR(100) NOT NULL,
    CHECK (team1_id != team2_id)
);

-- Player Stats Table (Stats for each player in each match)
CREATE TABLE player_stats (
    stat_id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    points INTEGER NOT NULL DEFAULT 0,
    rebounds INTEGER NOT NULL DEFAULT 0,
    assists INTEGER NOT NULL DEFAULT 0,
    steals INTEGER NOT NULL DEFAULT 0,
    blocks INTEGER NOT NULL DEFAULT 0,
    UNIQUE(match_id, player_id)
);

-- Schedule Table (Upcoming matches)
CREATE TABLE schedule (
    schedule_id SERIAL PRIMARY KEY,
    team1_id INTEGER NOT NULL REFERENCES teams(team_id),
    team2_id INTEGER NOT NULL REFERENCES teams(team_id),
    match_date DATE NOT NULL,
    venue VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'finished')),
    CHECK (team1_id != team2_id)
);

-- Standings Table (Team rankings and records)
CREATE TABLE standings (
    standing_id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    win_percentage DECIMAL(5,3) NOT NULL DEFAULT 0.000,
    conference_rank INTEGER,
    division_rank INTEGER,
    games_back DECIMAL(4,1) DEFAULT 0.0,
    streak VARCHAR(10), -- e.g., "W3" for 3 wins, "L2" for 2 losses
    last_updated DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE(team_id)
);

-- Injuries Table (Player injury reports)
CREATE TABLE injuries (
    injury_id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    injury_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Out', 'Questionable', 'Probable', 'Day-to-Day', 'Healthy')),
    date_reported DATE NOT NULL,
    expected_return DATE,
    description TEXT,
    last_updated DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Live Games Table (Games currently in progress)
CREATE TABLE live_games (
    live_game_id SERIAL PRIMARY KEY,
    team1_id INTEGER NOT NULL REFERENCES teams(team_id),
    team2_id INTEGER NOT NULL REFERENCES teams(team_id),
    team1_score INTEGER NOT NULL DEFAULT 0,
    team2_score INTEGER NOT NULL DEFAULT 0,
    quarter INTEGER NOT NULL DEFAULT 1,
    time_remaining VARCHAR(20), -- e.g., "5:32", "0:00"
    game_status VARCHAR(50) NOT NULL DEFAULT 'live' CHECK (game_status IN ('live', 'halftime', 'final', 'scheduled')),
    venue VARCHAR(100) NOT NULL,
    game_date DATE NOT NULL,
    game_time TIME,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (team1_id != team2_id)
);

-- Season Averages Table (Player season statistics)
CREATE TABLE season_averages (
    average_id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    games_played INTEGER NOT NULL DEFAULT 0,
    points_per_game DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    rebounds_per_game DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    assists_per_game DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    steals_per_game DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    blocks_per_game DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    field_goal_percentage DECIMAL(5,2) DEFAULT 0.00,
    three_point_percentage DECIMAL(5,2) DEFAULT 0.00,
    free_throw_percentage DECIMAL(5,2) DEFAULT 0.00,
    minutes_per_game DECIMAL(4,1) DEFAULT 0.0,
    season VARCHAR(10) NOT NULL DEFAULT '2025-26',
    last_updated DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE(player_id, season)
);

-- Team News Table (Team updates and news)
CREATE TABLE team_news (
    news_id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    headline VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    news_type VARCHAR(50) NOT NULL CHECK (news_type IN ('trade', 'injury', 'signing', 'roster', 'coaching', 'general')),
    published_date DATE NOT NULL DEFAULT CURRENT_DATE,
    source VARCHAR(100),
    is_breaking BOOLEAN DEFAULT FALSE
);

-- Create indexes for better query performance
CREATE INDEX idx_players_team ON players(team_id);
CREATE INDEX idx_matches_date ON matches(match_date);
CREATE INDEX idx_matches_teams ON matches(team1_id, team2_id);
CREATE INDEX idx_player_stats_match ON player_stats(match_id);
CREATE INDEX idx_player_stats_player ON player_stats(player_id);
CREATE INDEX idx_schedule_date ON schedule(match_date);
CREATE INDEX idx_schedule_status ON schedule(status);
CREATE INDEX idx_standings_team ON standings(team_id);
CREATE INDEX idx_standings_conference ON standings(conference_rank);
CREATE INDEX idx_injuries_player ON injuries(player_id);
CREATE INDEX idx_injuries_status ON injuries(status);
CREATE INDEX idx_injuries_date ON injuries(date_reported);
CREATE INDEX idx_live_games_status ON live_games(game_status);
CREATE INDEX idx_live_games_date ON live_games(game_date);
CREATE INDEX idx_season_averages_player ON season_averages(player_id);
CREATE INDEX idx_season_averages_season ON season_averages(season);
CREATE INDEX idx_team_news_team ON team_news(team_id);
CREATE INDEX idx_team_news_date ON team_news(published_date);
CREATE INDEX idx_team_news_type ON team_news(news_type);

