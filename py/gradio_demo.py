import gradio as gr
import pandas as pd
from utils.online_endpoint import get_data, check_status
from io import BytesIO

def update_placeholder(selected_service):

    """Update the placeholder based on the selected service."""
    if selected_service.lower() == "doordash":
        return "e.g., https://www.doordash.com/store/..."
    else:
        return "e.g., https://www.ubereats.com/store/..."

def show_selection(service, url):

    # Scrape data based on the service and URL
    api_url = "http://54.218.231.251:8000/menu-onboarding-scraper"
    request_data = { "link": url, "platform": service }
    data = get_data(request_data, api_url)  # Ensure this function returns data suitable for Excel

    message = f"You selected: {service}. URL entered: {url}"
    return message, data

# Define the Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# Online to AIO")

    with gr.Row():
        gr.Column()  # Left empty column for spacing

        with gr.Column():
            # Dropdown to select the online platform
            service = gr.Dropdown( choices=["Ubereats", "Doordash"], label="Select Online Platform", value="Ubereats" )

            # Textbox for entering the restaurant URL with a dynamic placeholder
            url = gr.Textbox( label="Enter Restaurant URL", placeholder="e.g., https://www.ubereats.com/store/...", type="text" )

            # Update the placeholder when the service changes
            service.change( fn=update_placeholder, inputs=service, outputs=url )

            # Button to start scraping
            submit_button = gr.Button( "Start Scraping", variant="primary", icon='./resource/logo.png' )

            # Output textbox to display messages
            output_text = gr.Textbox( label="Output", interactive=False )

            # File component for downloading the Excel file
            download_file = gr.File( label="Download Excel", visible=False)  # Initially hidden )

            # Define what happens when the submit button is clicked
            submit_button.click( fn=show_selection, inputs=[service, url], outputs=[output_text, download_file] )

        gr.Column()  # Right empty column for spacing

    # Optional: Automatically show the download button when a file is available
    download_file.change(
        lambda file: gr.update(visible=bool(file)),
        inputs=download_file,
        outputs=download_file
    )

# Launch the Gradio app
app.launch()
