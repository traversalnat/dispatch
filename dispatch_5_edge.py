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
freq = [200, 30, 20, 40, 50]
# r 分别为8 1 1 3 2
q = [2.0, 2.0, 13.0, 1, 4.0]

# 节点速率变化
freq = [200, 30, 70, 40, 30]
# r 分别为 [6, 2, 4, 2, 1]
q = [3.0, 1, 1, 1, 13.0]


# 预期 [8, 1, 1, 3, 2]

M = len(freq)
N = 15

ret = [[] for i in range(M)]
for _ in range(100):
    p = gen_p(freq, 10, N)
    result = resolve(p, q, M, N, 13)
    for i in range(M):
        ret[i].append(len(result[i]))

for i in range(M):
    print(ret[i])

