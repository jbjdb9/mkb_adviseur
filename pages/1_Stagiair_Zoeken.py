import streamlit as st
from backend import query_openwebui
from prompts import SYSTEEM_STAGIAIR
from pdf_generator import genereer_pdf

st.set_page_config(page_title="Stagiair zoeken", page_icon="🔍")

if st.button("← Terug naar home"):
    st.switch_page("app.py")

st.title("Stagiair zoeken")
st.markdown("Beschrijf de taak die de stagiair moet gaan uitvoeren en we zoeken passende opleidingen om een stagiair te vinden.")
st.divider()

niveau = st.selectbox(
    "Opleidingsniveau van de gewenste stagiair:",
    ["Weet ik niet", "MBO", "HBO", "WO"]
)
taak = st.text_area(
    "Beschrijf de taak of het project voor de stagiair:",
    placeholder="Bijv: Wij zoeken een stagiair die helpt bij het opzetten van onze social media strategie en content maakt voor Instagram en LinkedIn.",
    height=150
)
domein = st.text_input(
    "Domein (optioneel):",
    placeholder="Bijv: Webdesign, Techniek, ICT, Grafisch vormgeven"
)

st.divider()

if st.button("Zoek passende opleidingen", type="primary", use_container_width=True):
    if not taak.strip():
        st.warning("Vul een taakomschrijving in.")
    else:
        with st.spinner("Zoeken in kennisbank..."):
            gebruiker_prompt = f"""Zoek geschikte opleidingen om een stagiair te vinden voor het volgende bedrijf:

Gewenst niveau: {niveau}
Taakomschrijving: {taak}
{"Domein: " + domein if domein.strip() else "Geen specifiek domein opgegeven"}

Geef concrete suggesties met het gevraagde format."""

            resultaat = query_openwebui(niveau, SYSTEEM_STAGIAIR, gebruiker_prompt)

        st.markdown("### Resultaten")
        st.markdown(resultaat)
        st.divider()

        pdf_bytes = genereer_pdf("Stagiair suggesties", resultaat)
        st.download_button(
            label="Download resultaat als PDF",
            data=pdf_bytes,
            file_name="stagiair_suggesties.pdf",
            mime="application/pdf",
            use_container_width=True
        )