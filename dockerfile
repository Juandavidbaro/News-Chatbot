# Usa una imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de tu proyecto al contenedor
COPY . /app

# Instala las dependencias necesarias desde el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que Streamlit ejecutará la aplicación
EXPOSE 8501

# Define el comando para ejecutar la aplicación Streamlit
CMD ["streamlit", "run", "main.py"]
