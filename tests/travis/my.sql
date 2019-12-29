USE mysql;

CREATE USER 't_sa'@'localhost' IDENTIFIED BY 't_sa';

CREATE DATABASE t_sa;
CREATE DATABASE t_sa_1;
CREATE DATABASE t_sa_2;

GRANT ALL PRIVILEGES ON t_sa.* TO 't_sa'@'localhost';
GRANT ALL PRIVILEGES ON t_sa_1.* TO 't_sa'@'localhost';
GRANT ALL PRIVILEGES ON t_sa_2.* TO 't_sa'@'localhost';
