
import streamlit as st
from supabase import create_client

st.title("Tes Koneksi Supabase")

try:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

    response = (
        supabase
        .table("elections")
        .select("*")
        .execute()
    )

    st.success("Koneksi Supabase berhasil!")

    st.write("Data pemilihan:", response.data)

except Exception as e:
    st.error("Koneksi Supabase gagal.")
    st.write(str(e))
