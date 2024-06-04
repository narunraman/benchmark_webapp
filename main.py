import streamlit as st
import webbrowser
from streamlit_extras.stylable_container import stylable_container

def main():
    st.set_page_config(layout = 'wide', page_title='STEER') 
    st.title("STEER: Systematic and Tuneable Evaluation of Economic Rationality")
    st.logo('images/steer_logo.png', icon_image='images/steer_small.png')
    st.image('images/taxonomy.jpg')
    st.header('A reproducible framework for evaluating economic rationality in foundation models.')
    # with stylable_container(key='link_buttons', css_styles = '''
    #     .stLinkButton:first-child {
    #         margin-right: 20px;
    #     }
    #     #link_buttons {
    #         display: flex;
    #         justify-content: space-between;
    #         flex-direction: row;
    #     }
    # '''):
    st.markdown("""
    <style>
        .stButton>button {
            width: 10vw;
            height: 50px;
            font-size: 20vw;
            margin-right: 2vw;
        }
    </style>
    """, unsafe_allow_html=True)
    button_cols = st.columns([0.15, 0.15, 0.7])
    if button_cols[0].button('Paper'):
        webbrowser.open_new_tab('https://arxiv.org/abs/2402.09552')
    if button_cols[1].button('Github'):
        webbrowser.open_new_tab('https://github.com/narunraman/STEER')
    # st.button('Paper')#, 'https://arxiv.org/abs/2402.09552')
    # st.button('Github')#, 'https://github.com/narunraman/STEER')
    st.divider()
    # how to cite:
    st.header('Cite us if you use our work!')
    with st.columns(2)[0]:
        st.code('''
        @misc{raman2024steer,
            title={STEER: Assessing the Economic Rationality of Large Language Models}, 
            author={Narun Raman and Taylor Lundy and 
                Samuel Amouyal and Yoav Levine and 
                Kevin Leyton-Brown and Moshe Tennenholtz},
            year={2024},
            eprint={2402.09552},
            archivePrefix={arXiv},
            primaryClass={cs.CL}
        }
        ''', language='python')
if __name__ == '__main__':
    main()