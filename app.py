import streamlit as st

def set_page_style():
    st.set_page_config(page_title="SQL Assistant", page_icon="🤖", layout="wide")
    st.markdown("""
        <style>
            .title {
                font-size: 2.5em;
                font-weight: bold;
                color: #4A90E2;
                text-align: center;
                margin-bottom: 20px;
            }
            .subtitle {
                font-size: 1.5em;
                color: #333333;
                text-align: center;
            }
            .stButton>button {
                width: 100%;
                margin-top: 10px;
            }
            .reportview-container .markdown-text-container {
                font-family: 'Arial', sans-serif;
            }
        </style>
    """, unsafe_allow_html=True)

def main():
    set_page_style()
    st.markdown("<p class='title'>HCS SQL Assistant 🤖</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>SQL 생성, 수정, 최적화를 도와줍니다.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
