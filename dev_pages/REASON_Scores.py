import streamlit as st
import os
import pandas as pd
import random
import ast
import numpy as np
import seaborn as sns
import altair as alt
import re
from streamlit_extras.chart_container import chart_container 
import streamlit_antd_components as sac
pd.options.mode.chained_assignment = None
# from st_pages import Page, show_pages, add_page_title, Section
# from streamlit_extras.grid import grid
# from streamlit_elements import nivo
# from streamlit_elements import elements, mui, html, dashboard
# from streamlit_extras.tags import tagger_component
# from streamlit_extras.switch_page_button import switch_page
# from annotated_text import annotated_text, annotation

st.set_page_config(
    page_title="Model Performances",
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

st.title('Model Performances')
load_pickle('all_tasks')

categories = {
    "Foundations": [
        'Arithmetic',
        'Probability', 
        'Optimization', 
        'Logic', 
        'Theory of Mind'
    ], 
    "Decisions in Deterministic Settings": [
        'Utility Theory', 
        'Reference Independence'
    ], 
    "Decisions Under Uncertainty": [
        'Expected Utility Theory', 
        'Risk Preference'
    ], 
    "Decisions in Multiagent Settings": [
        'Single-Round Game Theory',
        'Multi-Round Game Theory',
    ],
    "Decisions For Groups of Agents": [
        'Single-Round Game Theory',
        'Multi-Round Game Theory',
    ],
}

categories_short = {
    "Foundations": 'Foundations',
    "Preferences": 'Preferences',
    "Decisions Under Uncertainty": "Decision Making With Uncertainty",
    "Decisions in Multiagent Settings": "Decision Making With Other Agents",
    "Decisions For Groups of Agents": "Decision Making With Other Agents"
}

name2index_tree = {}
with st.sidebar:
    st.session_state.view = st.radio('Pick a View:', ['Table', 'Comparison', 'Dependency'])
    # if st.session_state.view == 'Dependency':
        

# def display_sidebar():
        # elif st.session_state.view == 'Comparison':
            



def display_scores(task_name, model_df, baseline_df):
    if len(model_df) == 0 or len(baseline_df) == 0:
        st.error('No Results Found')
    else:

        # Data cleaning
        model_df['answer'] = model_df['answer'].apply(lambda x: ast.literal_eval(x) if type(x) == str else x)
        model_df['difficulty_level'] = model_df['difficulty_level'].apply(lambda x: int(x))
        
        if task_name == 'Ambiguity Aversion':
            model_df['is_correct'] = model_df.apply(lambda row: row['model_answer'] == ['A', 'D'] or row['model_answer'] == ['B', 'C'], axis = 1)    
        elif task_name == 'Irrelevant Alternatives':
            model_df['is_correct'] = model_df.apply(lambda row: row['model_answer'][0] == row['model_answer'][1], axis = 1)    
        elif task_name == 'Endowment Effect':
            model_df['is_correct'] = model_df.apply(lambda row: row['model_answer'] != ['B', 'D'] and row['model_answer'] != ['PARSER_FOUND_NOTHING', 'PARSER_FOUND_NOTHING'], axis = 1)    
        else:
            model_df['is_correct'] = model_df.apply(lambda row: row['answer'] == row['model_answer'], axis = 1)

        model_df['random'] = model_df['options'].apply(lambda x: 1/np.prod([len(options) for options in x]))
        model_df['model'] = model_df['model'].apply(lambda x: '-'.join(x.split('-')[:2]).upper())

        baseline_df['answer'] = baseline_df['answer'].apply(lambda x: ast.literal_eval(x) if type(x) == str else x)
        baseline_df['difficulty_level'] = baseline_df['difficulty_level'].apply(lambda x: int(x))
        
        if task_name == 'Ambiguity Aversion':
            baseline_df['is_correct'] = baseline_df.apply(lambda row: row['model_answer'] == ['A', 'D'] or row['model_answer'] == ['B', 'C'], axis = 1)    
        elif task_name == 'Irrelevant Alternatives':
            baseline_df['is_correct'] = baseline_df.apply(lambda row: row['model_answer'][0] == row['model_answer'][1], axis = 1)    
        elif task_name == 'Endowment Effect':
            baseline_df['is_correct'] = baseline_df.apply(lambda row: row['model_answer'] != ['B', 'D'] and row['model_answer'] != ['PARSER_FOUND_NOTHING', 'PARSER_FOUND_NOTHING'], axis = 1)    
        else:
            baseline_df['is_correct'] = baseline_df.apply(lambda row: row['answer'] == row['model_answer'], axis = 1)

        baseline_df['random'] = baseline_df['options'].apply(lambda x: 1/np.prod([len(options) for options in x]))
        # baseline_df['model'] = baseline_df['model'].apply(lambda x: 'Comparison')

        df = pd.concat([baseline_df, model_df], sort=False, ignore_index=True)
        df['domain'] = df['domain'].apply(lambda x: x.split(';'))
        df = df.explode('domain')

        # selection_diff = alt.selection_multi(fields=['difficulty_level', 'allow_explanation'], bind='legend')
        selection_grade_model = alt.selection_point(fields=['difficulty_level'])#, bind='legend')
        selection_grade_baseline = alt.selection_point(fields=['difficulty_level'])#, bind='legend')
        selection_diff_model = alt.selection_point(fields=['allow_explanation', 'num_shots'])
        selection_diff_baseline = alt.selection_point(fields=['allow_explanation', 'num_shots'])
        selection_domain_model = alt.selection_point(fields=['domain'])#, bind='legend')
        selection_domain_baseline = alt.selection_point(fields=['domain'])#, bind='legend')
        
        
        grade_bar_model = alt.Chart(df[df.model==model_df.model.unique()[0]]).mark_bar(cornerRadiusBottomRight=3, cornerRadiusTopRight=3).encode(
            x=alt.X('mean(is_correct):Q', title='', scale=alt.Scale(domain=[0, 1.0])),
            y=alt.Y('difficulty_level:O', axis=alt.Axis(title=model_df.model.unique()[0], labels=False)),#alt.Axis(labelAngle=0)),
            # color=diff_color,
            color=alt.Color('difficulty_level:O', scale=alt.Scale(domain=df.difficulty_level.unique(), range=sns.color_palette("Greens", len(df.difficulty_level.unique())).as_hex()), title='Grade Level'),
            opacity=alt.condition(selection_grade_model, alt.value(1), alt.value(0.2)),
            tooltip=[alt.Tooltip('difficulty_level:O', title='Grade Level'), alt.Tooltip('mean(is_correct):Q', format=".2f", title='Accuracy')]
        ).properties(
            width=alt.Step(40)  # controls width of bar.
        ).add_params(selection_grade_model)#.transform_filter(selection_diff)

        grade_bar_model += alt.Chart(df[df.model==model_df.model.unique()[0]]).mark_tick(
            color='red',#alt.condition(selection, alt.value(1), alt.value(0.2)),
            thickness=2,
            # style='dashed',
            size=40 * 0.5,  # controls width of tick.
        ).encode(
            x='random:Q',
            y='difficulty_level:O',
            opacity=alt.condition(selection_grade_model, alt.value(1), alt.value(0.2))
        ).transform_filter(selection_grade_model)

        grade_bar_baseline = alt.Chart(df[df.model==baseline_df.model.unique()[0]]).mark_bar(cornerRadiusBottomRight=3, cornerRadiusTopRight=3).encode(
            x=alt.X('mean(is_correct):Q', title='Accuracy', scale=alt.Scale(domain=[0, 1.0])),
            y=alt.Y('difficulty_level:O', title='', axis=alt.Axis(title=baseline_df.model.unique()[0], labels=False)),#alt.Axis(labelAngle=0)),
            # color=diff_color,
            color=alt.Color('difficulty_level:O', scale=alt.Scale(domain=df.difficulty_level.unique(), range=sns.color_palette("Greens", len(df.difficulty_level.unique())).as_hex()), title='Grade Level'),
            opacity=alt.condition(selection_grade_baseline, alt.value(1), alt.value(0.2)),
            tooltip=[alt.Tooltip('difficulty_level:O', title='Grade Level'), alt.Tooltip('mean(is_correct):Q', format=".2f", title='Accuracy')]
        ).properties(
            width=alt.Step(40)  # controls width of bar.
        ).add_params(selection_grade_baseline)

        grade_bar_baseline += alt.Chart(df[df.model==baseline_df.model.unique()[0]]).mark_tick(
            color='red',#alt.condition(selection, alt.value(1), alt.value(0.2)),
            thickness=2,
            # style='dashed',
            size=40 * 0.5,  # controls width of tick.
        ).encode(
            x='random:Q',
            y='difficulty_level:O',
            opacity=alt.condition(selection_grade_baseline, alt.value(1), alt.value(0.2))
        ).transform_filter(selection_grade_baseline)

        grade_chart = grade_bar_model & grade_bar_baseline




        # grade_chart = alt.layer(grade_bar, grade_tick, data=df).facet(
        #     row=alt.Row('model:N', sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]],title=None),
        #     title=alt.Title(' ', subtitle='Expected Accuracy by Grade Level', subtitleColor='lightgray', anchor='middle'),
        #     spacing=30
        # )


        # categorical = ["#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b", "#bdcf32", "#87bc45", "#27aeef", "#b33dc6"]
        # categorical = ["#35618f", "#6fef70", "#b7358d", "#1c9820", "#e70de5", "#1b511d", "#e68dd9", "#c0e15c"]
        # categorical = ['#FFA500', '#008000', '#FFFF00', '#FF7F50', '#FFD700', '#808000', '#800000', '#FFDAB9']
        # categorical = ['#008080', '#FFA500', '#008000', '#FFFF00', '#FF7F50', '#FFD700', '#808000', '#32CD32', '#FF6347', '#FFDAB9']
        # categorical = ['#FF6347', '#32CD32',  '#800000', '#FFA500', '#ADFF2F', '#FF8C00']
        categorical = ['#f7b799', '#dc6e57', '#529dc8', '#e1edf3', '#246aae', '#b61f2e', '#fae7dc', '#a7d0e4']#random.sample(sns.color_palette('RdBu', 8).as_hex(), k=8)
        # print(categorical)
        # categorical = ["#ffd700", "#ffb14e", "#fa8775", "#ea5f94", "#cd34b5", "#9d02d7", "#0000ff"]

        domain_bar_model = alt.Chart(df[df.model == model_df.model.unique()[0]]).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
            x=alt.X('mean(is_correct):Q', title='', scale=alt.Scale(domain=[0, 1.0])),
            y=alt.Y('domain:N', title='', axis=alt.Axis(title=model_df.model.unique()[0], labels = False), sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]]),
            color=alt.Color('domain:N', scale=alt.Scale(domain=df.domain.unique(), range=categorical), title='Domain'),
            opacity=alt.condition(selection_domain_model, alt.value(1), alt.value(0.2)),
            tooltip=[alt.Tooltip('domain:N', title='Domain'), alt.Tooltip('mean(is_correct):Q', format=".2f", title='Accuracy')]
        ).properties(
            # height=150,
            # width=alt.Step(20)  # controls width of bar.
        ).add_params(selection_domain_model)


        domain_bar_baseline = alt.Chart(df[df.model == baseline_df.model.unique()[0]]).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
            x=alt.X('mean(is_correct):Q', title='Accuracy', scale=alt.Scale(domain=[0, 1.0])),
            y=alt.Y('domain:N', title='', axis=alt.Axis(title=baseline_df.model.unique()[0], labels=False), sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]]),
            color=alt.Color('domain:N', scale=alt.Scale(domain=df.domain.unique(), range=categorical), title='Domain'),
            opacity=alt.condition(selection_domain_baseline, alt.value(1), alt.value(0.2)),
            tooltip=[alt.Tooltip('domain:N', title='Domain'), alt.Tooltip('mean(is_correct):Q', format=".2f", title='Accuracy')]
        ).properties(
            # height=150,
            # width=alt.Step(20)  # controls width of bar.
        ).add_params(selection_domain_baseline)

        domain_chart = alt.vconcat(domain_bar_model, domain_bar_baseline)#, spacing=50)

        # domain_chart = alt.layer(domain_bar, data=df).facet(
        #     column=alt.Column(
        #         'model:N', 
        #         sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]],
        #         # sort=alt.EncodingSortField('model:N', order='ascending'),
        #         header=alt.Header(orient='bottom'), 
        #         title=None
        #     ),
        #     title=alt.Title(' ', subtitle='Expected Accuracy by Domain', subtitleColor='lightgray', anchor='middle'),
        # )

        diff_chart_model = alt.layer(
            data=df
        ).transform_filter(
            filter={"field": 'num_shots',
                    "oneOf": [0, 1, 5]
            }
        ).transform_filter(
            filter={'field': 'allow_explanation',
                    "oneOf": [True, False]
            }
        )

        diff_chart_model += alt.Chart().mark_line(color='#db646f').encode(
            x = alt.X('mean(is_correct):Q'),
            y = alt.Y('num_shots:O', sort=alt.EncodingSortField('num_shots:O', order='descending')),
            detail = 'num_shots:O',
        ).properties(
            title=alt.Title(text=' ', subtitle=model_df.model.unique()[0], subtitleColor='white', anchor='middle'),
        )

        diff_chart_model += alt.Chart(df[df.model==model_df.model.unique()[0]]).mark_point(
            size=120,
            opacity=1,
            filled=True
        ).encode(
            x = alt.X('mean(is_correct):Q', scale=alt.Scale(domain=[0, 1.0]), title=''),
            y = alt.Y('num_shots:O', title="# of Prompts"),
            color=alt.Color('allow_explanation:O',
                scale=alt.Scale(
                    domain=[True, False],
                    range=['#911a24', '#e6959c']#sns.color_palette("Greens", 2).as_hex()
                ),
                title='Explanation',
            ),
            opacity = alt.condition(selection_diff_model, alt.value(1), alt.value(0.2)),
            tooltip=[alt.Tooltip('num_shots:O', title='Number of Prompts'), alt.Tooltip('allow_explanation:O', title='Explanation'), alt.Tooltip('mean(is_correct):Q', format=".2f", title='Accuracy')]
        ).properties(
            height=70,
            # width=300  # controls width of bar.
        ).add_params(selection_diff_model)



        diff_chart_baseline = alt.layer(
            data=df
        ).transform_filter(
            filter={"field": 'num_shots',
                    "oneOf": [0, 1, 5]
            }
        ).transform_filter(
            filter={'field': 'allow_explanation',
                    "oneOf": [True, False]
            }
        )

        diff_chart_baseline += alt.Chart().mark_line(color='#db646f').encode(
            x = alt.X('mean(is_correct):Q'),
            y = alt.Y('num_shots:O', sort=alt.EncodingSortField('num_shots:O', order='descending')),
            detail = 'num_shots:O',
        ).properties(
            title=alt.Title(text=' ', subtitle=baseline_df.model.unique()[0], subtitleColor='white', anchor='middle'),
        )

        diff_chart_baseline += alt.Chart(df[df.model==baseline_df.model.unique()[0]]).mark_point(
            size=120,
            opacity=1,
            filled=True
        ).encode(
            x = alt.X('mean(is_correct):Q', scale=alt.Scale(domain=[0, 1.0]), title='Accuracy'),
            y = alt.Y('num_shots:O', title="# of Prompts"),
            color=alt.Color('allow_explanation:O',
                scale=alt.Scale(
                    domain=[True, False],
                    range=['#911a24', '#e6959c']#sns.color_palette("Greens", 2).as_hex()
                ),
                title='Explanation',
            ),
            opacity = alt.condition(selection_diff_baseline, alt.value(1), alt.value(0.2)),
            tooltip=[alt.Tooltip('num_shots:O', title='Number of Prompts'), alt.Tooltip('allow_explanation:O', title='Explanation'), alt.Tooltip('mean(is_correct):Q', format=".2f", title='Accuracy')]
        ).properties(
            height=70,
            # width=300  # controls width of bar.
        ).add_params(selection_diff_baseline)
        diff_chart = alt.vconcat(diff_chart_model, diff_chart_baseline)#, spacing=50)

        # st.altair_chart(diff_chart_model | diff_chart_baseline, theme="streamlit", use_container_width=True)
        
        # diff_chart = alt.layer(diff_chart_model, diff_chart_baseline).facet(
        #     column=alt.Column('model:N', title=None, sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]],),
        #     spacing=100,
        # )

        # chart = chart
        # st.altair_chart(diff_chart)

        # diff_chart = alt.layer(diff_bar, diff_legend, data=df).facet(
        #     column=alt.Column(
        #         'model:N', 
        #         sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]],
        #         # sort=alt.EncodingSortField('model:N', order='ascending'),
        #         header=alt.Header(orient='bottom'), 
        #         title=None
        #     ),
        #     title=alt.Title(' ', subtitle='Expected Accuracy by Difficulty', subtitleColor='white', anchor='middle'),
        # )


        # sns.color_palette('RdPu', 2).as_hex()
        # ['#a8ddb5', '#54278f']
        # ['#c7e9c0', '#54278f']

        colors = ['#DDA0DD', '#800080']
        colors = ['#d4b9da', '#7a0177']
        # colors = ['#f1eef6', '#034e7b']
        # colors = [ '#BA55D3' , '#800080'  ]
        total_bar = alt.Chart(df[df.model==model_df.model.unique()[0]]).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x = alt.X(
                'model:N', 
                title='', 
                sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]], 
                axis=alt.Axis(labelAngle=0)
            ),
            y = alt.Y(
                'mean(is_correct):Q', 
                title='Accuracy', 
                scale=alt.Scale(domain=[0, 1.0])
            ),
            color = alt.Color(
                    'model:N', 
                    sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]], 
                    scale=alt.Scale(domain=df.model.unique(), range=colors), 
                    title='Model'
                ),
            # order=alt.Order('model:N', sort='descending'),
            tooltip=[alt.Tooltip('mean(is_correct):Q', format=".2f", title='Accuracy')]
        ).properties(
            # title={
            #     "text": ["Total Expected Accuracy Compared to Baseline"], 
            #     "color": "lightgray",
            #     "subtitleColor": "white"
            #     },
            height=500,
            width=alt.Step(70)  # controls width of bar.
        )#.transform_filter(selection_grade_model).transform_filter(selection_domain_model).transform_filter(selection_diff_model)

        total_bar += alt.Chart(df[df.model==baseline_df.model.unique()[0]]).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x = alt.X(
                'model:N', 
                title='', 
                sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]], 
                axis=alt.Axis(labelAngle=0)
            ),
            y = alt.Y(
                'mean(is_correct):Q', 
                title='Accuracy', 
                scale=alt.Scale(domain=[0, 1.0])
            ),
            color = alt.Color(
                    'model:N', 
                    sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]], 
                    scale=alt.Scale(domain=df.model.unique(), range=colors), 
                    title='Model'
                ),
            # order=alt.Order('model:N', sort='descending'),
            tooltip=[alt.Tooltip('mean(is_correct):Q', format=".2f", title='Accuracy')]
        ).properties(
            title=alt.Title(f"Total Accuracy Compared to {baseline_df.model.unique()[0]}:", fontSize=20),
            #     "text": [f"Total Accuracy Compared to {baseline_df.model.unique()[0]}"], 
            #     "color": "lightgray",
            #     "subtitleColor": "white"
            #     },
            height=500,
            width=alt.Step(70)  # controls width of bar.
        )#.transform_filter(selection_grade_baseline).transform_filter(selection_domain_baseline).transform_filter(selection_diff_baseline)

        


        total_rule_baseline = alt.Chart(df[df.model == baseline_df.model.unique()[0]]).mark_tick(
            color='red',
            size=200 * 0.5,
            thickness=2,
        ).encode(
            x=alt.X('model:N', sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]]),
            y=alt.Y('mean(random):Q'),
        )#.transform_filter(selection_grade_baseline)

        total_rule_model = alt.Chart(df[df.model == model_df.model.unique()[0]]).mark_tick(
            color='red',
            size=200 * 0.5,
            thickness=2,
        ).encode(
            x=alt.X('model:N', sort=[model_df.model.unique()[0], baseline_df.model.unique()[0]]),
            y=alt.Y('mean(random):Q'),
        )#.transform_filter(selection_grade_model)

        total_rule = total_rule_baseline + total_rule_model
        
        total_chart = total_bar + total_rule

        # vertically concatenate the difficulty and domain charts
        sub_chart = alt.hconcat(grade_chart, domain_chart, diff_chart, spacing=50).resolve_scale(color='independent')#.configure_view(stroke=None)
        print()
        print()
        print(selection_domain_model)

        # horizontally concatenate the total bar chart with the domain and difficulty charts
        chart = alt.vconcat(total_chart, sub_chart).resolve_scale(color='independent').configure_view(stroke=None)
        # print(total_chart)
        # chart = alt.vconcat(chart).resolve_scale(color='independent').configure_view(stroke=None)
        # st.altair_chart(chart, theme="streamlit", use_container_width=True)
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.write("")
            models = st.columns([0.5, 0.5])
            with models[0]:
                st.session_state.model = st.selectbox('Select a Model:', options=['GPT-3.5', 'GPT-4'])
            with models[1]:
                st.session_state.baseline = st.selectbox('Select a Comparison:', options=['GPT-4'])
            # st.write("")
            # st.write("")
            st.markdown('#### Breakdowns:')
            grade_expander = st.expander('Grade Level:')
            grade_expander.altair_chart(grade_chart, theme="streamlit", use_container_width=True)
            with st.expander('Domain:'):
                st.altair_chart(domain_chart, theme="streamlit", use_container_width=True)
            with st.expander('Question additions:'):
                st.altair_chart(diff_chart, theme="streamlit", use_container_width=True)
        with col2:
            # st.subheader(f'Total Accuracy Compared to {baseline_df.model.unique()[0]}:')
            st.altair_chart(total_chart, theme="streamlit", use_container_width=True)

def display_dependency(model_df, depths):
    if len(model_df) == 0:
        st.error('No Results Found')
    else:
        # get the necessary columns and get accuracy stats
        df = model_df[['answer', 'model_answer', 'task_name', 'Category', 'options']]
        # print(df.task_name.unique())
        # set is correct values conditioned on the task
        df['is_correct'] = df.apply(lambda row: row['model_answer'] == ['A', 'C'] or row['model_answer'] == ['B', 'D'] if row['task_name'] == 'Ambiguity Aversion' else row['model_answer'][0] == row['model_answer'][1] if row['task_name'] == 'Irrelevant Alternatives' else row['answer'] == row['model_answer'], axis = 1)
        df['random'] = df.apply(lambda row: 1/np.prod([len(options) for options in row['options']]), axis = 1)
        df['depth'] = df['task_name'].apply(lambda x: depths[x])

        # for some reason altair throws errors if I do not drop the options column
        df = df.drop('options', axis=1)

        selection = alt.selection_point(fields=['Category'], bind='legend')
        # categorical = ['#008080', '#FFA500', '#008000', '#FFFF00', '#FF7F50', '#FFD700', '#808000', '#32CD32', '#FF6347', '#FFDAB9']
        categorical = ['#3182bd', '#e6550d', '#756bb1',  '#17becf', '#31a354', '#d6616b', '#fd8d3c', '#98df8a', '#f7b6d2', '#5254a3', '#ce6dbd', '#9467bd',  '#ad494a']
        # bar chart of expected accuracy by task, grouped by the category they come from
        # print(sns.color_palette().as_hex())
        # print(alt.Scale(scheme='category20'))
        categorical = {cat_name: categorical[i] for i, cat_name in enumerate(flatten_list(categories.values()))}
        # print(flatten_list(categories.values()))

        bar = alt.Chart().mark_bar(cornerRadiusBottomRight=5, cornerRadiusTopRight=5).encode(
            x = alt.X('mean(is_correct):Q', scale=alt.Scale(domain=[0, 1.0]), title="Accuracy"),
            y = alt.Y('task_name:N', axis=alt.Axis(labelAngle=0, labelLimit=200), title=' '),
            tooltip=[alt.Tooltip('mean(is_correct):Q', format=".2f", title="Accuracy")],
            color=alt.Color('Category:N', 
                            scale = alt.Scale(domain = df.Category.unique(), range = [categorical[cat_name] for cat_name in df.Category.unique()]),
                            # scale=alt.Scale('accent'), 
                            title='Class'),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
        ).properties(
            title=alt.Title(text="", anchor='middle'),
            width=350  # controls width of bar.
        ).add_params(selection)

        tick = alt.Chart().mark_tick(
            color='red',
            thickness=2,
            size=20,  # controls width of tick.
        ).encode(
            x=alt.X('mean(random):Q'),
            y=alt.Y('task_name:N'),
            tooltip=alt.Tooltip('mean(random):Q', format=".2f"),
            # opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
        ).transform_filter(selection)

        

        chart = alt.layer(bar, tick, data=df).facet(
            row=alt.Row('depth:N',
                            #   sort=alt.EncodingSortField('depth:N', order='descending'), 
                        title="Depth"),
            title=alt.Title('Accuracy by Depth', anchor='middle'),
            # spacing=300,
        ).resolve_scale(
            y='independent', 
        )

        return chart

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
    # display_sidebar()
    st.session_state.table_columns = {}
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
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
                if 'Decision Making' in cat_name:
                    st.session_state.table_columns[cat_name] = st.checkbox(cat_name, True)
    with col2:
        display_models = {}
        with st.expander('**Models to Show:**', expanded=True):
            display_models['Chat'] = st.checkbox('Chat', True)
            display_models['Instruct'] = st.checkbox('Instruct', True)
    
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
    results_df = results_df.rename(columns={'Decision Making Under Uncertainty': 'Decision Making Under Uncertainty', 'Decision Making in the Presence of Other Agents': 'Decision Making in the Presence of Other Agents'})
    results_df = results_df.sort_values('Total Accuracy', ascending=False)
    display_df = results_df.drop([column for column in st.session_state.table_columns if not st.session_state.table_columns[column]], axis = 1)
    edited_df = st.data_editor(
        display_df.reset_index(), 
        column_config = {key: st.column_config.ProgressColumn(key, min_value=0, max_value=1, width=None) for key in results_df.columns},
        hide_index = True,
        use_container_width=True,
        disabled=True
    )
    
elif st.session_state.view == 'Comparison':
    generate_cascader()
    st.session_state.display_results = sac.cascader(items=st.session_state.cascader_items, label='**Choose a Task:**', format_func='title', placeholder='Type or Click to Select', search=True, clear=True)
    # display_sidebar()
    if st.session_state.display_results:
        display_scores(st.session_state.display_results[-1], st.session_state.model_df.query("task_name ==@ st.session_state.display_results[-1]"), st.session_state.baseline_df.query("task_name ==@ st.session_state.display_results[-1]"))

elif st.session_state.view == 'Dependency':
    generate_cascader()
    st.session_state.display_results = sac.cascader(items=st.session_state.cascader_items, label='**Choose a Task:**', format_func='title', placeholder='Type or Click to Select', search=True, clear=True)
    if st.session_state.display_results:
        # display_sidebar()
        col1, col2 = st.columns([0.8, 0.2])
        with col2:
            st.session_state.model = st.selectbox('**Select a Model:**', options=['GPT-3.5', 'GPT-4'])
            with st.expander('Filters:', expanded = True):
                st.session_state.depth = st.slider('Select a Depth:', 0, len(st.session_state.df.query('task_name ==@ st.session_state.display_results[-1]')['dependencies'].values[0]), 1)
        with col1:
            if st.session_state.depth >= 0:
                dependencies = st.session_state.df.query("task_name ==@ st.session_state.display_results[-1]")['dependencies'].values[0][:st.session_state.depth] 
            else: 
                dependencies = st.session_state.df.query("task_name ==@ st.session_state.display_results[-1]")['dependencies'].values[0]
            depths = {task_name: i+1 for i, tasks in enumerate(dependencies) for task_name in tasks}
            depths[st.session_state.display_results[-1]] = 0
            query_string = ' or '.join([f"task_name == '{task}'" for task in flatten_list(dependencies)]) if dependencies else "task_name == 'NONE_TASK'"
            chart = display_dependency(st.session_state.model_df.query("task_name ==@ st.session_state.display_results[-1] or " + query_string), depths)
            st.altair_chart(chart, theme="streamlit", use_container_width=True)