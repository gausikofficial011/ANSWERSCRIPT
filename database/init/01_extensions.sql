-- Enable uuid-ossp extension for UUID generation functions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm extension for trigram matching (fuzzy text search)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
