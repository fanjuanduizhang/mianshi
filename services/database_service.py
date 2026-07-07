import sqlite3
import json
import os
from datetime import datetime
from config import CHROMADB_PATH

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "job_hunter.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE DEFAULT 'default_user',
        education TEXT,
        school TEXT,
        major TEXT,
        target_position TEXT,
        skills_json TEXT DEFAULT '[]',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS job_description (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        position TEXT,
        location TEXT,
        raw_text TEXT NOT NULL,
        extracted_skills_json TEXT,
        match_score REAL,
        gap_analysis_json TEXT,
        ai_analysis TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS study_plan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jd_id INTEGER,
        title TEXT NOT NULL,
        plan_json TEXT NOT NULL,
        priority INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        estimated_hours INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (jd_id) REFERENCES job_description(id) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS question_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT NOT NULL,
        category TEXT,
        is_correct INTEGER,
        answer_text TEXT,
        is_collected INTEGER DEFAULT 0,
        review_count INTEGER DEFAULT 0,
        next_review_at TEXT,
        last_review_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(question_id)
    );
    
    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        mastered_count INTEGER DEFAULT 0,
        total_count INTEGER DEFAULT 0,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(category)
    );
    
    CREATE TABLE IF NOT EXISTS interview_session (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        position TEXT,
        questions_json TEXT,
        answers_json TEXT,
        score REAL,
        feedback TEXT,
        duration INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS resume_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT,
        resume_text TEXT,
        target_position TEXT,
        analysis_json TEXT,
        suggestions TEXT,
        skills_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("SELECT COUNT(*) FROM user_profile")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO user_profile (username) VALUES ('default_user')")
    
    conn.commit()
    conn.close()

def get_user_profile():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE username = 'default_user'")
    row = cursor.fetchone()
    conn.close()
    if row:
        profile = dict(row)
        profile['skills'] = json.loads(profile.get('skills_json', '[]'))
        return profile
    return None

def update_user_profile(data):
    conn = get_db()
    cursor = conn.cursor()
    skills_json = json.dumps(data.get('skills', []), ensure_ascii=False)
    cursor.execute("""
        UPDATE user_profile 
        SET education=?, school=?, major=?, target_position=?, skills_json=?, updated_at=?
        WHERE username='default_user'
    """, (
        data.get('education'), data.get('school'), data.get('major'),
        data.get('target_position'), skills_json,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def save_jd_analysis(jd_data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_description (company, position, location, raw_text, extracted_skills_json, match_score, gap_analysis_json, ai_analysis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        jd_data.get('company'), jd_data.get('position'), jd_data.get('location'),
        jd_data.get('raw_text'),
        json.dumps(jd_data.get('extracted_skills', []), ensure_ascii=False),
        jd_data.get('match_score'),
        json.dumps(jd_data.get('gap_analysis', {}), ensure_ascii=False),
        jd_data.get('ai_analysis')
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_jd_list(limit=10):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, company, position, match_score, created_at FROM job_description ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_study_plan(plan_data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO study_plan (jd_id, title, plan_json, priority, status, estimated_hours)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        plan_data.get('jd_id'), plan_data.get('title'),
        json.dumps(plan_data.get('plan', []), ensure_ascii=False),
        plan_data.get('priority', 0), plan_data.get('status', 'pending'),
        plan_data.get('estimated_hours', 0)
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_study_plans(status=None):
    conn = get_db()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM study_plan WHERE status=? ORDER BY priority DESC, created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM study_plan ORDER BY priority DESC, created_at DESC")
    rows = cursor.fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d['plan'] = json.loads(d.get('plan_json', '[]'))
        result.append(d)
    conn.close()
    return result

def update_study_plan_status(plan_id, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE study_plan SET status=?, updated_at=? WHERE id=?", 
                   (status, datetime.now().isoformat(), plan_id))
    conn.commit()
    conn.close()

def save_question_record(record):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO question_record 
        (question_id, category, is_correct, answer_text, is_collected, review_count, next_review_at, last_review_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record['question_id'], record.get('category'),
        record.get('is_correct'), record.get('answer_text'),
        record.get('is_collected', 0),
        record.get('review_count', 0),
        record.get('next_review_at'),
        record.get('last_review_at'),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_question_record(question_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM question_record WHERE question_id=?", (question_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_collected_questions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM question_record WHERE is_collected=1 ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_review_questions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM question_record WHERE next_review_at <= datetime('now') ORDER BY next_review_at ASC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_user_progress(category, mastered_count, total_count):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_progress (category, mastered_count, total_count)
        VALUES (?, ?, ?)
        ON CONFLICT(category) DO UPDATE SET 
            mastered_count=excluded.mastered_count,
            total_count=excluded.total_count,
            updated_at=CURRENT_TIMESTAMP
    """, (category, mastered_count, total_count))
    conn.commit()
    conn.close()

def get_all_progress():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_progress")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_interview_session(session_data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interview_session (position, questions_json, answers_json, score, feedback, duration)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session_data.get('position'),
        json.dumps(session_data.get('questions', []), ensure_ascii=False),
        json.dumps(session_data.get('answers', {}), ensure_ascii=False),
        session_data.get('score'),
        session_data.get('feedback'),
        session_data.get('duration')
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_interview_sessions(limit=5):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, position, score, created_at FROM interview_session ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_resume_analysis(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resume_analysis (file_name, resume_text, target_position, analysis_json, suggestions, skills_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get('file_name'), data.get('resume_text'), data.get('target_position'),
        json.dumps(data.get('analysis', {}), ensure_ascii=False),
        data.get('suggestions'),
        json.dumps(data.get('skills', []), ensure_ascii=False)
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id
