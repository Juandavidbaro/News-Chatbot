import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
import pandas as pd

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OpenAI API key not set. Please set it in the .env file")

try:

    news_df = pd.read_csv("news_data.csv")

    # Asegurarse de que el archivo tiene contenido en la columna esperada
    if 'content' not in news_df.columns:
        raise ValueError("El archivo CSV no contiene una columna 'content'")

    # Combinar todo el contenido de las noticias en un solo texto
    text = " ".join(news_df['content'].dropna())

    # Dividir el texto en fragmentos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    split_texts = text_splitter.split_text(text) 

    docs = [Document(page_content=chunk) for chunk in split_texts]
    
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Initialize Chroma vector store
    persist_directory = "./chroma_db"
    vectorstore = Chroma.from_documents(docs, embedding=embeddings, persist_directory=persist_directory)

    print("Success!")
except Exception as e:
    print(f"An error occurred: {e}")
