# encoding: utf-8

#在爆破中，如果一个无效ip多次出现，可以将IP加入到下列表中，程序会在爆破中过滤。
waiting_fliter_ip = [
                    '222.221.5.253',
                    '222.221.5.252',
                    '1.1.1.1'
                    ]


#速度分为三种模式，可以根据以下配置进行调节

#high
high_coroutine_num= 2500   #协程数量（每个协程大约在4-5kb，过高会占用过大的内存和带宽）
high_segment_num = 20000  #程序采用逐量放到内存爆破，以减少内存占用。该设置会改变每次的读取量

#medium
medium_coroutine_num= 1500
medium_segment_num = 15000

#low
low_coroutine_num = 1000
low_segment_num = 10000

#设置一个ip出现的最多次数,后续出现将被丢弃
ip_max_count=5




