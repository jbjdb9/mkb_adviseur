import streamlit as st
from backend import query_openwebui
from prompts import SYSTEEM_MEDEWERKER
from pdf_generator import genereer_pdf

st.set_page_config(page_title="Opleiding voor medewerker", page_icon="📚")

if st.button("← Terug naar home"):
    st.switch_page("app.py")

st.title("📚 Opleiding voor medewerker")
st.markdown("Beschrijf de taakomschrijving of vaardigheid die uw medewerker wilt aanleren en we zoeken passende opleidingen voor uw medewerker.")
st.divider()

niveau = st.selectbox(
    "Opleidingsniveau:",
    ["Weet ik niet", "MBO", "HBO", "WO"]
)
opleidingstype = st.selectbox(
    "Type opleiding:",
    ["Weet ik niet", "Associate Degree", "Bachelor", "Master"]
)
studievorm = st.selectbox(
    "Studievorm:",
    ["Weet ik niet", "Voltijd", "Deeltijd", "Beide mogelijk"]
)
taak = st.text_area(
    "Beschrijf wat de medewerker moet kunnen na de opleiding:",
    placeholder="Bijv: Onze medewerker moet zelfstandig financiële analyses kunnen maken en budgetten beheren voor onze afdeling.",
    height=150
)
domein = st.text_input(
    "Domein (optioneel):",
    placeholder="Bijv: Webdesign, Gamedesign, logistiek, ICT"
)

st.divider()

if st.button("Zoek passende opleidingen", type="primary", use_container_width=True):
    if not taak.strip():
        st.warning("Vul een omschrijving in.")
    else:
        with st.spinner("Zoeken in kennisbank..."):
            gebruiker_prompt = f"""Zoek geschikte opleidingen voor een medewerker van een bedrijf:

Gewenst niveau: {niveau}
Type opleiding: {opleidingstype}
Studievorm: {studievorm}
Wat de medewerker moet kunnen: {taak}
{"Domein: " + domein if domein.strip() else "Geen specifiek domein opgegeven"}

Geef concrete suggesties met het gevraagde format."""

            resultaat = query_openwebui(niveau, SYSTEEM_MEDEWERKER, gebruiker_prompt)

        st.markdown("### Resultaten")
        st.markdown(resultaat)
        st.divider()

        pdf_bytes = genereer_pdf("Opleidingssuggesties medewerker", resultaat)
        st.download_button(
            label="Download resultaat als PDF",
            data=pdf_bytes,
            file_name="opleiding_medewerker.pdf",
            mime="application/pdf",
            use_container_width=True
        )