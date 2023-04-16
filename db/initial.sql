CREATE TABLE IF NOT EXISTS quizzes (
    id INT GENERATED ALWAYS AS IDENTITY,
    question VARCHAR(255),
    answer VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS admins (
    username VARCHAR(255)
);


INSERT INTO quizzes (question, answer) VALUES 
    ('Mikä sun nimi on??', 'Samu'),
    ('Mikä päivä tänään on??', 'PERJANTAI!'),
    ('Toimiiko tää botti??', 'Ei paperilla...')
ON CONFLICT DO NOTHING;

INSERT INTO admins VALUES 
    ('kronkeli')
ON CONFLICT DO NOTHING;
