# Indic_History_Hub.py

import streamlit as st

st.set_page_config(
    page_title="Indic History Hub",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the dashboard
st.markdown("""
    <style>
        .main-title {
            font-size: 48px;
            font-weight: bold;
            color: #FF6347; /* Tomato */
            text-align: center;
            padding-top: 20px;
        }
        .subtitle {
            font-size: 24px;
            color: #4682B4; /* SteelBlue */
            text-align: center;
            padding-bottom: 30px;
        }
        .card {
            background: #f0f2f6;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .card:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        .card-title {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .card-text {
            font-size: 16px;
            color: #333;
            flex-grow: 1;
        }
        .card-button {
            margin-top: 20px;
            font-size: 18px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Main Dashboard UI ---

st.markdown('<div class="main-title">🇮🇳 Indic History Hub 🇮🇳</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Explore the Rich Tapestry of Indian Heritage</div>', unsafe_allow_html=True)

st.write("---")

st.info("👈 **Navigate using the sidebar to explore the different tools!**")

st.write("##") # Adds some vertical space

# Create columns for the cards
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    with st.container():
        st.markdown("""
            <div class="card">
                <div class="card-title">✨<br>Magic Stories</div>
                <p class="card-text">
                    Generate beautifully formatted and age-appropriate stories about India's great kings, queens, freedom fighters, and scholars. Perfect for young learners!
                </p>
                <p class="card-button">Discover Tales of Valor!</p>
            </div>
        """, unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown("""
            <div class="card">
                <div class="card-title">📚<br>Summary & Quiz</div>
                <p class="card-text">
                    Enter any topic, get a concise summary from Wikipedia in multiple Indian languages, and then test your knowledge with an auto-generated quiz.
                </p>
                <p class="card-button">Learn and Test Yourself!</p>
            </div>
        """, unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown("""
            <div class="card">
                <div class="card-title">🕉️<br>Sloka Translator</div>
                <p class="card-text">
                    Translate ancient Slokas and verses into modern languages. Listen to both the original pronunciation and the translated meaning with separate audio players.
                </p>
                <p class="card-button">Unlock Ancient Wisdom!</p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.write("---")
st.markdown("<p style='text-align: center; color: grey;'>Built with ❤️ using Streamlit. For educational and exploratory purposes.</p>", unsafe_allow_html=True)