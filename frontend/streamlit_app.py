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
""", unsafe_allow_html=True)

# App Header
st.markdown("""
    <div class="header-container">
        <div class="header-title">🗺️ Audio Memory Map</div>
        <div class="header-subtitle">Drop raw audio memories onto geographic coordinates and relive your moments visually.</div>
    </div>
""", unsafe_allow_html=True)

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

DEFAULT_LAT, DEFAULT_LON = 40.7128, -73.9352

if "pinned_lat" not in st.session_state:
    st.session_state.pinned_lat = DEFAULT_LAT
if "pinned_lon" not in st.session_state:
    st.session_state.pinned_lon = DEFAULT_LON
if "pin_mode" not in st.session_state:
    st.session_state.pin_mode = True
if "manual_coords" not in st.session_state:
    st.session_state.manual_coords = False

# Sidebar for Adding Memories
st.sidebar.markdown("### 🎙️ Add Memory")

st.sidebar.markdown("#### 📍 Location")
st.session_state.pin_mode = st.sidebar.toggle(
    "Pin on map",
    value=st.session_state.pin_mode,
    help="When on, click anywhere on the map to set this memory's location.",
)
st.session_state.manual_coords = st.sidebar.toggle(
    "Enter coordinates manually",
    value=st.session_state.manual_coords,
    help="Show latitude and longitude fields instead of clicking the map.",
)

if st.session_state.manual_coords:
    st.session_state.pinned_lat = st.sidebar.number_input(
        "Latitude",
        format="%.6f",
        value=float(st.session_state.pinned_lat),
    )
    st.session_state.pinned_lon = st.sidebar.number_input(
        "Longitude",
        format="%.6f",
        value=float(st.session_state.pinned_lon),
    )
else:
    if st.session_state.pin_mode:
        st.sidebar.info("Click the map to drop a pin for this memory.")
    else:
        st.sidebar.caption("Turn on **Pin on map** to choose a location by clicking.")
    st.sidebar.markdown(
        f"**Pinned location:** {st.session_state.pinned_lat:.5f}, {st.session_state.pinned_lon:.5f}"
    )
    if st.sidebar.button("Reset pin", use_container_width=True):
        st.session_state.pinned_lat = DEFAULT_LAT
        st.session_state.pinned_lon = DEFAULT_LON
        st.rerun()

with st.sidebar.form("memory_form", clear_on_submit=True):
    title = st.text_input("Memory Title", placeholder="E.g., Rain in Central Park")
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
                success, res = upload_memory(
                    title,
                    st.session_state.pinned_lat,
                    st.session_state.pinned_lon,
                    transcript,
                    audio_file,
                )
                if success:
                    st.sidebar.success("Memory saved successfully!")
                    st.rerun()
                else:
                    st.sidebar.error(f"Failed to save memory: {res}")

# Main Layout
col_map, col_details = st.columns([2, 1])

memories = fetch_memories()

with col_map:
    st.subheader("Interactive Memory Map")
    if st.session_state.pin_mode and not st.session_state.manual_coords:
        st.caption("Click the map to pin where this memory happened.")

    # Initialize Folium map
    # Center map on average coords or default NYC
    if memories:
        avg_lat = sum(m['lat'] for m in memories) / len(memories)
        avg_lon = sum(m['lon'] for m in memories) / len(memories)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
    else:
        m = folium.Map(location=[DEFAULT_LAT, DEFAULT_LON], zoom_start=12)

    # Show the pending pin for the memory being created
    folium.Marker(
        [st.session_state.pinned_lat, st.session_state.pinned_lon],
        tooltip="New memory location",
        icon=folium.Icon(color="red", icon="map-pin", prefix="fa"),
    ).add_to(m)

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

    # Render map and capture clicks when pin mode is active
    map_data = st_folium(
        m,
        width="100%",
        height=500,
        key="memory_map",
        returned_objects=["last_clicked"],
    )

    if (
        st.session_state.pin_mode
        and not st.session_state.manual_coords
        and map_data
        and map_data.get("last_clicked")
    ):
        clicked = map_data["last_clicked"]
        if (
            abs(clicked["lat"] - st.session_state.pinned_lat) > 1e-6
            or abs(clicked["lng"] - st.session_state.pinned_lon) > 1e-6
        ):
            st.session_state.pinned_lat = clicked["lat"]
            st.session_state.pinned_lon = clicked["lng"]
            st.rerun()

with col_details:
    st.subheader("Saved Memories")
    if not memories:
        st.info("No memories uploaded yet. Use the sidebar to add your first audio memory!")
    else:
        for idx, memory in enumerate(memories):
            audio_url = f"{BACKEND_URL}/memories/{memory['audio_ref']}/audio"
            with st.container(border=True):
                st.markdown(f"**{memory['title']}**")
                st.caption(f"📍 {memory['lat']:.5f}, {memory['lon']:.5f}")
                if memory.get('transcript'):
                    st.write(memory['transcript'])
                # Audio player using URL stream
                st.audio(audio_url)
                st.divider()
