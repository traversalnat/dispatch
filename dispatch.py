# 模拟到达 N 个任务时的任务调度
from resolver import resolve
from dataGen import genSample
import random
from edge import edge, es_edge, mec, participant

__author__ = "Zhihui Zhang"
__version__ = "1.0"
__email__ = "1726546320 [at] qq [dot] com"

# 协同空间任务到达速率
reach_rate = 0.3
# 最大可接受价格, 也是循环次数
max_q = 13

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

# frequence，节点速率(Hz)
freq = [60, 20]
# r 分别为8, 2
q = [2.0, 3.0]

ret = [[], []]
for _ in range(100):
    p = gen_p(freq, 10, 10)
    result = resolve(p, q, 2, 10, 13)
    ret[0].append(len(result[0]))
    ret[1].append(len(result[1]))

print(ret[0])
print(ret[1])



