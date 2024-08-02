CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';
SELECT pg_create_physical_replication_slot('replication_slot');
CREATE database tg_bot OWNER postgres;
\c tg_bot postgres;
CREATE TABLE email_tab(
ID SERIAL PRIMARY KEY,
email VARCHAR (100) NOT NULL);
CREATE TABLE phone_tab(
ID SERIAL PRIMARY KEY,
phone VARCHAR (100) NOT NULL);
INSERT INTO email_tab (email)
VALUES ('test1@email.ru'), ('test2@email.ru');
INSERT INTO phone_tab (phone)
VALUES ('+74991111111'), ('8(495)1234567');