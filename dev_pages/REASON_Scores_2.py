import streamlit as st
import os
import pandas as pd
import random
import ast
import numpy as np
import seaborn as sns
import altair as alt
import re
from textwrap import wrap
import streamlit_antd_components as sac
# from st_pages import Page, show_pages, add_page_title, Section
# from streamlit_extras.grid import grid
# from streamlit_elements import nivo
# from streamlit_elements import elements, mui, html, dashboard
# from streamlit_extras.tags import tagger_component
# from streamlit_extras.switch_page_button import switch_page
# from annotated_text import annotated_text, annotation

st.set_page_config(
    page_title="REASON Benchmark Scores",
    page_icon=":bar_chart:",
    layout='wide'
)

def flatten_list(lst):
    return [item for sublst in lst for item in sublst]

def format_modelname(model_name):
    if 'models' in model_name:
        name = model_name.split('--')[-1]
        name = ' '.join([sub.capitalize() for sub in name.split('-') if 'hf' not in sub])
        re.sub()


# @st.cache_data
def load_data(filename):
    return pd.read_pickle(f'data/results/{filename}.pkl')

if 'model_df' not in st.session_state:
    st.session_state.model_df = load_data('gpt-3.5_renamed')

if 'baseline_df' not in st.session_state:
    st.session_state.baseline_df = load_data('gpt-4_renamed')

if 'display_results' not in st.session_state:
    st.session_state.display_results = ['Dominated Strategies']

def load_pickle(filename):
    df = pd.read_pickle(f'data/{filename}.pkl')
    st.session_state.df = df

st.title('REASON Benchmark Scores')
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

categories_short = {
    "Foundations": 'Foundations',
    "Preferences": 'Preferences',
    "Decision Making Under Uncertainty": "Decision Making With Uncertainty",
    "Decision Making in the Presence of Other Agents": "Decision Making With Other Agents"
}

name2index_tree = {}
with st.sidebar:
    st.session_state.view = st.radio('Pick a View:', ['Table', 'Baseline', 'Dependency'])

def display_sidebar():
    with st.sidebar:
        if st.session_state.view == 'Table':
            st.session_state.table_columns = {}
            with st.expander('**Select Columns to Show:**', expanded=True):
                sub_col1, sub_col2 = st.columns([0.4, 0.4])
                with sub_col1:
                    for cat_name in categories:
                        if 'Decision Making' not in cat_name:
                            st.session_state.table_columns[cat_name] = st.checkbox(cat_name, True) if cat_name != 'Foundations' else st.checkbox(cat_name, False)
                with sub_col2:
                    st.session_state.table_columns['Total Accuracy'] = st.checkbox('Total Accuracy', True)
                    st.session_state.table_columns['Random'] = st.checkbox('Random', False)
                for cat_name in categories:
                    if 'Decision Making'  in cat_name:
                        st.session_state.table_columns[cat_name] = st.checkbox(cat_name, True)
            display_models = {}
            with st.expander('**Models to Show:**', expanded=True):
                display_models['Chat'] = st.checkbox('Chat', True)
                display_models['Instruct'] = st.checkbox('Instruct', True)
        elif st.session_state.view == 'Baseline':
            st.session_state.model = st.selectbox('Select a Model:', options=['GPT-3.5', 'GPT-4'])
            st.session_state.baseline = st.selectbox('Select a Baseline:', options=['GPT-4'])
        elif st.session_state.view == 'Dependency':
            st.session_state.model = st.selectbox('Select a Model:', options=['GPT-3.5', 'GPT-4'])
            st.session_state.depth = st.slider('Select a Depth:', 0, len(st.session_state.df.query('task_name ==@ st.session_state.display_results[-1]')['dependencies']), 1)



def display_scores(task_name, model_df, baseline_df):
    if len(model_df) == 0 or len(baseline_df) == 0:
        st.error('No Results Found')
    else:
        model_df['answer'] = model_df['answer'].apply(lambda x: ast.literal_eval(x) if type(x) == str else x)
        model_df['difficulty_level'] = model_df['difficulty_level'].apply(lambda x: int(x))
        model_df['is_correct'] = model_df.apply(lambda row: row['answer'] == row['model_answer'], axis = 1)
        model_df['random'] = model_df['options'].apply(lambda x: 1/np.prod([len(options) for options in x]))
        model_df['model'] = model_df['model'].apply(lambda x: '-'.join(x.split('-')[:2]).upper())

        baseline_df['answer'] = baseline_df['answer'].apply(lambda x: ast.literal_eval(x) if type(x) == str else x)
        baseline_df['difficulty_level'] = baseline_df['difficulty_level'].apply(lambda x: int(x))
        baseline_df['is_correct'] = baseline_df.apply(lambda row: row['answer'] == row['model_answer'], axis = 1)
        baseline_df['random'] = baseline_df['options'].apply(lambda x: 1/np.prod([len(options) for options in x]))
        baseline_df['model'] = baseline_df['model'].apply(lambda x: 'Baseline')

        df = pd.concat([baseline_df, model_df], sort=False, ignore_index=True)
        df['domain'] = df['domain'].apply(lambda x: x.split(';'))
        df = df.explode('domain')

        # selection_diff = alt.selection_multi(fields=['difficulty_level', 'allow_explanation'], bind='legend')
        selection_diff = alt.selection_point(fields=['difficulty_level'], bind='legend')
        # selection_explanation = alt.selection_point(fields=['allow_explanation'])
        selection_domain = alt.selection_point(fields=['domain'], bind='legend')
        
        # input_dropdown = alt.binding_select(options=['Allow'], name='Country')
        # selection_explanation = alt.selection_single(fields=['Origin'], bind=input_dropdown)

        diff_color = alt.condition(
            selection_diff,
            alt.Color('difficulty_level:O', 
                    legend=None, 
                    scale=alt.Scale(domain=df.difficulty_level.unique(), range=sns.color_palette("Blues", len(df.difficulty_level.unique())).as_hex())
            ),
            alt.Color('difficulty_level:O', 
                    scale=alt.Scale(domain=df.difficulty_level.unique(), range=sns.color_palette("Blues", len(df.difficulty_level.unique())).as_hex())
            ),
            # alt.value('lightgray')
        )
        
        diff_bar = alt.Chart(df).mark_bar().encode(
            x=alt.X('mean(is_correct):Q', title='Expected Accuracy', scale=alt.Scale(domain=[0, 1.0])),
            y=alt.Y('difficulty_level:O', title='', axis=None),#alt.Axis(labelAngle=0)),
            # color=diff_color,
            color=alt.Color('difficulty_level:O', scale=alt.Scale(domain=df.difficulty_level.unique(), range=sns.color_palette("Blues", len(df.difficulty_level.unique())).as_hex()), title='Grade Level'),
            opacity=alt.condition(selection_diff, alt.value(1), alt.value(0.2))
        ).properties(
            width=alt.Step(40)  # controls width of bar.
        ).add_params(selection_diff)#.transform_filter(selection_diff)

        # diff_legend = alt.Chart(df).mark_rect().encode(
        #     y=alt.Y('difficulty_level:O', axis=alt.Axis(orient='right'), title='Grade Level'),
        #     x=alt.X('allow_explanation:N', axis=alt.Axis(labelAngle=45), title='Explanation'),
        #     color=diff_color
        # ).add_params(
        #     selection_diff
        # )

        tick = alt.Chart().mark_tick(
            color='red',#alt.condition(selection, alt.value(1), alt.value(0.2)),
            thickness=2,
            style='dashed',
            size=40 * 0.5,  # controls width of tick.
        ).encode(
            x='random:Q',
            y='difficulty_level:O',
            opacity=alt.condition(selection_diff, alt.value(1), alt.value(0.2))
        ).transform_filter(selection_diff)

        # sns.color_palette("RdPu", 10)

        diff_chart = alt.layer(diff_bar, tick, data=df).facet(
            row=alt.Row('model:N', sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]],title=None),
            title=alt.Title(' ', subtitle='Expected Accuracy by Grade Level', subtitleColor='white', anchor='middle'),
        )


        # categorical = ["#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b", "#bdcf32", "#87bc45", "#27aeef", "#b33dc6"]
        # categorical = ["#35618f", "#6fef70", "#b7358d", "#1c9820", "#e70de5", "#1b511d", "#e68dd9", "#c0e15c"]
        categorical = ['#FFA500', '#008000', '#FFFF00', '#FF7F50', '#FFD700', '#808000', '#800000', '#FFDAB9']
        categorical = ['#008080', '#FFA500', '#008000', '#FFFF00', '#FF7F50', '#FFD700', '#808000', '#32CD32', '#FF6347', '#FFDAB9']
        # categorical = ["#ffd700", "#ffb14e", "#fa8775", "#ea5f94", "#cd34b5", "#9d02d7", "#0000ff"]
        domain_bar = alt.Chart(df).mark_bar().encode(
            x=alt.X('domain:N', title='', axis=None),
            y=alt.Y('mean(is_correct):Q', title='Expected Accuracy', scale=alt.Scale(domain=[0, 1.0])),
            color=alt.Color('domain:N', scale=alt.Scale(domain=df.domain.unique(), range=categorical), title='Domain'),
            opacity=alt.condition(selection_domain, alt.value(1), alt.value(0.2)),
        ).properties(
            height=150,
            width=alt.Step(38)  # controls width of bar.
        ).add_params(selection_domain)
        
        domain_chart = alt.layer(domain_bar, data=df).facet(
            column=alt.Column('model:N', sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]],header=alt.Header(orient='bottom'), title=None),
            title=alt.Title(' ', subtitle='Expected Accuracy by Domain', subtitleColor='white', anchor='middle'),
        )
        # sns.color_palette('RdPu', 2).as_hex()
        # ['#a8ddb5', '#54278f']
        # ['#c7e9c0', '#54278f']
        colors = ['#DDA0DD', '#800080']
        total_bar = alt.Chart(df).mark_bar().encode(
            x=alt.X('model:N', title='', sort=[f'{model_df.model.unique()[0]}', f'{baseline_df.model.unique()[0]}'], axis=alt.Axis(labelAngle=0)),
            y=alt.Y('mean(is_correct):Q', title='Expected Accuracy', scale=alt.Scale(domain=[0, 1.0])),
            color=alt.Color('model:N', sort=[f'{model_df.model.unique()[0]}', f'{baseline_df.model.unique()[0]}'], scale=alt.Scale(domain=df.model.unique(), range=colors), title='Model'),
            tooltip=alt.Tooltip('mean(is_correct):Q', format=".2f", title='Expected Accuracy')
        ).properties(
            title={
                "text": ["Total Expected Accuracy Compared to Baseline"], 
                "color": "white",
                "subtitleColor": "white"
                },
            height=400,
            width=alt.Step(70)  # controls width of bar.
        ).transform_filter(selection_diff).transform_filter(selection_domain)

        total_rule = alt.Chart(df).mark_rule(
            color='red',
            strokeWidth=2,
        ).encode(
            y=alt.Y('mean(random):Q'),
        ).transform_filter(selection_diff)
        
        total_chart = total_bar + total_rule
        # diff_chart = diff_chart | diff_legend

        sub_chart = alt.vconcat(diff_chart, domain_chart).resolve_scale(color='independent')#.configure_view(stroke=None)

        chart = alt.hconcat(total_chart, sub_chart).resolve_scale(color='independent').configure_view(stroke=None)


        st.altair_chart(chart, theme="streamlit", use_container_width=True)

def display_dependency(model_df, depths):
    if len(model_df) == 0:
        st.error('No Results Found')
    else:
        # get the necessary columns and get accuracy stats
        df = model_df[['answer', 'model_answer', 'task_name', 'Category', 'options']]
        df['is_correct'] = df.apply(lambda row: row['answer'] == row['model_answer'], axis = 1)
        df['random'] = df.apply(lambda row: 1/np.prod([len(options) for options in row['options']]), axis = 1)
        df['depth'] = df['task_name'].apply(lambda x: depths[x])
        # df['task_name'] = df['task_name'].apply(wrap, args=[15])
        # df['task_name'] = df['task_name'].str.replace('\n', '@')
        # df['task_name'] = df['task_name'].apply(lambda x: x.split(' ')[0] + x.split(' ')[1] + '\n' + x.split(' ')[2] if len(x.split(' ')) == 3 else x)

        # for some reason altait throws errors if I do not drop the options column
        df = df.drop('options', axis=1)

        categorical = ['#008080', '#FFA500', '#008000', '#FFFF00', '#FF7F50', '#FFD700', '#808000', '#32CD32', '#FF6347', '#FFDAB9']
        # bar chart of expected accuracy by task, grouped by the category they come from
        bar = alt.Chart(df).mark_bar().encode(
            x = alt.X('task_name:N', axis=alt.Axis(labelAngle=0, labelLimit=150, labelFontSize=8), title='Task'),
            y = alt.Y('mean(is_correct):Q', scale=alt.Scale(domain=[0, 1.0]), title="Expected Accuracy"),
            tooltip=alt.Tooltip('mean(is_correct):Q', format=".2f"),
            color=alt.Color('Category:N', scale=alt.Scale(scheme='accent'), title='Class'),
        ).properties(
            title=alt.Title(text="", anchor='middle'),
            width=alt.Step(100)  # controls width of bar.
        )

        tick = alt.Chart(df).mark_tick(
            color='red',
            thickness=2,
            size=100,  # controls width of tick.
        ).encode(
            x=alt.X('task_name:N'),
            y=alt.Y('mean(random):Q'),
            tooltip=alt.Tooltip('mean(random):Q', format=".2f"),
        )

        

        chart = alt.layer(bar+tick, data=df).facet(
            column=alt.Column('depth:N', sort=alt.EncodingSortField('depth:N', order='descending'), title=""),
            title=alt.Title('Expected Accuracy by Depth', anchor='middle'),
        # ).resolve_axis(
        #     x='independent'
        ).resolve_scale(
            x='independent', 
        )

        st.altair_chart(chart, theme="streamlit", use_container_width=True)

def generate_cascader():
    name2index_cascade = {}

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
    st.session_state.cascader_items = cascader_items

if st.session_state.view == 'Table':
    display_sidebar()
    
    df = pd.concat([load_data('gpt-4_renamed'), load_data('gpt-3.5_renamed')], sort=False, ignore_index=True)

    df['Total Accuracy'] = df.apply(lambda row: row['model_answer'] == row['answer'], axis=1)
    rev_categories = {key: value for value in categories for key in categories[value]}
    df['group_name'] = df['Category']
    df['Category'] = df['Category'].apply(lambda x: rev_categories.get(x, x) if x != 'Reference Independent Decision-Making' else 'Preferences')
    df['Random'] = df['options'].apply(lambda x: 1/np.prod([len(options) for options in x]))
    results_df = df.groupby(['Category', 'model'])['Total Accuracy'].mean().unstack(level=0)
    results_df['Random'] = df.groupby('model')['Random'].mean()
    results_df['Total Accuracy'] = results_df.apply(lambda row: np.mean(row.values[:-1]), axis = 1)
    results_df = results_df[['Total Accuracy', 'Random', 'Foundations', 'Preferences', 'Decision Making Under Uncertainty', 'Decision Making in the Presence of Other Agents']]
    results_df = results_df.sort_values('Total Accuracy', ascending=False)
    display_df = results_df.drop([column for column in st.session_state.table_columns if not st.session_state.table_columns[column]], axis = 1)
    edited_df = st.data_editor(
        display_df.reset_index(), 
        column_config = {key: st.column_config.ProgressColumn(key, min_value=0, max_value=1) for key in results_df.columns},
        hide_index = True,
        use_container_width=True,
        disabled=True
    )
    
elif st.session_state.view == 'Baseline':
    generate_cascader()
    st.session_state.display_results = sac.cascader(items=st.session_state.cascader_items, label='**Choose a Task:**', index=[25, 26, 27], format_func='title', placeholder='Type or Click to Select', search=True, clear=True)
    display_sidebar()
    display_scores(st.session_state.display_results[-1], st.session_state.model_df.query("task_name ==@ st.session_state.display_results[-1]"), st.session_state.baseline_df.query("task_name ==@ st.session_state.display_results[-1]"))
    # display_scores(st.session_state.model_df.query("task_name ==@ st.session_state.display_results"))

elif st.session_state.view == 'Dependency':
    generate_cascader()
    st.session_state.display_results = sac.cascader(items=st.session_state.cascader_items, label='**Choose a Task:**', index=[25, 26, 27], format_func='title', placeholder='Type or Click to Select', search=True, clear=True)
    display_sidebar()
    if st.session_state.depth:
        dependencies = st.session_state.df.query("task_name ==@ st.session_state.display_results[-1]")['dependencies'].values[0][:st.session_state.depth] 
    else: 
        dependencies = []
    depths = {task_name: i+1 for i, tasks in enumerate(dependencies) for task_name in tasks}
    depths[st.session_state.display_results[-1]] = 0
    # print(st.session_state.depth)
    # print(st.session_state.df.query("task_name ==@ st.session_state.display_results[-1]")['dependencies'][:st.session_state.depth].values[0][:1])
    query_string = ' or '.join([f"task_name == '{task}'" for task in flatten_list(dependencies)]) if dependencies else "task_name == 'NONE_TASK'"
    display_dependency(st.session_state.model_df.query("task_name ==@ st.session_state.display_results[-1] or " + query_string), depths)