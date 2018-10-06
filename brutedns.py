#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
    author:root@yanxiuer.com
'''
import sys
import platform
import time
import csv
import shutil

if sys.version > '3':
    from queue import Queue
else:
    from Queue import Queue
import gc
import os
import argparse
import dns.resolver
from IPy import IP
import gevent
from gevent import monkey
monkey.patch_all()
import lib.config as config

# import logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     filename="brute.log",
#     filemode="a",
#     datefmt='%(asctime)s-%(levelname)s-%(message)s'
# )


class Brutedomain:
    def __init__(self, args):
        self.target_domain = args.domain
        self.cdn_flag = args.cdn
        if not (self.target_domain):
            print('usage: brutedns.py -d/-f baidu.com/domains.txt -s low/medium/high -c y/n')
            sys.exit(1)
        self.level = args.level
        self.sub_dict=args.sub_file
        self.speed=args.speed
        self.next_sub_dict = args.next_sub_file
        self.other_result=args.other_file
        # self.project=args.project
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
        self.resolver.timeout = 10
        self.set_cdn = self.load_cdn()
        self.queues = Queue()
        self.set_next_sub = self.load_next_sub()
        self.extract_next_sub(self.target_domain)
        self.get_subname()
        self.dict_cname = dict()
        self.dict_ip = dict()
        self.dict_ip_block = dict()
        self.ip_flag = dict()
        self.cdn_set = set()
        self.flag_count = 0
        self.queue_sub = Queue()
        self.active_ip_dict = dict()
        self.segment_num = self.judge_speed(args.speed)
        self.found_count = 0
        self.add_ulimit()
        self.dict_ip_count = dict()


    def load_other_result_from_list(self):
        subdomain_list = list()
        for domain in self.other_result:
            if(('.'+str(self.target_domain)) in domain):
                self.queues.put(domain.strip())
                subdomain_list.append(domain.strip())
        return subdomain_list

    def load_other_result_from_file(self):
        subdomain_list = list()
        with open('{target_domain}.log'.format(target_domain=self.target_domain), 'r') as search_list:
            for domain in search_list:
                if (('.' + str(self.target_domain)) in domain):
                    self.queues.put(domain.strip().strip('\n').strip('\r\n'))
                    subdomain_list.append(domain.strip().strip('\n').strip('\r\n'))
        return subdomain_list

    def extract_next_sub(self, target_domain):
        if(os.path.exists('{target_domain}'.format(target_domain=self.other_result))):
            subdomain_list=self.load_other_result_from_file()
        elif(len(self.other_result)>0):
            subdomain_list=self.load_other_result_from_list()

            for subdoamin in subdomain_list:
                sub = subdoamin.strip(".{domain}".format(domain=target_domain))
                sub_num = sub.split(".")
                if (len(sub_num) != 1):
                    sub_num.remove(sub_num[-1])
                    for sub in sub_num:
                        self.set_next_sub.add(sub.strip())


    def load_next_sub(self):
        temp_set = set()
        with open('dict/next_sub_full.txt', 'r') as file_next_sub:
            for next_sub in file_next_sub:
                temp_set.add(next_sub)
        return temp_set

    def add_ulimit(self):
        if(platform.system() != "Windows"):
            os.system("ulimit -n 65535")

    def load_cdn(self):
        cdn_set = set()
        with open('dict/cdn_servers.txt', 'r') as file_cdn:
            for line in file_cdn:
                cdn_set.add(line.strip())
        return cdn_set

    def get_target_domain(self):
        file_name = args.file
        sets_domain = set()
        if file_name:
            with open(file_name, 'r') as file_domain:
                for line in file_domain:
                    sets_domain.add(line.strip())
        else:
            sets_domain.add(args.domain)
        return sets_domain

    def check_cdn(self, cname):
        for cdn in self.set_cdn:
            if(cdn in cname or 'cdn' in cname):
                return True
            self.cdn_set.add(cname)
        return False

    def get_type_id(self, name):
        return dns.rdatatype.from_text(name)

    def judge_speed(self, speed):
        if (speed == "low"):
            segment_num = config.low_segment_num
        elif (speed == "high"):
            segment_num = config.high_segment_num
        else:
            segment_num = config.medium_segment_num
        return segment_num

    def query_domain(self, domain):
        list_ip, list_cname = [], []
        try:
            record = self.resolver.query(domain)
            for A_CNAME in record.response.answer:
                for item in A_CNAME.items:
                    if item.rdtype == self.get_type_id('A'):
                        list_ip.append(str(item))
                        self.dict_ip[domain] = list_ip
                        self.dict_ip_block[domain]=list_ip
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

        except Exception as e:
            pass

    def get_subname(self):
        with open('dict/wydomain.csv', 'r') as file_sub:
            for sub in file_sub:
                domain = "{sub}.{target_domain}".format(
                    sub=sub.strip(), target_domain=self.target_domain)
                self.queues.put(domain)

    def get_block(self):
        domain_list = list()
        if (self.queues.qsize() > self.segment_num):
            for num in range(self.segment_num):
                domain_list.append(self.queues.get())
        else:
            for num in range(self.queues.qsize()):
                domain_list.append(self.queues.get())
        return domain_list

    def generate_sub(self):
        try:
            domain = self.queue_sub.get_nowait()
            for next_sub in self.set_next_sub:
                subdomain = "{next}.{domain}".format(
                    next=next_sub.strip(), domain=domain)
                self.queues.put_nowait(subdomain)
            return True
        except Exception:
            return False

    def set_dynamic_num(self):
        if(self.speed == "high"):
            return 350000
        elif(self.speed == "low"):
            return 150000
        else:
            return 250000

    def handle_data(self):
        temp_list = list()
        for subdomain, cname_list in self.dict_cname.items():
            for cname in cname_list:
                if(self.check_cdn(cname)):
                    self.dict_cname[subdomain] = "Yes"
                else:
                    self.dict_cname[subdomain] = "No"

        for subdomain, ip_list in self.dict_ip.items():
            ip_str = str(sorted(ip_list))
            if (self.dict_ip_count.__contains__(ip_str)):
                if(self.dict_ip_count[ip_str] > config.ip_max_count):
                    temp_list.append(subdomain)
                else:
                    self.dict_ip_count[ip_str] = self.dict_ip_count[ip_str] + 1
            else:
                self.dict_ip_count[ip_str] = 1

            for filter_ip in config.waiting_fliter_ip:
                if (filter_ip in ip_str):
                    temp_list.append(subdomain)


        subdomain_white=[]
        for subdomain1, ip_list1 in self.dict_ip.items():
            for subdomain2, ip_list2 in self.dict_ip.items():
                if not sys.version > '3':
                    if(((str('.')+subdomain1) in subdomain2) and cmp(ip_list1,ip_list2)):
                        subdomain_white.append(subdomain1)
                else:
                    if(((str('.')+subdomain1) in subdomain2) and ip_list1==ip_list2):
                        subdomain_white.append(subdomain1)
        subdomain_black=set()
        for subdomain1 in subdomain_white:
            i=0
            for subdomain3, ip_list1 in self.dict_ip.items():
                if(str('.')+subdomain1) in subdomain3:
                    subdomain_black.add(str(sorted(self.dict_ip[subdomain3])))
                    i=i+1
                    #print(subdomain_black)
                    if(i>5 and len(subdomain_black)==1):
                        temp_list.append(subdomain2)

        for subdomain in temp_list:
            try:
                del self.dict_ip[subdomain]
                del self.dict_cname[subdomain]
                del self.dict_ip_block[subdomain]
            except Exception:
                pass

        # self.found_count = self.found_count + self.dict_ip_block.__len__()
        self.found_count=self.dict_ip.__len__()

        for subdomain, ip_list in self.dict_ip_block .items():
            if (str(subdomain).count(".") < self.level):
                self.queue_sub.put(str(subdomain))
            for ip in ip_list:
                if (IP(ip).iptype() == 'PRIVATE'):
                    self.dict_ip[subdomain] = "private({ip})".format(ip=ip)
                else:
                    try:
                        key_yes = self.dict_cname[subdomain]
                    except KeyError:
                        key_yes = "No"
                    if (key_yes == "No"):
                        CIP = (IP(ip).make_net("255.255.255.0"))
                        if CIP in self.ip_flag:
                            self.ip_flag[CIP] = self.ip_flag[CIP] + 1
                        else:
                            self.ip_flag[CIP] = 1

                        if CIP in self.active_ip_dict:
                            active_ip_list = self.active_ip_dict[CIP]
                            if (ip not in active_ip_list):
                                active_ip_list.append(ip)
                                self.active_ip_dict[CIP] = active_ip_list
                        else:
                            active_ip_list = []
                            active_ip_list.append(ip)
                            self.active_ip_dict[CIP] = active_ip_list

    def raw_write_disk(self):
        self.flag_count = self.flag_count + 1
        if (not os.path.exists('result/{domain}'.format(domain=self.target_domain))):
            os.mkdir('result/{domain}'.format(domain=self.target_domain))
        with open('result/{name}/{name}.csv'.format(name=self.target_domain), 'w') as csvfile:
            writer = csv.writer(csvfile)
            if (self.flag_count == 1):
                writer.writerow(['domain', 'CDN', 'IP'])
                for subdomain, ip_list in self.dict_ip.items():
                    try:
                        flag = self.dict_cname[subdomain]
                    except BaseException:
                        flag = "No"
                    writer.writerow([subdomain, flag, ip_list])
            else:
                for subdomain, ip_list in self.dict_ip.items():
                    try:
                        flag = self.dict_cname[subdomain]
                    except BaseException:
                        flag = "No"
                    writer.writerow([subdomain, flag, ip_list])
        self.dict_ip_block.clear()



    def merge_subdomain(self):
        if (os.path.exists('{target_domain}.log'.format(
                target_domain=self.target_domain))):
            subdomain_list = self.load_other_result()
            temp_set = set()
            with open('./result/{result}/{result}.csv'.format(result=self.target_domain), 'a+') as csvfile:
                brute_result = csv.reader(csvfile)
                writer = csv.writer(csvfile)
                for each in brute_result:
                    if (each[0] != "domain"):
                        temp_set.add(each[0])
                for subdomain in subdomain_list:
                    if(subdomain not in temp_set):
                        writer.writerow([subdomain, '', ''])
            shutil.move('{target_domain}.log'.format(target_domain=self.target_domain),
                        './result/{result}/{result}.log'.format(result=self.target_domain))

    def deal_write_disk(self):
        if(not os.path.exists('result/{domain}'.format(domain=self.target_domain))):
            os.mkdir('result/{domain}'.format(domain=self.target_domain))
        ip_flags = sorted(
            self.ip_flag.items(),
            key=lambda d: d[1],
            reverse=True)
        with open('result/{name}/deal_{name}.csv'.format(name=self.target_domain), 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['IP', 'frequency', 'active'])
            for ip_frequency in ip_flags:
                writer.writerow([ip_frequency[0], ip_frequency[1],
                                 self.active_ip_dict[ip_frequency[0]]])

        self.merge_subdomain()

    def collect_cname(self):
        with open('result/cname.txt', 'a') as txt:
            for cname in self.cdn_set:
                txt.write('{cname}\r\n'.format(cname=cname))


    def cmd_print(self, wait_size, start, end, i):
        print("domain: {domain} |found: {found_count} number|speed:{velocity} number/s|waiting: {qsize} number|"
              .format(domain=self.target_domain,
                      qsize=wait_size,
                      found_count=self.found_count,
                      velocity=round(self.segment_num * i / (end - start), 2)))

    def run(self):
        start = time.time()
        print("*****************************Begin*******************************")
        i = 0
        while not self.queues.empty():
            i = i + 1
            domain_list = self.get_block()
            coroutines = [gevent.spawn(self.query_domain, l)
                          for l in domain_list]
            try:
                gevent.joinall(coroutines)
            except KeyboardInterrupt:
                print('user stop')
                sys.exit(1)
            # pool=gevent.pool.Pool(2000)
            # for l in domain_list:
            #     pool.spawn(self.query_domain,l)
            # pool.join()
            self.handle_data()
            self.cmd_print(self.queues.qsize(), start, time.time(), i)
            self.raw_write_disk()
            gc.collect()
            if (self.queues.qsize() < 30000):
                while (self.queues.qsize() < self.set_dynamic_num()):
                    if not self.generate_sub():
                        break
        self.deal_write_disk()
        print("*****************************Over********************************")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A new generation of tool for discovering subdomains( ip , cdn and so on),version=２.0')
    parser.add_argument('-s', '--speed', default="medium",
                        help='low,medium and high')
    parser.add_argument("-d", "--domain",
                        help="domain name,for example:baidu.com")
    parser.add_argument(
        "-l",
        "--level",
        default=2,
        type=int,
        help="example: 1,hello.baidu.com;2,hello.world.baidu.com")
    parser.add_argument("-f", "--file",
                        help="The list of domain")
    parser.add_argument("-c", "--cdn",
                        help="collect cnnames,y or n", default='n')
    parser.add_argument("-f1", "--sub_file",
                        help="sub dict", default='n')
    parser.add_argument("-f2", "--next_sub_file",
                        help="next_sub dict", default='n')
    parser.add_argument("-f3", "--other_file",
                        help="subdomain log", default='n')


    def banner():
        print("""
                          _         _                       _       ____  
                         | |       | |                     (_)     |___ \ 
                ___ _   _| |__   __| | ___  _ __ ___   __ _ _ _ __   __) |
               / __| | | | '_ \ / _` |/ _ \| '_ ` _ \ / _` | | '_ \ |__ < 
               \__ \ |_| | |_) | (_| | (_) | | | | | | (_| | | | | |___) |
               |___/\__,_|_.__/ \__,_|\___/|_| |_| |_|\__,_|_|_| |_|____/ 
                　 　Coded By yanxiu (V2.1 RELEASE) email:root@yanxiuer.com
                """)


    args = parser.parse_args()
    file_name = args.file
    sets_domain = set()
    if file_name:
        with open(file_name, 'r') as file_domain:
            for line in file_domain:
                sets_domain.add(line.strip())
    else:
        sets_domain.add(args.domain)
    banner()
    for domain in sets_domain:
        args.domain = domain
        brute = Brutedomain(args)
        try:
            brute.run()
            if ('y' in brute.cdn_flag or 'Y' in brute.cdn_flag):
                brute.collect_cname()
        except KeyboardInterrupt:
            print('user stop')

