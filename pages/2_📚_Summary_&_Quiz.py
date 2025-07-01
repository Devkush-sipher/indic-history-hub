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
        return text # Fallback

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
        with st.spinner("Searching Wikipedia for '" + topic + "'..."):
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
                with st.spinner("Translating summary to " + language + "..."):
                    translated_summary = safe_translate(summary_en, lang_code)
                st.write(translated_summary)

                with st.spinner("Generating audio..."):
                    try:
                        tts = gTTS(text=translated_summary, lang=lang_code)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            tts.save(fp.name)
                            st.audio(fp.name)
                    except Exception as audio_err:
                        st.warning("Could not generate audio. Error: " + str(audio_err))

                if st.button("✔️ Start Quiz", use_container_width=True):
                    # --- Radically Simplified Quiz Generation Logic ---
                    
                    # 1. Break summary into sentences using a simple for loop
                    initial_sentences = summary_en.split('.')
                    sentences = []
                    for s in initial_sentences:
                        s_stripped = s.strip()
                        if len(s_stripped.split()) > 8:
                            sentences.append(s_stripped)

                    if len(sentences) < 4:
                        st.warning("Summary is too short to generate a meaningful quiz. Please try another topic.")
                        st.stop()

                    quiz = []
                    num_questions = min(3, len(sentences))
                    questions_sentences = random.sample(sentences, num_questions)

                    for correct_sent_en in questions_sentences:
                        # 2. Create pool of wrong answers using a simple for loop
                        wrong_options_pool = []
                        for s in sentences:
                            if s != correct_sent_en:
                                wrong_options_pool.append(s)
                        
                        wrong_sents_en = random.sample(wrong_options_pool, min(3, len(wrong_options_pool)))

                        options_en = [correct_sent_en] + wrong_sents_en
                        random.shuffle(options_en)
                        
                        question_en = "Which of the following statements about '" + selected_title + "' is correct?"
                        question_trans = safe_translate(question_en, lang_code)
                        
                        # 3. Translate options using a simple for loop
                        options_trans = []
                        for opt in options_en:
                            options_trans.append(safe_translate(opt, lang_code))
                        
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
                st.error("Wikipedia Error: " + str(e) + ". Please try a more specific topic.")
            except Exception as e:
                st.error("An unexpected error occurred: " + str(e))

# --- Quiz Display Logic ---
if st.session_state.get("in_quiz", False):
    quiz = st.session_state.quiz
    qn = st.session_state.q_num
    total_q = len(quiz)

    st.header("Quiz on: " + st.session_state.topic)

    if qn < total_q:
        q_data = quiz[qn]
        st.subheader("❓ Question " + str(qn + 1) + " of " + str(total_q))
        st.write(q_data["q"])
        
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
                    st.markdown("**The correct statement was:** _" + q_data['answer_trans'] + "_")
                
                st.session_state.q_num += 1
                st.rerun()
    else:
        score = st.session_state.score
        st.success("🎉 Quiz Completed! Your score: " + str(score) + "/" + str(total_q))

        topic = st.session_state.topic
        if topic not in st.session_state.user_scores:
            st.session_state.user_scores[topic] = []
        st.session_state.user_scores[topic].append(str(score) + "/" + str(total_q))

        if st.button("🔁 Try Another Topic"):
            # Simple cleanup of session state
            keys_to_delete = ["quiz", "score", "q_num", "in_quiz", "topic"]
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# --- Score History ---
if st.session_state.user_scores:
    with st.expander("📊 Show Score History"):
        for topic, score_list in st.session_state.user_scores.items():
            st.write("**" + topic + "**: " + ', '.join(score_list))
