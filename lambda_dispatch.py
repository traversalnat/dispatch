from resolver import resolve

__author__ = "Zhihui Zhang"
__version__ = "1.0"
__email__ = "1726546320 [at] qq [dot] com"

# 3 edge server (include MEC)
prices = [3.2, 2.3]
# frequence，节点速率(Hz)
freq = [60, 20]
# task size,  任务大小(Hz) lambda 为 10 的指数分布
task_size = [8.31, 0.33, 14.97, 7.08, 7.69, 1.96, 2.13, 9.77, 18.12, 9.28]
# p_ij, 任务j在节点i上的运行速度
rates = []
for i in freq:
    price = []
    for j in task_size:
        if i == 0:
            price.append(0)
        else:
            price.append(j/i)
    rates.append(price)

# 任务数量
n_tasks = len(task_size)
# 节点数量
m_edge = len(freq)

# [qi, ] 常数
q = prices

# [[pij, ], ] 常数
p = rates

# 任务到达速率
reach_rate = 0.3

# 任务单位时间执行收益
R = 0.03
# 任务单位等待时间惩罚
C = 0.01

# 最大可接受价格, 也是循环次数
max_q = 13

def participant(pos, func, min_price):
    # 价格从min_price到max_q递增
    price = min_price
    # 各个价格下，整数规划的结果，{[xikj]}
    best_price = min_price
    max_profit = 0
    max_rate = 0
    while True:
        if price > max_q:
            break
        q[pos] = price
        result = resolve(p, q, m_edge, n_tasks, max_q)
        profit, valid = func(len(result[pos]), price)
        print(pos, ":", profit, " with price ",
              price, " and r ", len(result[pos]))
        if not valid:
            price = price + 1.0
            continue
        if profit > max_profit:
            max_profit = profit
            best_price = price
            max_rate = len(result[pos])
        price = price + 1.0
    return best_price, max_rate

# MEC 的效益函数


def mec_func(J, q) -> (float, bool):
    u = 6 # 每秒16个任务
    r = J * reach_rate # 实际到达速率
    if r >= u:
        return 0, False
    pp = r/u
    return r * (R/u - C * (pp / (u - r))), True

# ES 的效益函数
# float 表示效益函数值，bool 表示不满足约束


def es_func(J, q) -> (float, bool):
    EX2 = 1
    EX = 2
    u = 2
    r0 = 0.3
    r = J * reach_rate + r0
    # C1 约束
    if r * EX >= u:
        return 0, False

    # TODO C2 约束

    # 复合任务到达率 = r + 固定任务复合到达率

    pp = r * EX / u

    return r*(R+C)/u - C*((pp+r*EX2/u)/(2*(1-pp)*EX)), True

def es_func_low(J, q) -> (float, bool):
    EX2 = 1
    EX = 2
    u = 2
    r0 = 0.01
    r = J * reach_rate + r0
    # C1 约束
    if r * EX >= u:
        return 0, False

    # TODO C2 约束

    # 复合任务到达率 = r + 固定任务复合到达率

    pp = r * EX / u

    return r*(R+C)/u - C*((pp+r*EX2/u)/(2*(1-pp)*EX)), True


result = []
# MEC 首先给出价格
q[0] = 2.0
for i in range(10):
    # ES 根据 MEC 给出的价格计算得到自己的最优解
    es_best, es_rate = participant(1, es_func, 1.0)

    q[1] = es_best

    if len(result) >= 1:
        if q == result[-1]:
            break
    result.append(q.copy())

    # MEC 根据 ES 的回应重新计算自己的最优解
    mec_best, mec_rate = participant(0, mec_func, 2.0)

    q[0] = mec_best

    if q == result[-1]:
        break
    result.append(q.copy())

ret = resolve(p, q, m_edge, n_tasks, max_q)

for r in result:
    print(r)

print(ret)
