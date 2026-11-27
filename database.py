
import streamlit as st
from supabase import create_client


# =========================================================
# CONFIGURATION
# =========================================================

POSITIONS = {
    "ketua": "Ketua",
    "sekretaris": "Sekretaris",
    "bendahara": "Bendahara"
}

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():
    """
    Tabel dan data awal sudah dibuat di Supabase.
    Tidak perlu membuat ulang setiap aplikasi dijalankan.
    """
    pass


# =========================================================
# GET ELECTIONS
# =========================================================

def get_elections():
    response = (
        supabase.table("elections")
        .select("*")
        .execute()
    )

    order = {
        "ketua": 1,
        "sekretaris": 2,
        "bendahara": 3
    }

    return sorted(
        response.data,
        key=lambda row: order.get(row["position"], 99)
    )


def get_election(position):
    response = (
        supabase.table("elections")
        .select("*")
        .eq("position", position)
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None


# =========================================================
# CANDIDATES
# =========================================================

def get_candidates(position):
    response = (
        supabase.table("candidates")
        .select("*")
        .eq("position", position)
        .order("id")
        .execute()
    )

    return response.data


def add_candidate(position, name):
    name = name.strip()

    if not name:
        return False, "Nama calon tidak boleh kosong."

    election = get_election(position)

    if not election or election["status"] != "Persiapan":
        return False, "Calon hanya bisa ditambahkan saat persiapan."

    try:
        supabase.table("candidates").insert({
            "position": position,
            "name": name,
            "votes": 0
        }).execute()

        return True, "Calon berhasil ditambahkan."

    except Exception as e:
        if getattr(e, "code", None) == "23505":
            return False, "Nama calon sudah terdaftar."

        raise


def delete_candidate(candidate_id):
    response = (
        supabase.table("candidates")
        .select("*")
        .eq("id", candidate_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return False

    candidate = response.data[0]
    election = get_election(candidate["position"])

    if not election or election["status"] != "Persiapan":
        return False

    (
        supabase.table("candidates")
        .delete()
        .eq("id", candidate_id)
        .execute()
    )

    return True


# =========================================================
# START ELECTION
# =========================================================

def start_election(position):
    candidates = get_candidates(position)

    if len(candidates) < 2:
        return False, "Minimal harus ada 2 calon."

    election = get_election(position)

    if not election or election["status"] != "Persiapan":
        return False, "Pemilihan hanya bisa dimulai saat persiapan."

    (
        supabase.table("elections")
        .update({"status": "Berlangsung"})
        .eq("position", position)
        .eq("status", "Persiapan")
        .execute()
    )

    return True, "Penghitungan dimulai."


# =========================================================
# ADD VOTE
# =========================================================

def add_vote(position, candidate_id):
    election = get_election(position)

    if not election or election["status"] != "Berlangsung":
        return False

    response = (
        supabase.table("candidates")
        .select("name")
        .eq("id", candidate_id)
        .eq("position", position)
        .limit(1)
        .execute()
    )

    if not response.data:
        return False

    candidate = response.data[0]

    current = (
        supabase.table("candidates")
        .select("votes")
        .eq("id", candidate_id)
        .limit(1)
        .execute()
    )

    if not current.data:
        return False

    new_votes = current.data[0]["votes"] + 1

    (
        supabase.table("candidates")
        .update({"votes": new_votes})
        .eq("id", candidate_id)
        .execute()
    )

    supabase.table("vote_logs").insert({
        "position": position,
        "candidate_name": candidate["name"],
        "change_amount": 1,
        "note": "Penambahan suara"
    }).execute()

    return True


# =========================================================
# CORRECT VOTE
# =========================================================

def correct_vote(position, candidate_id):
    election = get_election(position)

    if not election or election["status"] != "Berlangsung":
        return False

    response = (
        supabase.table("candidates")
        .select("name, votes")
        .eq("id", candidate_id)
        .eq("position", position)
        .limit(1)
        .execute()
    )

    if not response.data:
        return False

    candidate = response.data[0]

    if candidate["votes"] <= 0:
        return False

    (
        supabase.table("candidates")
        .update({"votes": candidate["votes"] - 1})
        .eq("id", candidate_id)
        .execute()
    )

    supabase.table("vote_logs").insert({
        "position": position,
        "candidate_name": candidate["name"],
        "change_amount": -1,
        "note": "Koreksi suara"
    }).execute()

    return True


# =========================================================
# INVALID VOTE
# =========================================================

def add_invalid_vote(position):
    election = get_election(position)

    if not election or election["status"] != "Berlangsung":
        return False

    (
        supabase.table("elections")
        .update({
            "invalid_votes": election["invalid_votes"] + 1
        })
        .eq("position", position)
        .execute()
    )

    supabase.table("vote_logs").insert({
        "position": position,
        "candidate_name": "Suara Tidak Sah",
        "change_amount": 1,
        "note": "Penambahan suara tidak sah"
    }).execute()

    return True


# =========================================================
# FINISH ELECTION
# =========================================================

def finish_election(position):
    (
        supabase.table("elections")
        .update({"status": "Selesai"})
        .eq("position", position)
        .eq("status", "Berlangsung")
        .execute()
    )


# =========================================================
# VOTE LOGS
# =========================================================

def get_vote_logs(position, limit=30):
    response = (
        supabase.table("vote_logs")
        .select("*")
        .eq("position", position)
        .order("id", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data


# =========================================================
# TOTALS
# =========================================================

def get_totals(position):
    candidates = get_candidates(position)

    valid_votes = sum(
        candidate["votes"] for candidate in candidates
    )

    election = get_election(position)

    invalid_votes = (
        election["invalid_votes"] if election else 0
    )

    return valid_votes, invalid_votes
