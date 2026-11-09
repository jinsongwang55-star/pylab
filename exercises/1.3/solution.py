"""1.3 参考答案：闭包计数器与安全的列表追加。"""


def make_counter(start: int = 0):
    count = start

    def counter():
        nonlocal count
        value = count
        count += 1
        return value

    return counter


def append_item(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
