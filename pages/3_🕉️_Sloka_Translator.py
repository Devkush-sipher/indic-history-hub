# pages/3_🕉️_Sloka_Translator.py

import streamlit as st
from googletrans.client import Translator
from gtts import gTTS

# Language map for translation + TTS
language_map = {
    "English": "en", "Hindi": "hi", "Telugu": "te", "Tamil": "ta", "Kannada": "kn"
}

# Initialize the translator
translator = Translator(service_urls=['translate.google.com'])

# Streamlit UI
st.title("🕉️ Sloka Translator & Audio Guide")
st.markdown("Enter a sloka or verse to get its translation, pronunciation, and meaning as separate audio.")

# User input
sloka = st.text_area("📜 Enter the Sloka here (e.g., in Sanskrit, Hindi, or English transliteration):", height=150, placeholder="Example: Karmanye Vadhikaraste Ma Phaleshu Kadachana...")
target_lang_name = st.selectbox("🌍 Translate To", list(language_map.keys()))
lang_code = language_map[target_lang_name]

# Translation and audio generation
if st.button("Translate and Generate Audio", type="primary", use_container_width=True):
    if not sloka.strip():
        st.warning("⚠️ Please enter a sloka to translate.")
    else:
        with st.spinner("Translating and generating audio..."):
            try:
                # 1. Translate the sloka
                translation = translator.translate(sloka, dest=lang_code)
                translated_text = translation.text

                # 2. Generate pronunciation audio (Sloka in original style)
                tts_sloka = gTTS(text=sloka, lang="hi", slow=False)
                sloka_audio_path = "pronunciation.mp3"
                tts_sloka.save(sloka_audio_path)
                
                # 3. Generate explanation audio (Meaning in selected language)
                tts_explanation = gTTS(text=translated_text, lang=lang_code, slow=False)
                explanation_audio_path = "meaning.mp3"
                tts_explanation.save(explanation_audio_path)
                
                st.success("✅ Success! Here are your results:")
                
                st.subheader("📖 Translated Meaning")
                st.markdown(f"> {translated_text}")

                st.write("---")
                st.subheader("🔊 Sloka Pronunciation (Original)")
                st.audio(sloka_audio_path)

                st.subheader(f"🧠 Meaning in {target_lang_name}")
                st.audio(explanation_audio_path)

            except Exception as e:
                st.error(f"❌ An error occurred. This could be due to network issues or API limitations.")
                st.error(f"Details: {e}")
