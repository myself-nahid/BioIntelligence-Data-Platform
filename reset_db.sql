-- ========= PART 1: DROP EVERYTHING FOR A CLEAN SLATE =========
DROP MATERIALIZED VIEW IF EXISTS most_watched;
DROP MATERIALIZED VIEW IF EXISTS mechanism_crowding;
DROP TABLE IF EXISTS user_events, data_quality_logs, job_run_logs, watchlists, alerts, investigator_collaborations, investigators, trial_predictions, ml_models, trials CASCADE;


-- ========= PART 2: CREATE ALL TABLES AND VIEWS =========

-- A new 'trials' table is needed as a source for many features
CREATE TABLE trials (
    trial_id VARCHAR(50) PRIMARY KEY,
    trial_description TEXT,
    phase VARCHAR(50),
    status VARCHAR(50),
    indication VARCHAR(255),
    sponsor_size INT,
    mechanism_of_action VARCHAR(255),
    investigator_id UUID,
    outcome VARCHAR(50) -- 'Success' or 'Failure'
);

CREATE TABLE user_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    user_type VARCHAR(20) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100),
    entity_type VARCHAR(50),
    metadata JSONB,
    request_id UUID,
    event_version VARCHAR(10) DEFAULT 'v1.0',
    schema_version VARCHAR(10) DEFAULT 's1.0',
    "timestamp" TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_user_events_user ON user_events(user_id, "timestamp" DESC);

CREATE TABLE data_quality_logs ( log_id SERIAL PRIMARY KEY, job_name TEXT NOT NULL, run_date DATE DEFAULT CURRENT_DATE, anomalies JSONB, status VARCHAR(20) CHECK (status IN ('PASS','WARN','FAIL')), created_at TIMESTAMPTZ DEFAULT NOW() );
CREATE TABLE job_run_logs ( job_run_id SERIAL PRIMARY KEY, job_name TEXT NOT NULL, start_time TIMESTAMPTZ NOT NULL, end_time TIMESTAMPTZ, duration_ms INT, success_flag BOOLEAN, error_message TEXT, records_processed INT, alert_on_fail BOOLEAN DEFAULT TRUE, created_at TIMESTAMPTZ DEFAULT NOW() );

CREATE TABLE watchlists ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), user_id UUID NOT NULL, entity_type VARCHAR(50) NOT NULL, entity_id VARCHAR(100) NOT NULL, added_at TIMESTAMPTZ DEFAULT NOW(), removed_at TIMESTAMPTZ );
CREATE TABLE alerts ( alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), user_id UUID NOT NULL, entity_type VARCHAR(50) NOT NULL, entity_id VARCHAR(100) NOT NULL, alert_type VARCHAR(50) NOT NULL, title TEXT NOT NULL, message TEXT NOT NULL, urgency VARCHAR(20) DEFAULT 'normal', created_at TIMESTAMPTZ DEFAULT NOW(), sent_at TIMESTAMPTZ, opened_at TIMESTAMPTZ, clicked_at TIMESTAMPTZ, dismissed_at TIMESTAMPTZ );

CREATE TABLE investigators ( investigator_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), name VARCHAR(255) NOT NULL, institution VARCHAR(255), total_trials INT DEFAULT 0, successful_trials INT DEFAULT 0, success_rate DECIMAL(5,2) DEFAULT 0.0, influence_score DECIMAL(5,2) DEFAULT 0.0, last_updated TIMESTAMPTZ DEFAULT NOW() );
CREATE TABLE investigator_collaborations ( collab_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), investigator_a_id UUID REFERENCES investigators(investigator_id), investigator_b_id UUID REFERENCES investigators(investigator_id), collaboration_count INT DEFAULT 1, CHECK (investigator_a_id < investigator_b_id) );

CREATE TABLE trial_predictions ( prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), trial_id VARCHAR(50) NOT NULL, drug_id VARCHAR(100), predicted_probability DECIMAL(5,4), confidence_lower DECIMAL(5,4), confidence_upper DECIMAL(5,4), model_version VARCHAR(10), created_at TIMESTAMPTZ DEFAULT NOW(), UNIQUE(trial_id, model_version) );
CREATE TABLE ml_models ( model_id SERIAL PRIMARY KEY, name TEXT NOT NULL, version TEXT NOT NULL, trained_on DATE NOT NULL, auc FLOAT, calibration_score FLOAT, notes TEXT, artifact_path TEXT, UNIQUE(name, version) );

-- Materialized View for Feature #3: Mechanism Crowding
CREATE MATERIALIZED VIEW mechanism_crowding AS
SELECT
    mechanism_of_action,
    phase,
    COUNT(*) as competitor_count,
    CASE
        WHEN COUNT(*) >= 10 THEN 100
        WHEN COUNT(*) >= 7 THEN 80
        WHEN COUNT(*) >= 5 THEN 60
        WHEN COUNT(*) >= 3 THEN 40
        ELSE 20
    END as crowding_risk_score
FROM trials
WHERE phase IN ('Phase II', 'Phase III') AND status = 'Active'
GROUP BY mechanism_of_action, phase;

CREATE UNIQUE INDEX idx_mechanism_crowding_pk ON mechanism_crowding(mechanism_of_action, phase);


-- ========= PART 3: INSERT RICHER SEED DATA FOR TESTING =========

-- Create two investigators
INSERT INTO investigators (investigator_id, name, institution, success_rate, influence_score) VALUES
('a1a1a1a1-1111-1111-1111-111111111111', 'Dr. Jane Smith', 'PharmaCo', 0.82, 95.5),
('b2b2b2b2-2222-2222-2222-222222222222', 'Dr. John Doe', 'BioGen', 0.75, 88.0);

-- Create some trials for them
INSERT INTO trials (trial_id, trial_description, phase, status, indication, sponsor_size, mechanism_of_action, investigator_id, outcome) VALUES
-- Active Trials for Prediction
('NCT00000001', 'A Phase II study of Drug X in metastatic breast cancer.', 'Phase II', 'Active', 'Oncology', 750, 'mTOR Inhibitor', 'a1a1a1a1-1111-1111-1111-111111111111', NULL),
('NCT00000002', 'Trial of Compound Y for psoriasis.', 'Phase II', 'Active', 'Dermatology', 500, 'JAK Inhibitor', 'b2b2b2b2-2222-2222-2222-222222222222', NULL),

-- NEW, RICHER TRAINING DATA
('NCT00000003', 'A past successful Phase II trial for an mTOR inhibitor with a top investigator.', 'Phase II', 'Completed', 'Oncology', 1000, 'mTOR Inhibitor', 'a1a1a1a1-1111-1111-1111-111111111111', 'Success'),
('NCT00000004', 'A past failed Phase II trial for a JAK inhibitor with a less experienced investigator.', 'Phase II', 'Completed', 'Dermatology', 200, 'JAK Inhibitor', 'b2b2b2b2-2222-2222-2222-222222222222', 'Failure'),
('NCT00000005', 'Another successful mTOR trial that was very crowded.', 'Phase II', 'Completed', 'Oncology', 1200, 'mTOR Inhibitor', 'a1a1a1a1-1111-1111-1111-111111111111', 'Success'),
('NCT00000006', 'A failed mTOR trial from a small sponsor.', 'Phase II', 'Completed', 'Oncology', 50, 'mTOR Inhibitor', 'b2b2b2b2-2222-2222-2222-222222222222', 'Failure'),
('NCT00000007', 'Successful JAK inhibitor study, large enrollment.', 'Phase II', 'Completed', 'Dermatology', 1500, 'JAK Inhibitor', 'a1a1a1a1-1111-1111-1111-111111111111', 'Success'),
('NCT00000008', 'A Phase III trial to be ignored by the training query.', 'Phase III', 'Completed', 'Oncology', 2000, 'mTOR Inhibitor', 'a1a1a1a1-1111-1111-1111-111111111111', 'Success');