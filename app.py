import streamlit as st
import openai
import os
import html

# OpenAI API-Key setzen
client = openai.OpenAI(api_key=st.secrets.get("openai_api_key", os.getenv("OPENAI_API_KEY")))

st.set_page_config(page_title="SEO Snippet Generator", layout="centered")
st.title("🔧 SEO Titel- & Meta-Generator")

seitentyp = st.selectbox("Welchen Seitentyp möchtest Du optimieren?", [
    "Startseite",
    "Kategorieseite",
    "Produktseite",
    "Blogartikel",
    "Landingpage",
    "Über uns / Team",
    "Kontaktseite"
])

geräteansicht = st.radio("Vorschau-Modus", ["Desktop", "Mobil"])

st.subheader("🔍 Inhaltliche Angaben")
data = {}

if seitentyp == "Startseite":
    data['USP'] = st.text_input("Was ist Euer Alleinstellungsmerkmal?")
    data['Branche'] = st.text_input("In welcher Branche seid Ihr tätig?")
    data['Marke'] = st.text_input("Wie lautet der Markenname?")

elif seitentyp == "Kategorieseite":
    data['Produktkategorie'] = st.text_input("Welche Produktkategorie wird dargestellt?")
    data['Vorteile'] = st.text_area("Welche Vorteile bietet diese Kategorie?")
    data['Zielgruppe'] = st.text_input("Für wen ist das Angebot gedacht?")

elif seitentyp == "Produktseite":
    data['Produktname'] = st.text_input("Wie heißt das Produkt?")
    data['Features'] = st.text_area("Welche technischen Merkmale sind besonders?")
    data['Zielgruppe'] = st.text_input("Wer nutzt dieses Produkt typischerweise?")

elif seitentyp == "Blogartikel":
    data['Thema'] = st.text_input("Was ist das Thema des Artikels?")
    data['Keyword'] = st.text_input("Was ist das Haupt-Keyword?")
    data['Kernaussage'] = st.text_area("Was ist die zentrale Aussage?")

elif seitentyp == "Landingpage":
    data['Aktion'] = st.text_input("Welche Aktion wird beworben?")
    data['Zielgruppe'] = st.text_input("Wen wollt Ihr ansprechen?")
    data['Zeitraum'] = st.text_input("Gibt es eine zeitliche Begrenzung?")

elif seitentyp == "Über uns / Team":
    data['Unternehmen'] = st.text_input("Wie heißt das Unternehmen?")
    data['Werte'] = st.text_area("Welche Werte/Philosophie lebt Ihr?")
    data['Erfahrung'] = st.text_input("Wie viel Erfahrung bringt Ihr mit?")

elif seitentyp == "Kontaktseite":
    data['Kontaktoptionen'] = st.text_input("Welche Kontaktmöglichkeiten gibt es?")
    data['Reaktionszeit'] = st.text_input("Wie schnell antwortet Ihr in der Regel?")

# GPT Prompt-Generator

def build_prompt(seitentyp, inputs):
    base = f"Du bist ein erfahrener SEO-Texter. Erstelle einen suchmaschinenoptimierten Title (max. 60 Zeichen) und eine Meta Description (max. 155 Zeichen) für eine {seitentyp}-Seite. Sprich die Nutzer mit Du/Dein an, fokussiere Dich auf Relevanz, Nutzen und klare Sprache."
    context = "".join([f"\n- {key}: {value}" for key, value in inputs.items() if value])
    return base + context

# Snippet generieren mit OpenAI
if st.button("🔎 Snippet generieren"):
    with st.spinner("GPT denkt nach..."):
        prompt = build_prompt(seitentyp, data)
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein SEO-Experte."},
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content.strip().split("\n")
            title = result[0].replace("Title:", "").strip()
            meta = result[1].replace("Meta:", "").strip() if len(result) > 1 else ""

            st.subheader("📈 Vorschau Snippet")
            st.markdown(f"**Title (max 60 Zeichen):**\n\n{title}")
            st.markdown(f"**Meta Description (max 155 Zeichen):**\n\n{meta}")
            st.caption(f"🧮 Titel: {len(title)} Zeichen | Meta: {len(meta)} Zeichen")

            preview_style = "max-width:600px;" if geräteansicht == "Mobil" else "max-width:750px;"

            st.markdown(f"""
            <div style='border:1px solid #ddd; padding:16px; border-radius:8px; margin-top:20px; {preview_style} background:#fff;'>
                <p style='color:#202124; font-size:14px; margin-bottom:2px;'>
                    <span style='color:green;'>www.beispielseite.de/{seitentyp.lower().replace(' ', '-')}</span>
                </p>
                <p style='color:#1a0dab; font-size:18px; margin:0;'>
                    {html.escape(title)}
                </p>
                <p style='color:#4d5156; font-size:14px; margin-top:4px;'>
                    {html.escape(meta)}
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.code(title, language='text')
            st.code(meta, language='text')

        except Exception as e:
            st.error(f"Fehler bei der OpenAI-Abfrage: {e}")
