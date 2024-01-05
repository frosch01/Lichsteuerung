import timeit

def compare_runtimes(num, cmd_list):
    for setup, cmd in cmd_list:
        print(f"{setup}; {cmd}")
        print(timeit.repeat(cmd, setup, number=num))

compare_runtimes(1000000, [
    ("l=[11,22,33,44,55,66,77,88]; m=dict(zip(l, range(len(l))))", "[m[i] for i in l]"),
    ("l=[11,22,33,44,55,66,77,88]", "[l.index(i) for i in l]"),
])
