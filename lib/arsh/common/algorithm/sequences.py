# -*- coding: utf-8 -*-

def unique(seq, id_func=None):
    u""" عناصر تکراری لیست داده شده را حذف می‌کند و در قالب یک لیست جدید بازمی‌گرداند

        see: http://www.peterbe.com/plog/uniqifiers-benchmark
    """
    if id_func is None:
        def id_func(x): return x.id
    seen = {}
    result = []
    for item in seq:
        marker = id_func(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


def merge(list1, list2):
    u""" ادغام شده‌ی دو لیست مرتب را بازمی‌گرداند
    """
    answer = []
    left_size = len(list1)
    right_size = len(list2)
    left_ptr = 0
    right_ptr = 0
    while left_ptr < left_size or right_ptr < right_size:
        if left_ptr < left_size and right_ptr < right_size:
            if list1[left_ptr] < list2[right_ptr]:
                answer.append(list1[left_ptr])
                left_ptr += 1
            else:
                answer.append(list2[right_ptr])
                right_ptr += 1
        elif left_ptr < left_size:
            answer.append(list1[left_ptr])
            left_ptr += 1
        elif right_ptr < right_size:
            answer.append(list2[right_ptr])
            right_ptr += 1
    return answer


def generate_permutations(l):
    u""" تمام جایگشت‌های اعضای لیست داده شده را بازمی‌گرداند

        :type l: list
        :return: تمام جایگشت‌های لیست داده شده (خود هر جایگشت یک لیست است)
    """
    if len(l) <= 1:
        yield l
    else:
        a = [l.pop(0)]
        for p in generate_permutations(l):
            for i in range(len(p) + 1):
                yield p[:i] + a + p[i:]
