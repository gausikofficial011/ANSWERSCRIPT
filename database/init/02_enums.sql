-- Define Exam Status ENUM
DO $$ BEGIN
    CREATE TYPE exam_status AS ENUM ('draft', 'active', 'closed', 'archived');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Define Answer Sheet Status ENUM
DO $$ BEGIN
    CREATE TYPE answer_sheet_status AS ENUM (
        'uploaded', 'queued', 'processing', 'ocr_done', 'evaluated', 'verified', 'completed', 'failed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Define Grading Mode ENUM
DO $$ BEGIN
    CREATE TYPE grading_mode AS ENUM ('ai', 'manual', 'hybrid');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Define Pass/Fail Status ENUM
DO $$ BEGIN
    CREATE TYPE pass_fail_status AS ENUM ('pass', 'fail', 'absent', 'incomplete');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Define Plagiarism Status ENUM
DO $$ BEGIN
    CREATE TYPE plagiarism_status AS ENUM ('detected', 'reviewed', 'dismissed', 'confirmed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Define Notification Type ENUM
DO $$ BEGIN
    CREATE TYPE notification_type AS ENUM ('info', 'success', 'warning', 'error');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Define Audit Log Status ENUM
DO $$ BEGIN
    CREATE TYPE audit_status AS ENUM ('success', 'failure');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
