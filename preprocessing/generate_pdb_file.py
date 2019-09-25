import os
import time
from glob import glob
import requests
from requests_html import HTMLSession
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import re
import html


DATASET_DIR = "../data/"
RES_DIR = "../resource/pdb_files/"

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

def get_pdb_content(entry):
    entry = entry.find('pre', first=True)
    if entry is not None:
        return html.unescape(remove_tags(entry.html))
    else:
        return None

def write_pdb_content_to_file(content,pdb_id):
    with open(RES_DIR+pdb_id+'.pdb',"w") as file:
        print("..writing content to "+pdb_id+".pdb")
        file.write(content)


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def make_request(url):
    t0 = time.time()
    request = None;
    try:
        time.sleep(5)
        request = requests_retry_session(session = HTMLSession()).get(url)
    except Exception as x:
        time.sleep(5)
        print('request failed :(', x.__class__.__name__)
    else:
        print('request is successful', request.status_code)
    finally:
        t1 = time.time()
        print('Took', t1 - t0, 'seconds')
    return request


pdb_ids = []
for files in glob(DATASET_DIR+"*"):
    filename = os.path.split(files)[1]
    file = open(DATASET_DIR+filename,"r")
    for f in tqdm(file):
        id = f[0:4]
        pdb_ids.append(id)

pdb_ids = list(set(pdb_ids))

session = HTMLSession()
for pdb_id in pdb_ids:
    pdb_id = pdb_id.lower()
    try:
        url = 'https://mrs.cmbi.umcn.nl/search?db=pdb&q=' + pdb_id + '&count=3'
        request = make_request(url)
        print(url)
        entry = request.html.find('#entrytext', first=True)
        if entry is None:
            entry = request.html.find("table", first=True)
            data = entry.find('a', first=True);
            nr = (((data.attrs)['href']))
            nr = nr.split('entry?db=pdb&nr=')[1].split('&q=' + pdb_id)[0]
            new_url = 'https://mrs.cmbi.umcn.nl/entry?db=pdb&nr=' + nr + '&q=' + pdb_id
            new_request = make_request(new_url)
            entry = new_request.html.find('#entrytext', first=True)
            content = get_pdb_content(entry)
            write_pdb_content_to_file(content, pdb_id)
        else:
            content = get_pdb_content(entry)
            write_pdb_content_to_file(content, pdb_id)

    except Exception as e:
        with open("../resource/log.txt","a") as log:
            log.write(pdb_id)
        print("failed to generate pdb file for "+pdb_id)