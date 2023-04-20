import gurobipy as grb
from gurobipy import *
import re

__author__ = "Zhihui Zhang"
__version__ = "1.0"
__email__ = "1726546320 [at] qq [dot] com"

def resolve(p, q, m_edge, n_tasks, max_q, show=False):
    # Create a new model
    model = Model()

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
            model.addConstr(quicksum(x[i, k, j] * q[i] for j in range(n_tasks)) <= max_q)

    model.setObjective(quicksum(k * q[i] * p[i][j] * x[i, k, j]
        for k in range(n_tasks)
        for j in range(n_tasks)
        for i in range(m_edge)
        ), GRB.MINIMIZE)

    model.update()

    if show:
        model.Params.LogToConsole=True # 显示求解过程

    model.Params.MIPGap=0.0001 # 百分比界差
    model.Params.TimeLimit=100 # 限制求解时间为 100s
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
    best = 0
    for (i,r) in enumerate(result):
        for j in r:
            best = best + p[i][j] * q[i]
    return result, best


# 3 edge server (include MEC)
prices = [3.2, 2.3]
# frequence，节点速率(Hz)
freq = [300, 100]
# task size,  任务大小(Hz)
task_size = [10000, 8000, 7200, 6900, 2100, 3212, 3242, 8981, 98128]
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

# 最大可接受价格
max_q = 10

def participant(pos):
    # MEC价格从1.0到12.0递增，查看MEC得到的任务数量和利润
    price_mec = 1.0
    # 各个价格下，整数规划的结果，{[xikj]}
    rets = {}
    # 各价格下，整数规划的最优解
    bests = {}
    for i in range(1, 10):
        q[pos] = price_mec
        price_mec = price_mec + 1.0
        result, best = resolve(p, q, m_edge, n_tasks, max_q)
        rets[q[pos]] = result
        bests[q[pos]] = best

    best_price = 1.0
    best_profit = 0
    for price in rets.keys():
        size = 0
        for i in rets[price][pos]:
            size = size + p[pos][i]
        profit = size * price
        if profit > best_profit:
            best_price = price
            best_profit = profit
    return best_price, bests[best_price]

result = []
# MEC 首先给出价格
q[0] = 4.0
# 全局收益
best_global_profit = 0
for i in range(10):
    # ES 根据 MEC 给出的价格计算得到自己的最优解
    es_best, global_profit1 = participant(1)
    best_global_profit = max(best_global_profit, global_profit1)
    # 停止条件，在一定次数循环过后，如果全局收益低于之前的最大收益，那么结束循环
    if i > 8 and global_profit1 < best_global_profit:
        break
    q[1] = es_best

    result.append([q[0], q[1]])

    # MEC 根据 ES 的回应重新计算自己的最优解
    mec_best, global_profit2 = participant(0)
    best_global_profit = max(best_global_profit, global_profit2)
    # 停止条件，在一定次数循环过后，如果全局收益低于之前的最大收益，那么结束循环
    if i > 8 and global_profit2 < best_global_profit:
        break
    q[0] = mec_best

    result.append([q[0], q[1]])

ret, best = resolve(p, q, m_edge, n_tasks, max_q)

print("best_global_profit", best_global_profit)
print(q)
for r in result:
    print(r)
print(ret)
