import re
from bs4 import BeautifulSoup as bs
from downloadFuncs import download_zip, download_img, unzip_archive
import requests

resp = requests.get('http://az.lib.ru/b/bem_a_l/')
soap = bs(resp.text, 'lxml')
block = soap.find('i')
print(block.text)