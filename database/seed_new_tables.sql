-- Seed Data for New Real-Time Tables
-- This file contains data for standings, injuries, live_games, season_averages, and team_news

-- Insert Standings (Team records and rankings)
-- Eastern Conference
INSERT INTO standings (team_id, wins, losses, win_percentage, conference_rank, division_rank, games_back, streak) VALUES
(1, 25, 8, 0.758, 1, 1, 0.0, 'W4'),   -- Celtics
(2, 18, 15, 0.545, 7, 2, 7.0, 'L2'),   -- Nets
(3, 22, 11, 0.667, 3, 2, 3.0, 'W2'),   -- Knicks
(4, 24, 9, 0.727, 2, 1, 1.0, 'W3'),   -- 76ers
(5, 19, 14, 0.576, 6, 3, 6.0, 'L1'),  -- Raptors
(6, 15, 18, 0.455, 10, 4, 10.0, 'W1'), -- Bulls
(7, 21, 12, 0.636, 4, 2, 4.0, 'W1'),  -- Cavaliers
(8, 8, 25, 0.242, 15, 5, 17.0, 'L5'), -- Pistons
(9, 20, 13, 0.606, 5, 3, 5.0, 'W2'),  -- Pacers
(10, 23, 10, 0.697, 2, 1, 2.0, 'W3'),  -- Bucks
(11, 17, 16, 0.515, 8, 3, 8.0, 'L1'),  -- Hawks
(12, 12, 21, 0.364, 12, 4, 13.0, 'L3'), -- Hornets
(13, 19, 14, 0.576, 6, 2, 6.0, 'W1'), -- Heat
(14, 16, 17, 0.485, 9, 3, 9.0, 'L2'),  -- Magic
(15, 11, 22, 0.333, 13, 5, 14.0, 'L1'); -- Wizards

-- Western Conference
INSERT INTO standings (team_id, wins, losses, win_percentage, conference_rank, division_rank, games_back, streak) VALUES
(16, 26, 7, 0.788, 1, 1, 0.0, 'W5'),   -- Nuggets
(17, 24, 9, 0.727, 2, 2, 2.0, 'W2'),   -- Timberwolves
(18, 22, 11, 0.667, 4, 3, 4.0, 'W1'),  -- Thunder
(19, 13, 20, 0.394, 13, 4, 13.0, 'L2'), -- Trail Blazers
(20, 15, 18, 0.455, 11, 5, 11.0, 'L1'), -- Jazz
(21, 20, 13, 0.606, 5, 2, 6.0, 'L1'),  -- Warriors
(22, 23, 10, 0.697, 3, 1, 3.0, 'W4'),  -- Clippers
(23, 19, 14, 0.576, 6, 3, 7.0, 'W2'),  -- Lakers
(24, 21, 12, 0.636, 4, 1, 5.0, 'W1'),  -- Suns
(25, 18, 15, 0.545, 8, 2, 8.0, 'L2'),  -- Kings
(26, 17, 16, 0.515, 9, 3, 9.0, 'W1'),  -- Mavericks
(27, 14, 19, 0.424, 12, 4, 12.0, 'L3'), -- Rockets
(28, 16, 17, 0.485, 10, 2, 10.0, 'L1'), -- Grizzlies
(29, 19, 14, 0.576, 6, 1, 7.0, 'W2'),  -- Pelicans
(30, 10, 23, 0.303, 14, 5, 16.0, 'L4'); -- Spurs

-- Insert Injuries (Player injury reports)
-- Note: Player IDs verified from database
INSERT INTO injuries (player_id, injury_type, status, date_reported, expected_return, description) VALUES
-- Celtics - Jayson Tatum
(1, 'Ankle Sprain', 'Questionable', CURRENT_DATE - 2, CURRENT_DATE + 3, 'Right ankle sprain, day-to-day'),
-- Lakers - LeBron James
(89, 'Knee Soreness', 'Probable', CURRENT_DATE - 1, NULL, 'Minor knee soreness, expected to play'),
-- Warriors - Stephen Curry
(81, 'Shoulder Strain', 'Out', CURRENT_DATE - 6, CURRENT_DATE + 9, 'Left shoulder strain, out 2 weeks'),
-- Bucks - Giannis Antetokounmpo
(37, 'Back Tightness', 'Day-to-Day', CURRENT_DATE - 1, NULL, 'Lower back tightness'),
-- 76ers - Joel Embiid
(13, 'Hamstring', 'Out', CURRENT_DATE - 12, CURRENT_DATE + 8, 'Hamstring strain, out 3-4 weeks'),
-- Suns - Kevin Durant
(93, 'Calf Strain', 'Questionable', CURRENT_DATE - 3, CURRENT_DATE + 5, 'Calf strain, questionable for next game'),
-- Heat - Jimmy Butler
(49, 'Ankle', 'Probable', CURRENT_DATE - 1, NULL, 'Ankle soreness, probable to play'),
-- Nuggets - Nikola Jokic
(61, 'Wrist', 'Day-to-Day', CURRENT_DATE - 2, NULL, 'Wrist soreness, day-to-day'),
-- Clippers - Kawhi Leonard
(85, 'Groin', 'Out', CURRENT_DATE - 5, CURRENT_DATE + 9, 'Groin strain, out 2 weeks'),
-- Mavericks - Luka Doncic
(101, 'Knee', 'Questionable', CURRENT_DATE - 1, CURRENT_DATE + 3, 'Knee soreness, questionable');

-- Insert Live Games (Games currently in progress)
INSERT INTO live_games (team1_id, team2_id, team1_score, team2_score, quarter, time_remaining, game_status, venue, game_date, game_time) VALUES
(23, 22, 68, 65, 3, '5:32', 'live', 'Crypto.com Arena', CURRENT_DATE, '19:30:00'),
(16, 17, 45, 48, 2, '3:15', 'live', 'Ball Arena', CURRENT_DATE, '20:00:00'),
(1, 4, 52, 50, 2, '0:00', 'halftime', 'TD Garden', CURRENT_DATE, '19:00:00'),
(21, 24, 78, 82, 4, '2:45', 'live', 'Chase Center', CURRENT_DATE, '22:00:00');

-- Insert Season Averages (Player season statistics)
-- Note: Player IDs verified from database
-- Celtics
INSERT INTO season_averages (player_id, games_played, points_per_game, rebounds_per_game, assists_per_game, steals_per_game, blocks_per_game, field_goal_percentage, three_point_percentage, free_throw_percentage, minutes_per_game) VALUES
(1, 33, 27.5, 8.2, 5.1, 1.2, 0.8, 47.8, 36.5, 85.2, 35.4),  -- Jayson Tatum
-- Lakers
(89, 33, 25.2, 7.8, 7.1, 1.3, 0.6, 54.1, 40.2, 75.8, 35.6), -- LeBron James
(90, 32, 24.8, 12.1, 3.2, 1.1, 2.3, 55.3, 27.4, 83.5, 34.1), -- Anthony Davis
-- Warriors
(81, 31, 28.4, 4.5, 4.8, 0.9, 0.2, 47.2, 42.1, 91.5, 32.8), -- Stephen Curry
(82, 33, 18.2, 3.8, 2.4, 0.8, 0.4, 43.5, 38.7, 87.2, 30.1), -- Klay Thompson
-- Bucks
(37, 33, 30.8, 11.2, 6.1, 1.2, 1.1, 60.2, 28.5, 65.8, 32.5), -- Giannis Antetokounmpo
(38, 33, 25.6, 4.2, 7.8, 0.9, 0.2, 44.8, 35.2, 92.1, 35.2), -- Damian Lillard
-- Nuggets
(61, 33, 26.8, 12.4, 9.2, 1.3, 0.7, 58.1, 35.4, 81.2, 33.8), -- Nikola Jokic
(62, 33, 21.5, 4.1, 6.8, 1.1, 0.3, 48.2, 42.5, 85.3, 32.5), -- Jamal Murray
-- Suns
(93, 32, 31.2, 6.8, 5.4, 0.9, 1.2, 52.8, 47.2, 87.5, 37.1), -- Kevin Durant
(94, 33, 27.1, 4.8, 6.9, 1.2, 0.4, 49.5, 36.8, 86.2, 34.5), -- Devin Booker
-- 76ers
(13, 30, 34.2, 11.8, 5.9, 1.2, 1.8, 53.5, 33.2, 88.1, 34.2), -- Joel Embiid
(14, 33, 26.4, 3.8, 6.5, 1.1, 0.3, 45.8, 37.5, 86.8, 35.8), -- Tyrese Maxey
-- Heat
(49, 32, 22.8, 5.5, 5.2, 1.8, 0.3, 49.8, 35.2, 85.5, 33.5), -- Jimmy Butler
(50, 33, 20.2, 10.8, 3.9, 1.1, 0.9, 54.2, 13.5, 80.2, 32.8), -- Bam Adebayo
-- Mavericks
(101, 33, 33.5, 9.2, 9.8, 1.4, 0.5, 48.8, 38.2, 78.5, 36.2), -- Luka Doncic
(102, 32, 25.8, 5.1, 5.2, 1.2, 0.3, 48.5, 40.8, 90.2, 34.8), -- Kyrie Irving
-- Clippers
(85, 31, 23.8, 6.2, 3.8, 1.6, 0.6, 52.1, 42.5, 88.5, 34.2), -- Kawhi Leonard
(86, 33, 22.5, 5.8, 4.2, 1.4, 0.4, 47.2, 38.8, 87.2, 33.8), -- Paul George
-- Cavaliers
(25, 33, 27.8, 4.5, 5.2, 1.5, 0.4, 46.8, 36.5, 86.5, 35.5), -- Donovan Mitchell
(26, 32, 18.2, 2.8, 6.8, 1.0, 0.2, 46.2, 38.2, 85.8, 33.2), -- Darius Garland
-- Thunder
(69, 33, 31.2, 5.8, 6.5, 2.1, 0.8, 54.5, 37.8, 87.5, 35.8), -- Shai Gilgeous-Alexander
(70, 33, 17.2, 7.8, 2.5, 0.8, 2.3, 53.2, 39.5, 79.5, 29.8), -- Chet Holmgren
-- Timberwolves
(65, 33, 26.5, 5.2, 5.1, 1.2, 0.5, 46.5, 36.8, 83.5, 34.5), -- Anthony Edwards
(66, 32, 22.8, 8.9, 3.2, 0.9, 1.2, 52.8, 42.2, 87.2, 32.8), -- Karl-Anthony Towns
-- Hawks
(41, 33, 27.2, 2.8, 10.8, 1.4, 0.2, 43.2, 36.5, 86.5, 36.2), -- Trae Young
(42, 33, 21.5, 5.5, 5.2, 1.8, 0.3, 46.8, 38.5, 84.2, 34.5), -- Dejounte Murray
-- Knicks
(9, 33, 26.8, 3.8, 6.5, 0.9, 0.1, 47.5, 41.2, 84.5, 35.2), -- Jalen Brunson
(10, 32, 24.2, 9.5, 4.8, 0.8, 0.3, 47.2, 30.5, 78.2, 35.8), -- Julius Randle
-- Kings
(98, 33, 19.8, 13.2, 8.5, 1.2, 0.6, 61.2, 37.5, 70.8, 34.2), -- Domantas Sabonis
-- Pelicans
(113, 32, 22.8, 5.5, 5.2, 1.1, 0.6, 58.5, 35.2, 70.2, 32.5), -- Zion Williamson
(114, 33, 21.2, 5.1, 5.8, 1.0, 0.4, 48.8, 35.5, 88.5, 34.8); -- Brandon Ingram

-- Insert Team News
INSERT INTO team_news (team_id, headline, content, news_type, published_date, source, is_breaking) VALUES
-- Lakers
(23, 'Lakers Sign Free Agent Point Guard', 'The Los Angeles Lakers have signed veteran point guard to bolster their backcourt depth. The move comes as the team looks to strengthen their roster for the playoff push.', 'signing', CURRENT_DATE - 2, 'NBA.com', FALSE),
(23, 'LeBron James Reaches 40,000 Career Points', 'LeBron James made history by becoming the first player to reach 40,000 career points in a thrilling win over the Warriors.', 'general', CURRENT_DATE - 5, 'ESPN', TRUE),
-- Warriors
(21, 'Warriors Trade Rumors Heat Up', 'The Golden State Warriors are reportedly exploring trade options as they look to improve their roster before the deadline.', 'trade', CURRENT_DATE - 1, 'The Athletic', FALSE),
(21, 'Stephen Curry Out with Shoulder Injury', 'Warriors star Stephen Curry will miss the next 2 weeks with a shoulder strain, dealing a blow to the team''s playoff hopes.', 'injury', CURRENT_DATE - 6, 'Warriors PR', TRUE),
-- Celtics
(1, 'Celtics Extend Jayson Tatum', 'The Boston Celtics have signed Jayson Tatum to a contract extension, keeping the star forward in Boston for years to come.', 'signing', CURRENT_DATE - 3, 'Celtics.com', TRUE),
(1, 'Celtics Lead Eastern Conference', 'The Boston Celtics continue to dominate the Eastern Conference with the best record in the NBA.', 'general', CURRENT_DATE, 'NBA.com', FALSE),
-- Bucks
(10, 'Giannis Antetokounmpo MVP Candidate', 'Giannis Antetokounmpo is putting up MVP-caliber numbers this season, leading the Bucks to a strong start.', 'general', CURRENT_DATE - 2, 'Bleacher Report', FALSE),
-- Nuggets
(16, 'Nikola Jokic Triple-Double Streak', 'Nikola Jokic continues his incredible triple-double streak, showing why he''s considered the best center in the league.', 'general', CURRENT_DATE - 1, 'NBA.com', FALSE),
-- Suns
(24, 'Kevin Durant Scoring Title Race', 'Kevin Durant is in the running for the scoring title, averaging over 31 points per game this season.', 'general', CURRENT_DATE, 'ESPN', FALSE),
-- 76ers
(4, 'Joel Embiid Injury Update', 'Joel Embiid is expected to return from his hamstring injury in the next 2 weeks, according to team sources.', 'injury', CURRENT_DATE - 12, '76ers PR', FALSE),
-- Heat
(13, 'Jimmy Butler Leads Heat to Victory', 'Jimmy Butler''s leadership and clutch play have been key to the Heat''s recent success.', 'general', CURRENT_DATE - 1, 'Heat.com', FALSE),
-- Mavericks
(26, 'Luka Doncic Historic Performance', 'Luka Doncic recorded a historic 50-point triple-double, joining elite company in NBA history.', 'general', CURRENT_DATE - 3, 'Mavs.com', TRUE),
-- Clippers
(22, 'Kawhi Leonard Out with Groin Strain', 'The Clippers will be without Kawhi Leonard for the next 2 weeks as he recovers from a groin strain.', 'injury', CURRENT_DATE - 5, 'Clippers PR', FALSE),
-- Thunder
(18, 'Shai Gilgeous-Alexander All-Star Campaign', 'Shai Gilgeous-Alexander is making a strong case for All-Star selection with his outstanding play this season.', 'general', CURRENT_DATE - 2, 'Thunder.com', FALSE),
-- Timberwolves
(17, 'Anthony Edwards Rising Star', 'Anthony Edwards continues to develop into one of the league''s brightest young stars.', 'general', CURRENT_DATE - 1, 'NBA.com', FALSE),
-- Kings
(25, 'De''Aaron Fox Clutch Performance', 'De''Aaron Fox has been clutch for the Kings, hitting multiple game-winning shots this season.', 'general', CURRENT_DATE, 'Kings.com', FALSE);

