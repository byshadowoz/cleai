import streamlit as st

from algorithm.commands.autoCleanerB import DataCleaner
def streamlit_interface():
    st.title("Data Cleaner")
    
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        filename = uploaded_file.name
        cleaner = DataCleaner(uploaded_file, filename)
        
        if st.button("Clean Data"):
            cleaned_df, report = cleaner.auto_clean()
            st.write("Original Rows:", report["original_rows"])
            st.write("Original Columns:", report["original_cols"])
            st.dataframe(cleaned_df)
            
            # Optionally, allow users to download the cleaned data
            csv = cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Cleaned Data",
                data=csv,
                file_name="cleaned_data.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    streamlit_interface()
else:
    print("This script is intended to be run as a Streamlit app.")

