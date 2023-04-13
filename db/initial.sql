CREATE TABLE IF NOT EXISTS quizzes (
    id BIGINT PRIMARY KEY,
    description VARCHAR(255),
    answer VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS admins (
    username VARCHAR(255)
);


INSERT INTO quizzes VALUES 
    (0, 'Mikä sun nimi on??', 'Samu'),
    (1, 'Mikä päivä tänään on??', 'PERJANTAI!'),
    (2, 'Toimiiko tää botti??', 'Ei paperilla...')
ON CONFLICT DO NOTHING;

INSERT INTO admins VALUES 
    ('kronkeli')
ON CONFLICT DO NOTHING;
