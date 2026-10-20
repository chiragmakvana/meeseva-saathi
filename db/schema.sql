-- MeeSeva Saathi database schema (generated from app/models.py; SQLite dialect)
-- Regenerate: python -m scripts.export_schema   |   Load sample data: python -m app.seed

CREATE TABLE districts (
	id INTEGER NOT NULL, 
	name_en VARCHAR(80) NOT NULL, 
	name_te VARCHAR(80) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name_en)
);

CREATE TABLE documents (
	id INTEGER NOT NULL, 
	code VARCHAR(20) NOT NULL, 
	name_en VARCHAR(120) NOT NULL, 
	name_te VARCHAR(120) NOT NULL, 
	name_hi VARCHAR(120) NOT NULL, 
	name_ur VARCHAR(120) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (code)
);

CREATE TABLE otp_codes (
	id INTEGER NOT NULL, 
	mobile VARCHAR(10) NOT NULL, 
	code_hash VARCHAR(64) NOT NULL, 
	expires_at DATETIME NOT NULL, 
	attempts INTEGER NOT NULL, 
	used BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_otp_codes_mobile ON otp_codes (mobile);

CREATE TABLE services (
	id INTEGER NOT NULL, 
	code VARCHAR(10) NOT NULL, 
	category VARCHAR(40) NOT NULL, 
	department VARCHAR(80) NOT NULL, 
	name_en VARCHAR(120) NOT NULL, 
	name_te VARCHAR(120) NOT NULL, 
	name_hi VARCHAR(120) NOT NULL, 
	name_ur VARCHAR(120) NOT NULL, 
	description_en TEXT NOT NULL, 
	eligibility_en TEXT NOT NULL, 
	fee_inr INTEGER NOT NULL, 
	sla_days INTEGER NOT NULL, 
	keywords TEXT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (code)
);

CREATE TABLE centres (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	district_id INTEGER NOT NULL, 
	address VARCHAR(255) NOT NULL, 
	lat FLOAT NOT NULL, 
	lng FLOAT NOT NULL, 
	open_hours VARCHAR(60) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(district_id) REFERENCES districts (id)
);

CREATE TABLE service_documents (
	service_id INTEGER NOT NULL, 
	document_id INTEGER NOT NULL, 
	mandatory BOOLEAN NOT NULL, 
	PRIMARY KEY (service_id, document_id), 
	FOREIGN KEY(service_id) REFERENCES services (id) ON DELETE CASCADE, 
	FOREIGN KEY(document_id) REFERENCES documents (id)
);

CREATE TABLE users (
	id INTEGER NOT NULL, 
	mobile VARCHAR(10) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	preferred_lang VARCHAR(2) NOT NULL, 
	district_id INTEGER, 
	role VARCHAR(10) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_user_role CHECK (role in ('citizen','official')), 
	CONSTRAINT ck_user_lang CHECK (preferred_lang in ('en','te','hi','ur')), 
	FOREIGN KEY(district_id) REFERENCES districts (id)
);

CREATE UNIQUE INDEX ix_users_mobile ON users (mobile);

CREATE TABLE applications (
	id INTEGER NOT NULL, 
	reference_no VARCHAR(20) NOT NULL, 
	user_id INTEGER NOT NULL, 
	service_id INTEGER NOT NULL, 
	applicant_name VARCHAR(120) NOT NULL, 
	purpose VARCHAR(255) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	remarks TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_application_status CHECK (status in ('draft','submitted','under_verification','needs_documents','approved','rejected')), 
	UNIQUE (reference_no), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(service_id) REFERENCES services (id)
);

CREATE INDEX ix_applications_user_id ON applications (user_id);

CREATE TABLE notifications (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	title VARCHAR(160) NOT NULL, 
	body TEXT NOT NULL, 
	read BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_notifications_user_id ON notifications (user_id);

CREATE TABLE queries (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	text TEXT NOT NULL, 
	lang VARCHAR(2) NOT NULL, 
	matched_service_id INTEGER, 
	confidence FLOAT NOT NULL, 
	source VARCHAR(10) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(matched_service_id) REFERENCES services (id)
);

CREATE TABLE application_documents (
	id INTEGER NOT NULL, 
	application_id INTEGER NOT NULL, 
	document_id INTEGER NOT NULL, 
	provided BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(application_id) REFERENCES applications (id) ON DELETE CASCADE, 
	FOREIGN KEY(document_id) REFERENCES documents (id)
);

CREATE INDEX ix_application_documents_application_id ON application_documents (application_id);

CREATE TABLE feedback (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	query_id INTEGER, 
	service_id INTEGER, 
	rating INTEGER NOT NULL, 
	comment TEXT NOT NULL, 
	sentiment VARCHAR(10) NOT NULL, 
	topic VARCHAR(30) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_feedback_rating CHECK (rating between 1 and 5), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(query_id) REFERENCES queries (id), 
	FOREIGN KEY(service_id) REFERENCES services (id)
);
