-- Offline SQL migration for creating the `documents` table
-- Generated for review; does NOT execute against the DB

-- Upgrade: create table
CREATE TABLE IF NOT EXISTS documents (
    pyme_id UUID NOT NULL,
    contenido TEXT NOT NULL,
    firma_digital TEXT,
    fecha_firma TIMESTAMP,
    id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT documents_pkey PRIMARY KEY (id),
    CONSTRAINT documents_pyme_id_fkey FOREIGN KEY (pyme_id) REFERENCES pymes (id)
);

-- Downgrade: drop table
-- DROP TABLE IF EXISTS documents;
