-- Create the table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    INDEX (id),
    INDEX (email)
);

-- Optional: Add some seed data
INSERT INTO users (name, email) VALUES ('Admin', 'admin@example.com');
