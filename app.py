import streamlit as st
import os
from sqlalchemy import inspect
from sqlalchemy.sql import text
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from sqlalchemy.exc import OperationalError
from backend import answer_sql

# Cấu hình giao diện (chế độ wide)
st.set_page_config(page_title="SQLite Database Viewer", layout="wide")

# Tạo 2 cột trái và phải
col_left, col_right = st.columns(2)

with col_right:
    st.header("File Upload & Query Section")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a SQLite database file", type="db")
    question = None
    query_result = None

    if uploaded_file is not None:
        # Lưu file tạm thời
        temp_db_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)

        with open(temp_db_path, "wb") as f:
            f.write(uploaded_file.read())

        try:
            # Kết nối đến cơ sở dữ liệu SQLite
            db = SQLDatabase.from_uri(f"sqlite:///{temp_db_path}")
            inspector = inspect(db._engine)  

            # Chọn bảng để hiển thị nội dung
            tables = inspector.get_table_names()
            selected_table = st.selectbox("Select a table to view its content", ["Select"] + tables)

            # Thanh nhập câu hỏi liên quan đến database
            question = st.text_input("Ask a question about the database", placeholder="Enter your question here")

            # Xử lý truy vấn
            if st.button("Submit Query"):
                try:
                    query_result = answer_sql(question,db)
                    # Handle if query_result is a string or dictionary
                    if isinstance(query_result, dict):
                        query_result = query_result.get('text', 'No text found in response')
                except Exception as e:
                    query_result = f"Error executing query: {e}"

        except Exception as e:
            st.error(f"Error processing the database file: {e}")

    # Hiển thị kết quả truy vấn ở bên phải
    if question and query_result is not None:
        st.subheader("Query Result")
        st.write(query_result)

with col_left:
    st.header("Database Viewer")
    if uploaded_file is not None:
        try:
            if selected_table != "Select":
                # Hiển thị schema của bảng
                columns = inspector.get_columns(selected_table)

                # Truy vấn dữ liệu từ bảng
                query = text(f"SELECT * FROM {selected_table} LIMIT 100;")
                with db._engine.connect() as connection:
                    result = connection.execute(query)
                    rows = result.fetchall()
                    if rows:
                        st.dataframe(rows)
                    else:
                        st.write(f"Table `{selected_table}` is empty.")
        except Exception as e:
            st.error(f"Error retrieving data from table `{selected_table}`: {e}")
