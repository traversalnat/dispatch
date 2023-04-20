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
    return result


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

def participant(pos, func):
    # MEC价格从1.0到12.0递增，查看MEC得到的任务数量和利润
    price_mec = 1.0
    # 各个价格下，整数规划的结果，{[xikj]}
    rets = {}
    # 各价格下，整数规划的最优解
    bests = {}
    for i in range(1, 10):
        q[pos] = price_mec
        price_mec = price_mec + 1.0
        result = resolve(p, q, m_edge, n_tasks, max_q)
        rets[q[pos]] = result

    best_price = 0
    max_profit = 0
    max_rate = 0
    for price in rets.keys():
        profit = func(price, len(rets[price][pos]))
        if profit > max_profit:
            max_profit = profit
            best_price = price
            max_rate = len(rets[price][pos])
    return best_price, max_rate

# MEC 的效益函数
def mec_func(r, q) -> float:
    u = 0.1 # 每秒0.1个任务
    C = 0.3 # 等待成本/s
    pp = r/u
    return r * (q/u - C * (pp / (u - r)))

# ES 的效益函数
def es_func(r, q) -> float:
    EX2 = 3 
    EX = 5
    u = 0.03
    # 复合任务到达率 = r + 固定任务复合到达率
    r = r + 3
    pp = r * EX / u
    C = 0.3
    return r * ((q - 1)/u) - C * ((pp + r*EX2/u) / (2 * (1-pp) * EX))

result = []
# MEC 首先给出价格
q[0] = 4.0
for i in range(10):
    # ES 根据 MEC 给出的价格计算得到自己的最优解
    es_best, es_rate = participant(1, es_func)

    q[1] = es_best

    if len(result) >= 1:
        if q == result[-1]:
            break
    result.append(q.copy())

    # MEC 根据 ES 的回应重新计算自己的最优解
    mec_best, mec_rate = participant(0, mec_func)

    q[0] = mec_best

    if q == result[-1]:
        break
    result.append(q.copy())

ret = resolve(p, q, m_edge, n_tasks, max_q)

for r in result:
    print(r)

print(ret)
