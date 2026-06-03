import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import os
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Setup page config
st.set_page_config(
    page_title="Audio Memory Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        /* Apply Outfit Font globally */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }

        /* Glassmorphic Cards & UI styling */
        .header-container {
            background: linear-gradient(135deg, #1e1e38 0%, #0d0d1b 100%);
            padding: 2.5rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .header-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(90deg, #ff7b00, #ffae00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        .header-subtitle {
            font-size: 1.1rem;
            font-weight: 300;
            color: #d1d1e0;
        }

        /* Customize sidebar */
        .css-1d391tw {
            background-color: #0d0d1b !important;
        }
        
        /* Custom buttons styling */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #ff7b00, #ffae00);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 2rem;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(255, 123, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        div.stButton > button:first-child:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 123, 0, 0.5);
            background: linear-gradient(90deg, #ffae00, #ff7b00);
        }
    </style>
""", unsafe_allowed_html=True)

# App Header
st.markdown("""
    <div class="header-container">
        <div class="header-title">🗺️ Audio Memory Map</div>
        <div class="header-subtitle">Drop raw audio memories onto geographic coordinates and relive your moments visually.</div>
    </div>
""", unsafe_allowed_html=True)

# Fetch memories from API helper
def fetch_memories():
    try:
        response = requests.get(f"{BACKEND_URL}/memories")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching memories: {response.text}")
            return []
    except Exception as e:
        st.error(f"Failed to connect to backend API: {e}")
        return []

# Upload memory to API helper
def upload_memory(title, lat, lon, transcript, audio_file):
    files = {"audio": (audio_file.name, audio_file.read(), audio_file.type)}
    data = {
        "title": title,
        "lat": lat,
        "lon": lon,
        "transcript": transcript
    }
    try:
        response = requests.post(f"{BACKEND_URL}/memories", data=data, files=files)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, str(e)

# Sidebar Form for Adding Memories
st.sidebar.markdown("### 🎙️ Add Memory")
with st.sidebar.form("memory_form", clear_on_submit=True):
    title = st.text_input("Memory Title", placeholder="E.g., Rain in Central Park")
    lat = st.number_input("Latitude", format="%.6f", value=40.7128)
    lon = st.number_input("Longitude", format="%.6f", value=-73.9352)
    transcript = st.text_area("Transcript / Notes (Optional)", placeholder="What happened here?")
    audio_file = st.file_uploader("Upload Audio (WAV or MP3)", type=["wav", "mp3"])
    
    submitted = st.form_submit_button("Save Memory")
    
    if submitted:
        if not title:
            st.sidebar.error("Title is required.")
        elif not audio_file:
            st.sidebar.error("Please upload an audio file.")
        else:
            with st.spinner("Uploading memory..."):
                success, res = upload_memory(title, lat, lon, transcript, audio_file)
                if success:
                    st.sidebar.success("Memory saved successfully!")
                    # Refresh the page using experimental rerun
                    st.rerun()
                else:
                    st.sidebar.error(f"Failed to save memory: {res}")

# Main Layout
col_map, col_details = st.columns([2, 1])

memories = fetch_memories()

with col_map:
    st.subheader("Interactive Memory Map")
    
    # Initialize Folium map
    # Center map on average coords or default NYC
    if memories:
        avg_lat = sum(m['lat'] for m in memories) / len(memories)
        avg_lon = sum(m['lon'] for m in memories) / len(memories)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
    else:
        m = folium.Map(location=[40.7128, -73.9352], zoom_start=12)

    # Add markers
    for memory in memories:
        # Create audio element using direct backend url stream
        audio_url = f"{BACKEND_URL}/memories/{memory['audio_ref']}/audio"
        popup_html = f"""
        <div style="font-family: 'Outfit', sans-serif; font-size: 13px; min-width: 200px;">
            <b>{memory['title']}</b><br>
            <span style="color: #666; font-size: 11px;">{memory['lat']:.4f}, {memory['lon']:.4f}</span><br>
            <hr style="margin: 5px 0;">
            {f'<p style="margin: 5px 0; font-style: italic;">"{memory["transcript"]}"</p>' if memory.get('transcript') else ''}
            <audio controls style="width: 100%; height: 30px; margin-top: 5px;">
                <source src="{audio_url}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
        </div>
        """
        
        folium.Marker(
            [memory["lat"], memory["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=memory["title"],
            icon=folium.Icon(color="orange", icon="volume-up", prefix="fa")
        ).add_to(m)

    # Render map
    st_folium(m, width="100%", height=500, key="memory_map")

with col_details:
    st.subheader("Saved Memories")
    if not memories:
        st.info("No memories uploaded yet. Use the sidebar to add your first audio memory!")
    else:
        for idx, memory in enumerate(memories):
            audio_url = f"{BACKEND_URL}/memories/{memory['audio_ref']}/audio"
            with st.container(border=True):
                st.markdown(f"**{memory['title']}**")
                st.caption(f"Coordinates: {memory['lat']:.5f}, {memory['lon']:.5f}")
                if memory.get('transcript'):
                    st.write(memory['transcript'])
                # Audio player using URL stream
                st.audio(audio_url)
                st.divider()
