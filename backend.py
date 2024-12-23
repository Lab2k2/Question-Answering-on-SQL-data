from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from llm_model import llm  
from operator import itemgetter

def answer_sql(question,db):
    # Cấu hình top_k và table_info
    top_k = 10 #Giới hạn lại kết quả
    table_info = ['emp_table']

    # Tạo template prompt cho câu hỏi SQL
    mssql_prompt = PromptTemplate.from_template(
        """Given an input question, create a syntactically correct SQL query to run. 
        Only return SQL Query, nothing else like ```sql ... ```. 
        Unless the user specifies in his question a specific number of examples he wishes to obtain, 
        always limit your query to at most {top_k} results. 
        Never query for all the columns from a specific table; only ask for the few relevant columns given the question. 
        Pay attention to use only the column names that you can see in the schema description. 
        Be careful not to query for columns that do not exist. 
        Also, pay attention to which column is in which table. 
        
        Only use the following tables: {table_info}

        Question: {input}
        SQL query:"""
    )

    # Tạo công cụ thực thi truy vấn
    execute_query = QuerySQLDataBaseTool(db=db)

    # Tạo chuỗi tạo truy vấn SQL
    write_query = create_sql_query_chain(llm, db, prompt=mssql_prompt, k=top_k)

    # Prompt định dạng kết quả
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
    )

    # Tích hợp các bước xử lý vào chuỗi
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer_prompt
        | llm
        | StrOutputParser()
    )

    # Chạy chuỗi với câu hỏi
    response = chain.invoke({"question": question})
    return response
