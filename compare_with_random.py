# 与随机算法比较，整数规划算法的优势

from resolver import resolve
from dataGen import genSample
import random
from edge import edge, es_edge, mec, participant
from sum_Cj import *

import matplotlib.pyplot as plt
import numpy as np

__author__ = "Zhihui Zhang"
__version__ = "1.0"
__email__ = "1726546320 [at] qq [dot] com"

# 协同空间任务到达速率
reach_rate = 0.3
# 最大可接受价格, 也是循环次数
max_q = 13

freq = [60, 20]

q = [2.0, 6.0]

# 生成 p

def gen_p(freq, r, num):
    # task size,  任务大小(Hz) lambda 为 10 的指数分布
    task_size = genSample(r, num)
    # p_ij, 任务j在节点i上的运行速度
    rates = []
    for i in freq:
        price_rate = []
        for j in task_size:
            if i == 0:
                price_rate.append(0)
            else:
                price_rate.append(round(j/i, 2))
        rates.append(price_rate)
    return rates

sums_rand = []
sums_ret = []

for _ in range(100):
    p = gen_p(freq, 10, 10)
    a = [i for i in range(10)]
    rand = get_random_split(a)
    ret = resolve(p, q, 2, 10, 13)
    sum_ret_Cj = sum_Cj_for(p, q, ret)
    sum_rand_Cj = sum_Cj_for(p, q, rand)
    sums_rand.append(sum_rand_Cj)
    sums_ret.append(sum_ret_Cj)


fig, ax = plt.subplots()
ax.plot(range(100), sums_ret, label='Random')
ax.plot(range(100), sums_rand, label='RP')

ax.set_xlabel('X Label')
ax.set_ylabel('Sum of Cj')
ax.legend()

plt.show()
