import streamlit as st
import pandas as pd
from st_pages import Page, show_pages, add_page_title, Section
from streamlit_extras.grid import grid
from streamlit_extras.tags import tagger_component
from annotated_text import annotated_text, annotation

st.set_page_config(
    page_title="Benchmark Viewer",
    page_icon=":book:",
)

@st.cache_data
def load_data(filename):
    return pd.read_pickle(f'data/{filename}.pkl')

if 'df' not in st.session_state:
    st.session_state.df = load_data('all_tasks')


# Optional -- adds the title and icon to the current page
# add_page_title()

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("main.py", "Benchmark Viewer", ":book:"),
        # Page("pages/graphs.py", "Dependency Viewer", ":mag:"),
        # Section(name="Developer Tools", icon=":file_folder:"),
        Page("pages/validation.py", "Validation", ":pencil:"),
    ]
)

# df = pd.read_pickle("../generated_samples/utility_theory/filled/compute_expec_util.pkl")
# # @st.cache
# def convert_df(df):
#     # IMPORTANT: Cache the conversion to prevent computation on every rerun
#     return df.to_csv().encode('utf-8')

# csv = convert_df(df)

st.title("Rationality Benchmark")

st.sidebar.header("Filters")

categories = {
    "Foundations": [
        'Arithmetic', 
        'Probability', 
        'Optimization', 
        'Logic', 
        'Theory of Mind'
    ], 
    "Preferences": [
        'Utility Theory', 
        'Reference Independent Decision-Making'
    ], 
    "Decision Making Under Uncertainty": [
        'Expected Utility Theory', 
        'Risk Assessment'
    ], 
    "Decision Making in the Presence of Other Agents": [
        'Single-Round Game Theory',
        'Multi-Round Game Theory',
    ]
}

selected_categories = {category: [] for category in categories}
for category in categories:
    with st.sidebar.expander(category):
        selected_categories[category].append(st.slider('Difficulty range:', 0, 12, (2, 7), key=category))
# st.sidebar.write('Values:', values)
st.sidebar.download_button(label="Download Test", data="", file_name='benchmark_test.csv', mime='text/csv', type='primary')




tab_class = st.tabs(categories)


for tab_class, category_texts in zip(tab_class, categories):
    for category_text in categories[category_texts]:
        with tab_class.expander(category_text):
            task_name, difficulty_slider = st.columns([0.6, 0.3])

            task_name.write("**Task:**")
            task_name.write("")
            task_name.write("")
            difficulty_slider.write("**Difficulty Range:**")
            for name, row in st.session_state.df.groupby('Category').get_group(category_text).iterrows():

                if len(row['Difficulties']) > 1:
                    st.session_state[f"{row['Task Name']}_value"] = difficulty_slider.slider(" ", row['Difficulties'][0], row['Difficulties'][-1], key=row['Task Name'])
                else:
                    st.session_state[f"{row['Task Name']}_value"] = row['Difficulties'][0]
                    difficulty_slider.write(st.session_state[f"{row['Task Name']}_value"])
                
                if f"{row['Task Name']}_value" not in st.session_state:
                    st.session_state[f"{row['Task Name']}_value"] = 0
                
                if st.session_state[f"{row['Task Name']}_value"] == 0:
                    html=f'''
                    <p style="line-height:30px;border-radius:7px;padding:5px;width:425px;background-color:#262731;color:white;font-family:menlo;font-size:80%">
                     {row['Tasks'][0]}
                     </p>
                    '''
                else:
                    html=f'''
                    <p style="line-height:30px;border-radius:7px;padding:5px;width:425px;background-color:#262731;color:white;font-family:menlo;font-size:80%">{row['Tasks'][row['Difficulties'].index(st.session_state[f"{row['Task Name']}_value"])]}
                    </p>
                    '''
                task_name.markdown(html, unsafe_allow_html=True)
                task_name.write("")
                task_name.markdown("<br>", unsafe_allow_html=True)