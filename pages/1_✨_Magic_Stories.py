# pages/1_✨_Magic_Stories.py

import streamlit as st
import requests
from urllib.parse import quote
import re

# --- Page Configuration and Styling ---
st.markdown("""
    <style>
        .title {
            font-size: 38px;
            font-weight: bold;
            color: #4a2c2a;
            text-align: center;
        }
        .subtext {
            font-size: 18px;
            color: #5a3e36;
            text-align: center;
            margin-bottom: 20px;
        }
        .story-box {
            background: #fff9f0;
            padding: 30px;
            border-radius: 20px;
            line-height: 1.7;
            color: black;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        }
        .footer {
            font-size: 14px;
            text-align: center;
            color: gray;
            margin-top: 50px;
        }
    </style>
""", unsafe_allow_html=True)

# --- API and Data Configuration ---
WIKI_API_BASE = "https://{lang}.wikipedia.org/w/api.php"
WIKI_REST_BASE = "https://{lang}.wikipedia.org/api/rest_v1"

STORY_DB = {
    'Kings & Queens': [
        ('Krishnadevaraya', 'Vijayanagara king'),
        ('Rani Lakshmibai', 'Queen of Jhansi'),
        ('Raja Raja Chola', 'Great Chola emperor')
    ],
    'Freedom Fighters': [
        ('Subhas Chandra Bose', 'Netaji'),
        ('Bhagat Singh', 'Revolutionary'),
        ('Sarojini Naidu', 'Poet and activist')
    ],
    'Scientists & Scholars': [
        ('Aryabhata', 'Ancient mathematician'),
        ('C. V. Raman', 'Nobel Prize physicist'),
        ('Sushruta', 'Ancient surgeon')
    ]
}

LANGUAGES = {
    'English': 'en', 'Hindi': 'hi', 'Telugu': 'te', 'Tamil': 'ta', 'Bengali': 'bn'
}

AGE_CONFIG = {
    '5-8 years': {'max_words': 250, 'font': 20},
    '9-12 years': {'max_words': 600, 'font': 18},
    '13+ years': {'max_words': 1000, 'font': 16}
}

# --- Utility Functions (with enhanced error handling) ---

@st.cache_data(ttl=3600) # Cache API calls for 1 hour
def fetch_wiki_content(title, lang='en'):
    """Fetches and returns the summary of a Wikipedia page."""
    try:
        # Step 1: Find the exact page title
        search_params = {
            "action": "query", "list": "search", "srsearch": title,
            "format": "json", "srlimit": 1
        }
        search_url = WIKI_API_BASE.format(lang=lang)
        search_res = requests.get(search_url, params=search_params, timeout=10)
        search_res.raise_for_status()
        search_data = search_res.json()

        if not search_data.get('query', {}).get('search'):
            return None
        page_title = search_data['query']['search'][0]['title']

        # Step 2: Fetch the page summary using the exact title
        content_url = WIKI_REST_BASE.format(lang=lang) + f"/page/summary/{quote(page_title)}"
        content_res = requests.get(content_url, timeout=10)
        content_res.raise_for_status()
        return content_res.json().get('extract')
    except requests.exceptions.RequestException as e:
        st.warning(f"Network error while fetching content: {e}")
        return None
    except (KeyError, IndexError):
        return None # Handles cases where API response format is unexpected

def clean_text(text):
    """Removes Wikipedia citations and extra whitespace."""
    if not text:
        return ""
    text = re.sub(r'\[[0-9]+\]', '', text) # Remove [1], [2], etc.
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_story(content, character, char_type, age_group):
    """Formats the fetched content into a story."""
    if not content:
        return None
    
    clean_content = clean_text(content)
    words = clean_content.split()
    max_words = AGE_CONFIG[age_group]['max_words']
    truncated_content = ' '.join(words[:max_words])
    
    # Using more structured HTML for better rendering
    story_html = f"""
    <div style="font-size: {AGE_CONFIG[age_group]['font']}px;">
        <h4>🌟 The Amazing Story of {character} ({char_type}) 🌟</h4>
        <p>Long ago in the vast lands of India, lived a remarkable person whose story we remember to this day...</p>
        <p>{truncated_content}...</p>
        <p>And that is how {character} became a legendary figure in Indian history!</p>
    </div>
    """
    return story_html

@st.cache_data(ttl=3600)
def get_wiki_image_url(title, lang='en'):
    """Fetches a representative image URL from Wikipedia."""
    try:
        url = WIKI_REST_BASE.format(lang=lang) + f"/page/media-list/{quote(title)}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Find the first image in the media list
        if items := data.get("items"):
            for item in items:
                if item.get("type") == "image" and item.get("thumbnail"):
                    return item["thumbnail"]["source"]
        return None
    except Exception:
        return None

# --- UI Layout ---
st.markdown('<div class="title">📖 Magic Indian Stories for Kids</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">Discover tales of valor, wisdom, and courage from Indian history!</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    age = st.selectbox('👶 Choose Age Group', options=list(AGE_CONFIG.keys()))
with col2:
    language = st.selectbox('🌐 Select Language', options=list(LANGUAGES.keys()))

category = st.selectbox('🏰 Select a Story Category', options=list(STORY_DB.keys()))
character, char_type = st.selectbox('🎯 Choose a Historical Figure', options=STORY_DB[category])

# --- Story Generation Logic ---
if st.button('✨ Create My Magic Story!', type='primary', use_container_width=True):
    with st.spinner('🪄 Weaving your story from the threads of history...'):
        lang_code = LANGUAGES[language]
        content = fetch_wiki_content(character, lang_code)

        # Fallback to English if content not found in the selected language
        if not content and language != 'English':
            st.info(f"Couldn’t find a story in {language}. Trying the English version instead...")
            content = fetch_wiki_content(character, 'en')
            lang_code = 'en' # Switch lang_code for audio and image

        if not content:
            st.error(f"❌ So sorry, we couldn't find a story for '{character}'. Please try another historical figure.")
        else:
            story_html = format_story(content, character, char_type, age)

            # --- Display Story and Media ---
            st.markdown(f'<div class="story-box">{story_html}</div>', unsafe_allow_html=True)

            st.write("---")
            
            # Display Audio Player (with error handling)
            st.subheader("🎧 Listen to the Story")
            try:
                # Use a shorter, cleaned version of the text for the audio URL
                text_for_audio = clean_text(re.sub('<[^<]+?>', '', story_html))
                audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={quote(text_for_audio[:500])}&tl={lang_code}&client=tw-ob"
                st.audio(audio_url, format='audio/mp3')
            except Exception as e:
                st.warning(f"Could not generate audio at this time. Error: {e}")

            # Display Image (with error handling)
            st.subheader("🖼️ A Glimpse from History")
            image_url = get_wiki_image_url(character, lang_code)
            if image_url:
                st.image(image_url, caption=f"An image related to {character}")
            else:
                st.info(f"We couldn't find a suitable image for {character}.")

# Footer
st.markdown('<div class="footer">📚 All stories are adapted from Wikipedia and are for educational purposes.</div>', unsafe_allow_html=True)
