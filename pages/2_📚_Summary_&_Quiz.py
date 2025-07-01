# pages/2_📚_Summary_&_Quiz.py

import streamlit as st
from googletrans import Translator
from gtts import gTTS
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
import tempfile
import random
import re

# NOTE: No st.set_page_config() here

st.title("🌐 Multilingual Summary & Quiz Generator")

# Initialize translator
translator = Translator()

# Safe translation function
def safe_translate(text, dest_lang):
    if not text or not text.strip():
        return ""
    try:
        result = translator.translate(text, dest=dest_lang)
        return result.text if result else text
    except Exception:
        return text # Fallback to original text

# Supported languages
LANGUAGES = {
    "English": "en", "Telugu": "te", "Hindi": "hi", "Tamil": "ta", "Kannada": "kn"
}

# Initialize session state for scores if it doesn't exist
if "user_scores" not in st.session_state:
    st.session_state.user_scores = {}

# UI inputs
language = st.selectbox("🌐 Choose Language", list(LANGUAGES.keys()))
lang_code = LANGUAGES[language]
topic = st.text_input("🔍 Enter a topic (e.g., Ashoka, Indus Valley Civilization, Taj Mahal)")

if topic:
    try:
        with st.spinner(f"Searching Wikipedia for '{topic}'..."):
            # Set Wikipedia language for better search results initially
            wikipedia.set_lang("en")
            search_results = wikipedia.search(topic, results=5)
            if not search_results:
                st.error("No Wikipedia articles found for this topic. Please try another one.")
                st.stop()
        
        selected_title = st.selectbox("🔎 Please select the most relevant article:", search_results)

        if selected_title:
            try:
                with st.spinner("Fetching summary..."):
                    page = wikipedia.page(selected_title, auto_suggest=False)
                    summary_en = page.summary
                
                with st.spinner(f"Translating summary to {language}..."):
                    translated_summary = safe_translate(summary_en, lang_code)
                
                st.subheader("📖 Summary")
                st.write(translated_summary)

                # Audio generation
                with st.spinner("Generating audio..."):
                    try:
                        tts = gTTS(text=translated_summary, lang=lang_code)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            tts.save(fp.name)
                            st.audio(fp.name)
                    except Exception as audio_err:
                        st.warning(f"Could not generate audio for this language. Error: {audio_err}")

                if st.button("✔️ Start Quiz", use_container_width=True):
                    sentences = [s.strip() for s in summary_en.split(". ") if len(s.split()) > 5]
                    quiz = []
                    
                    if len(sentences) < 4:
                        st.warning("Summary is too short to generate a meaningful quiz. Please try another topic.")
                        st.stop()

                    selected_sentences = random.sample(sentences, min(3, len(sentences)))

                    for sent in selected_sentences:
                        # Extract a keyword (prioritize capitalized words)
                        words = re.findall(r'\b[A-Z][a-z]+\b', sent)
                        if not words:
                            words = [w for w in sent.split() if len(w) > 5]
                        
                        keyword = random.choice(words) if words else topic
                        
                        question_en = f"Which statement is correct regarding '{keyword}'?"
                        correct_en = sent
                        
                        # Get wrong options from the main sentences list
                        wrongs_pool = [s for s in sentences if s != correct_en]
                        wrongs = random.sample(wrongs_pool, min(3, len(wrongs_pool)))
                        
                        options_en = [correct_en] + wrongs
                        random.shuffle(options_en)

                        # Translate everything for the quiz
                        question_trans = safe_translate(question_en, lang_code)
                        options_trans = [safe_translate(opt, lang_code) for opt in options_en]
                        correct_trans = safe_translate(correct_en, lang_code)

                        quiz.append({
                            "q": question_trans,
                            "options": options_trans,
                            "answer_trans": correct_trans,
                            "explanation": correct_trans
                        })

                    st.session_state.quiz = quiz
                    st.session_state.q_num = 0
                    st.session_state.score = 0
                    st.session_state.in_quiz = True
                    st.session_state.topic = selected_title
                    st.rerun()

            except DisambiguationError:
                st.error("This topic is ambiguous on Wikipedia. Please select a more specific option from the list.")
            except PageError:
                st.error("Could not find a Wikipedia page for the selected title. Please try another topic.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# Quiz Display Logic
if st.session_state.get("in_quiz", False):
    quiz = st.session_state.quiz
    qn = st.session_state.q_num
    
    st.header(f"Quiz on: {st.session_state.topic}")

    if qn < len(quiz):
        q_data = quiz[qn]
        st.subheader(f"❓ Question {qn + 1} of {len(quiz)}")
        st.write(q_data["q"])
        
        # Display the radio button options
        user_answer = st.radio("Choose an option:", q_data["options"], key=f"q{qn}")

        if st.button("Submit Answer", key=f"submit_{qn}"):
            if user_answer == q_data["answer_trans"]:
                st.success("✅ Correct!")
                st.session_state.score += 1
            else:
                st.error("❌ Incorrect.")
                st.markdown(f"**Correct Answer:** _{q_data['answer_trans']}_")
            
            st.session_state.q_num += 1
            st.rerun()
    else:
        # Quiz finished
        score = st.session_state.score
        total = len(quiz)
        st.success(f"🎉 Quiz Completed! Your score: {score}/{total}")

        topic = st.session_state.topic
        if topic not in st.session_state.user_scores:
            st.session_state.user_scores[topic] = []
        st.session_state.user_scores[topic].append(f"{score}/{total}")

        if st.button("🔁 Try Another Topic"):
            # Clear all quiz-related state
            for k in list(st.session_state.keys()):
                if k in ["quiz", "score", "q_num", "in_quiz", "topic"]:
                    del st.session_state[k]
            st.rerun()

# Score History
if st.session_state.user_scores:
    with st.expander("📊 Show Score History"):
        for topic, score_list in st.session_state.user_scores.items():
            st.write(f"**{topic}**: {', '.join(score_list)}")