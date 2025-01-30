import streamlit as st
from agents.generate_agent import SQLgeneration
# from agents.generate_prompt import SQLgeneration

def main():
    st.title("SQL 자동 변환")
    st.write("자연어 질의를 입력하면, LLM이 SQL로 변환해줍니다.")

    # Initialize the SQLgeneration instance once and store it in session_state
    if "generator" not in st.session_state:
        st.session_state.generator = SQLgeneration()

    generator = st.session_state.generator

    # 대화 메세지 표시
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("DB에서 조회하고 싶은 질문을 입력하세요..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("SQL 생성 중..."):
                response = generator.generate_sql(user_input)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()