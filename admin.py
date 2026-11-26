
import streamlit as st
import os

import database as db

st.set_page_config(
    page_title="Admin Live Count | Rapat Anggota XX",
    page_icon="🔐",
    layout="wide"
)

db.init_db()

# =====================================================
# ADMIN LOGIN
# =====================================================

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not ADMIN_PASSWORD:
    st.error(
        "ADMIN_PASSWORD belum diatur. "
        "Atur password melalui environment variable."
    )
    st.stop()

if not st.session_state.admin_logged_in:

    st.title("🔐 Admin Live Count")
    st.caption("Rapat Anggota XX | PPGT Jemaat Labuang Baji")

    password = st.text_input(
        "Password Admin",
        type="password"
    )

    if st.button("Login", use_container_width=True):

        if password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Password salah.")

    st.stop()


# =====================================================
# HEADER
# =====================================================

col1, col2 = st.columns([4, 1])

with col1:
    st.title("Admin Live Count")
    st.caption("Panel pengelolaan penghitungan suara Rapat Anggota XX")

with col2:
    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()

st.divider()


# =====================================================
# PILIH JABATAN
# =====================================================

positions = {
    "Ketua": "ketua",
    "Sekretaris": "sekretaris",
    "Bendahara": "bendahara"
}

selected = st.selectbox(
    "Pilih Jabatan",
    list(positions.keys())
)

position = positions[selected]

election = db.get_election(position)
candidates = db.get_candidates(position)

status = election["status"]

# =====================================================
# STATUS
# =====================================================

st.subheader(f"Pemilihan {selected}")

if status == "Persiapan":
    st.info("Pemilihan belum dimulai.")

elif status == "Berlangsung":
    st.success("Penghitungan sedang berlangsung.")

else:
    st.success("Penghitungan telah selesai dan dikunci.")

# =====================================================
# PENGELOLAAN CALON
# =====================================================

st.subheader("Daftar Calon")

if status == "Persiapan":

    with st.form("add_candidate_form"):

        candidate_name = st.text_input(
            "Nama calon",
            placeholder="Masukkan nama lengkap calon"
        )

        submitted = st.form_submit_button(
            "Tambah Calon",
            use_container_width=True
        )

        if submitted:

            success, message = db.add_candidate(
                position,
                candidate_name
            )

            if success:
                st.success(message)
            else:
                st.error(message)

            st.rerun()

else:
    st.caption("Daftar calon sudah dikunci karena penghitungan telah dimulai.")

candidates = db.get_candidates(position)

if not candidates:
    st.warning("Belum ada calon yang ditambahkan.")

for candidate in candidates:

    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        st.write(f"**{candidate['name']}**")

    with col2:
        st.write(f"{candidate['votes']} suara")

    with col3:

        if status == "Persiapan":

            if st.button(
                "Hapus",
                key=f"delete_{candidate['id']}"
            ):
                db.delete_candidate(candidate["id"])
                st.rerun()

# =====================================================
# TOTAL SUARA
# =====================================================

valid, invalid = db.get_totals(position)
total = valid + invalid

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("Suara Sah", valid)
col2.metric("Suara Tidak Sah", invalid)
col3.metric("Total Suara", total)

# =====================================================
# MULAI PEMILIHAN
# =====================================================

if status == "Persiapan":

    if st.button(
        "MULAI PENGHITUNGAN",
        type="primary",
        use_container_width=True
    ):

        success, message = db.start_election(position)

        if success:
            st.success(message)
        else:
            st.error(message)

        st.rerun()

# =====================================================
# INPUT SUARA
# =====================================================

if status == "Berlangsung":

    st.divider()
    st.subheader("Input Hasil Penghitungan")

    st.caption(
        "Tekan +1 setiap kali surat suara dibacakan "
        "untuk calon yang bersangkutan."
    )

    for candidate in candidates:

        col1, col2, col3 = st.columns([4, 1, 2])

        with col1:
            st.write(f"**{candidate['name']}**")

        with col2:
            st.metric("Suara", candidate["votes"])

        with col3:

            if st.button(
                "+1 Tambah Suara",
                key=f"vote_{candidate['id']}",
                use_container_width=True
            ):

                db.add_vote(position, candidate["id"])
                st.rerun()

    st.divider()

    st.subheader("Suara Tidak Sah")

    if st.button(
        "+1 Suara Tidak Sah",
        use_container_width=True
    ):
        db.add_invalid_vote(position)
        st.rerun()

    st.divider()

    st.subheader("Koreksi Suara")

    st.caption(
        "Gunakan jika terjadi kesalahan input. "
        "Pastikan koreksi sesuai dengan surat suara fisik."
    )

    for candidate in candidates:

        col1, col2, col3 = st.columns([4, 1, 2])

        with col1:
            st.write(candidate["name"])

        with col2:
            st.write(candidate["votes"])

        with col3:

            confirm = st.checkbox(
                "Konfirmasi koreksi",
                key=f"confirm_{candidate['id']}"
            )

            if st.button(
                "-1 Koreksi",
                key=f"correct_{candidate['id']}",
                disabled=not confirm,
                use_container_width=True
            ):

                db.correct_vote(position, candidate["id"])
                st.rerun()

    st.divider()

    st.warning(
        "Pastikan seluruh surat suara sudah dihitung "
        "dan hasil sudah diverifikasi sebelum menyelesaikan."
    )

    if st.button(
        "SELESAIKAN & KUNCI HASIL",
        type="primary",
        use_container_width=True
    ):

        st.session_state.confirm_finish = True

    if st.session_state.get("confirm_finish", False):

        st.warning("Apakah Anda yakin ingin mengunci hasil pemilihan ini?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Ya, Kunci Hasil"):
                db.finish_election(position)
                st.session_state.confirm_finish = False
                st.rerun()

        with col2:
            if st.button("Batalkan"):
                st.session_state.confirm_finish = False
                st.rerun()

# =====================================================
# RIWAYAT INPUT
# =====================================================

st.divider()
st.subheader("Riwayat Penghitungan")

logs = db.get_vote_logs(position)

if logs:

    st.dataframe(
        [
            {
                "Waktu": log["created_at"],
                "Calon": log["candidate_name"],
                "Perubahan": (
                    f"+{log['change_amount']}"
                    if log["change_amount"] > 0
                    else str(log["change_amount"])
                ),
                "Keterangan": log["note"]
            }
            for log in logs
        ],
        use_container_width=True,
        hide_index=True
    )

else:
    st.caption("Belum ada riwayat penghitungan.")
