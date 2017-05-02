from gevent import monkey
monkey.patch_all()
import requests
import gevent.pool
import csv
import codecs
import lxml.etree as etree
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


result_name='baidu.com.csv'  #爆破的结果名称



dict_url=dict()
dict_urlssl=dict()
dict_ip = dict()
dict_ipssl=dict()
list_ip = list()
list_ipssl = list()

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                 'Accept-Encoding': 'gzip, deflate,sdch',
                 'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                 'Cache-Control': 'max-age=0',
                 'Connection': 'keep-alive',
                 'DNT': '1',
                 'Upgrade-Insecure-Requests': '1',
                 'Cookie': '',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

def load_brute_result():
    temp_dict = dict()
    with open('./result/{result}'.format(result=result_name), 'r') as csvfile:
        brute_result = csv.reader(csvfile)
        for each in brute_result:
            if (each[0] != "domain" and each[1] != "Yes" and "private" not in each[2]):
                temp_dict[each[0]] = each[2]
    return temp_dict


def load_deal_brute_result():
    c_ip=set()
    with open('./result/deal_{result}'.format(result=result_name), 'r') as csvfile:
        brute_result = csv.reader(csvfile)
        for each in brute_result:
            if(each[0]!="IP"):
                c_ip.add(each[0].rstrip('0/24'))
    return c_ip

def http_get(url):
    list_url=[]
    resps = requests.get(url, verify=False, headers=headers, timeout=7)
    list_url.append(url)
    list_url.append(resps.status_code)
    selector = etree.HTML(resps.content)
    titles = selector.xpath("//title")
    for title in titles:
        list_url.append(title.text)
    return list_url


def get_url_info(domain):
    list_url=[]
    url = "http://" + domain
    try:
       list_url=http_get(url)
    except Exception as e:
        pass
    dict_url[domain] = list_url

def get_urlssl_info(domain):
    list_url=[]
    url_ssl = "https://" + domain
    try:
        list_url=http_get(url_ssl)
    except Exception as e:
        pass
    dict_urlssl[domain]=list_url

def filter_nothing(l):
    if(l==[]):
        pass
    else:
        return l

def get_ip_info(domain,ip):
    list_ip = []
    ip=ip.strip().strip('\'')
    url = "http://" + ip
    try:
        list_ip=http_get(url)
    except Exception as e:
        pass
    if(domain!=2):
        dict_ip[domain]=list_ip
    else:
        list_ip.append(list_ip)


def get_ipssl_info(domain,ipssl):
    list_ip = []
    ipssl=ipssl.strip().strip('\'')
    ip_ssl = "https://" + ipssl
    try:
        list_ip=http_get(ip_ssl)
    except Exception as e:
        pass
    if(domain!=2):
        dict_ipssl[domain]=list_ip
    else:
        list_ipssl.append(list_ip)

def write_domain_result():
    dict_domain=load_brute_result()
    with open('./result/domain_{result}'.format(result=result_name),'a') as csvfile:
        writer = csv.writer(csvfile,codecs.BOM_UTF8)
        for k,v in dict_domain.items():
            writer.writerow([k,
                             "{url_list}\r\n{urls_list}".format(url_list=filter_nothing(dict_url[k]),urls_list=filter_nothing(dict_urlssl[k])),
                             "{ip_list}\r\n{ips_list}".format(ip_list=filter_nothing(dict_ip[k]),ips_list=filter_nothing(dict_ipssl[k]))])

def write_ip_result():
    with open('./result/ip_{result}'.format(result=result_name),'a') as csvfile:
        writer = csv.writer(csvfile,codecs.BOM_UTF8)
        for s in list_ip:
            if (s != []):
                writer.writerow(["{ip_list}".format(ip_list=filter_nothing(s))])

        for ss in list_ipssl:
            if (ss != []):
                writer.writerow(["{ip_list}".format(ip_list=filter_nothing(ss))])

coroutine_pool = gevent.pool.Pool(2000)
c_ip=load_deal_brute_result()
for i in range(1,255):
    for ip in c_ip:
        ip=ip+str(i)
        coroutine_pool.apply_async(get_ip_info, args=(2,ip,))
        coroutine_pool.apply_async(get_ipssl_info, args=(2, ip,))

temp_dict = load_brute_result()
for k, v in temp_dict.items():
    coroutine_pool.apply_async(get_url_info, args=(k,))
    coroutine_pool.apply_async(get_urlssl_info,args=(k,))
    v=v.strip('[').strip(']')
    v_num=v.split(',')
    for ip in v_num:
        coroutine_pool.apply_async(get_ip_info, args=(k,ip,))
        coroutine_pool.apply_async(get_ipssl_info, args=(k, ip,))
coroutine_pool.join(100000)
write_domain_result()
write_ip_result()