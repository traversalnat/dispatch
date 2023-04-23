import random

def get_random_split(arr):
    split_length = random.randint(4, 7)
    list1 = random.sample(arr, split_length)
    list2 = list(set(arr) - set(list1))
    return [list1, list2]

def sum_Cj_for(p, q, dst):
    sum_Cj = 0
    for i in range(len(dst)):
        max_k = len(dst[i])
        for k, j in enumerate(dst[i]):
            sum_Cj += p[i][j] * (k + 1) * q[i]
    return sum_Cj
