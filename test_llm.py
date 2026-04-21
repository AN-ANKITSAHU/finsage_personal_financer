from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")  # ← was llama3-70b-8192

response = llm.invoke("Say hello")
print(response.content)