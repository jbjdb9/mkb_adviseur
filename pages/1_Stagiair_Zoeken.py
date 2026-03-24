import streamlit as st
from backend import query_llm, vraag_contactgegevens
from prompts import SYSTEEM_STAGIAIR
from pdf_generator import genereer_pdf
import re

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
            gekozen_niveau = None if niveau == "Weet ik niet" else niveau
            resultaat = query_llm(gebruiker_prompt, SYSTEEM_STAGIAIR, gekozen_niveau=gekozen_niveau)

        # Opslaan in session_state zodat het na klikken op de knop blijft staan
        st.session_state["resultaat"] = resultaat
        st.session_state["niveau"] = niveau
        st.session_state["contactgegevens"] = None  # reset bij nieuwe zoekopdracht PRIVACY


# Resultaten tonen
if "resultaat" in st.session_state:
    resultaat = st.session_state["resultaat"]
    st.markdown("### Resultaten")
    st.markdown(resultaat)
    st.divider()

    # Contactgegevens knop (als het werkt vervangen voor automatisch inbegrepen bij opleiding suggesties)
    if st.button("📧 Contactgegevens opvragen voor deze suggesties", use_container_width=True):
        # Opleidingsnamen uit de output halen 
        opleidingen = re.findall(r"Suggestie\s*\d+[:\.]?\s*([^\n\[\(]+)", resultaat)
        opleidingen = [o.strip() for o in opleidingen if o.strip()]

        if not opleidingen:
            st.warning("Kon geen opleidingsnamen uit de resultaten halen.")
        else:
            with st.spinner("Contactgegevens ophalen..."):
                contact_output = ""
                zoek_niveau = st.session_state["niveau"]

                for i, opleiding in enumerate(opleidingen, 1):
                    contact = vraag_contactgegevens(opleiding, zoek_niveau, SYSTEEM_STAGIAIR)
                    contact_output += f"**Opleiding {i}: {opleiding}**\n\n{contact.strip()}\n\n---\n\n"

            st.session_state["contactgegevens"] = contact_output

    # Contactgegevens tonen als die er zijn
    # Met de gelimiteerde database controle en meta data binnen OpenWebUI
    # Erg experimentele optie, aka ik acht veel "geen contactgegevens" en dergelijke
    if st.session_state.get("contactgegevens"):
        st.markdown("### Contactgegevens")
        st.markdown(st.session_state["contactgegevens"])
        st.divider()

    # PDF download
    pdf_inhoud = resultaat
    if st.session_state.get("contactgegevens"):
        pdf_inhoud += "\n\n---\n\n## Contactgegevens\n\n" + st.session_state["contactgegevens"]

    pdf_bytes = genereer_pdf("Stagiair suggesties", pdf_inhoud)
    st.download_button(
        label="Download resultaat als PDF",
        data=pdf_bytes,
        file_name="stagiair_suggesties.pdf",
        mime="application/pdf",
        use_container_width=True
    )