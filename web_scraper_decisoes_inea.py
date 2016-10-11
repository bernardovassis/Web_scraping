import re
import os

from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.error import HTTPError
from bs4 import BeautifulSoup


# # Functions
# extract minute list
def extract_minute_list(page, current_collection):
    minute_data_list = []

    while page:
        beautifulsoup_object = get_beautifulsoup_obj(current_collection["url"]+page)
        for minute_entry in get_minute_entries(beautifulsoup_object):
            minute = {
                "name": extract_minute_name(minute_entry),
                "url": extract_minute_url(minute_entry)
            }

            minute_data_list.append(minute)

            page = extract_next_page(beautifulsoup_object)

    return minute_data_list


# get Beautiful Soup object from url
def get_beautifulsoup_obj(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
        return BeautifulSoup()

    bs_obj = BeautifulSoup(html.read(), "html.parser")
    return bs_obj


# get minute entries from page
def get_minute_entries(bs_obj):
    return bs_obj.find_all("div", {"class": "list-box"})


# extract minute name
def extract_minute_name(minute_entry):
    name = minute_entry.h3.a.string
    name = name.strip().replace('/', '-')
    return name


# extract document url
def extract_minute_url(minute_entry):
    link = minute_entry.find(attrs={"title": re.compile("Clique para baixar.*")})
    if 'href' in link.attrs:
        return link.attrs['href']
    else:
        return None


# extract link to next page
def extract_next_page(bs_obj):
    next_page_link = bs_obj.find("li", {"class": "next"})
    if next_page_link:
        next_page_link = next_page_link.find("a").attrs['href']
    return next_page_link


# download documents from collection
def download_documents_collection(minute_data_list, current_collection):
    for data in minute_data_list:
        download_pdf_document(data, current_collection["name"])


# download the minute pdf
def download_pdf_document(minute_data, folder):
    print()
    file_name = os.path.join(folder, minute_data['name']+".pdf")
    try:
        urlretrieve(minute_data['url'], file_name)
        print(minute_data['name']+": download successful."+"\n")
    except FileNotFoundError as e:
        print(minute_data['name']+": File not found.")


# # Running the scraper
collections = [{"name": "Pauta_Licenciamento",
                "url": "http://www.inea.rj.gov.br/Portal/MegaDropDown/Institucional/Conselhodiretor/Atosdoconselho/"
                        "Sessoesdeliberativas/"},
               {"name": "Ata_Licenciamento",
                "url": "http://www.inea.rj.gov.br/Portal/MegaDropDown/Institucional/Conselhodiretor/Atosdoconselho/"
                        "SessoesDelibLicenciamento/"},
               {"name":"Ata_Geral",
                "url":"http://www.inea.rj.gov.br/Portal/MegaDropDown/Institucional/Conselhodiretor/Atosdoconselho/"
                        "AtasReunioesOrdinariasExtraord/"}]

for collection in collections:
    print("Starting: " + collection['name'])

    try:
        os.mkdir(collection['name'])
        print("Created '"+collection['name']+"'folder")
    except FileExistsError as e:
        print("folder already exists\n")

    minute_list = extract_minute_list("index.htm&lang=", collection)
    download_documents_collection(minute_list, collection)
