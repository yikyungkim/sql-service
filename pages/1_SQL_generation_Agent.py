"""
사용자의 자연어 질의를 입력받고,
LLM으로부터 생성된 SQL을 보여준 뒤,
사용자가 수정/확인을 거쳐 DB 실행할 수 있게 함.
"""

import streamlit as st
from agents.generation_agent import sql_generation

def main():
    st.title("SQL Auto-Generation from Natural Language")
    st.write("자연어 질의를 입력하면, LLM이 SQL로 변환해줍니다.")

    user_query = st.text_area("질의 입력 (예: '최근 1주일간 가장 많이 주문한 상품은?')")
    generator = sql_generation()
    
    if st.button("SQL 생성"):
        if not user_query.strip():
            st.warning("질의를 입력해 주세요.")
        else:
            schema_info = generator.get_schema_info()
            prompt = generator.build_sql_generation_prompt(user_query, schema_info)

            with st.spinner("LLM으로부터 SQL 생성 중..."):
                generated_sql = generator.generate_sql(prompt)
            
            # 2) 생성된 SQL 표시
            st.subheader("생성된 SQL 쿼리")
            sql_query_input = st.text_area("수정 가능", value=generated_sql, height=150)

            # 3) 실행 여부 선택
            if st.button("이 SQL 실행하기"):
                try:
                    with st.spinner("쿼리 실행 중..."):
                        columns, rows = generator.execute_query(sql_query_input)
                    st.success("쿼리 실행 완료!")
                    if columns:
                        st.write(f"결과 컬럼: {columns}")
                        st.write("결과 데이터:")
                        st.dataframe(rows)
                    else:
                        st.write("SELECT 결과가 없거나, 쿼리가 변경되었습니다.")
                except Exception as e:
                    st.error(f"쿼리 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
