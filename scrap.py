from cgitb import lookup
from distutils.log import INFO
import logging
from bs4 import BeautifulSoup
from openpecha.core.pecha import OpenPechaFS
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum,PechaMetaData
from datetime import datetime
from openpecha import github_utils,config
from pathlib import Path
import requests
import re
import logging
logging.basicConfig(filename='pecha_id_name_map.log',level=logging.INFO)


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
                print("DONE")
                return
                

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
        #base_text=extract_text_attr(base_text[title])
        opf_path,src_meta = create_opf(base_text,result)
        opf_path = Path(opf_path)
        create_readme(opf_path,src_meta)
        publish_pecha(opf_path.parent)


def extract_text_attr(base_text):
    text = re.split("\d*",base_text)
    return text


def create_opf(base_text,result):
    opf_path=f"{config.PECHAS_PATH}/"
    meta,src_meta =get_metadata(result)
    opf = OpenPechaFS(
        meta=meta,
        base=base_text
        )
    opf_path = opf.save(output_path=opf_path)
    return opf_path,src_meta


def get_metadata(result):
    src_meta = parse_src_meta(result)
    instance_meta = PechaMetaData(
        initial_creation_type=InitialCreationEnum.input,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
        source_metadata=src_meta)
    return instance_meta,src_meta    


def parse_src_meta(result):
    src_meta = {}
    title_stmt = result.find('titleStmt')
    profileDesc = result.find('profileDesc')
    respStmt = title_stmt.find_all('respStmt')
    for elem in respStmt:
        src_meta.update({elem.find('resp').text:elem.find('name').text})
    languages = profileDesc.find_all('language')
    src_meta.update({'title':title_stmt.find("title").text})
    src_meta.update({'language':[x.text for x in languages]})
    src_meta.update({'term':profileDesc.find('term').text})
    return src_meta


def create_readme(opf_path,src_meta):
    readme_path = opf_path.parent / 'readme.md'
    pecha_id = opf_path.stem
    pecha = f"|Pecha id | {pecha_id}"
    Table = "| --- | --- "
    Title = f"|Title | {src_meta['title']} "
    lang = f"|Language | {src_meta['language']}"
    readme = f"{pecha}\n{Table}\n{Title}\n{lang}"
    Path(readme_path).touch()
    Path(readme_path).write_text(readme)
    logging.info(pecha_id+"  "+src_meta['title'])


def publish_pecha(opf_path):
    github_utils.github_publish(
    opf_path,
    not_includes=[],
    message="initial commit"
    )


if __name__ == '__main__':
    parse_page(start_url)
    #parse_tei('gretil/corpustei/sa_zaMkara-vivekacuDAmaNi.xml')
