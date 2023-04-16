CREATE TABLE IF NOT EXISTS quizzes (
    id INT GENERATED ALWAYS AS IDENTITY,
    question VARCHAR(255),
    answer VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS admins (
    username VARCHAR(255)
);


INSERT INTO quizzes (question, answer) VALUES 
    ('Mikä päivä tänään on?', 'Maanantai'),
    ('Mikä tulee aakkosissa l:n jälkeen?', 'm'),
    ('Toimiiko tää botti??', 'Ei')
ON CONFLICT DO NOTHING;

INSERT INTO admins VALUES 
    ('Kronkeli')
ON CONFLICT DO NOTHING;
