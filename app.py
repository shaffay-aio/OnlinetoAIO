import time
import pandas as pd
import streamlit as st
from utils.logging_config import setup_logger
from competitor.online.online_to_aio import process_online_only
from utils.online_endpoint import get_data, check_status, normalize_url

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
    st.markdown("<h6 style='text-align: center;'>Load data from DoorDash/UberEats directly to POS in up to 15 minutes</h4>", unsafe_allow_html=True)

    # Input URL
    st.markdown("<h4 style='text-align: center;'>Select a Service</h4>", unsafe_allow_html=True)
    selected_value = st.selectbox(" ", ["Doordash", "Ubereats"])

    st.markdown("<h4 style='text-align: center;'>Enter the Restaurant URL to process</h4>", unsafe_allow_html=True)

    if selected_value == 'Doordash': 
        placeholder="e.g., https://www.doordash.com/store/restaurantname-restaurantid/"
    elif selected_value == 'Ubereats': 
        placeholder="e.g., https://www.ubereats.com/store/restaurantname/restaurantid"
    
    input_url = st.text_input(" ", placeholder=placeholder)

    # Submit button
    st.markdown("<div class='center-button'>", unsafe_allow_html=True)
    if st.button("Submit"):

        if input_url:
            
            st.info("Processing your request. Please wait...")
            normalized_input_url = normalize_url(input_url, selected_value)

            if normalized_input_url is not None:

                with st.spinner(f"Fetching data from {selected_value}..."):  # Loader for the API call

                    # First request details
                    api_url = "http://54.218.231.251:8000/menu-onboarding-scraper"
                    request_data = { "link": normalized_input_url, "platform": selected_value }

                    logger.info(f"Scraping of url {normalized_input_url} started.")

                    # Get the link from the API
                    start = time.time()
                    link = get_data(api_url, request_data)

                    logger.info(f"File recieved from scraping endpoint. Took {round((time.time() - start)/60)} minutes.")

                    try:
                        if link:
                            st.success("URL processed successfully! Generating your file...")

                            # Process the file using the provided function
                            result_data, name = process_online_only(link)
                            logger.info("Online file processing completed.\n")

                            # Provide a download button for the processed file
                            st.markdown("<div class='center-button'>", unsafe_allow_html=True)
                            st.download_button( label="📂 Download Final Online to AIO File", data=result_data, file_name=f"{name}-{selected_value}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" )
                            st.markdown("</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Failed to process the URL. Dataframe is empty. Please try again. {e}")
            else:
                st.error("The input URL does not match the expected store format.")
        else:
            st.warning("Please enter a valid URL before submitting.")

    # Footer
    st.markdown( """ <hr> <p style="text-align: center; color: gray;"> Online To AIO App © 2024 | Powered by Streamlit </p> """, unsafe_allow_html=True )

if __name__ == "__main__":
    main()