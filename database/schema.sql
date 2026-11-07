-- =============================================================
--  Base de datos: tech_nueva_eps  (MySQL / MariaDB)
--  Ejecutar:  mysql -u root -p < database/schema.sql
-- =============================================================
-- El archivo está en UTF-8: sin esto, los acentos se guardan dañados (p. ej. "Ã©")
SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS tech_nueva_eps;
USE tech_nueva_eps;

CREATE TABLE IF NOT EXISTS users (
	id INT auto_increment NOT NULL,
	name varchar(100) NOT NULL,
	lastname varchar(100) NOT NULL,
	email varchar(100) NOT NULL,
	password varchar(100) NOT NULL,          -- hash bcrypt (60 caracteres), nunca el texto plano
	created_at DATETIME DEFAULT current_timestamp() NULL,
	updated_at DATETIME NULL DEFAULT NULL ON UPDATE current_timestamp(),
	CONSTRAINT users_pk PRIMARY KEY (id),
	CONSTRAINT users_unique UNIQUE KEY (email)
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;

CREATE TABLE IF NOT EXISTS medications (
	id INT auto_increment NOT NULL,
	name varchar(100) NOT NULL,
	is_pos TINYINT DEFAULT 0 NOT NULL,       -- 1 = POS, 0 = NO POS
	created_at DATETIME DEFAULT current_timestamp() NOT NULL,
	updated_at DATETIME DEFAULT NULL ON UPDATE current_timestamp() NULL,
	CONSTRAINT medications_pk PRIMARY KEY (id),
	CONSTRAINT medications_unique UNIQUE KEY (name)
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;

CREATE TABLE IF NOT EXISTS requests (
	id INT auto_increment NOT NULL,
	user_id INT NOT NULL,
	medication_id INT NOT NULL,
	order_number varchar(100) NULL,
	address varchar(100) NULL,
	phone varchar(20) NULL,
	email varchar(100) NULL,
	created_at DATETIME DEFAULT current_timestamp() NOT NULL,
	CONSTRAINT requests_pk PRIMARY KEY (id),
	CONSTRAINT requests_medications_FK FOREIGN KEY (medication_id) REFERENCES medications(id),
	CONSTRAINT requests_users_FK FOREIGN KEY (user_id) REFERENCES users(id)
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;

-- ---------- Datos de ejemplo ----------
INSERT IGNORE INTO medications (name, is_pos) VALUES
	('Acetaminofén 500 mg',      1),
	('Ibuprofeno 400 mg',        1),
	('Losartán 50 mg',           1),
	('Metformina 850 mg',        1),
	('Omeprazol 20 mg',          1),
	('Adalimumab 40 mg',         0),
	('Insulina Glargina 100 UI', 0),
	('Rituximab 500 mg',         0),
	('Sofosbuvir 400 mg',        0);
