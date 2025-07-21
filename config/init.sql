-- Script d'initialisation de la base de données AI PACS
-- Exécuté automatiquement lors du premier démarrage de PostgreSQL

-- Création de l'utilisateur (si n'existe pas)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'ai_pacs_user') THEN
        CREATE USER ai_pacs_user WITH PASSWORD 'changeme';
    END IF;
END
$$;

-- Création de la base de données
CREATE DATABASE ai_pacs OWNER ai_pacs_user;

-- Connexion à la base AI PACS
\c ai_pacs;

-- Accordation des privilèges
GRANT ALL PRIVILEGES ON DATABASE ai_pacs TO ai_pacs_user;
GRANT ALL ON SCHEMA public TO ai_pacs_user;

-- Table des études DICOM
CREATE TABLE IF NOT EXISTS studies (
    id SERIAL PRIMARY KEY,
    study_uid VARCHAR(64) UNIQUE NOT NULL,
    patient_id VARCHAR(64),
    patient_name VARCHAR(255),
    patient_birth_date DATE,
    patient_sex VARCHAR(1),
    study_date DATE,
    study_time TIME,
    study_description TEXT,
    modality VARCHAR(16),
    accession_number VARCHAR(32),
    institution_name VARCHAR(255),
    referring_physician VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table des séries DICOM
CREATE TABLE IF NOT EXISTS series (
    id SERIAL PRIMARY KEY,
    study_id INTEGER REFERENCES studies(id) ON DELETE CASCADE,
    series_uid VARCHAR(64) UNIQUE NOT NULL,
    series_number INTEGER,
    series_description TEXT,
    modality VARCHAR(16),
    body_part_examined VARCHAR(64),
    patient_position VARCHAR(16),
    protocol_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des instances DICOM
CREATE TABLE IF NOT EXISTS instances (
    id SERIAL PRIMARY KEY,
    series_id INTEGER REFERENCES series(id) ON DELETE CASCADE,
    sop_instance_uid VARCHAR(64) UNIQUE NOT NULL,
    instance_number INTEGER,
    image_position_patient TEXT,
    image_orientation_patient TEXT,
    pixel_spacing TEXT,
    rows INTEGER,
    columns INTEGER,
    bits_allocated INTEGER,
    bits_stored INTEGER,
    file_path VARCHAR(512),
    file_size BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des analyses IA
CREATE TABLE IF NOT EXISTS ai_analyses (
    id SERIAL PRIMARY KEY,
    instance_id INTEGER REFERENCES instances(id) ON DELETE CASCADE,
    study_uid VARCHAR(64),
    series_uid VARCHAR(64),
    instance_uid VARCHAR(64),
    model_name VARCHAR(64),
    model_version VARCHAR(32),
    confidence_score FLOAT,
    processing_time FLOAT,
    status VARCHAR(32) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Table des anomalies détectées
CREATE TABLE IF NOT EXISTS findings (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES ai_analyses(id) ON DELETE CASCADE,
    finding_type VARCHAR(64),
    confidence FLOAT,
    location_x INTEGER,
    location_y INTEGER,
    location_z INTEGER DEFAULT 0,
    location_width INTEGER,
    location_height INTEGER,
    location_depth INTEGER DEFAULT 1,
    severity VARCHAR(16) CHECK (severity IN ('low', 'medium', 'high')),
    description TEXT,
    measurements JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des rapports générés
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES ai_analyses(id) ON DELETE CASCADE,
    study_uid VARCHAR(64),
    report_type VARCHAR(16) CHECK (report_type IN ('DICOM_SR', 'PDF', 'HTML')),
    report_format VARCHAR(16) DEFAULT 'DICOM_SR',
    file_path VARCHAR(512),
    file_size BIGINT,
    sent_to_pacs BOOLEAN DEFAULT FALSE,
    pacs_response TEXT,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des logs système
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(16),
    message TEXT,
    module VARCHAR(64),
    function_name VARCHAR(64),
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour optimiser les performances
CREATE INDEX IF NOT EXISTS idx_studies_patient_id ON studies(patient_id);
CREATE INDEX IF NOT EXISTS idx_studies_study_date ON studies(study_date);
CREATE INDEX IF NOT EXISTS idx_studies_modality ON studies(modality);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_status ON ai_analyses(status);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_created_at ON ai_analyses(created_at);
CREATE INDEX IF NOT EXISTS idx_findings_analysis_id ON findings(analysis_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_reports_sent_to_pacs ON reports(sent_to_pacs);

-- Fonction pour mettre à jour le timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger pour la mise à jour automatique du timestamp
CREATE TRIGGER update_studies_updated_at 
    BEFORE UPDATE ON studies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Vues utiles pour les statistiques
CREATE OR REPLACE VIEW study_stats AS
SELECT 
    DATE(created_at) as date,
    modality,
    COUNT(*) as study_count
FROM studies 
GROUP BY DATE(created_at), modality
ORDER BY date DESC;

CREATE OR REPLACE VIEW analysis_stats AS
SELECT 
    DATE(created_at) as date,
    status,
    COUNT(*) as analysis_count,
    AVG(processing_time) as avg_processing_time,
    AVG(confidence_score) as avg_confidence
FROM ai_analyses 
GROUP BY DATE(created_at), status
ORDER BY date DESC;

-- Accordation des privilèges sur toutes les tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_pacs_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_pacs_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ai_pacs_user;

-- Message de fin
SELECT 'Base de données AI PACS initialisée avec succès!' as message;
