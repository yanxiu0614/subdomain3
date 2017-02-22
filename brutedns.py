#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
    author:root@yanxiuer.com
    blog(https://www.yanxiuer.com)
'''
from publicsuffix import PublicSuffixList
from publicsuffix import fetch
import dns.resolver
import time
import queue
import gevent.pool
import logging
import csv
from IPy import IP
import gc
import os
import sys
import argparse
import platform
from gevent import monkey
monkey.patch_all()

# logging.basicConfig(
#     level=logging.DEBUG,
#     filename="brute.log",
#     filemode="a",
#     datefmt='%(asctime)s-%(levelname)s-%(message)s'
# )

class brutedomain:
    def __init__(self,args):
        self.target_domain = args.domain
        if not self.target_domain:
            print('usage: brutedns.py -d baidu.com -s low/medium/high')
            sys.exit(1)
        self.level = args.level
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = [
            '114.114.114.114',
            '114.114.115.115',
            '223.5.5.5',
            '223.6.6.6',
            '180.76.76.76',
            '119.29.29.29',
            '182.254.116.116',
            '210.2.4.8',
            '112.124.47.27',
            '114.215.126.16',
            '101.226.4.6',
            '218.30.118.6',
            '123.125.81.6',
            '140.207.198.6'
            '8.8.8.8',
            '8.8.4.4']
        self.resolver.timeout = 4
        self.set_cdn = self.load_cdn()
        self.queues = queue.Queue()
        self.dict_cname = dict()
        self.dict_ip = dict()
        self.ip_flag = dict()
        self.flag_count = 0
        self.coroutine_num = 10000
        self.segment_num = 10000
        self.judge_speed(args.speed)
        self.count = self.get_payload()
        self.found_count=0
        self.add_ulimit()
        self.psl=self.get_suffix()

    def add_ulimit(self):
        if(platform.system()=="Linux"):
            os.system("ulimit -n 65535")

    def load_subname(self):
        lists = list()
        with open('dict/wydomain.csv','r') as file_sub:
            for line in file_sub:
                line = line.strip()
                lists.append(line)
        return lists

    def load_next_sub(self):
        lists = list()
        with open('dict/next_sub_full.txt','r') as file_sub:
            for line in file_sub:
                line = line.strip()
                lists.append(line)
        return lists

    def load_cdn(self):
        sets = set()
        with open('dict/cdn_servers.txt','r') as file_cdn:
            for line in file_cdn:
                line = line.strip()
                sets.add(line)
        return sets

    def get_suffix(self):
        suffix_list = fetch()
        psl = PublicSuffixList(suffix_list)
        return psl


    def check_cdn(self,cname):
        cdn_name=self.psl.get_public_suffix(cname)
        if cdn_name in self.set_cdn:
            return True
        else:
            return False

    def get_type_id(self, name):
        return dns.rdatatype.from_text(name)

    def judge_speed(self,speed):
        if(speed == "low"):
            self.coroutine_num = 1000
            self.segment_num = 7000
        elif(speed =="high"):
            self.coroutine_num == 2500
            self.segment_num = 20000
        else:
            self.coroutine_num =1500
            self.segment_num = 10000

    def query_domain(self,domain):
        list_ip=list()
        list_cname=list()
        try:
            record = self.resolver.query(domain)
            for A_CNAME in record.response.answer:
                for item in A_CNAME.items:
                    if item.rdtype == self.get_type_id('A'):
                        list_ip.append(str(item))
                        self.dict_ip[domain]=list_ip
                    elif(item.rdtype == self.get_type_id('CNAME')):
                        list_cname.append(str(item))
                        self.dict_cname[domain] = list_cname
                    elif(item.rdtype == self.get_type_id('TXT')):
                        pass
                    elif item.rdtype == self.get_type_id('MX'):
                        pass
                    elif item.rdtype == self.get_type_id('NS'):
                        pass
            del list_ip
            del list_cname
        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            pass
        except dns.resolver.Timeout:
            pass
        except Exception as e:
            pass

    def get_payload(self):
        list_subname = self.load_subname()
        list_next_sub = self.load_next_sub()
        for subname in list_subname:
            self.queues.put(subname)
            if(self.level==2):
                for next_sub in list_next_sub:
                    self.queues.put("{sub}.{subname}".format(sub = next_sub,subname = subname))
        del list_subname
        del list_next_sub
        count=((self.queues.qsize()-self.queues.qsize()%(self.segment_num))/self.segment_num)+1
        return count

    def run(self):
        lists = list()
        if (self.queues.qsize() > self.segment_num):
            for num in range(self.segment_num):
                lists.append(self.queues.get())
        else:
            for num in range(self.queues.qsize()):
                lists.append(self.queues.get())
        coroutine_pool = gevent.pool.Pool(self.coroutine_num)
        for l in lists:
            domain = "{sub}.{target_domain}".format(sub=l,target_domain=self.target_domain)
            coroutine_pool.apply_async(self.query_domain,args=(domain,))
        coroutine_pool.join(20)
        coroutine_pool.kill()
        del coroutine_pool
        del lists



    def handle_data(self):
        for k, v in self.dict_cname.items():
            for c in v:
                if(self.check_cdn(c)):
                    self.dict_cname[k] = "Yes"
                else:
                    self.dict_cname[k] = "No"
        invert_dict_ip={str(value):key for key,value in self.dict_ip.items()}
        self.found_count = self.found_count + invert_dict_ip.__len__()
        invert_dict_ip={value:key for key,value in invert_dict_ip.items()}
        for keys,values in self.dict_ip.items():
            if(invert_dict_ip.__contains__(keys)):
                for value in values:
                    if(IP(value).iptype() =='PRIVATE'):
                        self.dict_ip[keys] = "private address"
                    else:
                        try:
                            key_yes=self.dict_cname[keys]
                        except KeyError:
                            key_yes="No"
                        if(key_yes=="No"):
                            CIP = (IP(value).make_net("255.255.255.0"))
                            if CIP in self.ip_flag:
                                self.ip_flag[CIP] = self.ip_flag[CIP]+1
                            else:
                                self.ip_flag[CIP] = 1
    def raw_write_disk(self):
        self.flag_count = self.flag_count+1
        with open('result/{name}.csv'.format(name=self.target_domain), 'a') as csvfile:
            writer = csv.writer(csvfile)
            if(self.flag_count == 1):
                writer.writerow(['domain', 'CDN', 'IP'])
                for k,v in self.dict_ip.items():
                    try:
                        tmp = self.dict_cname[k]
                    except:
                        tmp="No"
                    writer.writerow([k,tmp,self.dict_ip[k]])
            else:
                for k,v in self.dict_ip.items():
                    try:
                        tmp = self.dict_cname[k]
                    except:
                        tmp="No"
                    writer.writerow([k,tmp,self.dict_ip[k]])
        self.dict_ip.clear()
        self.dict_cname.clear()

    def deal_write_disk(self):
        ip_flags = sorted(self.ip_flag.items(), key = lambda d: d[1], reverse = True)
        with open('result/deal_{name}.csv'.format(name = self.target_domain), 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['IP', 'frequency'])
            for ip in ip_flags:
                writer.writerow(ip)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A simple and fast tool for bruting subdomains,version=1.0')
    parser.add_argument('-s','--speed',default="medium",
                        help='low,medium and high')
    parser.add_argument("-d", "--domain",
                        help="domain name,for example:baidu.com")
    parser.add_argument("-l", "--level", default=2, type=int,
                        help="example: 1,hello.baidu.com;2,hello.world.baidu.com")
    args = parser.parse_args()
    brute = brutedomain(args)
    start=time.time()
    i = 0
    while(not brute.queues.empty()):
        i = i + 1
        try:
            brute.run()
            brute.handle_data()
            brute.raw_write_disk()
            gc.collect()
            end = time.time()
            print("percent：%{percent}|found：{found_count} number|speed：{velocity} number/s"
                  .format(percent=round(float(i)/float(brute.count)*100,2),
                          found_count=brute.found_count,
                          velocity=round(brute.segment_num*i/(end-start),2)))
        except KeyboardInterrupt:
            print("stop")
            sys.exit(1)
    brute.deal_write_disk()