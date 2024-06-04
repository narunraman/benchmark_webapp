import streamlit as st
import random
import os
import pandas as pd
import uuid
import streamlit_antd_components as sac
from streamlit_extras.grid import grid
from streamlit_extras.stylable_container import stylable_container

# from st_pages import Page, show_pages, add_page_title, Section
# from streamlit_extras.switch_page_button import switch_page


st.set_page_config(
    page_title="STEER Taxonomy",
    page_icon=":clipboard:",
    layout="wide"
)
st.logo('images/steer_logo.png', icon_image='images/steer_small.png')

if 'display_question' not in st.session_state:
    st.session_state.display_question = 'Dominated Strategies'

if 'cascade_clicked' not in st.session_state:
    st.session_state.cascade_clicked = False

if 'tree_clicked' not in st.session_state:
    st.session_state.tree_clicked = False

if 'tree_key' not in st.session_state:
    st.session_state.tree_key = 0

if 'cascade_key' not in st.session_state:
    st.session_state.cascade_key = 0

def load_pickle(filename):
    df = pd.read_pickle(f'data/{filename}.pkl')
    st.session_state.df = df


st.title('Elements of Rationality')
load_pickle('all_tasks')

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
#         'Reference Independence'
#     ], 
#     "Decision Making Under Uncertainty": [
#         'Expected Utility Theory', 
#         'Risk Assessment'
#     ], 
#     "Decision Making in the Presence of Other Agents": [
#         'Single-Round Game Theory',
#         'Multi-Round Game Theory',
#     ]
# }

categories = {
    "Foundations": [
        'Arithmetic',
        'Probability', 
        'Optimization', 
        'Logic', 
        'Theory of Mind'
    ], 
    "Decisions in Single-Agent Environments": [
        'Axioms of Utility in Deterministic Environments', 
        'Avoidance of Cognitive Biases in Deterministic Environments',
        'Axioms of Utility in Stochastic Environments', 
        'Avoidance of Cognitive Biases in Stochastic Environments',
    ], 
    "Decisions in Multi-Agent Environments": [
        'Normal Form Games',
        'Extensive Form Games',
        'Imperfect Information in Extensive Form Games',
        'Infinitely Repeated Games',
        'Bayesian Games'
    ],
    "Decisions on Behalf of Others": [
        'Axioms of Social Choice',
        'Social Choice',
        'Desirable Properties in Mechanism Design',
        'Mechanism Design',
    ],
}



# with st.sidebar:
#     st.session_state.view = st.radio('Select a View:', ['Hierarchy', 'Curriculum'])

# @st.cache_data
def gen_hierarchies():
    st.session_state.name2index = {}
    st.session_state.cascader_items = []
    st.session_state.tree_items = []
    counter = 0
    for category in categories:

        cascader_group_items = []
        tree_group_items = []

        cat_index = counter
        counter += 1
        for group_name in categories[category]:
            
            cascader_task_items = []
            tree_task_items = []

            group_index = counter
            counter += 1
            for name, row in st.session_state.df.groupby('group_name').get_group(group_name).iterrows():
                
                cascader_task_items.append(sac.CasItem(row['task_name'].replace("\'S", "\'s")))
                tree_task_items.append(sac.TreeItem(row['task_name']))

                task_index = counter
                st.session_state.name2index[row['task_name']] = [cat_index, group_index, task_index]
                counter += 1
            
            cascader_group_items.append(sac.CasItem(group_name, children = cascader_task_items))
            tree_group_items.append(sac.TreeItem(group_name, children=tree_task_items, disabled=True))
            
        st.session_state.cascader_items.append(sac.CasItem(category, children = cascader_group_items))
        st.session_state.tree_items.append(sac.TreeItem(category, children = tree_group_items, disabled=True))

@st.experimental_fragment
def cascade_callback():
    try:
        st.session_state.display_question = st.session_state[st.session_state.cascade_key][-1]
    except:
        st.session_state.display_question = 'EMPTY_DISPLAY'
    st.session_state.cascade_clicked = True

@st.experimental_fragment
def tree_callback():
    try:
        st.session_state.display_question = st.session_state[st.session_state.tree_key][-1]
    except:
        st.session_state.display_question = 'EMPTY_DISPLAY'
    st.session_state.tree_clicked = True

# def display_sidebar():
#     with st.sidebar:
#         tree_index = st.session_state.name2index.get(st.session_state.display_question, 'EMPTY_DISPLAY')
#         st.session_state.tree_key = str(uuid.uuid4())
#         if tree_index != 'EMPTY_DISPLAY': 
#             sac.tree(
#                     items = st.session_state.tree_items, 
#                     label = '**Taxonomy of Elements:**', 
#                     index = tree_index[-1], 
#                     format_func = 'title',
#                     key=st.session_state.tree_key,
#                     on_change=tree_callback,
#             )
#         else:
#             sac.tree(
#                     items = st.session_state.tree_items, 
#                     label = '**Taxonomy of Elements:**', 
#                     # index = tree_index[-1], 
#                     format_func = 'title',
#                     key=st.session_state.tree_key,
#                     on_change=tree_callback,
#             )

# Example texts for the carousel
texts = ["Text 1", "Text 2", "Text 3"]

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# Function to navigate the carousel
def navigate_carousel(direction):
    if direction == "next":
        st.session_state.current_index = (st.session_state.current_index + 1) % len(texts)
    elif direction == "prev":
        st.session_state.current_index = (st.session_state.current_index - 1) % len(texts)

def display_questions(row):
    try:
        st.header(row['task_name'].iloc[0], divider='gray')
        st.warning(f"**Element Description:**  \n{row['description'].iloc[0]}")
        col1, col2 = st.columns([0.45, 0.45])
        for i, diff in enumerate(row['difficulty_levels'].iloc[0]):
            question = row['questions'].iloc[0][i].replace('\n', '  \n').replace('$', '\$').replace('*', '$*$')
            text = f"""**Grade {diff} Example Question:**  \n{question}"""
            # print(row['difficulty_levels'].iloc[0])
                # if len(row['difficulty_levels'].iloc[0]) == 1:
                #     st.markdown(text)
                # else:
            if i % 2 == 0:
                with col1:
                    # with stylable_container(
                    #     key="container_with_border",
                    #     css_styles="""
                    #         {
                    #             border: 1px solid rgba(49, 51, 63, 0.2);
                    #             border-radius: 0.5rem;
                    #             padding: calc(1em - 1px)
                    #         }
                    #         """,
                    # ):
                    st.markdown(text)
            else:
                with col2:
                    # with st.container(border = True):
                    st.markdown(text)
        
        # with stylable_container(
        #     key="container_with_border",
        #     css_styles="""
        #         {
        #             border: 1px solid rgba(49, 51, 63, 0.2);
        #             border-radius: 0.5rem;
        #             padding: calc(1em - 1px);
        #             display: flex;
        #             flex-direction: column;
        #             justify-content: space-between;
        #             height: 200px;
        #         }
        #         .text-indicator {
        #             position: absolute;
        #             top: 0;
        #             right: 20px;
        #             padding: 10px;
        #         }
        #         """,
        # ):
        #     st.markdown('**Grade 2 Example Question:**')
        #     # Text indicator at the top right
        #     st.markdown(f'<div class="text-indicator">{st.session_state.current_index + 1} / {len(texts)}</div>', unsafe_allow_html=True)
        #     # st.markdown(f"**{st.session_state.current_index + 1} / {len(texts)}**", unsafe_allow_html=True)
            
        #     # Carousel content in the middle
        #     st.write(texts[st.session_state.current_index])

        #     # Navigation buttons at the bottom
        #     col1, col2 = st.columns([1, 1])
        #     with col1:
        #         st.button("Previous", on_click=navigate_carousel, args=("prev",))
        #     with col2:
        #         st.button("Next", on_click=navigate_carousel, args=("next",))

    except IndexError:
        with st.columns([0.09, 0.9, 0.01])[1]:
        # st.write("This is a web app that allows users to explore and learn about different elements of rationality. It provides a taxonomy of elements and displays example questions and descriptions for each element. Users can navigate through the elements using the cascader or tree view in the sidebar. The main content area displays the selected element's description and example questions. Additionally, there is a carousel at the bottom that showcases different texts related to the selected element. Feel free to explore and learn!")
            st.image('images/taxonomy.jpg')

    # with st.expander('Example Questions:'):
    # question_grid = grid([0.5, 0.5])
            # question_grid.markdown(text)


def display_explorer():
    cascade_index = st.session_state.name2index.get(st.session_state.display_question, 'EMPTY_DISPLAY')

    st.session_state.cascade_key = str(uuid.uuid4())
    if cascade_index != 'EMPTY_DISPLAY':
        value = sac.cascader(
                items=st.session_state.cascader_items, 
                label='**Choose an Element:**', 
                # index=cascade_index,
                format_func='title', 
                placeholder='Type or Click to Select', 
                search=True, 
                clear=True,
                # key=st.session_state.cascade_key,
                # on_change=cascade_callback
        )
        # st.write(value)
        display_questions(st.session_state.df.query("task_name ==@ value[-1]"))
    else:
        # st.session_state.display_question = st.session_state[st.session_state.cascade_key][-1]
        value = sac.cascader(
                items=st.session_state.cascader_items, 
                label='**Choose an Element:**', 
                format_func='title', 
                placeholder='Type or Click to Select', 
                search=True, 
                clear=True,
                # key=st.session_state.cascade_key,
                # on_change=cascade_callback
        )
        # st.write(value)
        # display_question = st.session_state[value][-1]
        if value:
            display_questions(st.session_state.df.query("task_name ==@ value[-1]"))

# name2index_cascade = {}
if __name__ == '__main__':
    if ['name2index'] not in st.session_state:
        gen_hierarchies()
    display_explorer()
    # print('hierarchy')
    # display_sidebar()
    # if st.session_state.display_question != 'EMPTY_DISPLAY':
    #     display_questions(st.session_state.df.query("task_name ==@ st.session_state.display_question"))


