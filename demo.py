import time
import streamlit as st
from competitor.online.online_to_aio import process_online_only
from utils.online_endpoint import fun_request, check_status
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    # Set page title and favicon
    st.set_page_config(page_title="Online To AIO", page_icon="🔄", layout="centered")

    # Title and description
    st.title("🔄 Online to AIO")
    st.markdown(
        """
        <style>
        .main {background-color: #f9f9f9; padding: 20px; border-radius: 10px;}
        h1 {color: #2c3e50; text-align: center;}
        .reportview-container {background: #f4f4f4;}
        h4 {font-size: 0.8rem; color: #6c757d; text-align: center;}
        .center-button {display: flex; justify-content: center; align-items: center; margin-bottom: 20px;}
        .center-input {display: flex; justify-content: center; align-items: center; margin-bottom: 20px;}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h6 style='text-align: center;'>Load data from DoorDash directly to POS in up to 15 minutes</h4>", unsafe_allow_html=True)

    # Input URL
    st.markdown("<h4 style='text-align: center;'>Enter the Restaurant URL to process</h4>", unsafe_allow_html=True)
    input_url = st.text_input(" ", placeholder="e.g., https://www.doordash.com/store/...")

    # Submit button
    st.markdown("<div class='center-button'>", unsafe_allow_html=True)
    if st.button("Submit"):
        if input_url:

            st.info("Processing your request. Please wait...")

            with st.spinner(f"Fetching data from Doordash..."):  # Loader for the API call

                # First request details
                api_url = "http://54.218.231.251:8000/menu-onboarding-scraper"
                request_data = { "link": input_url, "platform": "Doordash" }

                # Get the link from the API
                start = time.time()
                link = fun_request(api_url, request_data)

                logger.info(f"File recieved from scraping endpoint. Took {time.time() - start} seconds.")

                try:
                    if link:
                        st.success("URL processed successfully! Generating your file...")

                        # Process the file using the provided function
                        result_data = process_online_only(link)
                        logger.info("Online file processing completed.")

                        # Provide a download button for the processed file
                        st.markdown("<div class='center-button'>", unsafe_allow_html=True)
                        st.download_button(
                            label="📂 Download Final Online to AIO File",
                            data=result_data,
                            file_name=f"file.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
                except:
                    st.error("Failed to process the URL. Please try again.")
        else:
            st.warning("Please enter a valid URL before submitting.")

    # Footer
    st.markdown( """ <hr> <p style="text-align: center; color: gray;"> Online To AIO App © 2024 | Powered by Streamlit </p> """, unsafe_allow_html=True )

if __name__ == "__main__":
    main()
