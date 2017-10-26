# Subdomain3

![version](https://img.shields.io/badge/version-2.0-green.svg) ![stars](https://img.shields.io/github/stars/yanxiu0614/subdomain3.svg) ![forks](https://img.shields.io/github/forks/yanxiu0614/subdomain3.svg)  ![language](https://img.shields.io/badge/language-python2%2B-green.svg) ![language](https://img.shields.io/badge/language-python3%2B-green.svg)

**README.md in [English](https://github.com/yanxiu0614/subdomain3/blob/master/README.md)**

## 描述
Subdomain3是新一代子域名爆破工具,它帮助渗透测试者相比与其他工具更快发现更多的信息,这些信息包括子域名,IP,CDN信息等,开始使用它吧!

## 截图
medium 模式下的截图:

![](screenshot.png)

## 特性
* 更快

三种速度模式. 用户也可以修改配置文件(/lib/config.py) 来获得更高的速度.
* CDN识别支持

可以判定域名是否使用了CDN.
* 标准C段支持

可以对未使用CDN的域名IP进行分类.
* 多级域名支持

可以发现多级域名,无限制.
* 大字典支持

可以支持百万级字典
* 更少的资源占用

1个CPU/1GB内存/1Mbps带宽 即可获得很高速度

## 开始

```
git clone https://github.com/yanxiu0614/subdomain3.git

pip install -r requirement.txt

python2/3 brutedns.py -d tagetdomain -s high -l 5
```
## 使用方法

Short Form    | Long Form     | Description
------------- | ------------- |-------------
-d            | --domain      | 目标域名,例如: baidu.com
-s            | --speed  | 速度模式,三种速度模式:fast,medium,low
-l            | --level       | 例子: 2:baidu.com; 3:world.baidu.com;
-f            | --file        | 使用文件,每行一个子域名


## 致谢:

- <a href="https://github.com/smarttang" target="view_window">smarttang(Tangyucong)</a>
- <a href="https://security.yirendai.com/" target="view_window">宜人贷安全部</a>


## 日志:

- 2017-10-26:优化过程;修复BUG

- 2017-10-11:重构了部分代码;支持API调用;结果更加易读;更新了CDN厂商;修改了扫描算法,更快速;删除了验证域名脚本;

- 2017-6-17: 删除了泛解析选项(-p t/f);添加了配置文件;优化了泛解析策略;

- 2017-5-2: 添加了域名验证选项;修复了泛解析bug;更新了CDN列表等;

- 2017-4-21: 优化了子域名的爆破策略;提升了速度;

- 2017-3-23: 添加了泛解析选项(-p t/f)

- 2017-3-17: 大字典支持.支持百万级;

- 2017-3-10: 添加了文件中域名爆破的支持;更新了CDN厂商;

- 2017-2-26: 多级域名支持,没有级数上限;较大字典支持;内存占用为原来四分之一;更快;

- 2017-2-24: 支持mac os等


&copy;<a href="https://github.com/sixtant" target="_blank">Sixtant Security Lab</a> 2016-2017
