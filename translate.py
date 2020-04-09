import urllib
from urllib import request
from urllib import parse
import json
from googletrans import Translator
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from retry import retry


def trans(content):
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
    formData = {
        'i': content,
        'from': 'en',
        'to': 'zh-CHS',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': '1538959984992',
        'sign': 'e2fd5830da31a783b6c1f83b522a7d7c',
        'doctype': 'json',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_CLICKBUTTION',
        'typoResult': 'false',
    }
    text = ''
    from_data_parse = urllib.parse.urlencode(formData).encode('utf-8')
    response = request.urlopen(url, data=from_data_parse)
    response_str = response.read().decode('utf-8')
    try:
        response_dict = json.loads(response_str)
    except:
        print(response_str)
    else:
        for i in range(len(response_dict['translateResult'][0])):
            text += response_dict['translateResult'][0][i]['tgt']
    # print(response_dict)
    return text


def trans2(text):
    translator = Translator(service_urls=['translate.google.cn'])  # 国内使用的谷歌翻译host
    return translator.translate(text, dest='zh-CN').text


@retry(tries=3, delay=1)
def trans3(text):
    browser = webdriver.Chrome()

    base_url = 'https://translate.google.cn/#view=home&op=translate&sl=auto&tl=%s' % 'zh-CN'

    if browser.current_url != base_url:
        browser.get(base_url)

    submit = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="source"]')))
    submit.clear()
    submit.send_keys(text)
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//span[@class="tlid-translation translation"]')))
    source = etree.HTML(browser.page_source)
    result = source.xpath('//span[@class="tlid-translation translation"]//text()')[0]
    print(result)
    return result
