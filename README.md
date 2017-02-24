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
                            example: 1,hello.baidu.com;2,hello.world.baidu.com


example:pyrhon3 brutedns.py -d target -l 1/2 -s low/medium/high

screenshot(the speed of high)：

![](screenshot.png)

----------------------------------------------------------------------------------------
change log:

2017-2-24: mac support