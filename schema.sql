CREATE DATABASE discord_bot_db
USE discord_bot_db
CREATE TABLE IF NOT EXISTS game_profiles (     id INT AUTO_INCREMENT PRIMARY KEY,     full_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,     ingame_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,     is_active BOOLEAN DEFAULT FALSE )
CREATE TABLE IF NOT EXISTS nhibeo (  id INT AUTO_INCREMENT PRIMARY KEY,     nhibeo_weight INT)
