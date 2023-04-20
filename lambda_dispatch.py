import gurobipy as grb
from gurobipy import *
import re

__author__ = "Zhihui Zhang"
__version__ = "1.0"
__email__ = "1726546320 [at] qq [dot] com"


def resolve(p, q, m_edge, n_tasks, max_q, show=False):
    # Create a new model
    model = Model()
    model.setParam("OutputFlag", 0)

    x = model.addVars(m_edge, n_tasks, n_tasks, vtype=GRB.BINARY, name="X_ikj")
    model.update()

    # C1约束 (每一个任务被分配且只分配一次)
    for j in range(n_tasks):
        model.addConstr(quicksum(x[i, k, j]
                                 for i in range(m_edge)
                                 for k in range(n_tasks)) == 1)
    model.update()
    # C2 约束 (n 个任务，m 个节点中有 n*m 个位置，每一个位置只能有一个任务)
    for i in range(m_edge):
        for k in range(n_tasks):
            model.addConstr(quicksum(x[i, k, j] for j in range(n_tasks)) <= 1)

    # C3 约束 (单位价格超过一定值时，不考虑)
    for i in range(m_edge):
        for k in range(n_tasks):
            model.addConstr(quicksum(x[i, k, j] * q[i]
                                     for j in range(n_tasks)) <= max_q)

    model.setObjective(quicksum(k * q[i] * p[i][j] * x[i, k, j]
                                for k in range(n_tasks)
                                for j in range(n_tasks)
                                for i in range(m_edge)
                                ), GRB.MINIMIZE)

    model.update()

    if show:
        model.Params.LogToConsole = True  # 显示求解过程

    model.Params.MIPGap = 0.0001  # 百分比界差
    model.Params.TimeLimit = 100  # 限制求解时间为 100s
    model.optimize()
    result = [[] for i in range(m_edge)]
    regex = re.compile(r"\[.*\]")
    for v in model.getVars():
        line = f"{v.varName}：{round(v.x,3)}"
        if "0.0" not in line:
            arr = v.varName
            arr = regex.search(arr).group()
            i, k, j = arr[1:-1].split(',')
            result[int(i)].append(int(j))
    return result


# 3 edge server (include MEC)
prices = [3.2, 2.3]
# frequence，节点速率(Hz)
freq = [160, 80]
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


def mec_func(r, q) -> (float, bool):
    #  return r * q, True
    u = 16  # 每秒16个任务
    C = 0.3  # 等待成本/s
    if r >= u:
        return 0, False
    pp = r/u
    return r * (1/u - C * (pp / (u - r))), True

# ES 的效益函数
# float 表示效益函数值，bool 表示不满足约束


def es_func(r, q) -> (float, bool):
    #  return r * q, True
    EX2 = 1
    EX = 2
    C = 0.3
    u = 8
    r0 = 2
    r = r + r0
    # C1 约束
    if r * EX >= u:
        return 0, False

    # TODO C2 约束

    # 复合任务到达率 = r + 固定任务复合到达率

    pp = r * EX / u

    return r*(1+C)/u - C*((pp+r*EX2/u)/(2*(1-pp)*EX)), True


result = []
# MEC 首先给出价格
q[0] = 2.0
for i in range(10):
    # ES 根据 MEC 给出的价格计算得到自己的最优解
    es_best, es_rate = participant(1, es_func, 1.0)

    q[1] = es_best

    #  if len(result) >= 1:
    #      if q == result[-1]:
    #          break
    result.append(q.copy())

    # MEC 根据 ES 的回应重新计算自己的最优解
    mec_best, mec_rate = participant(0, mec_func, 2.0)

    q[0] = mec_best

    #  if q == result[-1]:
    #      break
    result.append(q.copy())

ret = resolve(p, q, m_edge, n_tasks, max_q)

for r in result:
    print(r)

print(ret)
