-- Seed Data for Fictional NBA Database
-- This file contains all 30 teams, players, matches, stats, and schedules

-- Insert All 30 NBA Teams
INSERT INTO teams (team_name, city, conference, division) VALUES
-- Eastern Conference
('Celtics', 'Boston', 'East', 'Atlantic'),
('Nets', 'Brooklyn', 'East', 'Atlantic'),
('Knicks', 'New York', 'East', 'Atlantic'),
('76ers', 'Philadelphia', 'East', 'Atlantic'),
('Raptors', 'Toronto', 'East', 'Atlantic'),
('Bulls', 'Chicago', 'East', 'Central'),
('Cavaliers', 'Cleveland', 'East', 'Central'),
('Pistons', 'Detroit', 'East', 'Central'),
('Pacers', 'Indiana', 'East', 'Central'),
('Bucks', 'Milwaukee', 'East', 'Central'),
('Hawks', 'Atlanta', 'East', 'Southeast'),
('Hornets', 'Charlotte', 'East', 'Southeast'),
('Heat', 'Miami', 'East', 'Southeast'),
('Magic', 'Orlando', 'East', 'Southeast'),
('Wizards', 'Washington', 'East', 'Southeast'),
-- Western Conference
('Nuggets', 'Denver', 'West', 'Northwest'),
('Timberwolves', 'Minnesota', 'West', 'Northwest'),
('Thunder', 'Oklahoma City', 'West', 'Northwest'),
('Trail Blazers', 'Portland', 'West', 'Northwest'),
('Jazz', 'Utah', 'West', 'Northwest'),
('Warriors', 'Golden State', 'West', 'Pacific'),
('Clippers', 'LA', 'West', 'Pacific'),
('Lakers', 'Los Angeles', 'West', 'Pacific'),
('Suns', 'Phoenix', 'West', 'Pacific'),
('Kings', 'Sacramento', 'West', 'Pacific'),
('Mavericks', 'Dallas', 'West', 'Southwest'),
('Rockets', 'Houston', 'West', 'Southwest'),
('Grizzlies', 'Memphis', 'West', 'Southwest'),
('Pelicans', 'New Orleans', 'West', 'Southwest'),
('Spurs', 'San Antonio', 'West', 'Southwest');

-- Insert Players (Top 3-4 players per team)
-- Celtics
INSERT INTO players (player_name, team_id, position) VALUES
('Jayson Tatum', 1, 'SF'), ('Jaylen Brown', 1, 'SG'), ('Kristaps Porzingis', 1, 'PF'), ('Derrick White', 1, 'PG');

-- Nets
INSERT INTO players (player_name, team_id, position) VALUES
('Mikal Bridges', 2, 'SF'), ('Cam Thomas', 2, 'SG'), ('Nic Claxton', 2, 'C'), ('Spencer Dinwiddie', 2, 'PG');

-- Knicks
INSERT INTO players (player_name, team_id, position) VALUES
('Jalen Brunson', 3, 'PG'), ('Julius Randle', 3, 'PF'), ('RJ Barrett', 3, 'SG'), ('Mitchell Robinson', 3, 'C');

-- 76ers
INSERT INTO players (player_name, team_id, position) VALUES
('Joel Embiid', 4, 'C'), ('Tyrese Maxey', 4, 'PG'), ('Tobias Harris', 4, 'PF'), ('DeAnthony Melton', 4, 'SG');

-- Raptors
INSERT INTO players (player_name, team_id, position) VALUES
('Pascal Siakam', 5, 'PF'), ('OG Anunoby', 5, 'SF'), ('Scottie Barnes', 5, 'SF'), ('Dennis Schroder', 5, 'PG');

-- Bulls
INSERT INTO players (player_name, team_id, position) VALUES
('DeMar DeRozan', 6, 'SG'), ('Zach LaVine', 6, 'SG'), ('Nikola Vucevic', 6, 'C'), ('Coby White', 6, 'PG');

-- Cavaliers
INSERT INTO players (player_name, team_id, position) VALUES
('Donovan Mitchell', 7, 'SG'), ('Darius Garland', 7, 'PG'), ('Evan Mobley', 7, 'PF'), ('Jarrett Allen', 7, 'C');

-- Pistons
INSERT INTO players (player_name, team_id, position) VALUES
('Cade Cunningham', 8, 'PG'), ('Jaden Ivey', 8, 'SG'), ('Ausar Thompson', 8, 'SF'), ('Jalen Duren', 8, 'C');

-- Pacers
INSERT INTO players (player_name, team_id, position) VALUES
('Tyrese Haliburton', 9, 'PG'), ('Buddy Hield', 9, 'SG'), ('Myles Turner', 9, 'C'), ('Bennedict Mathurin', 9, 'SG');

-- Bucks
INSERT INTO players (player_name, team_id, position) VALUES
('Giannis Antetokounmpo', 10, 'PF'), ('Damian Lillard', 10, 'PG'), ('Khris Middleton', 10, 'SF'), ('Brook Lopez', 10, 'C');

-- Hawks
INSERT INTO players (player_name, team_id, position) VALUES
('Trae Young', 11, 'PG'), ('Dejounte Murray', 11, 'SG'), ('Clint Capela', 11, 'C'), ('Bogdan Bogdanovic', 11, 'SG');

-- Hornets
INSERT INTO players (player_name, team_id, position) VALUES
('LaMelo Ball', 12, 'PG'), ('Terry Rozier', 12, 'SG'), ('Gordon Hayward', 12, 'SF'), ('Mark Williams', 12, 'C');

-- Heat
INSERT INTO players (player_name, team_id, position) VALUES
('Jimmy Butler', 13, 'SF'), ('Bam Adebayo', 13, 'C'), ('Tyler Herro', 13, 'SG'), ('Kyle Lowry', 13, 'PG');

-- Magic
INSERT INTO players (player_name, team_id, position) VALUES
('Paolo Banchero', 14, 'PF'), ('Franz Wagner', 14, 'SF'), ('Jalen Suggs', 14, 'PG'), ('Wendell Carter Jr', 14, 'C');

-- Wizards
INSERT INTO players (player_name, team_id, position) VALUES
('Kyle Kuzma', 15, 'PF'), ('Jordan Poole', 15, 'SG'), ('Tyus Jones', 15, 'PG'), ('Daniel Gafford', 15, 'C');

-- Nuggets
INSERT INTO players (player_name, team_id, position) VALUES
('Nikola Jokic', 16, 'C'), ('Jamal Murray', 16, 'PG'), ('Michael Porter Jr', 16, 'SF'), ('Aaron Gordon', 16, 'PF');

-- Timberwolves
INSERT INTO players (player_name, team_id, position) VALUES
('Anthony Edwards', 17, 'SG'), ('Karl-Anthony Towns', 17, 'C'), ('Rudy Gobert', 17, 'C'), ('Mike Conley', 17, 'PG');

-- Thunder
INSERT INTO players (player_name, team_id, position) VALUES
('Shai Gilgeous-Alexander', 18, 'PG'), ('Chet Holmgren', 18, 'C'), ('Jalen Williams', 18, 'SF'), ('Josh Giddey', 18, 'PG');

-- Trail Blazers
INSERT INTO players (player_name, team_id, position) VALUES
('Anfernee Simons', 19, 'PG'), ('Jerami Grant', 19, 'PF'), ('Deandre Ayton', 19, 'C'), ('Scoot Henderson', 19, 'PG');

-- Jazz
INSERT INTO players (player_name, team_id, position) VALUES
('Lauri Markkanen', 20, 'PF'), ('Jordan Clarkson', 20, 'SG'), ('Walker Kessler', 20, 'C'), ('Collin Sexton', 20, 'PG');

-- Warriors
INSERT INTO players (player_name, team_id, position) VALUES
('Stephen Curry', 21, 'PG'), ('Klay Thompson', 21, 'SG'), ('Draymond Green', 21, 'PF'), ('Andrew Wiggins', 21, 'SF');

-- Clippers
INSERT INTO players (player_name, team_id, position) VALUES
('Kawhi Leonard', 22, 'SF'), ('Paul George', 22, 'SF'), ('James Harden', 22, 'PG'), ('Ivica Zubac', 22, 'C');

-- Lakers
INSERT INTO players (player_name, team_id, position) VALUES
('LeBron James', 23, 'SF'), ('Anthony Davis', 23, 'PF'), ('Austin Reaves', 23, 'SG'), ('D Angelo Russell', 23, 'PG');

-- Suns
INSERT INTO players (player_name, team_id, position) VALUES
('Kevin Durant', 24, 'SF'), ('Devin Booker', 24, 'SG'), ('Bradley Beal', 24, 'SG'), ('Jusuf Nurkic', 24, 'C');

-- Kings
INSERT INTO players (player_name, team_id, position) VALUES
('DeAaron Fox', 25, 'PG'), ('Domantas Sabonis', 25, 'C'), ('Keegan Murray', 25, 'PF'), ('Malik Monk', 25, 'SG');

-- Mavericks
INSERT INTO players (player_name, team_id, position) VALUES
('Luka Doncic', 26, 'PG'), ('Kyrie Irving', 26, 'PG'), ('Grant Williams', 26, 'PF'), ('Dereck Lively II', 26, 'C');

-- Rockets
INSERT INTO players (player_name, team_id, position) VALUES
('Alperen Sengun', 27, 'C'), ('Jalen Green', 27, 'SG'), ('Jabari Smith Jr', 27, 'PF'), ('Fred VanVleet', 27, 'PG');

-- Grizzlies
INSERT INTO players (player_name, team_id, position) VALUES
('Ja Morant', 28, 'PG'), ('Jaren Jackson Jr', 28, 'PF'), ('Desmond Bane', 28, 'SG'), ('Steven Adams', 28, 'C');

-- Pelicans
INSERT INTO players (player_name, team_id, position) VALUES
('Zion Williamson', 29, 'PF'), ('Brandon Ingram', 29, 'SF'), ('CJ McCollum', 29, 'PG'), ('Jonas Valanciunas', 29, 'C');

-- Spurs
INSERT INTO players (player_name, team_id, position) VALUES
('Victor Wembanyama', 30, 'C'), ('Devin Vassell', 30, 'SG'), ('Keldon Johnson', 30, 'SF'), ('Jeremy Sochan', 30, 'PF');

-- Insert Past Matches (30+ games)
INSERT INTO matches (team1_id, team2_id, team1_score, team2_score, match_date, venue) VALUES
-- Recent games
(23, 21, 118, 112, '2024-01-15', 'Crypto.com Arena'),
(10, 16, 125, 120, '2024-01-14', 'Fiserv Forum'),
(1, 3, 115, 108, '2024-01-13', 'TD Garden'),
(24, 26, 132, 128, '2024-01-12', 'Footprint Center'),
(7, 6, 110, 105, '2024-01-11', 'Rocket Mortgage FieldHouse'),
(18, 17, 118, 115, '2024-01-10', 'Paycom Center'),
(22, 23, 120, 125, '2024-01-09', 'Crypto.com Arena'),
(16, 20, 128, 110, '2024-01-08', 'Ball Arena'),
(4, 1, 112, 118, '2024-01-07', 'Wells Fargo Center'),
(11, 13, 105, 98, '2024-01-06', 'State Farm Arena'),
(26, 25, 130, 125, '2024-01-05', 'American Airlines Center'),
(21, 24, 115, 120, '2024-01-04', 'Chase Center'),
(10, 14, 122, 108, '2024-01-03', 'Fiserv Forum'),
(7, 9, 118, 112, '2024-01-02', 'Rocket Mortgage FieldHouse'),
(1, 5, 125, 110, '2024-01-01', 'TD Garden'),
(23, 22, 128, 122, '2023-12-30', 'Crypto.com Arena'),
(16, 19, 132, 118, '2023-12-29', 'Ball Arena'),
(24, 21, 120, 115, '2023-12-28', 'Footprint Center'),
(18, 28, 125, 120, '2023-12-27', 'Paycom Center'),
(10, 1, 118, 112, '2023-12-26', 'Fiserv Forum'),
(7, 11, 110, 105, '2023-12-25', 'Rocket Mortgage FieldHouse'),
(23, 26, 128, 125, '2023-12-24', 'Crypto.com Arena'),
(16, 17, 120, 115, '2023-12-23', 'Ball Arena'),
(4, 3, 112, 108, '2023-12-22', 'Wells Fargo Center'),
(24, 25, 130, 125, '2023-12-21', 'Footprint Center'),
(10, 13, 125, 120, '2023-12-20', 'Fiserv Forum'),
(7, 8, 115, 110, '2023-12-19', 'Rocket Mortgage FieldHouse'),
(1, 2, 118, 112, '2023-12-18', 'TD Garden'),
(23, 29, 128, 122, '2023-12-17', 'Crypto.com Arena'),
(16, 20, 125, 118, '2023-12-16', 'Ball Arena'),
(18, 19, 120, 115, '2023-12-15', 'Paycom Center'),
(10, 11, 122, 118, '2023-12-14', 'Fiserv Forum'),
(7, 12, 110, 105, '2023-12-13', 'Rocket Mortgage FieldHouse');

-- Insert Player Stats for matches (sample stats for key players)
-- Match 1: Lakers vs Warriors
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(1, 89, 32, 8, 6, 1, 2),  -- LeBron James
(1, 90, 28, 12, 3, 0, 4),  -- Anthony Davis
(1, 81, 25, 4, 8, 2, 0),   -- Stephen Curry
(1, 82, 18, 5, 3, 1, 0);   -- Klay Thompson

-- Match 2: Bucks vs Nuggets
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(2, 37, 35, 12, 8, 2, 1),  -- Giannis
(2, 38, 28, 4, 10, 1, 0),  -- Damian Lillard
(2, 61, 30, 14, 9, 1, 1),  -- Nikola Jokic
(2, 62, 25, 5, 7, 2, 0);   -- Jamal Murray

-- Match 3: Celtics vs Knicks
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(3, 1, 28, 8, 5, 2, 1),    -- Jayson Tatum
(3, 2, 24, 6, 4, 1, 0),    -- Jaylen Brown
(3, 9, 22, 5, 8, 1, 0),    -- Jalen Brunson
(3, 10, 20, 10, 3, 0, 1);  -- Julius Randle

-- Match 4: Suns vs Mavericks
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(4, 93, 35, 8, 6, 1, 2),   -- Kevin Durant
(4, 94, 32, 5, 7, 2, 0),   -- Devin Booker
(4, 101, 38, 10, 12, 3, 1), -- Luka Doncic
(4, 102, 25, 4, 6, 1, 0);  -- Kyrie Irving

-- Match 5: Cavaliers vs Bulls
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(5, 25, 30, 5, 7, 2, 0),   -- Donovan Mitchell
(5, 26, 22, 3, 9, 1, 0),   -- Darius Garland
(5, 21, 28, 6, 5, 1, 0),   -- DeMar DeRozan
(5, 22, 24, 5, 4, 2, 0);   -- Zach LaVine

-- Match 6: Thunder vs Timberwolves
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(6, 69, 32, 6, 8, 3, 1),   -- Shai Gilgeous-Alexander
(6, 70, 18, 10, 2, 1, 3),  -- Chet Holmgren
(6, 65, 28, 7, 5, 2, 0),   -- Anthony Edwards
(6, 66, 24, 12, 3, 0, 2);  -- Karl-Anthony Towns

-- Match 7: Clippers vs Lakers
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(7, 85, 28, 7, 5, 2, 1),   -- Kawhi Leonard
(7, 86, 25, 6, 6, 1, 0),   -- Paul George
(7, 89, 35, 9, 7, 1, 2),   -- LeBron James
(7, 90, 30, 13, 4, 0, 3);  -- Anthony Davis

-- Match 8: Nuggets vs Jazz
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(8, 61, 32, 15, 10, 1, 2), -- Nikola Jokic
(8, 62, 26, 4, 8, 2, 0),   -- Jamal Murray
(8, 77, 28, 9, 3, 1, 1),   -- Lauri Markkanen
(8, 78, 22, 5, 5, 2, 0);   -- Jordan Clarkson

-- Match 9: 76ers vs Celtics
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(9, 13, 38, 12, 5, 1, 3),  -- Joel Embiid
(9, 14, 24, 4, 8, 2, 0),   -- Tyrese Maxey
(9, 1, 30, 9, 6, 2, 1),    -- Jayson Tatum
(9, 2, 26, 7, 4, 1, 0);    -- Jaylen Brown

-- Match 10: Hawks vs Heat
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(10, 41, 28, 4, 10, 2, 0), -- Trae Young
(10, 42, 22, 6, 7, 3, 0),  -- Dejounte Murray
(10, 49, 25, 8, 6, 2, 1),  -- Jimmy Butler
(10, 50, 20, 11, 4, 0, 2); -- Bam Adebayo

-- Add more stats for remaining matches (continuing pattern)
-- Match 11: Mavericks vs Kings
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(11, 101, 40, 11, 13, 4, 1), -- Luka Doncic
(11, 102, 28, 5, 7, 1, 0),   -- Kyrie Irving
(11, 97, 32, 6, 8, 2, 0),   -- DeAaron Fox
(11, 98, 24, 14, 5, 1, 1);  -- Domantas Sabonis

-- Match 12: Warriors vs Suns
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(12, 81, 30, 5, 9, 2, 0),   -- Stephen Curry
(12, 82, 22, 4, 4, 1, 0),   -- Klay Thompson
(12, 93, 35, 8, 6, 1, 2),   -- Kevin Durant
(12, 94, 28, 5, 7, 2, 0);   -- Devin Booker

-- Match 13: Bucks vs Magic
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(13, 37, 32, 13, 7, 2, 2),  -- Giannis
(13, 38, 26, 4, 9, 1, 0),   -- Damian Lillard
(13, 53, 24, 8, 5, 1, 1),   -- Paolo Banchero
(13, 54, 20, 6, 4, 2, 0);   -- Franz Wagner

-- Match 14: Cavaliers vs Pacers
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(14, 25, 28, 5, 8, 2, 0),   -- Donovan Mitchell
(14, 26, 24, 3, 10, 1, 0),  -- Darius Garland
(14, 33, 26, 4, 12, 3, 0),  -- Tyrese Haliburton
(14, 34, 22, 6, 3, 1, 0);   -- Buddy Hield

-- Match 15: Celtics vs Raptors
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(15, 1, 32, 9, 6, 2, 1),    -- Jayson Tatum
(15, 2, 28, 7, 5, 1, 0),    -- Jaylen Brown
(15, 17, 26, 8, 4, 1, 1),   -- Pascal Siakam
(15, 18, 22, 6, 3, 2, 0);   -- OG Anunoby

-- Continue adding stats for remaining matches...
-- Match 16: Lakers vs Clippers
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(16, 89, 38, 10, 8, 2, 1),  -- LeBron James
(16, 90, 30, 14, 4, 0, 4),  -- Anthony Davis
(16, 85, 30, 8, 6, 2, 1),   -- Kawhi Leonard
(16, 86, 28, 7, 7, 1, 0);   -- Paul George

-- Match 17: Nuggets vs Trail Blazers
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(17, 61, 35, 16, 11, 1, 2), -- Nikola Jokic
(17, 62, 28, 5, 9, 2, 0),   -- Jamal Murray
(17, 73, 26, 4, 6, 1, 0),   -- Anfernee Simons
(17, 74, 22, 8, 3, 0, 1);   -- Jerami Grant

-- Match 18: Suns vs Warriors
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(18, 93, 40, 9, 7, 1, 2),   -- Kevin Durant
(18, 94, 32, 6, 8, 2, 0),   -- Devin Booker
(18, 81, 28, 4, 10, 3, 0),  -- Stephen Curry
(18, 82, 20, 5, 4, 1, 0);   -- Klay Thompson

-- Match 19: Thunder vs Grizzlies
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(19, 69, 34, 7, 9, 4, 1),   -- Shai Gilgeous-Alexander
(19, 70, 20, 11, 3, 1, 4),  -- Chet Holmgren
(19, 105, 28, 5, 10, 2, 0), -- Ja Morant
(19, 106, 24, 9, 4, 1, 2);  -- Jaren Jackson Jr

-- Match 20: Bucks vs Celtics
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(20, 37, 38, 14, 9, 2, 2),  -- Giannis
(20, 38, 30, 5, 11, 1, 0),  -- Damian Lillard
(20, 1, 32, 10, 7, 2, 1),   -- Jayson Tatum
(20, 2, 28, 8, 5, 1, 0);    -- Jaylen Brown

-- Add stats for remaining matches (21-33) with similar patterns
-- Match 21: Cavaliers vs Hawks
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(21, 25, 32, 6, 8, 3, 0),   -- Donovan Mitchell
(21, 26, 24, 4, 9, 1, 0),   -- Darius Garland
(21, 41, 28, 5, 11, 2, 0),  -- Trae Young
(21, 42, 22, 7, 6, 3, 0);   -- Dejounte Murray

-- Match 22: Lakers vs Mavericks
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(22, 89, 35, 9, 7, 1, 2),   -- LeBron James
(22, 90, 28, 13, 4, 0, 3),  -- Anthony Davis
(22, 101, 42, 11, 14, 4, 1), -- Luka Doncic
(22, 102, 26, 5, 8, 1, 0);  -- Kyrie Irving

-- Match 23: Nuggets vs Timberwolves
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(23, 61, 30, 14, 10, 1, 1), -- Nikola Jokic
(23, 62, 26, 4, 8, 2, 0),   -- Jamal Murray
(23, 65, 30, 8, 6, 2, 0),   -- Anthony Edwards
(23, 66, 24, 13, 3, 0, 2);  -- Karl-Anthony Towns

-- Match 24: 76ers vs Knicks
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(24, 13, 36, 13, 5, 1, 3),  -- Joel Embiid
(24, 14, 26, 5, 9, 2, 0),   -- Tyrese Maxey
(24, 9, 28, 6, 9, 1, 0),    -- Jalen Brunson
(24, 10, 24, 11, 4, 0, 1);  -- Julius Randle

-- Match 25: Suns vs Kings
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(25, 93, 38, 9, 6, 1, 2),   -- Kevin Durant
(25, 94, 34, 6, 8, 2, 0),   -- Devin Booker
(25, 97, 30, 5, 9, 3, 0),   -- DeAaron Fox
(25, 98, 26, 15, 6, 1, 1);  -- Domantas Sabonis

-- Match 26: Bucks vs Heat
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(26, 37, 33, 12, 8, 2, 1),  -- Giannis
(26, 38, 28, 4, 10, 1, 0),  -- Damian Lillard
(26, 49, 26, 9, 7, 2, 1),   -- Jimmy Butler
(26, 50, 22, 12, 5, 0, 2);  -- Bam Adebayo

-- Match 27: Cavaliers vs Pistons
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(27, 25, 30, 6, 7, 2, 0),   -- Donovan Mitchell
(27, 26, 24, 4, 8, 1, 0),   -- Darius Garland
(27, 29, 28, 5, 9, 3, 0),   -- Cade Cunningham
(27, 30, 22, 6, 4, 1, 0);   -- Jaden Ivey

-- Match 28: Celtics vs Nets
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(28, 1, 30, 9, 6, 2, 1),    -- Jayson Tatum
(28, 2, 28, 7, 5, 1, 0),    -- Jaylen Brown
(28, 5, 26, 6, 4, 1, 0),    -- Mikal Bridges
(28, 6, 24, 5, 5, 2, 0);    -- Cam Thomas

-- Match 29: Lakers vs Pelicans
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(29, 89, 32, 8, 7, 1, 2),   -- LeBron James
(29, 90, 30, 14, 4, 0, 4),  -- Anthony Davis
(29, 109, 28, 7, 5, 1, 0),  -- Zion Williamson
(29, 110, 26, 6, 6, 2, 0);  -- Brandon Ingram

-- Match 30: Nuggets vs Jazz
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(30, 61, 33, 15, 11, 1, 2), -- Nikola Jokic
(30, 62, 28, 5, 9, 2, 0),   -- Jamal Murray
(30, 77, 30, 10, 4, 1, 1),  -- Lauri Markkanen
(30, 78, 24, 6, 6, 2, 0);   -- Jordan Clarkson

-- Match 31: Thunder vs Trail Blazers
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(31, 69, 36, 7, 10, 4, 1),  -- Shai Gilgeous-Alexander
(31, 70, 22, 12, 3, 1, 5),  -- Chet Holmgren
(31, 73, 28, 5, 7, 1, 0),   -- Anfernee Simons
(31, 74, 24, 9, 4, 0, 1);   -- Jerami Grant

-- Match 32: Bucks vs Hawks
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(32, 37, 35, 13, 8, 2, 2),  -- Giannis
(32, 38, 30, 4, 11, 1, 0),  -- Damian Lillard
(32, 41, 32, 5, 12, 3, 0),  -- Trae Young
(32, 42, 26, 7, 7, 2, 0);   -- Dejounte Murray

-- Match 33: Cavaliers vs Hornets
INSERT INTO player_stats (match_id, player_id, points, rebounds, assists, steals, blocks) VALUES
(33, 25, 34, 6, 9, 3, 0),   -- Donovan Mitchell
(33, 26, 26, 4, 10, 1, 0),  -- Darius Garland
(33, 45, 28, 5, 8, 2, 0),   -- LaMelo Ball
(33, 46, 24, 6, 5, 1, 0);   -- Terry Rozier

-- Insert Upcoming Matches (Schedule) - At least 3 upcoming games per team
-- Lakers upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(23, 21, '2024-02-15', 'Crypto.com Arena', 'upcoming'),
(23, 24, '2024-02-18', 'Crypto.com Arena', 'upcoming'),
(23, 26, '2024-02-20', 'American Airlines Center', 'upcoming'),
(23, 10, '2024-02-22', 'Fiserv Forum', 'upcoming');

-- Warriors upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(21, 16, '2024-02-16', 'Chase Center', 'upcoming'),
(21, 22, '2024-02-19', 'Chase Center', 'upcoming'),
(21, 25, '2024-02-21', 'Golden 1 Center', 'upcoming');

-- Celtics upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(1, 4, '2024-02-17', 'TD Garden', 'upcoming'),
(1, 10, '2024-02-19', 'Fiserv Forum', 'upcoming'),
(1, 3, '2024-02-21', 'Madison Square Garden', 'upcoming'),
(1, 5, '2024-02-23', 'Scotiabank Arena', 'upcoming');

-- Bucks upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(10, 1, '2024-02-19', 'Fiserv Forum', 'upcoming'),
(10, 7, '2024-02-21', 'Rocket Mortgage FieldHouse', 'upcoming'),
(10, 11, '2024-02-23', 'State Farm Arena', 'upcoming'),
(10, 13, '2024-02-25', 'FTX Arena', 'upcoming');

-- Nuggets upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(16, 17, '2024-02-18', 'Ball Arena', 'upcoming'),
(16, 18, '2024-02-20', 'Paycom Center', 'upcoming'),
(16, 20, '2024-02-22', 'Vivint Arena', 'upcoming'),
(16, 19, '2024-02-24', 'Moda Center', 'upcoming');

-- Suns upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(24, 23, '2024-02-18', 'Footprint Center', 'upcoming'),
(24, 21, '2024-02-20', 'Chase Center', 'upcoming'),
(24, 22, '2024-02-22', 'Crypto.com Arena', 'upcoming'),
(24, 25, '2024-02-24', 'Footprint Center', 'upcoming');

-- Mavericks upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(26, 23, '2024-02-20', 'American Airlines Center', 'upcoming'),
(26, 28, '2024-02-22', 'FedExForum', 'upcoming'),
(26, 27, '2024-02-24', 'Toyota Center', 'upcoming'),
(26, 29, '2024-02-26', 'Smoothie King Center', 'upcoming');

-- Heat upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(13, 11, '2024-02-17', 'FTX Arena', 'upcoming'),
(13, 10, '2024-02-25', 'Fiserv Forum', 'upcoming'),
(13, 14, '2024-02-27', 'Amway Center', 'upcoming'),
(13, 15, '2024-02-29', 'Capital One Arena', 'upcoming');

-- 76ers upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(4, 1, '2024-02-17', 'Wells Fargo Center', 'upcoming'),
(4, 3, '2024-02-19', 'Madison Square Garden', 'upcoming'),
(4, 5, '2024-02-21', 'Scotiabank Arena', 'upcoming'),
(4, 2, '2024-02-23', 'Barclays Center', 'upcoming');

-- Cavaliers upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(7, 10, '2024-02-21', 'Rocket Mortgage FieldHouse', 'upcoming'),
(7, 9, '2024-02-23', 'Gainbridge Fieldhouse', 'upcoming'),
(7, 6, '2024-02-25', 'United Center', 'upcoming'),
(7, 8, '2024-02-27', 'Little Caesars Arena', 'upcoming');

-- Thunder upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(18, 16, '2024-02-20', 'Paycom Center', 'upcoming'),
(18, 17, '2024-02-22', 'Target Center', 'upcoming'),
(18, 19, '2024-02-24', 'Moda Center', 'upcoming'),
(18, 20, '2024-02-26', 'Vivint Arena', 'upcoming');

-- Clippers upcoming games
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(22, 21, '2024-02-19', 'Crypto.com Arena', 'upcoming'),
(22, 24, '2024-02-22', 'Crypto.com Arena', 'upcoming'),
(22, 23, '2024-02-24', 'Crypto.com Arena', 'upcoming'),
(22, 25, '2024-02-26', 'Golden 1 Center', 'upcoming');

-- Continue with remaining teams...
-- Knicks
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(3, 1, '2024-02-21', 'Madison Square Garden', 'upcoming'),
(3, 4, '2024-02-19', 'Wells Fargo Center', 'upcoming'),
(3, 2, '2024-02-23', 'Barclays Center', 'upcoming'),
(3, 5, '2024-02-25', 'Scotiabank Arena', 'upcoming');

-- Hawks
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(11, 13, '2024-02-17', 'State Farm Arena', 'upcoming'),
(11, 10, '2024-02-23', 'Fiserv Forum', 'upcoming'),
(11, 12, '2024-02-25', 'Spectrum Center', 'upcoming'),
(11, 14, '2024-02-27', 'Amway Center', 'upcoming');

-- Timberwolves
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(17, 16, '2024-02-18', 'Target Center', 'upcoming'),
(17, 18, '2024-02-22', 'Paycom Center', 'upcoming'),
(17, 19, '2024-02-24', 'Moda Center', 'upcoming'),
(17, 20, '2024-02-26', 'Vivint Arena', 'upcoming');

-- Kings
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(25, 21, '2024-02-21', 'Golden 1 Center', 'upcoming'),
(25, 24, '2024-02-24', 'Footprint Center', 'upcoming'),
(25, 22, '2024-02-26', 'Crypto.com Arena', 'upcoming'),
(25, 26, '2024-02-28', 'American Airlines Center', 'upcoming');

-- Grizzlies
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(28, 26, '2024-02-22', 'FedExForum', 'upcoming'),
(28, 27, '2024-02-24', 'Toyota Center', 'upcoming'),
(28, 29, '2024-02-26', 'Smoothie King Center', 'upcoming'),
(28, 30, '2024-02-28', 'Frost Bank Center', 'upcoming');

-- Pelicans
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(29, 26, '2024-02-26', 'Smoothie King Center', 'upcoming'),
(29, 28, '2024-02-26', 'FedExForum', 'upcoming'),
(29, 27, '2024-02-28', 'Toyota Center', 'upcoming'),
(29, 30, '2024-03-01', 'Frost Bank Center', 'upcoming');

-- Spurs
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(30, 28, '2024-02-28', 'Frost Bank Center', 'upcoming'),
(30, 29, '2024-03-01', 'Smoothie King Center', 'upcoming'),
(30, 27, '2024-03-03', 'Toyota Center', 'upcoming'),
(30, 26, '2024-03-05', 'American Airlines Center', 'upcoming');

-- Rockets
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(27, 26, '2024-02-24', 'Toyota Center', 'upcoming'),
(27, 28, '2024-02-24', 'FedExForum', 'upcoming'),
(27, 29, '2024-02-28', 'Smoothie King Center', 'upcoming'),
(27, 30, '2024-03-03', 'Frost Bank Center', 'upcoming');

-- Trail Blazers
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(19, 16, '2024-02-24', 'Moda Center', 'upcoming'),
(19, 18, '2024-02-24', 'Paycom Center', 'upcoming'),
(19, 17, '2024-02-24', 'Target Center', 'upcoming'),
(19, 20, '2024-02-28', 'Vivint Arena', 'upcoming');

-- Jazz
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(20, 16, '2024-02-22', 'Vivint Arena', 'upcoming'),
(20, 18, '2024-02-26', 'Paycom Center', 'upcoming'),
(20, 17, '2024-02-26', 'Target Center', 'upcoming'),
(20, 19, '2024-02-28', 'Moda Center', 'upcoming');

-- Nets
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(2, 1, '2024-02-20', 'Barclays Center', 'upcoming'),
(2, 3, '2024-02-23', 'Madison Square Garden', 'upcoming'),
(2, 4, '2024-02-25', 'Wells Fargo Center', 'upcoming'),
(2, 5, '2024-02-27', 'Scotiabank Arena', 'upcoming');

-- Raptors
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(5, 1, '2024-02-23', 'Scotiabank Arena', 'upcoming'),
(5, 4, '2024-02-21', 'Wells Fargo Center', 'upcoming'),
(5, 3, '2024-02-25', 'Madison Square Garden', 'upcoming'),
(5, 2, '2024-02-27', 'Barclays Center', 'upcoming');

-- Bulls
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(6, 7, '2024-02-25', 'United Center', 'upcoming'),
(6, 8, '2024-02-27', 'Little Caesars Arena', 'upcoming'),
(6, 9, '2024-03-01', 'Gainbridge Fieldhouse', 'upcoming'),
(6, 10, '2024-03-03', 'Fiserv Forum', 'upcoming');

-- Pistons
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(8, 7, '2024-02-27', 'Little Caesars Arena', 'upcoming'),
(8, 6, '2024-02-27', 'United Center', 'upcoming'),
(8, 9, '2024-03-01', 'Gainbridge Fieldhouse', 'upcoming'),
(8, 10, '2024-03-03', 'Fiserv Forum', 'upcoming');

-- Pacers
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(9, 7, '2024-02-23', 'Gainbridge Fieldhouse', 'upcoming'),
(9, 8, '2024-03-01', 'Little Caesars Arena', 'upcoming'),
(9, 6, '2024-03-01', 'United Center', 'upcoming'),
(9, 10, '2024-03-05', 'Fiserv Forum', 'upcoming');

-- Magic
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(14, 13, '2024-02-27', 'Amway Center', 'upcoming'),
(14, 11, '2024-02-27', 'State Farm Arena', 'upcoming'),
(14, 12, '2024-03-01', 'Spectrum Center', 'upcoming'),
(14, 15, '2024-03-03', 'Capital One Arena', 'upcoming');

-- Hornets
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(12, 11, '2024-02-25', 'Spectrum Center', 'upcoming'),
(12, 13, '2024-02-27', 'FTX Arena', 'upcoming'),
(12, 14, '2024-03-01', 'Amway Center', 'upcoming'),
(12, 15, '2024-03-03', 'Capital One Arena', 'upcoming');

-- Wizards
INSERT INTO schedule (team1_id, team2_id, match_date, venue, status) VALUES
(15, 13, '2024-02-29', 'Capital One Arena', 'upcoming'),
(15, 14, '2024-03-03', 'Amway Center', 'upcoming'),
(15, 11, '2024-03-05', 'State Farm Arena', 'upcoming'),
(15, 12, '2024-03-03', 'Spectrum Center', 'upcoming');

