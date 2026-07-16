from bs4 import BeautifulSoup
import requests
from decimal import Decimal

def scrapper_kabum(url):
    
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"}

    page = requests.get(url, headers = headers)

    soup = BeautifulSoup(page.text, "html.parser")

    nome_produto = (soup.find("h1").string)

    preco_texto = (soup.find("h4").string)

    preco_produto = Decimal(preco_texto.replace("R$", "").replace(".", "").replace(",", ".").strip()) #Removendo pontuações para transformar valor em Decimal

    return nome_produto, preco_produto
