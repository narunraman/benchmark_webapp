import streamlit as st
import pandas as pd
from streamlit_extras.grid import grid
from st_pages import Page,Section, show_pages, add_page_title
from streamlit_agraph import agraph, Node, Edge, Config

# @st.cache_data
def load_data(filename):
    return pd.read_pickle(f'data/{filename}.pkl')

if 'df' not in st.session_state:
    st.session_state.df = load_data('all_tasks')


show_pages(
    [
        Page("main.py", "Benchmark Viewer", ":book:"),
        Page("pages/graphs.py", "Dependency Viewer", ":mag:"),
        # Section(name="Developer Tools", icon=":file_folder:"),
        Page("pages/validation.py", "Validation", ":pencil:"),
    ]
)

# categories = {
#     "Foundations": [
#         'Arithmetic', 
#         'Probability', 
#         'Optimization', 
#         'Logic', 
#         'Theory of Mind'
#     ], 
#     "Preferences": [
#         'Utility Theory', 
#         'Reference Independent Decision-Making'
#     ], 
#     "Decision Making Under Uncertainty": [
#         'Expected Utility Theory', 
#         'Judgements Under Limited Data'
#     ], 
#     "Decision Making in the Presence of Other Agents": [
#         'Game Theory'
#     ]
# }


# tab_class = st.tabs(categories)

# for tab_class, category_texts in zip(tab_class, categories):
#     for category_text in categories[category_texts]:
#         with tab_class.expander(category_text):
st.write("**Task:**")
# rows = st.session_state.df.groupby('Category').get_group(category_text)
# for name in rows['Tasks']:
nodes = []
edges = []
for i, row in st.session_state.df.iterrows():
    # html=f'''<p style="border-radius:7px;padding:5px;width:425px;background-color:#262731;color:white;font-family:menlo;font-size:80%">
    #         {name[0]}
    #         </p>'''
    # st.markdown(html, unsafe_allow_html=True)
    nodes.append( Node(id=f"{i}", 
                    label=row['Task Name'], 
                    size=20, 
                    shape="box",
                    # image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png"
                    ) 
                ) # includes **kwargs
    if row['Dependencies']:
        for d in row['Dependencies']:
            edges.append( Edge(source=f"{i}", 
                            # label="requires", 
                            target=f"{d}", 
                            type="CURVE_SMOOTH",
                            # **kwargs
                            ) 
                        ) 

config = Config(width=700,
                height=500,
                directed=True, 
                physics=True, 
                hierarchical=False,
                levelSeparation=500,
                collapsible=True,
                # direction='LR',
                node={'labelProperty':'label', 'renderLabel':False},
                # **kwargs
                )
agraph(nodes=nodes, edges=edges, config=config)


