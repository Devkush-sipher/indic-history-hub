# pages/2_📚_Summary_&_Quiz.py

import streamlit as st
from googletrans.client import Translator
from gtts import gTTS
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
import tempfile
import random
import re

st.title("🌐 Multilingual Summary & Quiz Generator")

# Initialize translator for the updated library
translator = Translator(service_urls=['translate.google.com'])

# Safe translation function
def safe_translate(text, dest_lang):
    if not text or not text.strip():
        return ""
    try:
        result = translator.translate(text, dest=dest_lang)
        return result.text
    except Exception:
        # Fallback to original text if translation fails
        return text

# Supported languages
LANGUAGES = {
    "English": "en", "Telugu": "te", "Hindi": "hi", "Tamil": "ta", "Kannada": "kn"
}

# Initialize session state for scores if it doesn't exist
if "user_scores" not in st.session_state:
    st.session_state.user_scores = {}

# --- UI Inputs ---
language = st.selectbox("🌐 Choose Language", list(LANGUAGES.keys()))
lang_code = LANGUAGES[language]
topic = st.text_input("🔍 Enter a topic (e.g., Ashoka, Indus Valley Civilization, Taj Mahal)")

if topic:
    try:
        with st.spinner("Searching Wikipedia for '{}'...".format(topic)):
            wikipedia.set_lang("en")
            search_results = wikipedia.search(topic, results=5)
            if not search_results:
                st.error("No Wikipedia articles found. Please try another topic.")
                st.stop()
        
        selected_title = st.selectbox("🔎 Please select the most relevant article:", search_results)

        if selected_title:
            try:
                page = wikipedia.page(selected_title, auto_suggest=False, redirect=True)
                summary_en = page.summary

                st.subheader("📖 Summary")
                with st.spinner("Translating summary to {}...".format(language)):
                    translated_summary = safe_translate(summary_en, lang_code)
                st.write(translated_summary)

                with st.spinner("Generating audio..."):
                    try:
                        tts = gTTS(text=translated_summary, lang=lang_code)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            tts.save(fp.name)
                            st.audio(fp.name)
                    except Exception as audio_err:
                        st.warning("Could not generate audio. Error: {}".format(audio_err))

                if st.button("✔️ Start Quiz", use_container_width=True):
                    sentences = [s.strip() for s in summary_en.split('.') if len(s.split()) > 8]
                    if len(sentences) < 4:
                        st.warning("Summary is too short to generate a meaningful quiz. Please try another topic.")
                        st.stop()

                    quiz = []
                    num_questions = min(3, len(sentences))
                    questions_sentences = random.sample(sentences, num_questions)

                    for correct_sent_en in questions_sentences:
                        wrong_options_pool = [s for s in sentences if s != correct_sent_en]
                        wrong_sents_en = random.sample(wrong_options_pool, min(3, len(wrong_options_pool)))

                        options_en = [correct_sent_en] + wrong_sents_en
                        random.shuffle(options_en)

                        # Create question and translate (removed f-string)
                        question_en = "Which of the following statements about '{}' is correct?".format(selected_title)
                        question_trans = safe_translate(question_en, lang_code)
                        
                        options_trans = [safe_translate(opt, lang_code) for opt in options_en]
                        correct_trans = safe_translate(correct_sent_en, lang_code)

                        quiz.append({
                            "q": question_trans,
                            "options": options_trans,
                            "answer_trans": correct_trans
                        })

                    st.session_state.quiz = quiz
                    st.session_state.q_num = 0
                    st.session_state.score = 0
                    st.session_state.in_quiz = True
                    st.session_state.topic = selected_title
                    st.rerun()

            except (DisambiguationError, PageError) as e:
                st.error("Wikipedia Error: {}. Please try a more specific topic.".format(e))
            except Exception as e:
                st.error("An unexpected error occurred: {}".format(e))

# --- Quiz Display Logic ---
if st.session_state.get("in_quiz", False):
    quiz = st.session_state.quiz
    qn = st.session_state.q_num
    total_q = len(quiz)

    # Removed f-string
    st.header("Quiz on: {}".format(st.session_state.topic))

    if qn < total_q:
        q_data = quiz[qn]
        # Removed f-string
        st.subheader("❓ Question {} of {}".format(qn + 1, total_q))
        st.write(q_data["q"])
        
        # Using string concatenation for keys (removed f-string)
        user_answer = st.radio("Choose an option:", q_data["options"], key="q" + str(qn), index=None)

        if st.button("Submit Answer", key="submit" + str(qn)):
            if user_answer is None:
                st.warning("Please select an answer!")
            else:
                if user_answer == q_data["answer_trans"]:
                    st.success("✅ Correct!")
                    st.session_state.score += 1
                else:
                    st.error("❌ Incorrect.")
                    # Removed f-string
                    st.markdown("**The correct statement was:** _{}_".format(q_data['answer_trans']))
                
                st.session_state.q_num += 1
                st.rerun()
    else:
        score = st.session_state.score
        # Removed f-string
        st.success("🎉 Quiz Completed! Your score: {}/{}".format(score, total_q))

        topic = st.session_state.topic
        if topic not in st.session_state.user_scores:
            st.session_state.user_scores[topic] = []
        st.session_state.user_scores[topic].append("{}/{}".format(score, total_q))

        if st.button("🔁 Try Another Topic"):
            for k in list(st.session_state.keys()):
                if k.startswith("q") or k in ["quiz", "score", "in_quiz", "topic"]:
                    del st.session_state[k]
            st.rerun()

# --- Score History ---
if st.session_state.user_scores:
    with st.expander("📊 Show Score History"):
        for topic, score_list in st.session_state.user_scores.items():
            # Removed f-string
            st.write("**{}**: {}".format(topic, ', '.join(score_list)))
