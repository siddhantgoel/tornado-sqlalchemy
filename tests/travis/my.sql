USE mysql;

CREATE USER 't_sa'@'localhost' IDENTIFIED BY 't_sa';

CREATE DATABASE t_sa;
GRANT ALL PRIVILEGES ON t_sa.* TO 't_sa'@'localhost';
