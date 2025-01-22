#!/usr/bin/env python
# coding: utf-8

# In[4]:


get_ipython().system('pip install selenium')
get_ipython().system('pip install flask')
get_ipython().system('pip install Flask-Caching')
get_ipython().system('pip install flask-cors')


# In[ ]:


from flask import Flask, jsonify, redirect, url_for, send_from_directory
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import json
import os


app = Flask(__name__)
CORS(app)
# Vérifier si les données sont déjà présentes dans le fichier JSON
def load_voitures_data():
    with open('dataV.json', 'r') as file:
        return json.load(file)
    return None

def save_voitures_data(data):
    with open('dataV.json', 'w') as file:
         json.dump(data, file) 



@app.route('/')
def home():
    return redirect(url_for('get_voitures'))  # Redirige vers la route '/api/voitures'

@app.route('/api/voitures', methods=['GET'])
def get_voitures():
    
    
    def liensVoitures():
    
        liens_fiches = []
        url_base = "https://www.automobile.tn"
        url = "https://www.automobile.tn/fr/neuf/recherche/s="

        page = 1
        while page < 13:
            url_page = f"{url}?page={page}"
            reponse = requests.get(url_page)
            if reponse.status_code != 200:
                break
            soup = BeautifulSoup(reponse.content, 'html.parser')
            voitures = soup.find_all('div', class_='versions-item')
            for voiture in voitures:
                link = voiture.find('a')['href'] if voiture.find('a') else None
                if link.count('/') == 5:
                    liens_fiches.append(url_base + link)
            page += 1
        print("succes")
        liens_fiches=set(liens_fiches)
        return liens_fiches

    def detailsFiches():
        print("Scraping in progress...")
        driver = webdriver.Chrome() 
        links = liensVoitures()
        data = []
        for link in links:
            driver.get(link)
            driver.implicitly_wait(5)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Scraping des informations
            prix_scrap = soup.find('div', class_='price').get_text(strip=True) if soup.find('div', class_='price') else None
            prix = prix_scrap.replace("à partir de", "").strip() if prix_scrap else "Indisponible"
            image_tag = soup.find('img', class_='img-fluid')
            image_url = image_tag['src'] if image_tag else "Aucune image"
            titre_element = soup.find('h3', class_='page-title')
            
            if titre_element:
                titre = titre_element.text.split(' ', 2)
                version = titre_element.find('span').text if titre_element.find('span') else "Indisponible"
                marque = titre[0] if len(titre) > 0 else "Indisponible"
                modele = titre[1] if len(titre) > 1 else "Indisponible"
            else:
                version, marque, modele = "Indisponible", "Indisponible", "Indisponible"
            
            # Scraping des caractéristiques techniques
            carosserie = soup.find('th', string='Carrosserie')
            carosserie = carosserie.find_next('td').text if carosserie else "Indisponible"

            nb_place = soup.find('th', string='Nombre de places')
            nb_place = nb_place.find_next('td').text if nb_place else "Indisponible"

            type_boite = soup.find('th', string='Boîte')
            type_boite = type_boite.find_next('td').text if type_boite else "Indisponible"

            nb_cylindre = soup.find('th', string='Nombre de cylindres')
            nb_cylindre = nb_cylindre.find_next('td').text if nb_cylindre else "Indisponible"

            type_energie = soup.find('th', string='Energie ')
            type_energie = type_energie.find_next('td').text if type_energie else "Indisponible"

            conso = soup.find('th', string='Consommation mixte ')
            conso = conso.find_next('td').text if conso else "Indisponible"

            # Ajout des données dans un tableau
            data.append({
                "prix": prix,
                "image_url": image_url,
                "version": version,
                "marque": marque,
                "modele": modele,
                "Carosserie": carosserie,
                "nb_place": nb_place,
                "type_boite": type_boite,
                "nb_cylindre": nb_cylindre,
                "type_energie": type_energie,
                "conso": conso
            })
        
        driver.quit() 
        return data
    if os.path.exists('dataV.json'):
        v=load_voitures_data()
        return v
    else : 
        voitures_data = detailsFiches()
        save_voitures_data(voitures_data)
        return jsonify(voitures_data)


if __name__ == '__main__':
    app.run(debug=True,use_reloader=False,port=5001)


# In[3]:


get_ipython().run_line_magic('tb', '')



# In[ ]:




