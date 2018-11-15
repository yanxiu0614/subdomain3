# encoding: utf-8

# 在爆破中，如果一个无效ip多次出现，可以将IP加入到下列表中，程序会在爆破中过滤。
waiting_fliter_ip = [
    '222.221.5.253',
    '222.221.5.252',
    '1.1.1.1'
]


# 速度分为三种模式，可以根据以下配置进行调节

# high
high_segment_num = 10000  # 程序采用逐量放到内存爆破，以减少内存占用。该设置会改变每次的读取量

# medium
medium_segment_num = 5000

# low
low_segment_num = 2000

# 设置一个ip出现的最多次数,后续出现将被丢弃
ip_max_count = 30
