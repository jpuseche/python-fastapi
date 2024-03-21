USE python_fastapi;

CREATE TABLE characters(
    id SERIAL PRIMARY KEY,
    marvel_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    modified DATE,
    thumbnail_path VARCHAR(255),
    thumbnail_extension VARCHAR(10)
);