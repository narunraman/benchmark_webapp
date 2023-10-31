import streamlit as st
import pandas as pd
import os
from st_pages import Page, show_pages, Section, add_page_title
from string import ascii_uppercase
import numpy as np
LETTERS = list(ascii_uppercase)

# TODO: add validated column, which takes three values: np.nan for not-visited, 0 for bad, 1 for good
# TODO: need to be able to keep the state of the counters i.e. need to update the actual dataframe

# add_page_title()

show_pages(
    [
        Page("main.py", "Benchmark Viewer", ":book:"),
        # Page("pages/graphs.py", "Dependency Viewer", ":mag:"),
        # Section(name="Developer Tools", icon=":open_file_folder:"),
        Page("pages/validation.py", "Validation", ":pencil:"),
    ]
)

st.sidebar.title("Toolbar")
tasks = {' '.join([elm.capitalize() for elm in task.replace('.pkl', '').split('_')]): task for task in os.listdir('data/validate')} #['sunk_cost', 'ambigiuty', 'endowment']
selected_task = st.sidebar.selectbox("Select a Task", tasks.keys())

@st.cache_data
def load_df(task_name):
    return pd.read_pickle(f'data/validate/{tasks[task_name]}')

for task in tasks:
    if f'{task}_df' not in st.session_state:
        st.session_state[f'{task}_df'] = load_df(task)

# Difficulty Selection
domains = st.session_state[f'{selected_task}_df']['domain'].unique()
task_types = st.session_state[f'{selected_task}_df']['type'].unique()
selected_domain = st.sidebar.selectbox("Select a Domain", domains)
selected_type = st.sidebar.selectbox("Select a Type", task_types)
if st.session_state[f'{selected_task}_df']['difficulty_level'].min() != st.session_state[f'{selected_task}_df']['difficulty_level'].max():
    slider_difficulty = st.sidebar.slider("Select a Difficulty", min_value=int(st.session_state[f'{selected_task}_df']['difficulty_level'].min()), max_value=int(st.session_state[f'{selected_task}_df']['difficulty_level'].max()), value=int(st.session_state[f'{selected_task}_df']['difficulty_level'].median()))
else:
    st.sidebar.write("Difficulty: ", st.session_state[f'{selected_task}_df']['difficulty_level'].max())



st.title(f"Validate {' '.join(selected_task.split('/')[-1].capitalize().split('_'))} Questions")

# st.session_state['modified_data'] = pd.read_pickle(f'data/validate/{tasks[selected_task]}')
# Initialize counters
if 'good_counter' not in st.session_state:
    st.session_state['good_counter'] = st.session_state[f'{selected_task}_df'][st.session_state[f'{selected_task}_df']['domain'] == selected_domain]['validated'].sum()
if 'total_counter' not in st.session_state:
    st.session_state['total_counter'] = st.session_state[f'{selected_task}_df'][st.session_state[f'{selected_task}_df']['domain'] == selected_domain]['validated'].count()

# Initialize shuffled DataFrame and current_row_index


# Function to initialize and shuffle the DataFrame
def initialize_and_shuffle_dataframe(domain, task_type):
    if 'df_shuffled_indexes' not in st.session_state:
        st.session_state['df_shuffled_indexes'] = st.session_state[f'{selected_task}_df'].index[(st.session_state[f'{selected_task}_df']['domain'] == domain) & (st.session_state[f'{selected_task}_df']['validated'].isnull()) & (st.session_state[f'{selected_task}_df']['type'] == task_type)].to_list()
        np.random.shuffle(st.session_state['df_shuffled_indexes'])
        print(f"len obs: {len(st.session_state['df_shuffled_indexes'])}")


# Function to get the next row from the shuffled DataFrame
def get_next_row():
    try:
        print(f"curr index: {st.session_state['df_shuffled_indexes'][-1]}")
        next_row = st.session_state[f'{selected_task}_df'].iloc[st.session_state['df_shuffled_indexes'][-1]]
        curr_index = st.session_state['df_shuffled_indexes'].pop()
    except:
        print({'status': 'done'})
        return
    return next_row, curr_index

initialize_and_shuffle_dataframe(selected_domain, selected_type)

def clean_text(string):
    string = string.replace('$', '\$')
    string = string.replace('{}', '[BLANK]')
    return string

# NOTE: this assumes the number of options per question is the same. 
def get_option_number(i, j, num_options):
    return (i * num_options) + j

def save_counters():
    return

# Function to update counters and display new text
def update_counters_and_display():
    current_row,curr_index = get_next_row()
    if current_row.get('status') != 'done':
        st.write('Requirements')
        st.warning('- '+'  \n- '.join(current_row['description']))# '- Hello  \n - Goodbye')
        st.write("Current Text:")
        try:
            questions = [clean_text(question) for question in current_row['questions']]
            options_lst = [[clean_text(option) for option in options] for options in current_row['options']]
            st.info('  \n  \n'.join([question + '  \n' + '  \n'.join([f'{LETTERS[get_option_number(i, j, len(options))]}. {option}' for j, option in enumerate(options)]) for i, (question, options) in enumerate(zip(questions, options_lst))]))
        except AttributeError as ex:
            questions = [clean_text(question) for question in current_row['questions']]
            options_lst = [[clean_text(option) for option in options] for options in current_row['options']]
            print(ex)
            print (current_row['questions'])
            st.info('  \n  \n'.join([question + '  \n' + '  \n'.join([f'{LETTERS[get_option_number(i, j, len(options))]}. {option}' for j, option in enumerate(options)]) for i, (question, options) in enumerate(zip(questions, options_lst))]))
        st.text("")
        st.text("")
        button_cols = st.columns(5)
        if button_cols[0].button("Valid Question"):
             st.session_state['good_counter'] += 1
             st.session_state['total_counter'] += 1
             st.session_state[f'{selected_task}_df'].at[curr_index,'validated'] = 1
        if button_cols[1].button("Bad Question"):
            st.session_state['total_counter'] += 1
            st.session_state[f'{selected_task}_df'].at[curr_index,'validated'] = 0
        print( st.session_state[f'{selected_task}_df'].loc[curr_index]['validated'])
        if button_cols[-1].button("Save and Exit", type='primary'):
            save_counters()
            st.session_state[f'{selected_task}_df'].to_pickle(f'data/validate/{selected_task}.pkl')
            print('done')
            st.stop()
    else:
        st.info("Completed All Questions")
        st.text("")
        st.text("")
        button_cols = st.columns(5)
        if button_cols[-1].button("Save and Exit", type='primary'):
            save_counters()
            st.stop()



# Initial random row
current_row = None
update_counters_and_display()
st.sidebar.write("Good Questions:", st.session_state['good_counter'])
st.sidebar.write("Total Validated:", st.session_state['total_counter'])
    
try:
    percent_good = round(int(st.session_state.good_counter)/(int(st.session_state.total_counter))*100, 2)
except:
    percent_good = 0

st.sidebar.write(f"Percent Good: {percent_good}%")