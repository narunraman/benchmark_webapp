import streamlit as st
import random
import os
import pandas as pd
import streamlit_antd_components as sac
from st_pages import Page, show_pages, add_page_title, Section
from streamlit_extras.grid import grid
from streamlit_extras.tags import tagger_component
import streamlit_vertical_slider as svs
from streamlit_extras.switch_page_button import switch_page
from annotated_text import annotated_text, annotation

# def example_one():

pages = st.source_util.get_pages('main.py')
new_page_names = {
    'main': '📖 REASON Benchmark',
    'results': '📈 REASON Scores',
}

for key, page in pages.items():
  if page['page_name'] in new_page_names:
    page['page_name'] = new_page_names[page['page_name']]

st.set_page_config(
    page_title="REASON Benchmark",
    page_icon=":book:",
    layout="wide"
)

if 'display_question' not in st.session_state:
    st.session_state.display_question = ['Dominated Strategies']

def load_pickle(filename):
    df = pd.read_pickle(f'data/{filename}.pkl')
    st.session_state.df = df

st.title('REASON Benchmark')
load_pickle('all_tasks')

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
        'Reference Independence'
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

name2index_tree = {}
with st.sidebar:
    st.session_state.view = st.radio('Select a View:', ['Hierarchy', 'Curriculum'])

def display_sidebar():
    with st.sidebar:
        placeholder = st.empty()
        if st.session_state.view == 'Hierarchy':
            tree_items = []

            index = 0
            for category in categories:
                sub_category_items = []
                index += 1
                for sub_category in categories[category]:
                    task_items = []
                    index += 1
                    for name, row in st.session_state.df.groupby('group_name').get_group(sub_category).iterrows():
                        task_items.append(sac.TreeItem(row['task_name']))
                        
                        name2index_tree[row['task_name']] = [index]
                        index += 1

                    sub_category_items.append(sac.TreeItem(sub_category, children=task_items, disabled=True))
                tree_items.append(sac.TreeItem(category, children = sub_category_items, disabled=True))

            names = list(name2index_tree.keys())
            for name in st.session_state.display_question:
                if name in names:
                    tree_index = name2index_tree[name]
            
            with placeholder:
                sac.tree(
                    items = tree_items, 
                    label = '**Task Hierarchy:**', 
                    # index = tree_index, 
                    format_func = 'title',
                    key='first')
                
            placeholder.empty()
            st.session_state.display_question = sac.tree(
                    items = tree_items, 
                    label = '**Task Hierarchy:**', 
                    index = tree_index, 
                    format_func = 'title',
                    key='second')

        
        elif st.session_state.view == 'Curriculum':
            st.session_state.grade_range = st.sidebar.slider('Choose a Grade Range:', 0, 12, (2, 7)) 



def display_questions(row):
    st.header(row['task_name'].iloc[0], divider='gray')
    st.warning(f"**Task Description:**  \n{row['description'].iloc[0]}")
    with st.expander('Example Questions:'):
        question_grid = grid([0.3, 0.3])
        for i, diff in enumerate(row['difficulty_levels'].iloc[0]):
            question = row['questions'].iloc[0][i].replace('\n', '  \n').replace('$', '\$').replace('*', '$*$')
            html = f"""<span style="color: #F9EA9A;font-size:100%">**Grade {diff} Example Question:**</span>  \n{question}"""
            question_grid.markdown(html, unsafe_allow_html=True)

def display_callback():
    print(st.session_state.cascade_value)

def display_explorer():
    placeholder = st.empty()

    counter = 0
    for category in categories:
        group_items = []
        cat_index = counter
        counter += 1
        for group_name in categories[category]:
            task_items = []
            group_index = counter
            counter += 1
            for name, row in st.session_state.df.groupby('group_name').get_group(group_name).iterrows():
                task_items.append(sac.CasItem(row['task_name'].replace("'S", "\'s")))
                task_index = counter
                name2index_cascade[row['task_name']] = [cat_index, group_index, task_index]
                counter += 1
            group_items.append(sac.CasItem(group_name, children = task_items))
            
        cascader_items.append(sac.CasItem(category, children = group_items))

    names = list(name2index_cascade.keys())
    for name in st.session_state.display_question:
        if name in names:
            cascade_index = name2index_cascade[name]

    # with placeholder:

    #     st.session_state.display_question = sac.cascader(
    #         items=cascader_items, 
    #         label='**Choose a Task:**', 
    #         # index=casecade_index,#name2index_cascade[st.session_state.display_question[-1]],
    #         # index=[25, 26, 27], 
    #         format_func='title', 
    #         placeholder='Type or Click to Select', 
    #         search=True, 
    #         clear=True)
        
    # placeholder.empty()
    st.session_state.display_question = sac.cascader(
            items=cascader_items, 
            label='**Choose a Task:**', 
            index=cascade_index,#name2index_cascade[st.session_state.display_question[-1]],
            # index=[25, 26, 27], 
            format_func='title', 
            placeholder='Type or Click to Select', 
            search=True, 
            clear=True,
            key='cascade_value',
            on_change=display_callback)

name2index_cascade = {}

if st.session_state.view == 'Hierarchy':
    cascader_items = []
    
    display_explorer()
    display_sidebar()
    
    display_questions(st.session_state.df.query("task_name ==@ st.session_state.display_question"))

elif st.session_state.view == 'Curriculum':
    st.markdown(
        """
    <style>
    .streamlit-expanderHeader {
        font-size: x-large;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
    display_sidebar()
    grade_df = st.session_state.df[st.session_state.df.difficulty_levels.apply(lambda x: any([diff in range(*st.session_state.grade_range) for diff in x]))]
    rev_categories = {key: value for value in categories for key in categories[value]}
    grade_df['category'] = grade_df['group_name'].apply(lambda x: rev_categories[x])
    for category_name, category_group in grade_df.groupby('category', sort=False):
        st.header(category_name, divider='gray')
        for group_name, group_df in category_group.groupby('group_name', sort=False):
            st.subheader(group_name+":")
            question_grid = grid([0.3, 0.3])
            for _, group_row in group_df.iterrows():
                with question_grid.expander(group_row['task_name']):
                    for i, diff in enumerate(group_row['difficulty_levels']):
                        if diff in list(range(st.session_state.grade_range[0], st.session_state.grade_range[1]+1)):
                            question = group_row['questions'][i].replace('$', '\$').replace('\n', '  \n')
                            st.markdown(f':orange[Grade {diff} Example Question:]  \n{question}')

