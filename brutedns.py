#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
    author:root@yanxiuer.com
    blog(https://www.yanxiuer.com)
'''
# std lib
import time
import queue
import csv
import os
import sys
import argparse
import platform
import gc

#third-party lib
import dns.resolver
import gevent.pool
from gevent import monkey
monkey.patch_all()
# import logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     filename="brute.log",
#     filemode="a",
#     datefmt='%(asctime)s-%(levelname)s-%(message)s'
# )

#private-lib
import lib.config as config
from IPy import IP
from publicsuffix import PublicSuffixList
from publicsuffix import fetch

class Brutedomain:
    def __init__(self,args):
        self.target_domain = args.domain
        if not (self.target_domain):
            print('usage: brutedns.py -d/-f baidu.com/domains.txt -s low/medium/high')
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
        self.get_subname()
        self.dict_cname = dict()
        self.dict_ip = dict()
        self.ip_flag = dict()
        self.flag_count = 0
        self.queue_sub=queue.Queue()
        self.coroutine_num = 10000
        self.segment_num = 10000
        self.judge_speed(args.speed)
        self.found_count=0
        self.add_ulimit()
        self.psl=self.get_suffix()
        self.dict_ip_count = {}

    def add_ulimit(self):
        if(platform.system()!="Windows"):
            os.system("ulimit -n 65535")

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
        if (speed == "low"):
            self.coroutine_num = config.low_coroutine_num
            self.segment_num = config.low_segment_num
        elif (speed == "high"):
            self.coroutine_num == config.high_coroutine_num
            self.segment_num = config.high_segment_num
        else:
            self.coroutine_num = config.medium_coroutine_num
            self.segment_num = config.high_segment_num

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

    def get_subname(self):
        with open('dict/wydomain.csv', 'r') as file_sub:
            for subname in file_sub:
                domain = "{sub}.{target_domain}".format(sub=subname.strip(), target_domain=self.target_domain)
                self.queues.put(domain)

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
            coroutine_pool.apply_async(self.query_domain,args=(l,))
        coroutine_pool.join(20)
        coroutine_pool.kill()
        del coroutine_pool
        del lists

    def generate_sub(self):
        try:
            domain=self.queue_sub.get_nowait()
            with open('dict/next_sub_full.txt', 'r') as file_next_sub:
                for next_sub in file_next_sub:
                    subdomain = "{next}.{domain}".format(next=next_sub.strip(), domain=domain)
                    self.queues.put_nowait(subdomain)
                return True
        except Exception:
            return False

    def set_dynamic_num(self):
        if(args.speed=="high"):
            return 350000
        elif(args.speed=="low"):
            return 150000
        else:
            return 250000

    def handle_data(self):
        temp_list=list()
        for k, v in self.dict_cname.items():
            for c in v:
                if(self.check_cdn(c)):
                    self.dict_cname[k] = "Yes"
                else:
                    self.dict_cname[k] = "No"

        for name,ip_list in self.dict_ip.items():
            ip_str=str(sorted(ip_list))
            if (self.dict_ip_count.__contains__(ip_str)):
                if(self.dict_ip_count[ip_str]>config.ip_max_count):
                    temp_list.append(name)
                else:
                    self.dict_ip_count[ip_str] = self.dict_ip_count[ip_str] + 1
            else:
                self.dict_ip_count[ip_str] = 1
            for filter_ip in config.waiting_fliter_ip:
                if (filter_ip in ip_list):
                    temp_list.append(name)

        for name in temp_list:
            try:
                del self.dict_ip[name]
            except Exception:
                pass
        self.found_count = self.found_count +self.dict_ip.__len__()
        invert_dict_ip = self.dict_ip

        for keys, values in self.dict_ip.items():
            if (str(keys).count(".") < self.level):
                self.queue_sub.put(str(keys))
            if (invert_dict_ip.__contains__(keys)):
                for value in values:
                    if (IP(value).iptype() == 'PRIVATE'):
                        invert_dict_ip[keys] = "private({ip})".format(ip=value)
                    else:
                        try:
                            key_yes = self.dict_cname[keys]
                        except KeyError:
                            key_yes = "No"
                        if (key_yes == "No"):
                            CIP = (IP(value).make_net("255.255.255.0"))
                            if CIP in self.ip_flag:
                                self.ip_flag[CIP] = self.ip_flag[CIP] + 1
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
    parser.add_argument("-f", "--file",
                        help="The list of domain")

    args = parser.parse_args()
    file_name=args.file
    sets_domain = set()
    if file_name:
        with open(file_name, 'r') as file_domain:
            for line in file_domain:
                sets_domain.add(line.strip())
    else:
        sets_domain.add(args.domain)
    for domain in sets_domain:
        args.domain=domain
        brute = Brutedomain(args)
        start=time.time()
        i = 0
        print("*****************************Begin*******************************")
        while(not brute.queues.empty()):
            i = i + 1
            try:
                brute.run()
                brute.handle_data()
                brute.raw_write_disk()
                if(brute.queues.qsize() < 30000):
                    while(brute.queues.qsize()<brute.set_dynamic_num()):
                        if(not brute.generate_sub()):
                            break
                gc.collect()
                end = time.time()
                wait_size = brute.queues.qsize()
                print(
                    "domain: {domain} |found：{found_count} number|speed：{velocity} number/s|waiting：{qsize} number|"
                      .format(domain=domain,
                              qsize=wait_size,
                              found_count=brute.found_count,
                              velocity=round(brute.segment_num*i/(end-start),2)))
            except KeyboardInterrupt:
                print("user stop")
                sys.exit(1)
        brute.deal_write_disk()
        print("*****************************Over********************************")
