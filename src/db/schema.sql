CREATE TABLE incoming_calls (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    caller_number VARCHAR(20),
    called_number VARCHAR(20),
    pbx_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 