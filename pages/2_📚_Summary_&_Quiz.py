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

# Initialize translator
# Use the service URL for the updated library
translator = Translator(service_urls=['translate.google.com'])

# Safe translation function
def safe_translate(text, dest_lang):
    if not text or not text.strip():
        return ""
    try:
        # The new library requires a direct call
        result = translator.translate(text, dest=dest_lang)
        return result.text
    except Exception as e:
        st.warning(f"Translation failed: {e}. Falling back to original text.")
        return text

# Supported languages
LANGUAGES = {
    "English": "en", "Telugu": "te", "Hindi": "hi", "Tamil": "ta", "Kannada": "kn"
}

# Initialize session state
if "user_scores" not in st.session_state:
    st.session_state.user_scores = {}

# UI inputs
language = st.selectbox("🌐 Choose Language", list(LANGUAGES.keys()))
lang_code = LANGUAGES[language]
topic = st.text_input("🔍 Enter a topic (e.g., Ashoka, Indus Valley Civilization, Taj Mahal)")

if topic:
    try:
        with st.spinner(f"Searching Wikipedia for '{topic}'..."):
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
                with st.spinner(f"Translating summary to {language}..."):
                    translated_summary = safe_translate(summary_en, lang_code)
                st.write(translated_summary)

                with st.spinner("Generating audio..."):
                    try:
                        tts = gTTS(text=translated_summary, lang=lang_code)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            tts.save(fp.name)
                            st.audio(fp.name)
                    except Exception as audio_err:
                        st.warning(f"Could not generate audio. Error: {audio_err}")

                if st.button("✔️ Start Quiz", use_container_width=True):
                    # --- Robust Quiz Generation Logic ---
                    sentences = [s.strip() for s in summary_en.split('.') if len(s.split()) > 8]
                    if len(sentences) < 4:
                        st.warning("Summary is too short to generate a meaningful quiz. Please try another topic.")
                        st.stop()

                    quiz = []
                    # Ensure we have enough unique sentences for the quiz
                    num_questions = min(3, len(sentences))
                    questions_sentences = random.sample(sentences, num_questions)

                    for correct_sent_en in questions_sentences:
                        # Pool of wrong answers are all sentences EXCEPT the correct one
                        wrong_options_pool = [s for s in sentences if s != correct_sent_en]
                        # Select 3 wrong answers
                        wrong_sents_en = random.sample(wrong_options_pool, min(3, len(wrong_options_pool)))

                        options_en = [correct_sent_en] + wrong_sents_en
                        random.shuffle(options_en)

                        # Translate everything for the quiz
                        question_trans = safe_translate(f"Which of the following statements about '{selected_title}' is correct?", lang_code)
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
                st.error(f"Wikipedia Error: {e}. Please try a more specific topic.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# Quiz Display Logic
if st.session_state.get("in_quiz", False):
    quiz = st.session_state.quiz
    qn = st.session_state.q_num
    total_q = len(quiz)

    st.header(f"Quiz on: {st.session_state.topic}")

    if qn < total_q:
        q_data = quiz[qn]
        st.subheader(f"❓ Question {qn + 1} of {total_q}")
        st.write(q_data["q"])
        
        user_answer = st.radio("Choose an option:", q_data["options"], key=f"q{qn}", index=None)

        if st.button("Submit Answer", key=f"submit_{qn}"):
            if user_answer is None:
                st.warning("Please select an answer!")
            else:
                if user_answer == q_data["answer_trans"]:
                    st.success("✅ Correct!")
                    st.session_state.score += 1
                else:
                    st.error("❌ Incorrect.")
                    st.markdown(f"**The correct statement was:** _{q_data['answer_trans']}_")
                
                st.session_state.q_num += 1
                st.rerun()
    else:
        score = st.session_state.score
        st.success(f"🎉 Quiz Completed! Your score: {score}/{total_q}")

        topic = st.session_state.topic
        if topic not in st.session_state.user_scores:
            st.session_state.user_scores[topic] = []
        st.session_state.user_scores[topic].append(f"{score}/{total_q}")

        if st.button("🔁 Try Another Topic"):
            for k in list(st.session_state.keys()):
                if k.startswith("q") or k in ["quiz", "score", "in_quiz", "topic"]:
                    del st.session_state[k]
            st.rerun()

# Score History
if st.session_state.user_scores:
    with st.expander("📊 Show Score History"):
        for topic, score_list in st.session_state.user_scores.items():
            st.write(f"**{topic}**: {', '.join(score_list)}")
