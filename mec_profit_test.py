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
prices = [3.2, 2.3, 2.5]
# frequence，节点速率(Hz)
freq = [300, 100, 200]
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

# MEC价格从1.0到12.0递增，查看MEC得到的任务数量和利润
price_mec = 1.0
# 各个价格下，整数规划的结果，{[xikj]}
rets = {}
# 各价格下，整数规划的最优解
bests = {}
for i in range(1, 12):
    q[0] = price_mec
    price_mec = price_mec + 1.0
    result, best = resolve(p, q, m_edge, n_tasks, max_q)
    rets[q[0]] = result
    bests[q[0]] = best

for price in rets.keys():
    for i in range(len(rets[price])):
        print(i, ":", rets[price][i])

    size = 0
    for i in rets[price][0]:
        size = size + p[0][i]

    print("best: ", bests[price])
    print("tasks size: ", size, end="\n")
    print("profit: ", size * price, end="\n\n")
