import io
import pandas as pd
import streamlit as st

from utils.missing_fields.fill import fix_missing_fields

def run_fix_missing_fields():

    st.write()
    _, col2, _ = st.columns(3)

    with col2:
        st.image('./resource/logo.png', width=300)

    st.title("Upload a file to fix missing fields 📑")

    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        try:
            dataframes = fix_missing_fields(uploaded_file)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for key in dataframes.keys():
                    dataframes[key].to_excel(writer, sheet_name=key, index=False)
            output.seek(0)

            # Provide the download link
            st.download_button(
                label="Download Excel file",
                data=output,
                file_name='missing_fields_fix.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            st.write("Error Occured: ", e)