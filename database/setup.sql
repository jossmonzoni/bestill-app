CREATE TABLE facts (
    id SERIAL PRIMARY KEY,
    fact TEXT NOT NULL,
    details TEXT NOT NULL,
    verse TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO facts (fact, details, verse) VALUES
('The human body regenerates approximately 300 million cells each day.', 'Cells in the human body have different lifespans. Red blood cells last about 120 days, while skin cells regenerate every 2-3 weeks.', 'Psalm 139:14 - I praise you because I am fearfully and wonderfully made; your works are wonderful, I know that full well.');

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    post_type VARCHAR(10) NOT NULL CHECK (post_type IN ('prayer', 'praise')),
    author VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);

CREATE TABLE post_replies (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    content TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO posts (content, post_type, author) VALUES
('Please pray for my upcoming medical procedure next week. I''m feeling anxious and could use your prayers for peace and successful outcomes.', 'prayer', 'Sarah'),
('Grateful to share that my daughter got accepted into her dream college! God is faithful!', 'praise', 'John');
