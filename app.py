import streamlit as st
import base64
import html
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from pathlib import Path
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Rapat Anggota XX | PPGT JLB",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

TZ = ZoneInfo("Asia/Makassar") 
EVENT_DATE = date(2026, 11, 25)
PDF_PATH = Path(__file__).parent / "dokumen" / "rancangan_keputusan.pdf"

# Refresh seluruh halaman setiap 30 detik.
st_autorefresh(interval=30_000, key="rapat_anggota_refresh")

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f5f7f6;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 1rem;
}

.hero {
    background: linear-gradient(135deg, #123b2b, #236747);
    padding: 55px 25px;
    border-radius: 18px;
    text-align: center;
    color: white;
    margin-bottom: 38px;
}

.hero-label {
    color: #b9dfc8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 4px;
    margin-bottom: 18px;
}

.hero h1 {
    color: white;
    font-size: clamp(28px, 5vw, 46px);
    font-weight: 800;
    margin: 0;
    line-height: 1.2;
}

.hero p {
    color: #d4e8dc;
    font-size: 15px;
    margin-top: 15px;
    margin-bottom: 0;
}

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

.schedule-container {
    background: white;
    border: 1px solid #e3e9e4;
    border-radius: 12px;
    padding: 12px;
    overflow-x: auto;
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

.live-wrapper {
    background: white;
    border: 1px solid #e3e9e4;
    padding: 25px;
    border-radius: 15px;
    margin-top: 35px;
    margin-bottom: 20px;
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
    margin-bottom: 0;
}

.current-card {
    background: #e5f5e9;
    border: 1px solid #b7dfc2;
    padding: 24px;
    border-radius: 12px;
    min-height: 155px;
}

.next-card {
    background: #f5f7f6;
    border: 1px solid #e3e9e4;
    padding: 24px;
    border-radius: 12px;
    min-height: 155px;
}

.card-label {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.3px;
    margin-bottom: 18px;
}

.current-card .card-label {
    color: #25834a;
}

.next-card .card-label {
    color: #7c8980;
}

.card-title {
    font-size: clamp(17px, 2vw, 23px);
    font-weight: 800;
    color: #173d2d;
    margin-bottom: 9px;
}

.card-time {
    font-size: 13px;
    color: #65736a;
}

.status-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #269b52;
    margin-right: 7px;
}

.document-wrapper {
    background: white;
    border: 1px solid #e3e9e4;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 35px;
}

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

@media (max-width: 640px) {
    .hero {
        padding: 40px 15px;
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

    .current-card, .next-card {
        padding: 18px;
        min-height: 135px;
    }

    .block-container {
        padding-left: 12px;
        padding-right: 12px;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# RUNDOWN DATA
# =========================================================

schedule = [
    {
        "start": "16:00", "end": "17:00",
        "time": "16.00–17.00",
        "activity": "REGISTRASI",
        "person": "Panitia",
        "details": []
    },
    {
        "start": "17:00", "end": "18:30",
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
        "start": "18:30", "end": "19:00",
        "time": "18.30–19.00",
        "activity": "Istirahat",
        "person": "-",
        "details": []
    },
    {
        "start": "19:00", "end": "21:00",
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
        "start": "21:00", "end": "22:00",
        "time": "21.00–22.00",
        "activity": "SIDANG PLENO II",
        "person": "PIMPINAN SIDANG",
        "details": [
            ("", "Laporan Pertanggungjawaban Pengurus PPGT Jemaat Labuang Baji Periode 2024–2026", "", 0),
            ("", "Pembacaan Laporan", "", 0),
        ]
    },
    {
        "start": "22:00", "end": "22:15",
        "time": "22.00–22.15",
        "activity": "Doa Malam",
        "person": "Panitia",
        "details": []
    }
]

# =========================================================
# HEADER
# =========================================================

st.html("""
<div class="hero">
    <div class="hero-label">PPGT JEMAAT LABUANG BAJI</div>
    <h1>RAPAT ANGGOTA XX</h1>
    <p>PPGT JEMAAT LABUANG BAJI</p>
</div>
""")

# =========================================================
# SCHEDULE TABLE
# =========================================================

st.html("""
<div class="section-title">Rundown Kegiatan</div>
<div class="section-subtitle">Rabu, 25 November 2026</div>
""")

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
    <td colspan="3" class="date-row">Rabu, 25 November 2026</td>
</tr>
"""

for item in schedule:
    details = item["details"]
    rowspan = len(details) + 1
    break_class = "break-row" if item["activity"] == "Istirahat" else ""

    # Jika rincian memiliki pelaksana masing-masing, kolom pelaksana
    # ditampilkan per baris rincian. Jika tidak, pelaksana di- rowspan.
    shared_person = not details or all(not d[2] for d in details)

    table_html += f"""
    <tr class="{break_class}">
        <td class="time" rowspan="{rowspan}">{html.escape(item['time'])}</td>
        <td class="activity">
            <span class="main-activity">{html.escape(item['activity'])}</span>
        </td>
    """

    if shared_person:
        table_html += f"""
        <td class="person" rowspan="{rowspan}">
            {html.escape(item['person'])}
        </td>
        """
    else:
        table_html += '<td class="person"></td>'

    table_html += "</tr>"

    for number, detail, person, level in details:
        if number == "•":
            content = f"•&nbsp;&nbsp;{html.escape(detail)}"
            padding = "padding-left:45px;"
        elif number:
            content = f"{html.escape(number)}&nbsp;&nbsp;{html.escape(detail)}"
            padding = "padding-left:12px;"
        else:
            content = html.escape(detail)
            padding = "padding-left:12px;"

        table_html += f"""
        <tr>
            <td class="activity" style="{padding}">{content}</td>
        """

        if not shared_person:
            table_html += f'<td class="person">{html.escape(person)}</td>'

        table_html += "</tr>"

table_html += """
</tbody>
</table>
</div>
"""

st.html(table_html)

# =========================================================
# LIVE AGENDA LOGIC
# =========================================================

def get_live_agenda(now):
    if now.date() < EVENT_DATE:
        return None, schedule[0], "Belum Dimulai"

    if now.date() > EVENT_DATE:
        return None, None, "Kegiatan Selesai"

    for index, item in enumerate(schedule):
        start = time.fromisoformat(item["start"])
        end = time.fromisoformat(item["end"])

        if start <= now.time() < end:
            next_item = schedule[index + 1] if index + 1 < len(schedule) else None
            return item, next_item, "Sedang Berlangsung"

        if now.time() < start:
            return None, item, "Belum Dimulai"

    return None, None, "Kegiatan Selesai"

# =========================================================
# LIVE AGENDA DISPLAY
# =========================================================

st.html("""
<div class="live-wrapper">
    <div class="live-header">Live Agenda</div>
    <div class="live-description">
        Pantau kegiatan Rapat Anggota XX secara langsung.
    </div>
</div>
""")

now = datetime.now(TZ)
current, next_activity, status = get_live_agenda(now)

if current:
    current_title = current["activity"]
    current_time = current["time"]
elif status == "Belum Dimulai":
    current_title = "Belum Dimulai"
    current_time = "Menunggu agenda berikutnya"
else:
    current_title = "Kegiatan Selesai"
    current_time = "Rapat Anggota XX telah berakhir"

if next_activity:
    next_title = next_activity["activity"]
    next_time = next_activity["time"]
else:
    next_title = "Tidak Ada"
    next_time = "Tidak ada agenda selanjutnya"

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.html(f"""
    <div class="current-card">
        <div class="card-label">
            <span class="status-dot"></span>{html.escape(status.upper())}
        </div>
        <div class="card-title">{html.escape(current_title)}</div>
        <div class="card-time">{html.escape(current_time)}</div>
    </div>
    """)

with col2:
    st.html(f"""
    <div class="next-card">
        <div class="card-label">KEGIATAN SELANJUTNYA</div>
        <div class="card-title">{html.escape(next_title)}</div>
        <div class="card-time">{html.escape(next_time)}</div>
    </div>
    """)

# Nama hari dan bulan dalam Bahasa Indonesia
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
    f"{hari[now.weekday()]}, {now.day} "
    f"{bulan[now.month - 1]} {now.year}"
)

st.html(f"""
<div style="
    text-align:center;
    margin-top:15px;
    color:#829087;
    font-size:12px;
">
    {tanggal_indonesia} &nbsp; | &nbsp;
    {now.strftime('%H:%M:%S')} WITA
</div>
""")

# =========================================================
# PDF DOCUMENT
# =========================================================

st.html("""
<div style="margin-top:38px;">
    <div class="section-title">Dokumen Rapat</div>
    <div class="section-subtitle">
        Rancangan Keputusan Rapat Anggota XX PPGT Jemaat Labuang Baji.
    </div>
</div>
""")

with st.container(border=True):
    st.html("""
        <h3 style="
            color: #173d2d;
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 15px;
        ">
            📄 Rancangan Keputusan
        </h3>
    """)

    if PDF_PATH.exists():
        pdf_bytes = PDF_PATH.read_bytes()
        encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

        pdf_html = f"""
        <iframe
            src="data:application/pdf;base64,{encoded_pdf}"
            width="100%"
            height="750"
            style="border:none; border-radius:8px; background:white;">
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
