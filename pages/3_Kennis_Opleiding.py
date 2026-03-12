import streamlit as st
from backend import query_openwebui
from prompts import SYSTEEM_KENNIS
from pdf_generator import genereer_pdf

st.set_page_config(page_title="Kennis van opleiding", page_icon="💡")

if st.button("← Terug naar home"):
    st.switch_page("app.py")

st.title("Wat leren studenten bij de gegeven opleiding?")
st.markdown("Voer een opleidingsnaam in en ontdek welke kennis en vaardigheden een student heeft na het afstuderen.")
st.divider()

niveau = st.selectbox(
    "Niveau van de opleiding:",
    ["Weet ik niet", "MBO", "HBO", "WO"]
)
opleiding_naam = st.text_input(
    "Naam van de opleiding:",
    placeholder="Bijv: HBO Technische Bedrijfskunde, MBO Logistiek medewerker, WO Wiskunde"
)

st.divider()

if st.button("oek opleidingsinformatie", type="primary", use_container_width=True):
    if not opleiding_naam.strip():
        st.warning("Vul een opleidingsnaam in.")
    else:
        with st.spinner("Zoeken in kennisbank..."):
            gebruiker_prompt = f"""Geef een volledig overzicht van de kennis, vaardigheden en competenties
die iemand opdoet tijdens de volgende opleiding:

Opleiding: {opleiding_naam}
Niveau: {niveau}

Gebruik het gevraagde format en baseer je uitsluitend op de kennisbank."""

            resultaat = query_openwebui(niveau, SYSTEEM_KENNIS, gebruiker_prompt)

        st.markdown("### Resultaten")
        st.markdown(resultaat)
        st.divider()

        pdf_bytes = genereer_pdf(f"Kennis: {opleiding_naam}", resultaat)
        st.download_button(
            label="Download resultaat als PDF",
            data=pdf_bytes,
            file_name="kennis_opleiding.pdf",
            mime="application/pdf",
            use_container_width=True
        )