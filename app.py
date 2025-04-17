import streamlit as st
import openai
import os
import html
import requests
from bs4 import BeautifulSoup

# Muss als erste Streamlit-Funktion kommen
st.set_page_config(page_title="SEO Snippet Generator", layout="centered", page_icon="🛠", initial_sidebar_state="collapsed")

# Hintergrund auf Weiß setzen
st.markdown("""
    <style>
        .stApp {
            background-color: white;
        }
    </style>
""", unsafe_allow_html=True)

# 🔒 Einfacher Passwortschutz mit Button und Ausblendung nach Login
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False

if not st.session_state.access_granted:
    password = st.text_input("Zugangscode", type="password")
    if st.button("Einloggen"):
        if password == st.secrets.get("app_password"):
            st.session_state.access_granted = True
            st.success("Zugang erfolgreich. Die App ist jetzt freigeschaltet.")
            st.stop()
        else:
            st.warning("Zugriff verweigert. Bitte gültigen Code eingeben.")
    st.stop()

# OpenAI API-Key setzen
client = openai.OpenAI(api_key=st.secrets.get("openai_api_key", os.getenv("OPENAI_API_KEY")))

st.title("SEO Titel- & Meta-Generator")

seitentyp = st.selectbox("Welchen Seitentyp möchtest Du optimieren?", [
    "Startseite",
    "Kategorieseite",
    "Produktseite",
    "Blogartikel",
    "Landingpage",
    "Über uns / Team",
    "Kontaktseite"
])

st.subheader("Inhaltliche Angaben")
marke = st.text_input("Wie lautet der Marken- oder Shopname?", key="marke")
usps = st.text_input("Was ist Euer Alleinstellungsmerkmal?", key="usps")
branche = st.text_input("In welcher Branche seid Ihr tätig?", key="branche")

# Weitere Felder dynamisch anzeigen je nach Seitentyp
if seitentyp == "Produktseite":
    st.text_input("Produktname", key="produktname")
    st.text_area("Produktbeschreibung", key="beschreibung")
elif seitentyp == "Blogartikel":
    st.text_input("Artikelthema", key="artikelthema")
    st.text_area("Kurze Zusammenfassung", key="zusammenfassung")
elif seitentyp == "Landingpage":
    st.text_input("Aktion oder Angebot", key="aktion")
    st.text_input("Zielgruppe oder Kampagnenziel", key="ziel")

st.subheader("Optional: Live-URL analysieren")
url_input = st.text_input("Falls Du möchtest, analysieren wir automatisch die Inhalte einer URL.")

# Funktion zum Crawlen der Seite und Weitergabe an GPT

def scrape_url_and_generate_prompt(url, seitentyp):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        title_tag = soup.title.string.strip() if soup.title else ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_tag['content'].strip() if meta_tag and 'content' in meta_tag.attrs else ""
        h1 = soup.find("h1")
        headline = h1.get_text(strip=True) if h1 else ""
        text_body = soup.get_text(separator=' ', strip=True)

        prompt = f"Du bist ein erfahrener SEO-Texter. Erstelle einen suchmaschinenoptimierten Title (max. 60 Zeichen) und eine Meta Description (max. 155 Zeichen) für eine {seitentyp}-Seite. Sprich die Nutzer mit Du/Dein an, fokussiere Dich auf Relevanz, Nutzen und klare Sprache. Der Titel soll am Ende folgenden Zusatz enthalten: | {title_tag}. Die Meta Description darf den Titel nicht wiederholen und soll neugierig machen. Gib Deine Antwort bitte genau in folgendem Format zurück (keine zusätzlichen Erklärungen):\n\nTitle: ...\nMeta: ...\n\nInhalt der Seite (nur zur Kontextbildung):\n- Titel: {title_tag}\n- Meta: {meta_desc}\n- H1: {headline}\n- Text: {text_body[:1000]}"

        return prompt
    except Exception as e:
        st.error(f"Fehler beim Auslesen der Seite: {e}")
        return None

# Prompt zusammenbauen
if url_input:
    prompt = scrape_url_and_generate_prompt(url_input, seitentyp)
else:
    prompt = f"Du bist ein erfahrener SEO-Texter. Erstelle einen suchmaschinenoptimierten Title (max. 60 Zeichen) und eine Meta Description (max. 155 Zeichen) für eine {seitentyp}-Seite. Sprich die Nutzer mit Du/Dein an, fokussiere Dich auf Relevanz, Nutzen und klare Sprache. Der Titel soll am Ende folgenden Zusatz enthalten: | {marke}. Die Meta Description darf die Marke NICHT enthalten. Gib Deine Antwort bitte genau in folgendem Format zurück (keine zusätzlichen Erklärungen):\n\nTitle: ...\nMeta: ...\n\nEingaben:\n- Marke: {marke}\n- USP: {usps}\n- Branche: {branche}"

if st.button("Snippet generieren"):
    with st.spinner("GPT denkt nach..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Du bist ein SEO-Experte."},
                    {"role": "user", "content": prompt}
                ]
            )
            raw_output = response.choices[0].message.content.strip()

            # Versuche sauber Titel & Meta zu extrahieren
            title = ""
            meta = ""
            for line in raw_output.split("\n"):
                if line.lower().startswith("title:"):
                    title = line.split(":", 1)[1].strip()
                elif line.lower().startswith("meta:"):
                    meta = line.split(":", 1)[1].strip()

            st.subheader("Vorschau Snippet")
            st.markdown(f"**Title (max 60 Zeichen):**\n\n{title}")
            st.markdown(f"**Meta Description (max 155 Zeichen):**\n\n{meta if meta else '— Keine Meta Description erkannt —'}")
            st.caption(f"Titel: {len(title)} Zeichen | Meta: {len(meta)} Zeichen")

            for ansicht, style in {"Desktop": "max-width:750px;", "Mobil": "max-width:600px;"}.items():
                st.markdown(f"#### Vorschau {ansicht}")
                st.markdown(f"""
                <div style='border:1px solid #ddd; padding:16px; border-radius:8px; margin-top:12px; {style} background:#fff;'>
                    <p style='color:#202124; font-size:14px; margin-bottom:2px;'>
                        <span style='color:green;'>{url_input if url_input else 'www.beispielseite.de'}</span>
                    </p>
                    <p style='color:#1a0dab; font-size:18px; margin:0;'>
                        {html.escape(title) if title else '<em>Kein Titel erkannt</em>'}
                    </p>
                    <p style='color:#4d5156; font-size:14px; margin-top:4px;'>
                        {html.escape(meta) if meta else '<em>Keine Beschreibung erkannt</em>'}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.code(title, language='text')
            st.code(meta, language='text')

        except Exception as e:
            st.error(f"Fehler bei der OpenAI-Abfrage: {e}")
