from curses import flash
from email.mime import base
from fileinput import filename
from unicodedata import name
from unittest import result
from urllib import response
from bs4 import BeautifulSoup
from openpecha.core.pecha import OpenPechaFS
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum,PechaMetaData
from datetime import datetime
import requests


start_url = 'http://gretil.sub.uni-goettingen.de/gretil.html'
pre_url = 'http://gretil.sub.uni-goettingen.de/'

def make_request(url):

    response = requests.get(url)

    return response


def parse_page(url):
    page = make_request(url)
    soup = BeautifulSoup(page.text,'html.parser')
    outlines = soup.find_all('div',attrs={'class':'outline-5'})
    parse_links(outlines)


def parse_links(outlines):
    for outline in outlines:
        ol = outline.find('ol',attrs={'class':'org-ol'})
        lis = ol.find_all('li',recursive=False)

        for li in lis:
            link = li.find('a',text = 'TEI-conformant XML')
            if link:
                parse_tei(link['href'])
                


def parse_tei(link):
    xml = make_request(pre_url+link)
    if xml:
        result = BeautifulSoup(xml.text,'xml')
        body = result.find('body') 
        divs = body.find_all("div", recursive=False)
        title=result.find('title').text
        base_text={}
        if divs and divs[0].find_all('div',recursive=False) == None:
            if len(divs) == 1:
                divs = divs[0].find_all('div',recursive=False) 

                
            for div in divs:
                filename = title if div.find("head") == None else div.find("head").text
                base_text.update({filename:div.get_text().replace(filename,'').strip("\n")})         
        else:
            base_text.update({title: body.get_text().strip("\n")})

        print(title)
        opf_path = create_opf(base_text,result)


def create_opf(base_text,result):
    opf_path="./opfs"
    src_meta =get_metadata(result)
    opf = OpenPechaFS(
        meta=src_meta,
        base=base_text
        )
    opf_path = opf.save(output_path=opf_path)
    return opf_path


def get_metadata(result):
    src_meta = parse_src_meta(result)
    instance_meta = PechaMetaData(
        initial_creation_type=InitialCreationEnum.input,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
        source_metadata=src_meta)

    return instance_meta    


def parse_src_meta(result):
    src_meta = {}
    title_stmt = result.find('titleStmt')
    profileDesc = result.find('profileDesc')
    respStmt = title_stmt.find_all('respStmt')

    for elem in respStmt:
        src_meta.update({elem.find('resp').text:elem.find('name').text})

    languages = profileDesc.find_all('language')
    src_meta.update({'title':title_stmt.find("title").text})
    src_meta.update({'lang':[x.text for x in languages]})
    src_meta.update({'term':profileDesc.find('term').text})

    return src_meta
    

if __name__ == '__main__':
    parse_page(start_url)
    #parse_tei('gretil/corpustei/sa_zaMkara-vivekacuDAmaNi.xml')
