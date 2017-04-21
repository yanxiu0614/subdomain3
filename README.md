# subdomain3
description：a simple and fast tool for bruting subdomains

author:yanxiu

blog:https://www.yanxiuer.com

Python：python3.5+

three patterns for speed：

      low：around 350 number/s
      
      medium：around 450 number/s
      
      high：around 700 number/s 
      
usage:

      -h, --help            show this help message and exit
      -s SPEED, --speed SPEED
                            low,medium and high
      -d DOMAIN, --domain DOMAIN
                            domain name,for example:baidu.com
      -l LEVEL, --level LEVEL
                            example: 1,baidu.com;2,world.baidu.com;3,hello.world.baidu.com
      -f FILE,  --file FILE
                            The list of domain
      -p PARSE  --parse PARSE
                            universal parsing,t or f


example:pyrhon3 brutedns.py -d target -l 1/2 -s low/medium/high

screenshot(the speed of medium)：

![](screenshot.png)

----------------------------------------------------------------------------------------
change log:

2017-4-21：optimze strategy for generating subname，improve the speed

2017-3-23: add universal parse opthon(-p t/f)

2017-3-17: big dict support(for example:200 million)

2017-3-10: read several domains from file support(-f domains);update cdn-servers

2017-2-26: multilevel domain support(no upper limit);big dict support;take up about a third to a quarter as much memory; faster

2017-2-24: mac support
