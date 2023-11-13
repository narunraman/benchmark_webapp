import streamlit as st
import pandas as pd
import streamlit_antd_components as sac
import random
from streamlit_extras.grid import grid


# def example_one():
st.set_page_config(layout="centered")
st.title('REASON Benchmark Scores')

@st.cache_data
def load_data(filename):
    return pd.read_pickle(f'data/results/{filename}.pkl')
df = pd.concat([load_data('gpt-4_renamed'), load_data('gpt-3.5_renamed')], sort=False, ignore_index=True)

df['Expected Accuracy'] = df.apply(lambda row: row['model_answer'] == row['answer'], axis=1)
results_df = df.groupby('model')['Expected Accuracy'].mean().reset_index()
results_df['95% ci'] = [random.random()]*len(results_df)
results_df['Random Performance'] = [random.random()]*len(results_df)

edited_df = st.data_editor(results_df, 
               column_config={
                    "Expected Accuracy": st.column_config.ProgressColumn(
                        "Expected Accuracy",
                        # help="The sales volume in USD",
                        # format="%f",
                        min_value=0,
                        max_value=1,
                    ),
                    "Random Performance": st.column_config.ProgressColumn(
                        "Random Performance",
                        # help="The sales volume in USD",
                        # format="%f",
                        min_value=0,
                        max_value=1,
                    ),
                },
                hide_index = True)

_ = '''


if 'display_question_cascade' not in st.session_state:
    st.session_state.display_question_cascade = ['Dominated Strategies']
    # print('init', st.session_state.display_question_cascade)
    # st.session_state.display_question_tree = ['Dominated Strategies']

# print(st.session_state.display_question_cascade)

def load_pickle(filename):
    df = pd.read_pickle(f'data/{filename}.pkl')
    # df['Tasks'] = df.apply(lambda row: {f'difficulty_{diff}': row['Tasks'][i] for i, diff in enumerate(row['Difficulties'])}, axis=1)
    # df['questions'] = df.apply(lambda row: {f'question_{diff}': row['questions'][i] for i, diff in enumerate(row['Difficulties'])}, axis=1)
    # df = df.drop('Tasks', axis=1).assign(**df.Tasks.dropna().apply(pd.Series))
    # df = df.drop('questions', axis=1).assign(**df.questions.dropna().apply(pd.Series))
    # df = df.drop(['Tasks', 'questions', 'Difficulties'], axis=1)
    st.session_state.df = df

st.title('Rationality Benchmark')
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
    st.session_state.view = st.radio('Select a View:', ['Curriculum Viewer', 'Grade Viewer'])

def display_sidebar():
    # st.sidebar.empty()
    with st.sidebar:
        if st.session_state.view == 'Curriculum Viewer':
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

            # st.session_state.display_question = 
            # print(name2index_tree)
            # print(st.session_state.display_question_cascade)
            # print(name2index_tree[st.session_state.display_question[-1]])

            # if st.session_state.display_question_cascade != st.session_state.display_question_tree:
                # st.session_state.display_question_tree = sac.tree(items=tree_items, label='**Task Hierarchy:**', index=name2index_tree[st.session_state.display_question_cascade[-1]], format_func='title')
            #     st.session_state.display_question = st.session_state.display_question_tree
            # else:
            # print(st.session_state.display_question_tree)
            # st.session_state.display_question_tree = sac.tree(items=tree_items, label='**Task Hierarchy:**', index=name2index_tree[st.session_state.display_question_tree[-1]], format_func='title')
            # st.session_state.display_question = st.session_state.display_question_tree
            # st.info(st.session_state.display_question_cascade[-1])

            names = list(name2index_tree.keys())
            for name in  st.session_state.display_question_cascade:
                if name in names:
                    tree_index = name2index_tree[name]

            sac.tree(items=tree_items, label='**Task Hierarchy:**', index=tree_index, format_func='title', return_index=True)
        
        elif st.session_state.view == 'Grade Viewer':
            st.session_state.grade_range = st.sidebar.slider('Choose a Grade Range:', 0, 12, (2, 7)) 



def display_questions(row):
    # print(row['task_name'])
    st.header(row['task_name'].iloc[0], divider='gray')
    question_grid = grid([0.3, 0.3])
    for i, diff in enumerate(row['difficulty_levels'].iloc[0]):
        question = row['questions'].iloc[0][i].replace('\n', '<br>')#.replace(' ', '&nbsp;&nbsp;')
        html = f"""<pre><span style="color: #F9EA9A;font-size:150%"><b>Grade {diff} Example Question:</b></span><br>{question}</pre>"""
        question_grid.markdown(html, unsafe_allow_html=True)

name2index_cascade = {}

if st.session_state.view == 'Curriculum Viewer':
    cascader_items = []
    
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
                task_items.append(sac.CasItem(row['task_name']))
                task_index = counter
                name2index_cascade[row['task_name']] = [cat_index, group_index, task_index]
                counter += 1
            group_items.append(sac.CasItem(group_name, children = task_items))
            
        cascader_items.append(sac.CasItem(category, children = group_items))
    
    # if st.session_state.display_question_cascade != st.session_state.display_question_tree:
    #     st.session_state.display_question_cascade = sac.cascader(items=cascader_items, label='**Choose a Task:**', index=name2index_cascade[st.session_state.display_question_tree[-1]], format_func='title', placeholder='Type or Click to Select', search=True, clear=True)
    #     st.session_state.display_question = st.session_state.display_question_cascade
    # else:
    #     st.session_state.display_question_cascade = sac.cascader(items=cascader_items, label='**Choose a Task:**', index=name2index_cascade[st.session_state.display_question_cascade[-1]], format_func='title', placeholder='Type or Click to Select', search=True, clear=True)
    #     st.session_state.display_question = st.session_state.display_question_cascade

    st.session_state.display_question_cascade = sac.cascader(items=cascader_items, label='**Choose a Task:**', index=[25, 26, 27], format_func='title', placeholder='Type or Click to Select', search=True, clear=True)
    display_sidebar()
    
    display_questions(st.session_state.df.query("task_name ==@ st.session_state.display_question_cascade"))

elif st.session_state.view == 'Grade Viewer':
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
    # print(st.session_state.grade_range)
    grade_df = st.session_state.df[st.session_state.df.difficulty_levels.apply(lambda x: x[0]>=st.session_state.grade_range[0] or st.session_state.grade_range[1] in x)]
    # grade_df = grade_df[grade_df.difficulty_levels.apply(lambda x: )]
    print('dataframe')
    print(st.session_state.grade_range)
    print(grade_df)
    rev_categories = {key: value for value in categories for key in categories[value]}
    grade_df['category'] = grade_df['group_name'].apply(lambda x: rev_categories[x])
    # for category in categories:
    for category_name, category_group in grade_df.groupby('category', sort=False):
        st.header(category_name, divider='gray')
        # for group_name in categories[category]:
        for group_name, group_df in category_group.groupby('group_name', sort=False):
            st.subheader(group_name+":")
            question_grid = grid([0.3, 0.3])
            for _, group_row in group_df.iterrows():
                # question_cols = st.columns(2)
                with question_grid.expander(group_row['task_name']):
                    # for index, row in group.iterrows():
                    for i, diff in enumerate(group_row['difficulty_levels']):
                        if diff in list(range(st.session_state.grade_range[0], st.session_state.grade_range[1]+1)):
                            question = group_row['questions'][i].replace('$', '\$').replace('\n', '  \n')#.replace(' ', '&nbsp;&nbsp;')
                            # html = f"""<pre><span style="color: #F9EA9A;font-size:70%"><b>Grade {diff} Example Question:</b></span><br>{question}</pre>"""
                            st.markdown(f':orange[Grade {diff} Example Question:]  \n{question}')
                            # st.markdown(html, unsafe_allow_html=True)
'''
