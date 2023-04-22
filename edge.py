from resolver import resolve

# 任务单位时间执行收益
R = 0.03
# 任务单位等待时间惩罚
C = 0.01

class edge:
    # 报价
    q = 0
    def profit(self, J, q) -> (float, bool):
        0.0, False


class es_edge(edge):
    r0 = 0.3
    # 期望
    EX = 2
    # 方差
    EX2 = 1
    # 服务速率
    u = 2
    # 节点位置(p和q array 中)
    pos = 0

    def __init__(self, r0, u, EX, EX2, pos):
        self.r0 = r0
        self.u = u
        self.EX = EX
        self.EX2 = EX2
        self.pos = pos

    # ES 的效益函数
    # float 表示效益函数值，bool 表示不满足约束
    # rate 计算任务到达率
    def profit(self, rate, q) -> (float, bool):
        r0 = self.r0
        EX = self.EX
        EX2 = self.EX2
        u = self.u

        r = rate + r0
        # C1 约束
        if r * EX >= u:
            return 0, False

        # TODO C2 约束

        pp = r * EX / u

        return r*(R+C)/u - C*((pp+r*EX2/u)/(2*(1-pp)*EX)), True


class mec(edge):
    # 服务速率
    u = 2

    # 节点位置(p和q array 中)
    pos = 0

    def __init__(self, u, pos):
        self.u = u
        self.pos = pos

    # rate 计算任务到达率
    def profit(self, rate, q) -> (float, bool):
        u = self.u
        r = rate # 实际到达速率
        if r >= u:
            return 0, False
        pp = r/u
        return r * (R/u - C * (pp / (u - r))), True


def participant(edge, p, q, m_edge, n_tasks, min_price, max_price, reach_rate):
    pos = edge.pos
    # 价格从min_price到max_price递增
    price = min_price
    # 各个价格下，整数规划的结果，{[xikj]}
    best_price = min_price
    max_profit = 0
    max_rate = 0
    while True:
        if price > max_price:
            break
        q[pos] = price
        result = resolve(p, q, m_edge, n_tasks, max_price)
        profit, valid = edge.profit(len(result[pos]) * reach_rate, price)
        #  print(pos, ":", profit, " with price ",
        #        price, " and r ", len(result[pos]))
        if not valid:
            price = price + 1.0
            continue
        if profit >= max_profit:
            max_profit = profit
            best_price = price
            max_rate = len(result[pos])
        price = price + 1.0
    return best_price, max_rate
