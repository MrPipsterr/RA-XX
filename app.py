
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

LOGO_PATH = BASE_DIR / "logo_ppgt.png"
PDF_PATH = BASE_DIR / "dokumen" / "rancangan_keputusan.pdf"

EVENT_DATE = date(2026, 11, 25)

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

LIVE_STATUS = "BELUM DIMULAI"

CURRENT_ACTIVITY = "-"
CURRENT_TOPIC = "-"

NEXT_ACTIVITY = "REGISTRASI"
NEXT_TOPIC = "Registrasi"

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
        "time": "16.00–17.00",
        "activity": "REGISTRASI",
        "person": "Panitia",
        "details": []
    },

    {
        "time": "17.00–18.30",
        "activity": "OPENING CEREMONY",
        "person": "",
        "details": [
            ("1.", "Ibadah Pembukaan", "Pdt. Paulus Palute", 0),
            ("2.", "Acara Nasional", "-", 0),
            ("•", "Menyanyikan Lagu Indonesia Raya", "Panitia", 1),
            ("•", "Mengheningkan Cipta (PK)", "Panitia", 1),
            ("3.", "Acara Organisasi", "-", 0),
            ("•", "Menyanyikan Mars PPGT", "Panitia", 1),
            ("•", "Pembacaan Mukadimah AD/ART PPGT", "Sekretaris PPGT", 1),
            ("•", "Menyanyikan Hymne PPGT", "Panitia", 1),
            ("4.", "Laporan Ketua Panitia", "Ketua Panitia", 0),
            ("5.", "Sambutan-sambutan:", "-", 0),
            ("•", "Pengurus PPGT Jemaat Labuang Baji", "-", 1),
            ("•", "Pengurus PPGT Klasis Makassar", "-", 1),
            ("•", "PMG Jemaat Labuang Baji", "-", 1),
        ]
    },

    {
        "time": "18.30–19.00",
        "activity": "Istirahat",
        "person": "-",
        "details": []
    },

    {
        "time": "19.00–21.00",
        "activity": "SIDANG PLENO I",
        "person": "PIMPINAN SIDANG SEMENTARA",
        "details": [
            ("1.", "Pengesahan RA", "", 0),
            ("2.", "Pengesahan Peserta RA", "", 0),
            ("3.", "Pembahasan dan Pengesahan Jadwal Acara", "", 0),
            ("4.", "Pembahasan dan Pengesahan Tata Tertib", "", 0),
            ("5.", "Pemilihan Pimpinan Sidang", "", 0),
            ("6.", "Pengesahan Penasehat Rapat Anggota", "", 0),
        ]
    },

    {
        "time": "21.00–22.00",
        "activity": "SIDANG PLENO II",
        "person": "PIMPINAN SIDANG",
        "details": [
            (
                "",
                "Laporan Pertanggungjawaban Pengurus PPGT Jemaat Labuang Baji Periode 2024–2026",
                "",
                0
            ),
            ("", "Pembacaan Laporan", "", 0),
        ]
    },

    {
        "time": "22.00–22.15",
        "activity": "Doa Malam",
        "person": "Panitia",
        "details": []
    }

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
    font-size: 23px;
    font-weight: 800;
    color: #173d2d;
    margin-bottom: 5px;
}

.section-subtitle {
    font-size: 13px;
    color: #829087;
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

.current-card {
    background: #e5f5e9;
    border: 1px solid #b7dfc2;
    padding: 25px;
    border-radius: 12px;
    min-height: 190px;
    box-sizing: border-box;
}

.next-card {
    background: #f1f3f2;
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

.current-card .card-label {
    color: #25834a;
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

/* MOBILE */

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

    .schedule-container {
        padding: 5px;
    }

    .schedule-table {
        min-width: 680px;
        font-size: 12px;
    }

    .live-wrapper {
        padding: 17px;
    }

    .live-grid {
        grid-template-columns: 1fr;
    }

    .current-card,
    .next-card {
        padding: 18px;
        min-height: 160px;
    }

    .block-container {
        padding-left: 12px;
        padding-right: 12px;
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
    Rabu, 25 November 2026
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
Rabu, 25 November 2026
</td>
</tr>
"""

for item in schedule:

    details = item["details"]

    rowspan = len(details) + 1

    break_class = (
        "break-row"
        if item["activity"] == "Istirahat"
        else ""
    )

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

hari = [
    "Senin", "Selasa", "Rabu", "Kamis",
    "Jumat", "Sabtu", "Minggu"
]

bulan = [
    "Januari", "Februari", "Maret", "April",
    "Mei", "Juni", "Juli", "Agustus",
    "September", "Oktober", "November", "Desember"
]

tanggal_indonesia = (
    f"{hari[EVENT_DATE.weekday()]}, "
    f"{EVENT_DATE.day} "
    f"{bulan[EVENT_DATE.month - 1]} "
    f"{EVENT_DATE.year}"
)

st.html(f"""
<div class="live-date">
{tanggal_indonesia}
</div>
""")

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
# DOCUMENT / PDF
# =========================================================

st.html("""
<div style="margin-top:38px;">

<div class="section-title">
Dokumen Rapat
</div>

<div class="section-subtitle">
Rancangan Keputusan Rapat Anggota XX
PPGT Jemaat Labuang Baji.
</div>

</div>
""")

with st.container(border=True):

    st.html("""
    <h3 style="
        color:#173d2d;
        font-size:20px;
        font-weight:800;
        margin-bottom:15px;
    ">
        📄 Rancangan Keputusan
    </h3>
    """)

    if PDF_PATH.exists():

        pdf_bytes = PDF_PATH.read_bytes()

        encoded_pdf = base64.b64encode(
            pdf_bytes
        ).decode("utf-8")

        pdf_html = f"""
        <iframe
            src="data:application/pdf;base64,{encoded_pdf}"
            width="100%"
            height="750px"
            style="
                border:none;
                border-radius:8px;
                background:white;
            ">
        </iframe>
        """

        components.html(
            pdf_html,
            height=770,
            scrolling=True
        )

        st.download_button(
            label="⬇ Download Rancangan Keputusan",
            data=pdf_bytes,
            file_name="Rancangan_Keputusan_RA_XX.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    else:

        st.info(
            "PDF belum tersedia. Masukkan file "
            "'rancangan_keputusan.pdf' ke dalam folder dokumen."
        )

# =========================================================
# FOOTER
# =========================================================

st.html("""
<div class="footer">

MADE WITH ❤️ BY <strong>PPGT JLB</strong>

<br><br>

RAPAT ANGGOTA XX · 2026

</div>
""")
