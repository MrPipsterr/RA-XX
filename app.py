import database as db
import streamlit as st
import base64
import html
from datetime import date
from pathlib import Path
import streamlit.components.v1 as components

# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

from database import (
    init_db,
    get_elections,
    get_candidates,
    add_candidate,
    add_vote,
    correct_vote,
    get_totals
)

db.init_db()

LOGO_PATH = BASE_DIR / "logo_ppgt.png"
PDF_PATH = BASE_DIR / "dokumen" / "rancangan_keputusan.pdf"

EVENT_DATE = date(2026, 11, 28)

st.set_page_config(
    page_title="Rapat Anggota XX | PPGT JLB",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# MANUAL LIVE AGENDA
# UPDATE BAGIAN INI SAAT KEGIATAN BERUBAH
# =========================================================

LIVE_STATUS = "SIDANG DIPENDING"

CURRENT_ACTIVITY = "SIDANG DISKORS"
CURRENT_TOPIC = "Seluruh Kegiatan sedang Diskors"

NEXT_ACTIVITY = "SIDANG PLENO IV"
NEXT_TOPIC = "Pembahasan dan Pengesahan GBPP"

# Contoh update:
#
# LIVE_STATUS = "SEDANG BERLANGSUNG"
# CURRENT_ACTIVITY = "SIDANG PLENO I"
# CURRENT_TOPIC = "Pembahasan dan Pengesahan Tata Tertib"
# NEXT_ACTIVITY = "SIDANG PLENO II"
# NEXT_TOPIC = "Laporan Pertanggungjawaban Pengurus"
#
# Status yang tersedia:
# BELUM DIMULAI
# SEDANG BERLANGSUNG
# SELESAI

# =========================================================
# RUNDOWN DATA
# =========================================================

schedule = [

    {
        "time": "10.00-10.15",
        "activity": "DOA PAGI",
        "person": "Panitia",
        "details": []
    },

    {
        "time": "10.15-12.30",
        "activity": "SIDANG PLENO IV",
        "person": "Pimpinan Sidang",
        "details": [
            ("", "Sidang Komisi", "", 0),
        ]
    },

    {
        "time": "12.30-13.00",
        "activity": "MAKAN SIANG",
        "person": "Panitia",
        "details": []
    },

    {
        "time": "13.00-16.00",
        "activity": "SIDANG PLENO V",
        "person": "Pimpinan Sidang",
        "details": [
            ("", "Pembahasan Hasil Sidang Komisi", "", 0),
        ]
    },

    {
        "time": "16.00-19.00",
        "activity": "",
        "person": "Pimpinan Sidang",
        "details": [
            ("", "Lanjutan Pembahasan Komisi", "", 0),
        ]
    },

    {
        "time": "19.00-19.30",
        "activity": "MAKAN MALAM",
        "person": "Panitia",
        "details": []
    },

    {
        "time": "19.30-20.30",
        "activity": "LANJUTAN SIDANG PLENO V",
        "person": "Pimpinan Sidang",
        "details": [
            ("", "Pembahasan Hasil Sidang Komisi", "", 0),
            ("", "Lanjutan Pembahasan Komisi", "", 0),
            ("", "Pengesahan Hasil Sidang Komisi", "", 0),
        ]
    },

    {
        "time": "20.30-22.30",
        "activity": "SIDANG PLENO VI",
        "person": "Pimpinan Sidang",
        "details": [
            ("", "Pemilihan KSB PPGT Jemaat Labuang Baji Periode 2026-2028", "", 0),
            ("", "Pembentukan Tim Formatur", "", 0),
        ]
    },

    {
        "time": "22.30-23.00",
        "activity": "Closing Ceremony",
        "person": "Pimpinan Sidang",
        "details": [
            ("", "Penutupan Rapat Anggota XX PPGT JLB", "", 0),
        ]
    },

    {
        "time": "",
        "activity": "DOA PENUTUP",
        "person": "Panitia",
        "details": []
    },

]

# =========================================================
# GLOBAL CSS
# =========================================================

st.html("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: #f5f7f6;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 1rem;
}

/* JARAK COVER DAN TOMBOL DOWNLOAD */

.document-cover {
    margin-bottom: 0 !important;
}

/* Mengurangi jarak container tombol */
div[data-testid="stDownloadButton"] {
    margin-top: -12px !important;
}

/* HEADER */

.hero-header {
    background: linear-gradient(120deg, #1e4031, #35674d);
    border-radius: 25px;
    padding: 60px 45px;
    margin-bottom: 40px;
    color: white;
}

.hero-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 40px;
}

.hero-text {
    text-align: center;
    flex: 1;
}

.hero-eyebrow {
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 5px;
    color: #b9d8c4;
    margin-bottom: 25px;
}

.hero-text h1 {
    font-size: clamp(25px, 5vw, 65px);
    font-weight: 800;
    color: white;
    margin: 0;
    line-height: 1.2;
}

.hero-text p {
    font-size: 24px;
    color: #d4e5da;
    margin-top: 20px;
    margin-bottom: 0;
}

.hero-logo {
    width: 180px;
    min-width: 140px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.hero-logo img {
    width: 100%;
    max-width: 180px;
    height: auto;
    object-fit: contain;
}

/* SECTION */

.section-title {
    font-size: 29px;
    font-weight: 800;
    color: #173d2d;
    margin-bottom: 5px;
}

.section-subtitle {
    font-size: 24px;
    # color: #829087;
    color: #637545;
    margin-bottom: 20px;
}

/* TABLE */

.schedule-container {
    background: white;
    border: 1px solid #e3e9e4;
    border-radius: 12px;
    padding: 12px;
    overflow-x: auto;
    width: 100%;
    box-sizing: border-box;
}

.schedule-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    color: #252d27;
}

.schedule-table th {
    background: #173d2d;
    color: white;
    padding: 15px 12px;
    text-align: center;
    border: 1px solid #173d2d;
}

.schedule-table td {
    padding: 12px;
    border: 1px solid #e0e7e1;
    vertical-align: middle;
}

.schedule-table .date-row {
    background: #eaf2ec;
    color: #173d2d;
    text-align: center;
    font-weight: 800;
    padding: 12px;
}

.schedule-table .time {
    width: 19%;
    text-align: center;
    white-space: nowrap;
    font-weight: 600;
}

.schedule-table .activity {
    width: 59%;
}

.schedule-table .person {
    width: 22%;
    text-align: center;
}

.schedule-table .main-activity {
    color: #173d2d;
    font-weight: 800;
}

.schedule-table .break-row {
    background: #f5f8f5;
}

.schedule-table .break-row td {
    font-weight: 700;
}

/* LIVE AGENDA */

.live-wrapper {
    background: white;
    border: 1px solid #e3e9e4;
    padding: 25px;
    border-radius: 15px;
    margin-top: 35px;
    margin-bottom: 18px;
}

.live-header {
    font-size: 23px;
    font-weight: 800;
    color: #173d2d;
    margin-bottom: 5px;
}

.live-description {
    color: #829087;
    font-size: 13px;
}

.live-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 20px;
}

/* HIJAU ORANGE */
.current-card {
    # background: #e5f5e9; /* kalau dimulai */
    background: #FFEED9; /* kalau dipending */
    # border: 1px solid #b7dfc2; /* kalau dimulai */
    border: 1px solid #FF8C00; /* kalau dipending */
    padding: 25px;
    border-radius: 12px;
    min-height: 190px;
    box-sizing: border-box;
}

.next-card {
    background: #f1f3f2;
    # background: #F5deb3;
    border: 1px solid #e3e9e4;
    padding: 25px;
    border-radius: 12px;
    min-height: 190px;
    box-sizing: border-box;
}

.card-label {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.3px;
    margin-bottom: 20px;
}

/* HIJAU ORANGE */
.current-card .card-label {
    # color: #25834a;/* kalau dimulai */
    color: #FF0D00; /* kalau dipending */
}

.next-card .card-label {
    color: #7c8980;
}

.card-title {
    font-size: clamp(18px, 2vw, 25px);
    font-weight: 800;
    color: #173d2d;
    margin-bottom: 0;
    line-height: 1.4;
    overflow-wrap: anywhere;
}

.card-topic-label {
    font-size: 12px;
    color: #65736a;
    margin-top: 18px;
    margin-bottom: 5px;
}

.card-topic {
    font-size: 15px;
    font-weight: 600;
    color: #344b3c;
    line-height: 1.6;
}

.status-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #269b52;
    margin-right: 7px;
}

.status-dot.waiting {
    background: #d49a32;
}

.status-dot.finished {
    background: #829087;
}

.status-dot.pending {
    background: #FFA500;
}

/* DATE */

.live-date {
    color: #829087;
    font-size: 13px;
    margin-bottom: 18px;
}

/* FOOTER */

.footer {
    text-align: center;
    border-top: 1px solid #e1e7e2;
    padding: 28px 10px;
    color: #849087;
    font-size: 12px;
    letter-spacing: 1.5px;
}

.footer strong {
    color: #173d2d;
}

/* DOKUMEN RAPAT */

.document-card {
    width: 100%;
    max-width: 600px;
    margin: 20px auto 25px;
    padding: 20px;
    box-sizing: border-box;

    background: white;
    border: 1px solid #e3e9e4;
    border-radius: 15px;
    overflow: hidden;
}

.document-header {
    font-size: 23px;
    font-weight: 800;
    color: #173d2d;
    margin-bottom: 5px;
}

.document-description {
    color: #829087;
    font-size: 13px;
    line-height: 1.6;
    margin-bottom: 20px;
}

.document-cover {
    display: block;
    width: 100%;
    max-width: 500px;
    max-height: 700px;
    height: auto;
    object-fit: contain;
    margin: 0 auto;
    border-radius: 8px;
}

/* MOBILE */

@media (max-width: 650px) {

    .document-card {
        max-width: 420px;
        padding: 12px;
        margin: 15px auto 20px;
        border-radius: 12px;
    }

    .document-header {
        font-size: 20px;
        margin-bottom: 5px;
    }

    .document-description {
        font-size: 12px;
        margin-bottom: 15px;
    }

    .document-cover {
        max-width: 360px;
        max-height: 550px;
    }
}

/* MOBILE */

@media (max-width: 650px) {

    .document-card {
        padding: 12px;
        border-radius: 12px;
        margin-top: 15px;
    }

    .document-title {
        font-size: 20px;
        margin-bottom: 15px;
    }

    .document-description {
        font-size: 13px;
        margin-top: 15px;
    }
}

@media (max-width: 650px) {

    .hero-header {
        padding: 40px 20px;
    }

    .hero-content {
        flex-direction: column-reverse;
        gap: 20px;
    }

    .hero-logo {
        width: 110px;
        min-width: 110px;
    }

    .hero-eyebrow {
        font-size: 10px;
        letter-spacing: 3px;
    }

    .hero-text p {
        font-size: 17px;
    }

    /* RUNDOWN RESPONSIVE */

    .schedule-container {
        width: 100%;
        max-width: 100%;
        padding: 4px;
        overflow-x: hidden;
        box-sizing: border-box;
    }

    .schedule-table {
        width: 100%;
        min-width: 0;
        table-layout: fixed;
        font-size: 10px;
        border-collapse: collapse;
    }

    .schedule-table th {
        padding: 8px 4px;
        font-size: 10px;
        text-align: center;
        overflow-wrap: anywhere;
    }

    .schedule-table td {
        padding: 8px 4px;
        vertical-align: middle;
        overflow-wrap: anywhere;
        word-break: normal;
    }

    /* Pembagian lebar kolom */

    .schedule-table .time {
        width: 22%;
        white-space: normal;
        text-align: center;
    }

    .schedule-table .activity {
        width: 53%;
    }

    .schedule-table .person {
        width: 25%;
        text-align: center;
    }

    /* Judul kegiatan */

    .schedule-table .main-activity {
        overflow-wrap: anywhere;
    }

    /* Baris tanggal */

    .schedule-table .date-row {
        padding: 8px 4px;
        font-size: 11px;
    }

    /* LIVE AGENDA */

    .live-wrapper {
        padding: 17px;
    }

    .live-grid {
        grid-template-columns: 1fr;
        gap: 12px;
    }

    .current-card,
    .next-card {
        padding: 16px;
        min-height: auto;
    }

/* RESPONSIVE HP */

@media (max-width: 650px) {

    .document-wrapper {
        padding: 17px;
        margin-top: 25px;
    }

    .document-header {
        font-size: 23px;
    }

    .document-description {
        font-size: 13px;
    }
}

    /* HALAMAN */

    .block-container {
        padding-left: 8px;
        padding-right: 8px;
    }
}

</style>
""")

# =========================================================
# HEADER
# =========================================================

logo_html = ""

if LOGO_PATH.exists():

    logo_base64 = base64.b64encode(
        LOGO_PATH.read_bytes()
    ).decode("utf-8")

    logo_html = f"""
    <div class="hero-logo">
        <img
            src="data:image/png;base64,{logo_base64}"
            alt="Logo PPGT"
        >
    </div>
    """

else:
    st.warning(
        "Logo PPGT tidak ditemukan. "
        "Pastikan logo_ppgt.png berada di folder dashboard."
    )

st.html(f"""
<div class="hero-header">
    <div class="hero-content">

        <div class="hero-text">

            <div class="hero-eyebrow">
                PPGT JEMAAT LABUANG BAJI
            </div>

            <h1>RAPAT ANGGOTA XX</h1>

            <p>PPGT JEMAAT LABUANG BAJI</p>

        </div>

        {logo_html}

    </div>
</div>
""")

# =========================================================
# SCHEDULE TITLE
# =========================================================

st.html("""
<div class="section-title">
    Rundown Kegiatan
</div>

<div class="section-subtitle">
    Sabtu, 28 November 2026
</div>
""")

# =========================================================
# GENERATE SCHEDULE TABLE
# =========================================================

table_html = """
<div class="schedule-container">

<table class="schedule-table">

<thead>
<tr>
<th>WAKTU<br>(WITA)</th>
<th>KEGIATAN</th>
<th>PELAKSANA</th>
</tr>
</thead>

<tbody>

<tr>
<td colspan="3" class="date-row">
Sabtu, 28 November 2026
</td>
</tr>
"""

for item in schedule:

    details = item["details"]

    break_class = (
        "break-row"
        if item["activity"] == "Istirahat"
        else ""
    )

    # KHUSUS SIDANG PLENO IV

# =========================================
# KHUSUS SIDANG PLENO IV, V, DAN VI
# =========================================

    if item["activity"] in [
        "SIDANG PLENO IV",
        "SIDANG PLENO V",
        "LANJUTAN SIDANG PLENO V",
        "SIDANG PLENO VI"
    ]:

        # Jumlah baris menyesuaikan jumlah detail
        rowspan = len(details) + 1

        table_html += f"""
        <tr class="{break_class}">

            <td class="time" rowspan="{rowspan}">
                {html.escape(item['time'])}
            </td>

            <td class="activity">
                <span class="main-activity">
                    {html.escape(item['activity'])}
                </span>
            </td>

            <td class="person" rowspan="{rowspan}">
                {html.escape(item['person'])}
            </td>

        </tr>
        """

        # Tampilkan seluruh detail kegiatan
        for number, detail, person, level in details:

            if number == "•":
                content = (
                    f"•&nbsp;&nbsp;{html.escape(detail)}"
                )
                padding = "padding-left:45px;"

            elif number:
                content = (
                    f"{html.escape(number)}&nbsp;&nbsp;"
                    f"{html.escape(detail)}"
                )
                padding = "padding-left:12px;"

            else:
                content = html.escape(detail)
                padding = "padding-left:12px;"

            table_html += f"""
            <tr>
                <td class="activity" style="{padding}">
                    {content}
                </td>
            </tr>
            """

        continue


    # =========================================
    # KEGIATAN LAINNYA
    # =========================================

    rowspan = len(details) + 1

    shared_person = (
        not details
        or all(not detail[2] for detail in details)
    )

    table_html += f"""
    <tr class="{break_class}">

        <td class="time" rowspan="{rowspan}">
            {html.escape(item['time'])}
        </td>

        <td class="activity">
            <span class="main-activity">
                {html.escape(item['activity'])}
            </span>
        </td>
    """

    if shared_person:

        table_html += f"""
        <td class="person" rowspan="{rowspan}">
            {html.escape(item['person'])}
        </td>
        """

    else:

        table_html += """
        <td class="person"></td>
        """

    table_html += "</tr>"

    for number, detail, person, level in details:

        if number == "•":

            content = (
                f"•&nbsp;&nbsp;{html.escape(detail)}"
            )

            padding = "padding-left:45px;"

        elif number:

            content = (
                f"{html.escape(number)}&nbsp;&nbsp;"
                f"{html.escape(detail)}"
            )

            padding = "padding-left:12px;"

        else:

            content = html.escape(detail)

            padding = "padding-left:12px;"

        table_html += f"""
        <tr>
            <td class="activity" style="{padding}">
                {content}
            </td>
        """

        if not shared_person:

            table_html += f"""
            <td class="person">
                {html.escape(person)}
            </td>
            """

        table_html += "</tr>"

table_html += """
</tbody>
</table>
</div>
"""

# PENTING:
# Gunakan st.html, BUKAN st.markdown.
# Ini mencegah HTML dibaca sebagai Markdown/code block.

st.html(table_html)

# =========================================================
# LIVE AGENDA HEADER
# =========================================================

st.html("""
<div class="live-wrapper">

<div class="live-header">
Live Agenda
</div>

<div class="live-description">
Informasi kegiatan Rapat Anggota XX secara langsung.
</div>

</div>
""")

# =========================================================
# INDONESIAN DATE
# =========================================================

# hari = [
#     "Senin", "Selasa", "Rabu", "Kamis",
#     "Jumat", "Sabtu", "Minggu"
# ]

# bulan = [
#     "Januari", "Februari", "Maret", "April",
#     "Mei", "Juni", "Juli", "Agustus",
#     "September", "Oktober", "November", "Desember"
# ]

# tanggal_indonesia = (
#     f"{hari[EVENT_DATE.weekday()]}, "
#     f"{EVENT_DATE.day} "
#     f"{bulan[EVENT_DATE.month - 1]} "
#     f"{EVENT_DATE.year}"
# )

# st.html(f"""
# <div class="live-date">
# {tanggal_indonesia}
# </div>
# """)

# =========================================================
# LIVE AGENDA STATUS
# =========================================================

status = LIVE_STATUS.upper().strip()

if status == "BELUM DIMULAI":

    status_label = "BELUM DIMULAI"

    status_indicator = """
    <span class="status-dot waiting"></span>
    """

    current_title = "Belum Dimulai"

    current_topic = "Menunggu dimulainya rangkaian kegiatan."

elif status == "SELESAI":

    status_label = "KEGIATAN SELESAI"

    status_indicator = """
    <span class="status-dot finished"></span>
    """

    current_title = "Rapat Anggota XX Selesai"

    current_topic = "Seluruh rangkaian kegiatan telah selesai dilaksanakan."

elif status == "SIDANG DIPENDING":

    status_label = "SIDANG DISKORS"

    status_indicator = """
    <span class="status-dot pending"></span>
    """

    current_title = "Rapat Anggota XX Diskors"

    current_topic = "Seluruh rangkaian kegiatan sedang diskors."

else:

    status_label = "SEDANG BERLANGSUNG"

    status_indicator = """
    <span class="status-dot"></span>
    """

    current_title = CURRENT_ACTIVITY

    current_topic = CURRENT_TOPIC

# Agenda selanjutnya

if status == "SELESAI":

    next_title = "Tidak Ada"

    next_topic = "Seluruh rangkaian kegiatan telah selesai."

else:

    next_title = NEXT_ACTIVITY

    next_topic = NEXT_TOPIC

# =========================================================
# LIVE AGENDA CARDS
# =========================================================

live_cards_html = f"""
<div class="live-grid">

    <div class="current-card">

        <div class="card-label">
            {status_indicator}
            {html.escape(status_label)}
        </div>

        <div class="card-title">
            {html.escape(current_title)}
        </div>

        <div class="card-topic-label">
            Sedang membahas:
        </div>

        <div class="card-topic">
            {html.escape(current_topic)}
        </div>

    </div>

    <div class="next-card">

        <div class="card-label">
            KEGIATAN SELANJUTNYA
        </div>

        <div class="card-title">
            {html.escape(next_title)}
        </div>

        <div class="card-topic-label">
            Agenda:
        </div>

        <div class="card-topic">
            {html.escape(next_topic)}
        </div>

    </div>

</div>
"""

st.html(live_cards_html)

# =========================================================
# LIVE COUNT PUBLIC
# =========================================================

st.html("""
<div style="
    background: white;
    border:1px solid #e3e9e4;
    padding:25px;
    border-radius:15px;
    margin-top:35px;
    margin-bottom:18px;
">
    <div style="
        font-size:23px;
        font-weight:800;
        color:#173d2d;
    ">
        Live Count Pemilihan
    </div>

    <div style="
        color:#829087;
        font-size:13px;
        margin-top:5px;
    ">
        Pantau perkembangan hasil penghitungan
        suara Rapat Anggota XX secara langsung.
    </div>
</div>
""")


st.html("""
<style>

/* LIVE COUNT */

/* Judul pemilihan */
[data-testid="stVerticalBlock"] h3 {
    color: #173d2d !important;
}

/* Label metric */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #64748b !important;
}

/* Angka metric */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: #173d2d !important;
}

/* Alert: info, success, warning */
div[data-testid="stAlert"] {
    background-color: #d8e8f7 !important;
    border: 1px solid #c5d9ed !important;
    color: white !important;
}

/* Paksa seluruh teks di dalam alert */
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div {
    color: white !important;
}

/* Progress bar */
[data-testid="stProgressBar"] {
    background-color: #e5e7eb !important;
}

</style>
""")


# =========================================================
# LIVE COUNT PUBLICATION
# =========================================================

LIVE_COUNT_PUBLISHED = True # KASIH KE TRUE KALAU SUDAH MULAI PEMILIHAN

@st.fragment(run_every="4s")
def show_live_count():

    positions = db.get_elections()

    for election in positions:

        position = election["position"]
        title = db.POSITIONS[position]
        status = election["status"]

        candidates = db.get_candidates(position)
        valid, invalid = db.get_totals(position)
        total = valid + invalid

        st.markdown(f"### Pemilihan {title}")

        if status == "Persiapan":

            st.info(
                "Menunggu dimulainya penghitungan suara."
            )

        elif status == "Berlangsung":

            st.success("Penghitungan sedang berlangsung.")

        else:

            st.success("Penghitungan selesai.")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Suara", total)
        col2.metric("Suara Sah", valid)
        col3.metric("Tidak Sah", invalid)

        if candidates and valid > 0:

            ranked = sorted(
                candidates,
                key=lambda x: x["votes"],
                reverse=True
            )

            for candidate in ranked:

                votes = candidate["votes"]

                percentage = (
                    votes / valid * 100
                    if valid else 0
                )

                st.markdown(
                    f"**{candidate['name']}**"
                    f" — {votes} suara "
                    f"({percentage:.1f}%)"
                )

                st.progress(
                    min(percentage / 100, 1.0)
                )

        elif candidates:

            st.caption(
                "Belum ada suara yang masuk."
            )

        if status == "Selesai" and candidates:

            if valid > 0:

                highest = max(
                    candidate["votes"]
                    for candidate in candidates
                )

                winners = [
                    candidate["name"]
                    for candidate in candidates
                    if candidate["votes"] == highest
                ]

                if len(winners) == 1:

                    st.success(
                        f"Pemenang Terpilih: {winners[0]}"
                    )

                else:

                    st.warning(
                        "Hasil seri: " + ", ".join(winners)
                    )

        st.divider()


if LIVE_COUNT_PUBLISHED:
    show_live_count()
else:
    st.markdown(
        """
        <div style="
            background: #f8faf9;
            border: 1px solid #e3e9e4;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            margin-bottom: 25px;
        ">
            <div style="
                color: #64746b;
                font-size: 16px;
                font-weight: 600;
            ">
                Belum memasuki agenda pemilihan
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DOCUMENT / PDF
# =========================================================

COVER_PATH = BASE_DIR / "dokumen" / "cover_rancangan.jpg"

if PDF_PATH.exists() and COVER_PATH.exists():

    pdf_bytes = PDF_PATH.read_bytes()

    cover_bytes = COVER_PATH.read_bytes()

    encoded_cover = base64.b64encode(
        cover_bytes
    ).decode("utf-8")

    # CARD DOKUMEN + COVER

    st.html(f"""
    <div class="document-card">

        <div class="document-header">
            📄 Dokumen Rapat
        </div>

        <div class="document-description">
            Rancangan Keputusan Rapat Anggota XX
            PPGT Jemaat Labuang Baji.
        </div>

        <img
            src="data:image/jpeg;base64,{encoded_cover}"
            class="document-cover"
            alt="Cover Rancangan Keputusan"
        >

    </div>
    """)

    # TOMBOL DOWNLOAD

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.download_button(
            label="⬇ Download Rancangan Keputusan",
            data=pdf_bytes,
            file_name="Rancangan_Keputusan_RA_XX.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # KETERANGAN DOWNLOAD

    st.html("""
        <div style="
            text-align:center;
            margin-top:5px;
            margin-bottom:15px;
            color:#829087;
            font-size:13px;
            line-height:1.6;
        ">
            Untuk melihat dokumen lengkap, silakan
            download rancangan keputusan di atas.
        </div>
    """)

elif not PDF_PATH.exists():

    st.info(
        "PDF belum tersedia. Masukkan file "
        "'rancangan_keputusan.pdf' ke dalam folder dokumen."
    )

else:

    st.info(
        "Cover dokumen belum tersedia. Masukkan file "
        "'cover_rancangan.jpg' ke dalam folder dokumen."
    )

# =========================================================
# FOOTER
# =========================================================

st.html("""
<div class="footer">

MADE WITH ❤️ BY <strong>PPGT JLB</strong>

<br><br>

RAPAT ANGGOTA XX PPGT JLB · 2026

</div>
""")
