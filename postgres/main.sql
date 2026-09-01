CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,                     
    firstname VARCHAR(100), 
    lastname VARCHAR(100),
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(225) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(100) NOT NULL UNIQUE
);

CREATE TYPE gametype_enum AS ENUM(
    'cooperative', 
    'strategic', 
    'party', 
    'deduction', 
    'deckbuilder', 
    'filler', 
    'other'
);

CREATE TABLE IF NOT EXISTS games(
    id SERIAL PRIMARY KEY,  
    name VARCHAR(100) NOT NULL,
    min_players INT NOT NULL,
    max_players INT NOT NULL,
    optimal_players INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gametype gametype_enum[] NOT NULL DEFAULT '{"other"}',
    personal_rating INT CHECK (personal_rating >= 1 AND personal_rating <= 5),
    group_rating INT CHECK (group_rating >= 1 AND group_rating <= 5),
    comments VARCHAR(1000),
    playtime INT NOT NULL,
    complexity INT NOT NULL CHECK (complexity >= 1 AND complexity <= 5)
    owner_username VARCHAR(100) REFERENCES users(username) ON DELETE CASCADE
);
