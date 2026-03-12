import streamlit as st

st.set_page_config(
    page_title="MKB Opleidingsadviseur",
    page_icon="🎓",
    layout="centered"
)

st.title("Opleidingsadviseur")
st.markdown("Welkom! Kies hieronder waarmee je geholpen wilt worden.")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Passende stagiair zoeken")
    st.write("Vind een passende opleiding om een stagiair van te vinden voor uw bedrijf.")
    if st.button("Ga naar deze tool", key="btn1", use_container_width=True):
        st.switch_page("pages/1_Stagiair_Zoeken.py")

with col2:
    st.markdown("### Opleiding voor medewerker")
    st.write("Zoek een opleiding die past bij de ontwikkelbehoefte van een medewerker.")
    if st.button("Ga naar deze tool", key="btn2", use_container_width=True):
        st.switch_page("pages/2_Opleiding_Medewerker.py")

with col3:
    st.markdown("### Wat weet een afgestudeerde?")
    st.write("Ontdek welke kennis en vaardigheden iemand heeft na een specifieke opleiding.")
    if st.button("Ga naar deze tool", key="btn3", use_container_width=True):
        st.switch_page("pages/3_Kennis_Opleiding.py")

st.divider()
st.caption("Gebaseerd op opleidingen in noord Nederland - Prototype")