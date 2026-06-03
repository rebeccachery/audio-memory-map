import gradio as gr

from utils.storage import add_memory
from utils.map_utils import generate_map


def upload_memory(title, lat, lon, audio):

    if audio is None:
        return "Please upload audio.", generate_map()

    add_memory(
        title=title,
        lat=float(lat),
        lon=float(lon),
        audio_path=audio
    )

    return "Memory added successfully!", generate_map()


with gr.Blocks() as demo:

    gr.Markdown("# Audio Memory Map")

    with gr.Row():

        with gr.Column():

            title = gr.Textbox(label="Memory Title")

            lat = gr.Textbox(label="Latitude")

            lon = gr.Textbox(label="Longitude")

            audio = gr.Audio(
                type="filepath",
                label="Record or Upload Audio"
            )

            submit = gr.Button("Save Memory")

            status = gr.Textbox(label="Status")

        with gr.Column():

            map_display = gr.HTML(generate_map())

    submit.click(
        fn=upload_memory,
        inputs=[title, lat, lon, audio],
        outputs=[status, map_display]
    )


if __name__ == "__main__":
    demo.launch()