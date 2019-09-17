#encoding=utf8
from brutedns import Brutedomain


class cmd_args:
    def __init__(self):
        self.domain=''
        self.speed=''
        self.level=''
        self.cname = 'n'
        self.sub_dict=''
        self.next_sub_dict =''
        self.default_dns = ''
        self.other_result=''


def brute_subdomain_api(domain, speed, level,default_dns,sub_dict,next_sub_dict,other_file):
    cmd_args.domain = domain
    cmd_args.speed = speed
    cmd_args.level = level
    cmd_args.sub_file = sub_dict
    cmd_args.default_dns= default_dns
    cmd_args.next_sub_file = next_sub_dict
    cmd_args.other_file = other_file
    cmd_args.cdn=1
    brute = Brutedomain(cmd_args)
    brute.run()
    return brute.found_count
