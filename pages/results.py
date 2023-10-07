import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
  
  
# st.set_page_config(page_title="This is a Simple Streamlit WebApp")
# st.title("This is the Home Page Geeks.")
# st.text("Geeks Home Page")
  
df =  pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
  
filtered_df = dataframe_explorer(df, case=False)

# st.line_chart(filtered_df)

st.dataframe(filtered_df, use_container_width=True)