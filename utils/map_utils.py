import folium # type: ignore

from utils.storage import load_memories


def generate_map():

    memories = load_memories()

    m = folium.Map(
        location=[40.74, -74.03],
        zoom_start=11
    )

    for memory in memories:

        popup_html = f"""
        <b>{memory['title']}</b><br>
        Latitude: {memory['lat']}<br>
        Longitude: {memory['lon']}
        """

        folium.Marker(
            [memory["lat"], memory["lon"]],
            popup=popup_html
        ).add_to(m)

    return m._repr_html_()