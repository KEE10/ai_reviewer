-- CREATE TABLES
CREATE TABLE IF NOT EXISTS pull_requests (
    id BIGSERIAL PRIMARY KEY,
    pull_request_id VARCHAR NOT NULL UNIQUE,
    title VARCHAR NOT NULL,
    description VARCHAR,
    repo_owner VARCHAR NOT NULL,
    repo_name VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews(
    id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT REFERENCES pull_requests(id) on delete CASCADE,
    status VARCHAR not NULL DEFAULT 'created',
    summary VARCHAR,
    details JSONB,
    ai_model VARCHAR not NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS review_comments (
    id BIGSERIAL PRIMARY KEY,
    review_id BIGINT REFERENCES reviews(id) on delete CASCADE,
    file_path VARCHAR not NULL,
    line_number BIGINT not NULL,
    severity VARCHAR not NULL,
    message VARCHAR not NULL
);

-- INDEXES
CREATE INDEX idx_pull_requests_repo on pull_requests(repo_owner);
CREATE INDEX idx_reviews_pr_id_status on reviews(pull_request_id, status) INCLUDE (details, ai_model, created_at, summary);
CREATE INDEX idx_review_comments_rv_id on review_comments(review_id) INCLUDE (file_path, line_number, severity);
