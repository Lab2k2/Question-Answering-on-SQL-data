import os

from langchain_google_genai import ChatGoogleGenerativeAI


# Nhập API Key cho Google Vertex AI
os.environ["GOOGLE_API_KEY"] = ("AIzaSyCy-F4waBhpZEwUeT5FH-ulfOT_0ySKOXw")

# Sử dụng model "gemini-1.5-flash" từ Google Vertex AI
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
