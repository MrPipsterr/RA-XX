
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "live_count.db"

POSITIONS = {
    "ketua": "Ketua",
    "sekretaris": "Sekretaris",
    "bendahara": "Bendahara"
}


from contextlib import contextmanager

@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS elections (
                position TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'Persiapan',
                invalid_votes INTEGER NOT NULL DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position TEXT NOT NULL,
                name TEXT NOT NULL,
                votes INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(position) REFERENCES elections(position),
                UNIQUE(position, name)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS vote_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position TEXT NOT NULL,
                candidate_name TEXT NOT NULL,
                change_amount INTEGER NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL DEFAULT
                    (datetime('now', 'localtime'))
            )
        """)

        for position in POSITIONS:
            conn.execute("""
                INSERT OR IGNORE INTO elections(position)
                VALUES (?)
            """, (position,))


def get_elections():
    with connect() as conn:
        return conn.execute("""
            SELECT * FROM elections
            ORDER BY CASE position
                WHEN 'ketua' THEN 1
                WHEN 'sekretaris' THEN 2
                WHEN 'bendahara' THEN 3
            END
        """).fetchall()


def get_election(position):
    with connect() as conn:
        return conn.execute("""
            SELECT * FROM elections
            WHERE position = ?
        """, (position,)).fetchone()


def get_candidates(position):
    with connect() as conn:
        return conn.execute("""
            SELECT * FROM candidates
            WHERE position = ?
            ORDER BY id
        """, (position,)).fetchall()


def add_candidate(position, name):
    name = name.strip()

    if not name:
        return False, "Nama calon tidak boleh kosong."

    with connect() as conn:
        election = conn.execute("""
            SELECT status FROM elections
            WHERE position = ?
        """, (position,)).fetchone()

        if not election or election["status"] != "Persiapan":
            return False, "Calon hanya bisa ditambahkan saat persiapan."

        try:
            conn.execute("""
                INSERT INTO candidates(position, name)
                VALUES (?, ?)
            """, (position, name))

            return True, "Calon berhasil ditambahkan."

        except sqlite3.IntegrityError:
            return False, "Nama calon sudah terdaftar."


def delete_candidate(candidate_id):
    with connect() as conn:
        candidate = conn.execute("""
            SELECT * FROM candidates WHERE id = ?
        """, (candidate_id,)).fetchone()

        if not candidate:
            return False

        election = conn.execute("""
            SELECT status FROM elections
            WHERE position = ?
        """, (candidate["position"],)).fetchone()

        if election["status"] != "Persiapan":
            return False

        conn.execute("""
            DELETE FROM candidates WHERE id = ?
        """, (candidate_id,))

        return True


def start_election(position):
    with connect() as conn:
        count = conn.execute("""
            SELECT COUNT(*) FROM candidates
            WHERE position = ?
        """, (position,)).fetchone()[0]

        if count < 2:
            return False, "Minimal harus ada 2 calon."

        conn.execute("""
            UPDATE elections
            SET status = 'Berlangsung'
            WHERE position = ? AND status = 'Persiapan'
        """, (position,))

        return True, "Penghitungan dimulai."


def add_vote(position, candidate_id):
    with connect() as conn:
        election = conn.execute("""
            SELECT status FROM elections
            WHERE position = ?
        """, (position,)).fetchone()

        if not election or election["status"] != "Berlangsung":
            return False

        candidate = conn.execute("""
            SELECT name FROM candidates
            WHERE id = ? AND position = ?
        """, (candidate_id, position)).fetchone()

        if not candidate:
            return False

        conn.execute("""
            UPDATE candidates
            SET votes = votes + 1
            WHERE id = ?
        """, (candidate_id,))

        conn.execute("""
            INSERT INTO vote_logs
            (position, candidate_name, change_amount, note)
            VALUES (?, ?, 1, 'Penambahan suara')
        """, (position, candidate["name"]))

        return True


def correct_vote(position, candidate_id):
    with connect() as conn:
        election = conn.execute("""
            SELECT status FROM elections
            WHERE position = ?
        """, (position,)).fetchone()

        if not election or election["status"] != "Berlangsung":
            return False

        candidate = conn.execute("""
            SELECT name, votes FROM candidates
            WHERE id = ? AND position = ?
        """, (candidate_id, position)).fetchone()

        if not candidate or candidate["votes"] <= 0:
            return False

        conn.execute("""
            UPDATE candidates
            SET votes = votes - 1
            WHERE id = ?
        """, (candidate_id,))

        conn.execute("""
            INSERT INTO vote_logs
            (position, candidate_name, change_amount, note)
            VALUES (?, ?, -1, 'Koreksi suara')
        """, (position, candidate["name"]))

        return True


def add_invalid_vote(position):
    with connect() as conn:
        election = conn.execute("""
            SELECT status FROM elections
            WHERE position = ?
        """, (position,)).fetchone()

        if not election or election["status"] != "Berlangsung":
            return False

        conn.execute("""
            UPDATE elections
            SET invalid_votes = invalid_votes + 1
            WHERE position = ?
        """, (position,))

        conn.execute("""
            INSERT INTO vote_logs
            (position, candidate_name, change_amount, note)
            VALUES (?, 'Suara Tidak Sah', 1, 'Penambahan suara tidak sah')
        """, (position,))

        return True


def finish_election(position):
    with connect() as conn:
        conn.execute("""
            UPDATE elections
            SET status = 'Selesai'
            WHERE position = ? AND status = 'Berlangsung'
        """, (position,))


def get_vote_logs(position, limit=30):
    with connect() as conn:
        return conn.execute("""
            SELECT * FROM vote_logs
            WHERE position = ?
            ORDER BY id DESC
            LIMIT ?
        """, (position, limit)).fetchall()


def get_totals(position):
    with connect() as conn:
        result = conn.execute("""
            SELECT
                COALESCE(SUM(votes), 0) AS valid_votes
            FROM candidates
            WHERE position = ?
        """, (position,)).fetchone()

        invalid = conn.execute("""
            SELECT invalid_votes FROM elections
            WHERE position = ?
        """, (position,)).fetchone()

        return result["valid_votes"], invalid["invalid_votes"]
