# News-Chatbot

## Descripción
Este proyecto es un sistema inteligente de noticias que utiliza diversas tecnologías como scraping de noticias, creación de una base de datos vectorial, RAG (Retrieval-Augmented Generation), evaluación de métricas y narración de respuestas, para proporcionar un asistente interactivo que puede responder preguntas relacionadas con noticias específicas.

### El sistema permite:

* Realizar scraping de noticias desde un enlace proporcionado.
* Guardar la información extraída en un archivo CSV.
* Utilizar una base de datos vectorial para almacenar y recuperar información.
* Responder preguntas usando un modelo de lenguaje (GPT-4) con el contexto proporcionado por las noticias.
* Evaluar la calidad de las respuestas usando DeepEval.
* Narrar las respuestas en audio utilizando la tecnología gTTS.
* Realizar la comparación entre dos noticias al ingresar la consulta "Realiza una comparación entre las últimas noticias" o "Realiza la comparación entre las primeras dos noticias relacionadas con (noticia a consultar)", para ello es necesario que las noticias se encuentren en el historial de consultas.

## Funcionalidades
1. Scraping de Noticias
El sistema puede extraer datos de una noticia a partir de su URL, incluyendo el título, autores, fecha, contenido y enlace. Esta información se guarda en un archivo CSV para su posterior consulta.

2. Base de Datos Vectorial (Vector Store)
Se utiliza Chroma junto con OpenAI Embeddings para crear una base de datos vectorial donde se almacenan los textos de las noticias. Este sistema permite la recuperación eficiente de datos relevantes utilizando vectores de características generados por el modelo.

3. RAG (Retrieval-Augmented Generation)
El sistema emplea el enfoque RAG para mejorar las respuestas, combinando la recuperación de información relevante con la generación de texto de un modelo de lenguaje (GPT-4). La recuperación de información se realiza desde la base de datos vectorial, y luego, el modelo utiliza esa información para generar una respuesta adecuada a la consulta.

4. Evaluación de Métricas con DeepEval
El sistema puede integrar métricas de calidad para evaluar las respuestas generadas por el modelo, asegurando que sean lo más precisas y útiles posibles.

5. Narración de Respuestas
Una vez que el modelo responde a una consulta, el sistema tiene la capacidad de narrar la respuesta utilizando gTTS (Google Text-to-Speech), lo que permite reproducir la respuesta en formato de audio.

# Instalación

Siga estos pasos para clonar el repositorio, instalar las dependencias y ejecutar el proyecto:

### 1. Clonar el Repositorio
Primero, clone el repositorio utilizando el siguiente comando:

```bash
git clone https://github.com/Juandavidbaro/News-Chatbot.git
cd tu_repositorio
```

### 2. Crear un entorno virtual (windows)
Crea el entorno virtual utilizando:

```bash
python -m venv myvenv 
```

### 3. Activar el entorno virtual (windows)
Activa el entorno virtual utilizando:

```bash
myvenv\Scripts\activate
```

### 4. Instalar Dependencias
Instale las dependencias utilizando pip:

```bash
pip install -r requirements.txt
```

### 5. Configurar las Variables de Entorno
Cree un archivo .env en la raíz del proyecto y agregue su clave de API de OpenAI:

```bash
OPENAI_API_KEY=your_openai_api_key
```

### 6. Ejecutar la Aplicación
Para ejecutar la aplicación, use el siguiente comando:

```bash
streamlit run main.py
```

### 7. Evaluación de Métricas con DeepEval
Para ejecutar las pruebas abra otra terminar con el entorno virtual activado, y use el siguiente comando:

```bash
deepeval test run test_deepeval.py
```

# Construcción y ejecución de contenedor de docker

### 1. Construir la imagen de Docker
Puedes construir la imagen de Docker ejecutando el siguiente comando en el directorio donde se encuentra el Dockerfile:

```bash
docker build -t news-chatbot .
```

2. Ejecutar el contenedor
Una vez que la imagen se haya construido, puedes ejecutar el contenedor de la siguiente manera:

```bash
docker run -p 8501:8501 news-chatbot
```

Esto hará que tu aplicación Streamlit esté disponible en http://localhost:8501.
