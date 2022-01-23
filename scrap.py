from curses import flash
from email.mime import base
from fileinput import filename
from unicodedata import name
from urllib import response
from bs4 import BeautifulSoup
from openpecha.core.pecha import OpenPechaFS
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum,PechaMetaData
from datetime import datetime
import requests


start_url = 'http://gretil.sub.uni-goettingen.de/gretil.html'
pre_url = 'http://gretil.sub.uni-goettingen.de/'

def make_request(url):

    page = requests.get(url)
    print(page.status_code)

    return page.text

def parse_page(url):
    page = make_request(url)

    soup = BeautifulSoup(page,'html.parser')
    outline = soup.find_all('div',attrs={'class':'outline-5'})
    get_links(outline)

def get_links(outlines):
    for outline in outlines:
        ol = outline.find('ol',attrs={'class':'org-ol'})
        lis = ol.find_all('li',recursive=False)

        for li in lis:
            filename = li.find(text=True,recursive = False)
            link = li.find('a',text = 'TEI-conformant XML')
            if link:
                parse_tei(link['href'])

def parse_tei(link):
    xml = make_request(pre_url+link)
    result = BeautifulSoup(xml,'xml')
    body = result.find('body') 
    divs = body.find_all("div", recursive=False)
    title=result.find('title').text
    base_dic={}
    if divs:
        if len(divs) == 1:
            divs = divs[0].find_all('div',recursive=False)
            
        for div in divs:
            filename = title if div.find("head") == None else div.find("head").text
            base_dic.update({filename:div.get_text().replace(filename,'').strip("\n")})         
    else:
        base_dic.update({title: body.get_text().strip("\n")})

    opf_path = create_opf(base_dic)

def create_opf(base_text):
    opf_path="./opfs"
    instance_meta = PechaMetaData(
        initial_creation_type=InitialCreationEnum.input,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
        source_metadata="")

    opf = OpenPechaFS(
        meta=instance_meta,
        base=base_text
        )

    opf_path = opf.save(output_path=opf_path)
    return opf_path


if __name__ == '__main__':
    parse_page(start_url)
    #parse_tei('gretil/corpustei/sa_Rgveda-edAufrecht.xml')
