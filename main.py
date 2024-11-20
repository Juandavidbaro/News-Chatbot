import os
import tempfile
import uuid
from get_news import get_news_from_url, save_to_csv
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from retriever import retriever
import pandas as pd
from gtts import gTTS

load_dotenv()

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Check if environment variables are set
if not openai_api_key:
    raise ValueError("OpenAI environment variables not set. Please set them in the .env file")

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Initialize model
llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key, temperature=0)

# Prompt templates
question_prefix = (
    "Dada una historia de chat (si existe) y la última pregunta del usuario, "
    "formula una pregunta clara y coherente que represente adecuadamente lo que el usuario está buscando. "
    "Si la pregunta ya está formulada de manera adecuada, devuélvela tal cual, sin cambios. "
    "Si la pregunta necesita ajustes, reformúlala para hacerla más precisa o clara, "
    "pero no respondas la pregunta ni des ningún tipo de explicación, solo reformúlala si es necesario."
)

contextualize_question_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", question_prefix),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_question_prompt
)

answer_prefix = (
    "Eres un asistente encargado de responder preguntas utilizando contexto relevante. "
    "Para cada noticia que se te presente, muestra la siguiente información de manera ordenada para las dos primeras noticias: \n"
    "- Título\n"
    "- Fecha\n"
    "- Autor\n"
    "- Contenido\n"
    "- Enlace\n\n"
    
    "Si la respuesta está claramente indicada en el contexto, proporciónala de manera directa. Si el contexto no proporciona una respuesta completa, "
    "completa la información con el historial de chat si es relevante. "
    "Si no puedes encontrar la respuesta en ninguno de estos, responde de manera educada diciendo: "
    "\"Lo siento, no sé la respuesta a esa pregunta. Intenta volviendo a cargar el link de la noticia\" "
    "Asegúrate de dar una respuesta concisa, clara, en español. "
    "Si la respuesta involucra detalles específicos, proporciónalos de manera ordenada y comprensible, "
    "sin agregar información innecesaria ni suposiciones.\n\n"
    "{context}"
)




qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", answer_prefix),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# Initialize chain
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# Use Streamlit session state for chat history
def convert_to_chat_message_history(session_history) -> BaseChatMessageHistory:
    chat_history = ChatMessageHistory()
    for message in session_history:
        if message["type"] == "human":
            chat_history.add_user_message(message["content"])
        else:
            chat_history.add_ai_message(message["content"])
    return chat_history

# Función para narrar el texto
def narrate_text(text):
    tts = gTTS(text, lang='es')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
        tts.save(temp_audio.name)
        audio_path = temp_audio.name
    return audio_path

def main():

    if "waiting_for_answer" not in st.session_state:
        st.session_state.waiting_for_answer = False

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())  # Asigna un ID único

    st.set_page_config(page_title="Sistema Inteligente de Noticias")
    st.title("Samanta - Asistente de Noticias")
    st.sidebar.header("Opciones")

    # Opción 1: Agregar noticia mediante scraping
    st.sidebar.subheader("Agregar Noticia")
    news_url = st.sidebar.text_input("Ingresa el enlace de la noticia:")
    if st.sidebar.button("Agregar Noticia", key="add_news_button"):
        if news_url:
            try:
                news_data = get_news_from_url(news_url)
                if "error" in news_data:
                    st.sidebar.error(news_data["error"])
                else:
                    save_to_csv(news_data)
                    st.session_state.news_data = news_data
                    st.sidebar.success("Noticia agregada exitosamente.")
            except Exception as e:
                st.sidebar.error(f"Error al agregar la noticia: {e}")

    # Chat con Samanta
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Mostrar el historial del chat
    for i, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["type"]):
            st.markdown(message["content"])

            # Si el mensaje es de tipo "AI", mostrar el botón de reproducir
            if message["type"] == "ai":
                if st.button(f"Reproducir Respuesta", key=f"play_button_{i}"):
                    audio_path = narrate_text(message["content"])  # Generar la narración
                    st.audio(audio_path)  # Reproducir el audio


    # Entrada de usuario
    user_input = st.text_input("Escribe tu mensaje aquí...", key="chat_input")
    if st.button("Procesar pregunta", disabled=st.session_state.waiting_for_answer):


        if user_input and not st.session_state.waiting_for_answer:
            # Agregar la pregunta al historial de chat
            st.session_state.chat_history.append({"type": "human", "content": user_input})
            st.session_state.waiting_for_answer = True  # Marcar que estamos esperando la respuesta
            try:
                # Preparar el historial de chat y el contexto
                chat_history = convert_to_chat_message_history(st.session_state.chat_history)
                news_data = st.session_state.get("news_data", "")
                combined_context = f"{news_data}\n\n{user_input}"

                # Crear la cadena de recuperación
                conversational_rag_chain = RunnableWithMessageHistory(
                    rag_chain,
                    lambda _: chat_history,
                    input_messages_key="input",
                    history_messages_key="chat_history",
                    output_messages_key="answer",
                )

                # Invocar la cadena de recuperación
                response = conversational_rag_chain.invoke(
                    {"input": combined_context},
                    {"configurable": {"session_id": st.session_state.session_id}}
                )

                answer = response["answer"]
                st.session_state.chat_history.append({"type": "ai", "content": answer})
            except Exception as e:
                st.error(f"Error al procesar la pregunta: {e}")
                st.session_state.chat_history.append({"type": "ai", "content": "Ocurrió un error al procesar tu pregunta."})
                
            finally:
                st.session_state.waiting_for_answer = False
                
            st.rerun()

if __name__ == "__main__":
    main()
