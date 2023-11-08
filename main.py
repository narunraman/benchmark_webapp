import streamlit as st
import pandas as pd
from st_pages import Page, show_pages, add_page_title, Section
from streamlit_extras.grid import grid
from streamlit_extras.tags import tagger_component
import streamlit_vertical_slider as svs
from streamlit_extras.switch_page_button import switch_page
from annotated_text import annotated_text, annotation

st.set_page_config(
    page_title="Benchmark Viewer",
    page_icon=":book:",
)

# @st.cache_data
def load_data(filename):
    return pd.read_pickle(f'data/{filename}.pkl')

if 'df' not in st.session_state:
    st.session_state.df = load_data('all_tasks')


# Optional -- adds the title and icon to the current page
# add_page_title()

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
# show_pages(
#     [
#         Page("main.py", "Benchmark Viewer", ":book:"),
#         # Page("pages/graphs.py", "Dependency Viewer", ":mag:"),
#         # Section(name="Developer Tools", icon=":file_folder:"),
#         Page("pages/validation.py", "Validation", ":pencil:"),
#         Page("pages/results.py", "Results"),
#     ]
# )

# df = pd.read_pickle("../generated_samples/utility_theory/filled/compute_expec_util.pkl")
# # @st.cache
# def convert_df(df):
#     # IMPORTANT: Cache the conversion to prevent computation on every rerun
#     return df.to_csv().encode('utf-8')

# csv = convert_df(df)

st.title("Rationality Benchmark")
# st.divider()

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

st.session_state['category'] = st.sidebar.radio('Select a Category:', categories)
st.sidebar.divider()

with st.sidebar.expander('Filters'):
    for category in categories:
        st.markdown(f'{category}:')
        st.slider('Difficulty range', 0, 12, (2, 7), key=category)    

# selected_categories = {category: [] for category in categories}
# for category in categories:
#     with st.sidebar.expander(category):
#         selected_categories[category].append(st.slider('Difficulty range:', 0, 12, (2, 7), key=category))

st.sidebar.download_button(label="Download Test", data="", file_name='benchmark_test.csv', mime='text/csv', type='primary')

tab_class = st.tabs(['Curriculum Viewer', 'Score Viewer'])


for category_text in categories[st.session_state.category]:
    with tab_class[0].expander(category_text):
        description_grid = grid([0.2, 0.6], vertical_align='top')
        for name, row in st.session_state.df.groupby('Category').get_group(category_text).iterrows():
            
            # CODE TO SET THE POSITION OF SLIDER
            if len(row['Difficulties']) > 1:
                NB = description_grid.select_slider('Difficulty Level:', options = row['Difficulties'], value = row['Difficulties'][0], key=row['Task Name'])
            else:
                NB = row['Difficulties'][0]
                description_grid.write(f"Difficulty Level: :red[{row['Difficulties'][0]}]", )
            
            # CODE TO GENERATE TASK NAME AND DESCRIPTION
            html=f'''
                <details>
                <summary>{row['Tasks'][row['Difficulties'].index(NB)]}
                </summary>
                <p style='font-family:menlo;font-size:70%;white-space:pre-wrap;background-color:#262731;padding:7px;border-radius:7px;width:425px;'>Example Question:\n{row['questions'][row['Difficulties'].index(NB)]}</p>
                </details>
            '''
            description_grid.markdown(html, unsafe_allow_html=True)

            # CODE TO CHANGE COLOR OF SLIDER
            if len(row['Difficulties']) > 1:
                ColorMinMax = description_grid.markdown(''' <style> div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {
                    background: rgb(1 1 1 / 0%); } </style>''', unsafe_allow_html = True)


                Slider_Cursor = description_grid.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{
                    background-color: rgb(200, 200, 200); box-shadow: rgb(14 38 74 / 20%) 0px 0px 0px 0.2rem;} </style>''', unsafe_allow_html = True)

                    
                Slider_Number = description_grid.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div > div
                                                { color: rgb(200, 60, 15); } </style>''', unsafe_allow_html = True)
                    

                col = f''' <style> div.stSlider > div[data-baseweb = "slider"] > div > div {{
                    background: linear-gradient(to right, rgb(1, 1, 1) 0%, 
                                                rgb(1, 1, 1) {NB}%, 
                                                rgb(1, 1, 1) {NB}%, 
                                                rgb(1, 1, 1) 100%); }} </style>'''

                ColorSlider = description_grid.markdown(col, unsafe_allow_html = True)
            
            
            
            
            # description_grid.write('')

# tab_class = st.tabs(categories)

# for tab_class, category_texts in zip(tab_class, categories):
#     for category_text in categories[category_texts]:
#         with tab_class.expander(category_text):
#             # task_name, difficulty_slider
#             description_grid = grid([0.2, 0.7], vertical_align='top')

#             description_grid.write("**Difficulty Level:**")
#             description_grid.write("**Task:**")
            
#             for name, row in st.session_state.df.groupby('Category').get_group(category_text).iterrows():


#                 if len(row['Difficulties']) > 1:
#                     st.session_state[f"{row['Task Name']}_value"] = description_grid.slider(" ", row['Difficulties'][0], row['Difficulties'][-1], key=row['Task Name'])
#                 else:
#                     st.session_state[f"{row['Task Name']}_value"] = row['Difficulties'][0]
#                     description_grid.write(st.session_state[f"{row['Task Name']}_value"])
                
#                 if f"{row['Task Name']}_value" not in st.session_state:
#                     st.session_state[f"{row['Task Name']}_value"] = 0
                
#                 # if st.session_state[f"{row['Task Name']}_value"] == 0:
#                 #     html=f'''
#                 #     <p style="line-height:30px;border-radius:7px;padding:5px;width:425px;background-color:#262731;color:white;font-family:menlo;font-size:80%">
#                 #      {row['Tasks'][0]}
#                 #      </p>
#                 #     '''
#                 # else:

#                 html=f'''
#                 <br>
#                 <details>
#                 <summary style="line-height:30px;border-radius:7px;padding:5px;width:425px;background-color:#262731;color:white;font-family:menlo;font-size:80%">{row['Tasks'][row['Difficulties'].index(st.session_state[f"{row['Task Name']}_value"])]}
#                 </summary>
#                 Example Question:
#                 </details>
#                 '''
#                     # <p style="line-height:30px;border-radius:7px;padding:5px;width:425px;background-color:#262731;color:white;font-family:menlo;font-size:80%">{row['Tasks'][row['Difficulties'].index(st.session_state[f"{row['Task Name']}_value"])]}
#                     # </p>
#                     # '''
#                 description_grid.markdown(html, unsafe_allow_html=True)
#                 description_grid.write("")
#                 description_grid.markdown("<br>", unsafe_allow_html=True)
                
#                 # task_state = st.button(f"{task_name}")
#                 # if task_state:
#                 #     switch_page(f"pages/{category_text.lower()}/{category.lower()}/{task_name}")
                
