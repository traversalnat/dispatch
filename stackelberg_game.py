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

def distance(list1, list2):
    import numpy as np
    arr1 = np.array(list1)
    arr2 = np.array(list2)
    # 计算P2范数
    dist = np.linalg.norm(arr1 - arr2, 2)
    return dist

lambda_of_task = 10

# mec 速率 (任务数量/s)
mec_rate = 20

# 各 ES 节点的速率(任务数/s)
u_rate = [3, 2, 4, 5]

# 节点数量
M = len(u_rate) + 1

# 对应实际速率
freq = [mec_rate * lambda_of_task] + [i * lambda_of_task for i in u_rate]


# 任务数量
N = 15

# pij 对应任务 j 在 节点 i 上的速率
p = gen_p(freq, 10, N)


r0_es_edge = [0.3, 0.2, 0.6, 0.5]
EX_es_edge = [2, 2, 1, 3]
EX2_es_edge = [1, 0.5, 0.9, 1.2]

# 节点
edges = [mec(mec_rate, 0)]
for i in range(len(u_rate)):
    r0 = r0_es_edge[i]
    u = u_rate[i]
    EX = EX_es_edge[i]
    EX2 = EX2_es_edge[i]
    edges.append(es_edge(r0, u, EX, EX2, i + 1))

Q_MIN = 1
Q_MAX = 13

# 第一步， 得到一个初始策略

# MEC 随机策略
edges[0].q = random.randint(Q_MIN, Q_MAX)

# 目标 q 策略 (全局)
q_target = [0 for i in range(M)]
q_target[0] = edges[0].q


# 开始时 ES i 将 MEC q 视为其余节点的q
qarray = [edges[0].q for i in range(M)]

for i in range(1, M):
    edges[i].q = random.randint(Q_MIN, Q_MAX)
    bp, mr = participant(edges[i], p, qarray, M, N, Q_MIN, Q_MAX, reach_rate)
    # 更新策略
    q_target[edges[i].pos] = bp

# 初始策略
print(q_target)

# 得到初始策略 q_target后, 进行第二步博弈
# 策略 q'
q_temp = q_target.copy()

for _ in range(10):
    # MEC 更新策略
    bp, _ = participant(edges[0], p, qarray, M, N, Q_MIN, Q_MAX, reach_rate)
    # 更新策略
    q_temp[edges[0].pos] = bp
    #  q_next[0] = bp

    for i in range(1, M):
        # ES 更新策略并广播(追随者合作博弈)
        bp, rate = participant(edges[i], p, q_temp, M, N, Q_MIN, Q_MAX, reach_rate)
        q_temp[edges[i].pos] = bp

    if distance(q_temp, q_target) < 8:
        break
    q_target = q_temp.copy()
    print(q_target)

print(q_target)

result = resolve(p, q_target, M, N, 13)
result = [len(r) for r in result]
print(result)
