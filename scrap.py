from curses import flash
from email.mime import base
from fileinput import filename
from unicodedata import name
from urllib import response
from bs4 import BeautifulSoup
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
    if divs:
        if len(divs) == 1:
            divs = divs[0].find_all('div',recursive=False)
            
        for div in divs:
            filename = div.find("head").text
            with open(f"{filename}.txt","w") as f:
                f.write(div.get_text().replace(filename,'').strip("\n"))
    else:
        base_text = body.get_text().strip("\n")
        filename = title
        """ texts = body.find_all('p',recursive=False)
        for text in texts:
            base_text+=text.text+"\n" """
            
        with open(f"{filename}.txt","w") as f:
            f.write(base_text)

if __name__ == '__main__':
    #parse_page(start_url)
    parse_tei('gretil/corpustei/sa_sAmavedasaMhitA.xml')
