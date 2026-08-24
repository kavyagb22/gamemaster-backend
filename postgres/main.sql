CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,                     
    firstname VARCHAR(100), 
    lastname VARCHAR(100),
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(225) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(100) NOT NULL UNIQUE
);
