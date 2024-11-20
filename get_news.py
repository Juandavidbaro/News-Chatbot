import os
import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd


# Web scraping function
def get_news_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": f"Error al acceder a la URL: {response.status_code}"}

    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title').text if soup.find('title') else 'Título no encontrado'
    authors = [author.get('content', 'Autor no encontrado') for author in soup.find_all('meta', {'name': 'author'})]
    date = soup.find('meta', {'name': 'date'})['content'] if soup.find('meta', {'name': 'date'}) else 'Fecha no encontrada'
    article_section = soup.find('div', {'class': 'article-body'}) or \
                      soup.find('section', {'class': 'content'}) or \
                      soup.find('article')
    content = " ".join([p.get_text(strip=True) for p in article_section.find_all('p')]) if article_section else 'Contenido no encontrado'

    return {
        'Título': title,
        'Autores': ", ".join(authors) if authors else "No se encontraron autores",
        'Fecha': date,
        'Contenido': content,
        'Enlace': url
    }

def save_to_csv(data, filename="news_data.csv"):
    if os.path.exists(filename):
        df_existing = pd.read_csv(filename)
        df_new = pd.DataFrame([data])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = pd.DataFrame([data])
    df_combined.to_csv(filename, index=False)