# imports

import requests
import json
import re
import fitz
import html2text

# load JSONs
with open('headers.json') as headers_file:
    headers = json.load(headers_file)
with open('config.json') as config_file:
    config = json.load(config_file)


baseUrl = config["baseUrl"]

# get data for post
postdata = {
    'username': config["studId"],
    'password': config["pass"],
    'loginSubmit': 'Login'
}


def login() -> None:
    """Login to save the cookies for the session"""

    sess.post(url=f'{baseUrl}/', headers=headers["login"], data=postdata)


def list_circ() -> None:
    """get all circulars and print them to the shell"""

    print("通告列表".center(75, "="))
    print(f'{"Id".center(6)} | {"Date".center(25)} | Title')

    circ_list_html = sess.get(
        f'{baseUrl}/circulars/student.php', headers=headers["circ"]
    )
    lines = html2text.html2text(circ_list_html.text).split(
        '---|---|---')[1].splitlines()

    for line in lines:
        line_is_circular = re.fullmatch(
            r'(.*)\|\s*(\[.*\])\s*\(view.php\?id=([0-9]*)\)\|\s*', line)

        if not line_is_circular:
            continue

        regex_res = re.search(
            r'^(.*)\|\s*\[(.*)\]\s*\(view.php\?id=([0-9]*)\)\|\s*$', line)
        circ_date = regex_res.group(1)
        circ_title = regex_res.group(2)
        circ_id = regex_res.group(3)

        print(f'{circ_id.center(6)} | {circ_date.center(25)} | {circ_title}')


def ask_for_id() -> str:
    print('='*79)
    circ_id = input('請輸入通告id: ')
    print('='*79)
    return circ_id


def get_circ_url(circ_id: str) -> str:
    """
    Gets circular's url by id
    """

    circ_html = sess.get(
        url=f'{baseUrl}/circulars/view.php?id={circ_id}',
        headers=headers["circ"]
    )

    circ_page_txt = ''.join(html2text.html2text(circ_html.text).splitlines())
    circ_pdf_url = re.sub(r'[\s\S]*\[Download\]\(', '', circ_page_txt, re.M)
    circ_pdf_url = re.sub(r'\)[\s\S]*', '', circ_pdf_url, re.M)

    return circ_pdf_url


def read_pdf(url: str):
    """
    Get PDF from the url given and print text inside the PDF
    """

    r = sess.get(url, headers=headers["circ"])

    # Store content to tmp.pdf
    with open('tmp.pdf', 'wb') as tmp_file:
        tmp_file.write(r.content)

    doc = fitz.open("tmp.pdf")
    for x in range(doc.pageCount):
        pageobj = doc.load_page(x)
        circ_text = re.sub(r'\n+', '\ue020', pageobj.get_text("text"), re.M)
        circ_text = re.sub(r'\s', '', circ_text, re.M)
        circ_text = re.sub(r'\ue020', '\n', circ_text)
        print(circ_text)


sess = requests.Session()
login()
list_circ()
circ_id = ask_for_id()
circ_url = get_circ_url(circ_id)
read_pdf(circ_url)
