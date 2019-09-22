# Subdomain3

![version](https://img.shields.io/badge/version-3.0-green.svg) ![stars](https://img.shields.io/github/stars/yanxiu0614/subdomain3.svg) ![forks](https://img.shields.io/github/forks/yanxiu0614/subdomain3.svg)  ![language](https://img.shields.io/badge/language-python2%2B-green.svg) ![language](https://img.shields.io/badge/language-python3%2B-green.svg)

**README.md in [Chinese 中文](https://github.com/yanxiu0614/subdomain3/blob/master/README_ZH.md)**


## Description
Subdomain3 is a new generation of tool , It helps penetration testers to discover more information  in a shorter time than other tools.The  information includes subdomains, IP, CDN, and so on. Please enjoy it.

## Screenshot
medium pattern for speed

![](screenshot.png)

## Features

* More quick

Three patterns for speed. User can modify the configuration(lib/config.py) file to speed-up.
* CDN support

Determines whether the subdomain  uses CDN storage automatically,even though the dict of CDN severs not contain the cname suffix.
* RFC CIDR

Sorting ip and report CIDR(example 1.1.1.1/24) that it not use CDN storage;
* Multi-level subdomain support

Discover more subdomains,example:admin.test.xx.com
* Big dict support

Million of subs support
* Less resource consumption

1 CPU/1GB Memory/1Mbps bandwidth
* More intelligent

Discover the fastest nameserver;The strategy of dynamically adjusting of dict by importing subdomains from other sources;Prevent dns cache pollution;


## Getting started

```
git clone https://github.com/yanxiu0614/subdomain3.git

pip install -r requirement.txt

python2/3 brutedns.py -d tagetdomain -s high -l 5
```
## Usage

Short Form    | Long Form      | Description
------------- | -------------  |-------------
-d            | --domain       | target domain,for example: baidu.com
-s            | --speed        | speed,three patterns:fast,medium,low
-l            | --level        | example: 2:w.baidu.com; 3:w.w.baidu.com;
-f            | --file         | The list of target domain
-c            | --cname        | n or y,collect cnames
-ns           | --default_dns  | n or y
-f1           | --sub_file     | sub dict
-f2           | --next_sub_file| next sub dict
-f3           | --other_file   | subdomain log from search engine

## Thanks:

- <a href="https://github.com/smarttang" target="view_window">smarttang(Tangyucong)</a>
- <a href="https://security.yirendai.com/" target="view_window">Yirendai security department</a>


## Changelog:
- 2019-09-22: New strategy to prevent dns cache pollution;Optimize the  processes,Fixed bug e.g

- 2019-09-17: Automatically discover the fastest nameserver support;Determines whether the subdomain  uses CDN storage automatically support;Improve the speed;Optimize the  processes,Fix bug e.g

- 2018-11-6: Improve the speed;Optimize the  processes;

- 2018-10-6: Api support,import brutedns_api and you will get the number of results in the end;Optimized the deduplication strategy;

- 2018-2-14: Fix issue(TypeError: argument of type 'NoneType' is not iterable)

- 2018-1-9: CDN PLAN;Add opthon oc collecting cname (-c --cdn  t/f)

- 2017-11-11: Import subdomains from other sources support（You should create a new file of target_domain.log, and put it with 'brutedns.py' in the same directory），it will improve the accuracy；it is more convenient for use API；

- 2017-10-26: Optimize the  processes;Fix bug;

- 2017-10-11:Rebuild part of the program; Api support; Result is more readable;Update cdn-severs；faster

- 2017-6-17: Delete universal parse opthon(-p t/f);Add a file of config;Optimze strategy for universal parse

- 2017-5-2: Add a module(validate the domain),please modify "result_name" in the validate_domain.py if you will use it;fix universal bug;update cdn-servers,etc

- 2017-4-21: Optimze strategy for generating subname，Improve the speed

- 2017-3-23: Add universal parse opthon(-p t/f)

- 2017-3-17: Big dict support(for example: two million)

- 2017-3-10: Read several domains from file support(-f domains) support;Update cdn-servers

- 2017-2-26: Multilevel domain support(no upper limit);Big dict support;Take up about a third to a quarter as much memory;Faster

- 2017-2-24: Mac support




&copy;<a href="https://github.com/monsterzer0" target="_blank">Monster Zero Team</a>  2019
