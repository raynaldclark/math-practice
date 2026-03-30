# File: question_generator.py
# Version: 2.0
# Last Updated: 2026-03-30
# Changes: 每个生成函数返回 (questions, answers) 元组，支持答案生成
# Status: COMPLETE

import random
import re

QUESTION_CATEGORIES = {
    "竖式计算": [
        ("竖式加减法", "vert_addsub"),
        ("竖式乘法", "vert_mul"),
        ("竖式除法", "vert_div"),
    ],
    "混合运算": [
        ("加减乘除混合", "mixed_all"),
        ("带括号混合运算", "mixed_bracket"),
        ("求未知数△", "solve_tri"),
    ],
    "单位换算": [
        ("人民币换算", "rmb_exchange"),
        ("时间换算", "time_exchange"),
        ("长度换算", "length_exchange"),
        ("质量换算", "weight_exchange"),
    ],
    "图形与测量": [
        ("周长计算", "perimeter"),
        ("面积计算", "area"),
        ("面积单位换算", "area_unit"),
    ],
    "概念题": [
        ("找规律填数", "pattern"),
        ("倍的认识", "times"),
        ("小数加减法", "decimal"),
        ("方向与位置", "direction"),
    ],
}

QUESTION_RULES = {
    "vert_addsub": "竖式计算，最多五位数的加减法，计算结果不超过五位数",
    "vert_mul": "竖式计算，最多五位数乘一位数，乘积不超过五位数",
    "vert_div": "竖式计算，最多五位数除以一位数，含整除与非整除",
    "mixed_all": "加减乘除混合运算，最大到五位数",
    "mixed_bracket": "含括号优先级的四则混合运算",
    "solve_tri": "混合运算，求未知数△",
    "rmb_exchange": "元、角、分的换算及加减计算",
    "time_exchange": "小时、分钟、秒的换算及加减计算",
    "length_exchange": "米、分米、厘米、毫米的换算及加减计算",
    "weight_exchange": "千克、克的换算及加减计算",
    "perimeter": "长方形周长计算，周长=(长+宽)×2",
    "area": "长方形面积计算，面积=长×宽",
    "area_unit": "平方米与平方分米的换算",
    "pattern": "找规律填数，如等差数列、倍数关系等",
    "times": "倍的认识：求一个数的几倍是多少（乘法），求一个数是另一个数的几倍（除法）",
    "decimal": "一位小数加减法，如 3.5 + 2.1",
    "direction": "东南西北方向的认知与相反方向",
}


class QuestionGenerator:
    @staticmethod
    def gen_vert_addsub(count):
        questions, answers = [], []
        for _ in range(count):
            if random.choice([True, False]):
                a = random.randint(1000, 50000)
                b = random.randint(100, 99999 - a)
                questions.append(f"{a} + {b} =")
                answers.append(str(a + b))
            else:
                a = random.randint(5000, 99999)
                b = random.randint(100, a - 100)
                questions.append(f"{a} - {b} =")
                answers.append(str(a - b))
        return questions, answers

    @staticmethod
    def gen_vert_mul(count):
        questions, answers = [], []
        for _ in range(count):
            b = random.randint(2, 9)
            a = random.randint(100, 99999 // b)
            questions.append(f"{a} × {b} =")
            answers.append(str(a * b))
        return questions, answers

    @staticmethod
    def gen_vert_div(count):
        questions, answers = [], []
        used_divisors = []
        for _ in range(count):
            available = [d for d in range(2, 10) if d not in used_divisors]
            if not available:
                used_divisors = []
                available = list(range(2, 10))
            b = random.choice(available)
            used_divisors.append(b)

            digits = random.randint(3, 5)
            if digits == 3:
                a = random.randint(100, 999)
            elif digits == 4:
                a = random.randint(1000, 9999)
            else:
                a = random.randint(10000, 99999)
            q = f"{a} ÷ {b} ="
            quotient = a // b
            remainder = a % b
            if remainder == 0:
                ans = str(quotient)
            else:
                ans = f"{quotient}···{remainder}"
            questions.append(q)
            answers.append(ans)
        return questions, answers

    @staticmethod
    def gen_mixed_all(count):
        questions, answers = [], []
        for _ in range(count):
            if random.choice([True, False]):
                a = random.randint(1000, 30000)
                b = random.randint(100, 10000)
                c = random.randint(100, 5000)
                result = a + b - c
                if 0 < result <= 99999:
                    questions.append(f"{a} + {b} - {c} =")
                    answers.append(str(result))
                else:
                    questions.append(f"{a} - {b} + {c} =")
                    answers.append(str(a - b + c))
            else:
                a = random.randint(100, 9999)
                b = random.randint(2, 9)
                c = random.randint(2, 9)
                result = a * b // c
                if 0 < result <= 99999:
                    questions.append(f"{a} × {b} ÷ {c} =")
                    answers.append(str(result))
        return questions, answers

    @staticmethod
    def gen_mixed_bracket(count):
        questions, answers = [], []
        for _ in range(count):
            typ = random.randint(1, 3)
            if typ == 1:
                c = random.randint(2, 9)
                ab = random.randint(40, min(99, 999 // c))
                b = random.randint(20, ab - 20)
                if random.choice([True, False]):
                    if ab + b <= 999 // c:
                        questions.append(f"({ab} + {b}) × {c} =")
                        answers.append(str((ab + b) * c))
                    else:
                        questions.append(f"({ab} - {b}) × {c} =")
                        answers.append(str((ab - b) * c))
                else:
                    questions.append(f"({ab} - {b}) × {c} =")
                    answers.append(str((ab - b) * c))
            elif typ == 2:
                while True:
                    c = random.randint(2, 9)
                    result = random.randint(2, 99)
                    b = random.randint(1, 9)
                    a = result * c + b
                    if a <= 999 and b < result * c:
                        questions.append(f"({a} - {b}) ÷ {c} =")
                        answers.append(str(result))
                        break
            else:
                a = random.randint(2, 9)
                bc = random.randint(20, 999 // a)
                if random.choice([True, False]):
                    c = random.randint(1, bc - 20) if bc > 20 else 1
                    questions.append(f"{a} × ({bc} - {c}) =")
                    answers.append(str(a * (bc - c)))
                else:
                    c_max = max(1, 99 - bc)
                    c = random.randint(1, min(c_max, 9))
                    questions.append(f"{a} × ({bc} + {c}) =")
                    answers.append(str(a * (bc + c)))
        return questions, answers

    @staticmethod
    def gen_solve_tri(count):
        questions, answers = [], []
        for _ in range(count):
            typ = random.randint(1, 5)

            if typ == 1:
                a = random.randint(10, 30)
                tri = random.randint(10, 75)
                b = random.randint(2, 9)
                bracket = tri + a
                c = bracket * b
                questions.append(f"(△ + {a}) × {b} = {c}")
                answers.append(str(tri))

            elif typ == 2:
                a = random.randint(50, 89)
                tri = random.randint(10, min(69, a - 20))
                b = random.randint(2, 9)
                bracket = a - tri
                c = bracket * b
                questions.append(f"({a} - △) × {b} = {c}")
                answers.append(str(tri))

            elif typ == 3:
                a = random.randint(2, 9)
                b = random.randint(10, 30)
                tri = random.randint(10, 80)
                bracket = tri + b
                c = a * bracket
                questions.append(f"{a} × (△ + {b}) = {c}")
                answers.append(str(tri))

            elif typ == 4:
                a = random.randint(2, 9)
                b = random.randint(30, 89)
                tri = random.randint(10, b - 20)
                bracket = b - tri
                c = a * bracket
                questions.append(f"{a} × ({b} - △) = {c}")
                answers.append(str(tri))

            else:
                a = random.randint(10, 40)
                tri = random.randint(10, 90)
                bracket = tri + a
                b = random.randint(10, 199 - bracket)
                c = bracket + b
                questions.append(f"(△ + {a}) + {b} = {c}")
                answers.append(str(tri))

        return questions, answers

    @staticmethod
    def gen_rmb_exchange(count):
        items = [
            "铅笔",
            "橡皮擦",
            "直尺",
            "三角尺",
            "圆规",
            "量角器",
            "彩笔",
            "胶水",
            "剪刀",
            "笔记本",
            "书包",
            "转笔刀",
            "修正带",
            "笔袋",
            "故事书",
            "足球",
        ]
        templates = [
            (
                "小明有{value}元硬币，相当于多少角？",
                {"value": (1, 99)},
                {},
                lambda v: str(v * 10),
            ),
            (
                "小红拿了{value}角钱去买{item}，相当于(   )元(   )角？",
                {"value": (1, 999)},
                {"item": items},
                lambda v: f"{v // 10}元{v % 10}角",
            ),
            (
                "一个{item}{value}角，小明买了{value2}个，总共付了{value3}元，应该找回(   )元(   )角？",
                {"value": (1, 9), "value2": (1, 9), "value3": (11, 99)},
                {"item": items},
                lambda v, v2, v3: (
                    f"{(v3 * 10 - v * v2) // 10}元{(v3 * 10 - v * v2) % 10}角"
                ),
            ),
            (
                "一个{item}{value}元{value2}角，相当于多少角？",
                {"value": (1, 9), "value2": (1, 9)},
                {"item": items},
                lambda v, v2: str(v * 10 + v2),
            ),
            (
                "一个{item}{value}元，小红付了{value2}元，应找回多少元？",
                {"value": (1, 59), "value2": (61, 999)},
                {"item": items},
                lambda v, v2: str(v2 - v),
            ),
            (
                "老师买了{value}元{value2}角的{item}，付了{value3}元，应找回多少元？",
                {"value": (1, 300), "value2": (1, 9), "value3": (11, 9999)},
                {"item": items},
                lambda v, v2, v3: str(v3 - v),
            ),
            (
                "一个笔记本{value1}元，一支铅笔{value2}角，小明各买{value3}个，一共要(   )元(   )角？",
                {"value1": (1, 99), "value2": (1, 9), "value3": (1, 10)},
                {},
                lambda v1, v2, v3: f"{v1 * v3}元{v2 * v3}角",
            ),
            (
                "小红买{item}{value1}元{value2}角，买本子{value3}元{value4}角，一共要付多少元？",
                {
                    "value1": (1, 199),
                    "value2": (1, 9),
                    "value3": (1, 299),
                    "value4": (1, 9),
                },
                {"item": items},
                lambda v1, v2, v3, v4: f"{v1 + v3}元{v2 + v4}角",
            ),
            (
                "一个{item}{value}元，小华要付多少张10元？",
                {"value": (1, 99)},
                {"item": items},
                lambda v: str((v + 9) // 10),
            ),
            (
                "小明的妈妈买了{value}元的蛋糕，付了100元，找回多少元？",
                {"value": (1, 69)},
                {},
                lambda v: str(100 - v),
            ),
            (
                "小芳有10元，买了{value}元{value2}角的贴纸，还剩(   )元(   )角？",
                {"value": (1, 9), "value2": (1, 9)},
                {},
                lambda v, v2: (
                    f"{10 - v}元{10 - v2}角"
                    if v <= 9 and v2 <= 9
                    else f"{9 - v}元{10 - v2}角"
                ),
            ),
            (
                "小明有{value}元，每本故事书{value2}元，最多可以买几本？",
                {"value": (50, 200), "value2": (3, 9)},
                {},
                lambda v, v2: str(v // v2),
            ),
        ]
        questions, answers = [], []
        for _ in range(count):
            tpl, ranges, extras, answer_func = random.choice(templates)
            vals = {k: random.randint(*v) for k, v in ranges.items()}
            vals.update({k: random.choice(v) for k, v in extras.items()})
            questions.append(tpl.format(**vals))
            answer_keys = list(ranges.keys())
            if answer_keys == ["value"]:
                answers.append(answer_func(vals["value"]))
            elif answer_keys == ["value", "value2"]:
                answers.append(answer_func(vals["value"], vals["value2"]))
            elif answer_keys == ["value", "value2", "value3"]:
                answers.append(
                    answer_func(vals["value"], vals["value2"], vals["value3"])
                )
            elif answer_keys == ["value1", "value2", "value3"]:
                answers.append(
                    answer_func(vals["value1"], vals["value2"], vals["value3"])
                )
            elif answer_keys == ["value1", "value2", "value3", "value4"]:
                answers.append(
                    answer_func(
                        vals["value1"], vals["value2"], vals["value3"], vals["value4"]
                    )
                )
        return questions, answers

    @staticmethod
    def gen_time_exchange(count):
        templates = [
            (
                "{value}小时等于多少分钟？",
                {"value": (10, 50)},
                {},
                lambda v: str(v * 60),
            ),
            (
                "{value}小时{value2}分钟等于(   )分钟？",
                {"value": (1, 20), "value2": (1, 59)},
                {},
                lambda v, v2: str(v * 60 + v2),
            ),
            (
                "小明早上{value}时{value2}分起床，洗漱用了{value3}分钟，他(   )时(   )分准备好？",
                {"value": (6, 9), "value2": (30, 59), "value3": (1, 20)},
                {},
                lambda v, v2, v3: (
                    f"{v}时{v2 + v3}分"
                    if v2 + v3 < 60
                    else f"{v + 1}时{v2 + v3 - 60}分"
                ),
            ),
            (
                "小华{value}时{value2}分开始写作业，写了{value3}分钟，他(   )时(   )分写完？",
                {"value": (16, 19), "value2": (1, 59), "value3": (30, 180)},
                {},
                lambda v, v2, v3: f"{v + (v2 + v3) // 60}时{(v2 + v3) % 60}分",
            ),
            (
                "图书馆{value}时开门，小红{value2}时{value3}分到，还要等多少分钟？",
                {"value": (9, 18), "value2": (8, 17), "value3": (1, 59)},
                {},
                lambda v, v2, v3: str((v - v2) * 60 - v3),
            ),
            (
                "小华从家到学校走了{value}分钟，从学校到图书馆走了{value2}分钟，一共走了(   )小时(   )分钟？",
                {"value": (40, 120), "value2": (20, 120)},
                {},
                lambda v, v2: f"{(v + v2) // 60}小时{(v + v2) % 60}分",
            ),
            (
                "第1节课8时开始，第{value}节课{value2}时{value3}分下课，课间休息10分钟，一节课多少分钟？",
                {"value": (3, 5), "value2": (8, 12), "value3": (30, 50)},
                {},
                lambda v, v2, v3: str((v2 - 8) * 60 + v3 - (v - 1) * 10),
            ),
            (
                "早上{value}时{value2}分上学，下午{value}时{value2}分放学，小明在学校待了(   )小时(   )分钟？",
                {"value": (7, 9), "value2": (20, 59)},
                {},
                lambda v, v2: f"{12 - v}小时{v2 - v2}分",
            ),
        ]
        questions, answers = [], []
        for _ in range(count):
            tpl, ranges, extras, answer_func = random.choice(templates)
            vals = {k: random.randint(*v) for k, v in ranges.items()}
            questions.append(tpl.format(**vals))
            answer_keys = list(ranges.keys())
            if answer_keys == ["value"]:
                answers.append(answer_func(vals["value"]))
            elif answer_keys == ["value", "value2"]:
                answers.append(answer_func(vals["value"], vals["value2"]))
            elif answer_keys == ["value", "value2", "value3"]:
                answers.append(
                    answer_func(vals["value"], vals["value2"], vals["value3"])
                )
        return questions, answers

    @staticmethod
    def gen_length_exchange(count):
        templates = [
            ("{value}米等于多少分米？", {"value": (1, 40)}, {}, lambda v: str(v * 10)),
            (
                "{value}分米等于多少厘米？",
                {"value": (10, 300)},
                {},
                lambda v: str(v * 10),
            ),
            (
                "{value}厘米等于多少毫米？",
                {"value": (1, 40)},
                {},
                lambda v: str(v * 10),
            ),
            (
                "{value}米{value2}分米等于多少分米？",
                {"value": (1, 20), "value2": (1, 9)},
                {},
                lambda v, v2: str(v * 10 + v2),
            ),
            (
                "小明的身高是{value}厘米，比小红高{value2}厘米，小红身高(   )米(   )厘米？",
                {"value": (140, 190), "value2": (15, 40)},
                {},
                lambda v, v2: f"{(v - v2) // 100}米{(v - v2) % 100}厘米",
            ),
            (
                "绳子长{value}米，用掉了{value2}厘米，还剩多少分米？",
                {"value": (2, 10), "value2": (50, 2000)},
                {},
                lambda v, v2: str(v * 10 - v2 // 10),
            ),
            (
                "{value}厘米和{value2}毫米相差多少？",
                {"value": (10, 100), "value2": (1, 999)},
                {},
                lambda v, v2: str(abs(v * 10 - v2)),
            ),
            (
                "小华跳远跳了{value}米{value2}厘米，小明跳了{value3}米{value4}厘米，谁跳得远？远多少？",
                {
                    "value": (2, 4),
                    "value2": (1, 99),
                    "value3": (2, 4),
                    "value4": (1, 99),
                },
                {},
                lambda v, v2, v3, v4: (
                    f"小华{abs(v * 100 + v2 - v3 * 100 - v4)}厘米"
                    if v * 100 + v2 > v3 * 100 + v4
                    else f"小明{abs(v * 100 + v2 - v3 * 100 - v4)}厘米"
                ),
            ),
            (
                "一根绳子{value}米，第一次用掉{value2}分米，第二次用掉{value3}厘米，还剩多少厘米？",
                {"value": (3, 10), "value2": (5, 20), "value3": (40, 100)},
                {},
                lambda v, v2, v3: str(v * 100 - v2 * 10 - v3),
            ),
        ]
        questions, answers = [], []
        for _ in range(count):
            tpl, ranges, extras, answer_func = random.choice(templates)
            vals = {k: random.randint(*v) for k, v in ranges.items()}
            questions.append(tpl.format(**vals))
            answer_keys = list(ranges.keys())
            if answer_keys == ["value"]:
                answers.append(answer_func(vals["value"]))
            elif answer_keys == ["value", "value2"]:
                answers.append(answer_func(vals["value"], vals["value2"]))
            elif answer_keys == ["value", "value2", "value3"]:
                answers.append(
                    answer_func(vals["value"], vals["value2"], vals["value3"])
                )
            elif answer_keys == ["value", "value2", "value3", "value4"]:
                answers.append(
                    answer_func(
                        vals["value"], vals["value2"], vals["value3"], vals["value4"]
                    )
                )
        return questions, answers

    @staticmethod
    def gen_weight_exchange(count):
        templates = [
            (
                "{value}千克等于多少克？",
                {"value": (1, 20)},
                {},
                lambda v: str(v * 1000),
            ),
            (
                "{value}克等于多少千克？",
                {"value": (1000, 20000)},
                {},
                lambda v: f"{v // 1000}千克{v % 1000}克",
            ),
            (
                "{value}千克{value2}克等于多少克？",
                {"value": (1, 10), "value2": (1, 999)},
                {},
                lambda v, v2: str(v * 1000 + v2),
            ),
            (
                "一袋大米重{value}千克{value2}克，一袋面粉重{value3}千克{value4}克，一共多少千克？",
                {
                    "value": (1, 5),
                    "value2": (1, 999),
                    "value3": (1, 5),
                    "value4": (1, 999),
                },
                {},
                lambda v, v2, v3, v4: f"{(v * 1000 + v2 + v3 * 1000 + v4) / 1000}千克",
            ),
            (
                "一个西瓜重{value}千克，吃掉一半后还剩多少克？",
                {"value": (4, 10)},
                {},
                lambda v: str(int(v * 1000 / 2)),
            ),
            (
                "一箱牛奶重{value}千克，拿出{value2}袋后，剩下的牛奶重{value3}千克，每袋牛奶多少克？",
                {"value": (4, 20), "value2": (1, 10), "value3": (2, 18)},
                {},
                lambda v, v2, v3: str(int((v * 1000 - v3 * 1000) / v2)),
            ),
            (
                "一袋面粉{value}千克，做馒头用了{value2}克，还剩多少克？",
                {"value": (2, 10), "value2": (50, 2000)},
                {},
                lambda v, v2: str(v * 1000 - v2),
            ),
            (
                "一筐苹果{value}千克，拿走一半后，剩下的苹果连筐一起重{value2}克，筐重多少克？",
                {"value": (5, 20), "value2": (100, 18000)},
                {},
                lambda v, v2: str(int(v2 - v * 1000 / 2)),
            ),
        ]
        questions, answers = [], []
        for _ in range(count):
            tpl, ranges, extras, answer_func = random.choice(templates)
            vals = {k: random.randint(*v) for k, v in ranges.items()}
            if tpl.startswith("{value}克等于") and "千克" in tpl:
                vals["value"] = (vals["value"] // 1000) * 1000
                vals["value"] = max(1000, vals["value"])
            questions.append(tpl.format(**vals))
            answer_keys = list(ranges.keys())
            if answer_keys == ["value"]:
                answers.append(answer_func(vals["value"]))
            elif answer_keys == ["value", "value2"]:
                answers.append(answer_func(vals["value"], vals["value2"]))
            elif answer_keys == ["value", "value2", "value3"]:
                answers.append(
                    answer_func(vals["value"], vals["value2"], vals["value3"])
                )
            elif answer_keys == ["value", "value2", "value3", "value4"]:
                answers.append(
                    answer_func(
                        vals["value"], vals["value2"], vals["value3"], vals["value4"]
                    )
                )
        return questions, answers

    @staticmethod
    def gen_perimeter(count):
        questions, answers = [], []
        for _ in range(count):
            l = random.randint(10, 99)
            w = random.randint(10, 99)
            perimeter = 2 * (l + w)
            questions.append(f"长方形长{l}cm，宽{w}cm，周长是（  ）cm")
            answers.append(str(perimeter))
        return questions, answers

    @staticmethod
    def gen_area(count):
        questions, answers = [], []
        for _ in range(count):
            l = random.randint(5, 30)
            w = random.randint(5, 30)
            area = l * w
            questions.append(f"长方形长{l}m，宽{w}m，面积是（  ）平方米")
            answers.append(str(area))
        return questions, answers

    @staticmethod
    def gen_area_unit(count):
        questions, answers = [], []
        for _ in range(count):
            sqm = random.randint(1, 50)
            questions.append(f"{sqm}平方米 = （  ）平方分米")
            answers.append(str(sqm * 100))
        return questions, answers

    @staticmethod
    def gen_pattern(count):
        questions, answers = [], []
        for _ in range(count):
            typ = random.randint(1, 4)
            if typ == 1:
                start = random.randint(1, 20)
                diff = random.randint(2, 5)
                nums = [start + i * diff for i in range(4)]
                next_num = start + 4 * diff
                questions.append(f"{nums[0]}, {nums[1]}, {nums[2]}, ________")
                answers.append(str(next_num))
            elif typ == 2:
                a = random.randint(2, 5)
                nums = [a, a * 2, a * 3, a * 4]
                next_num = a * 5
                questions.append(f"{nums[0]}, {nums[1]}, {nums[2]}, ________")
                answers.append(str(next_num))
            elif typ == 3:
                a = random.randint(1, 3)
                b = random.randint(1, 3)
                nums = [a, b, a, b]
                next_num = a if len(nums) % 2 == 0 else b
                questions.append(f"{nums[0]}, {nums[1]}, {nums[2]}, ________")
                answers.append(str(a))
            else:
                n = random.randint(1, 10)
                nums = [n, n + 2, n + 4, n + 6]
                next_num = n + 8
                questions.append(f"{nums[0]}, {nums[1]}, {nums[2]}, ________")
                answers.append(str(next_num))
        return questions, answers

    @staticmethod
    def gen_times(count):
        questions, answers = [], []
        for _ in range(count):
            typ = random.randint(1, 3)
            if typ == 1:
                a = random.randint(2, 9)
                b = random.randint(2, 9)
                questions.append(f"{a}的{b}倍是（  ）")
                answers.append(str(a * b))
            elif typ == 2:
                a = random.randint(2, 9) * random.randint(2, 9)
                b = random.randint(2, 9)
                questions.append(f"{a}是{b}的（  ）倍")
                answers.append(str(a // b))
            else:
                a = random.randint(1, 9)
                b = a * random.randint(2, 5)
                names = [
                    ("小明", "小红"),
                    ("爸爸", "儿子"),
                    ("哥哥", "弟弟"),
                    ("小红", "小丽"),
                ]
                name1, name2 = random.choice(names)
                questions.append(
                    f"{name1}有{a}本书，{name2}有{b}本书，{name2}的书的数量是{name1}的（  ）倍"
                )
                answers.append(str(b // a))
        return questions, answers

    @staticmethod
    def gen_decimal(count):
        questions, answers = [], []
        for _ in range(count):
            a = round(random.randint(1, 100) + random.random(), 1)
            b = round(random.randint(1, 50) + random.random(), 1)
            if a + b < 200:
                questions.append(f"{a} + {b} =")
                answers.append(str(round(a + b, 1)))
            else:
                a, b = max(a, b), min(a, b)
                questions.append(f"{a} - {b} =")
                answers.append(str(round(a - b, 1)))
        return questions, answers

    @staticmethod
    def gen_direction(count):
        dirs = {"东": "西", "南": "北", "西": "东", "北": "南"}
        questions, answers = [], []
        for _ in range(count):
            if random.choice([True, False]):
                d = random.choice(list(dirs.keys()))
                questions.append(f"{d}的相反方向是（  ）")
                answers.append(dirs[d])
            else:
                questions.append("地图上通常上面是（  ），右面是（  ）")
                answers.append("北，东")
        return questions, answers


GENERATORS = {
    "vert_addsub": QuestionGenerator.gen_vert_addsub,
    "vert_mul": QuestionGenerator.gen_vert_mul,
    "vert_div": QuestionGenerator.gen_vert_div,
    "mixed_all": QuestionGenerator.gen_mixed_all,
    "mixed_bracket": QuestionGenerator.gen_mixed_bracket,
    "solve_tri": QuestionGenerator.gen_solve_tri,
    "rmb_exchange": QuestionGenerator.gen_rmb_exchange,
    "time_exchange": QuestionGenerator.gen_time_exchange,
    "length_exchange": QuestionGenerator.gen_length_exchange,
    "weight_exchange": QuestionGenerator.gen_weight_exchange,
    "perimeter": QuestionGenerator.gen_perimeter,
    "area": QuestionGenerator.gen_area,
    "area_unit": QuestionGenerator.gen_area_unit,
    "pattern": QuestionGenerator.gen_pattern,
    "times": QuestionGenerator.gen_times,
    "decimal": QuestionGenerator.gen_decimal,
    "direction": QuestionGenerator.gen_direction,
}


def get_questions_data(selected):
    """根据选择的题型生成题目和答案数据

    Args:
        selected: List of (type_key, count) tuples

    Returns:
        List of (section_name, questions, answers, qtype) tuples
    """
    questions_data = []
    for type_key, count in selected:
        generator = GENERATORS[type_key]
        questions, answers = generator(count)

        type_name = type_key
        qtype = type_key
        for cat_name, cat_types in QUESTION_CATEGORIES.items():
            for t in cat_types:
                if t[1] == type_key:
                    type_name = t[0]
                    qtype = t[1]
                    break
                if t[0] == type_key:
                    type_name = t[0]
                    qtype = t[1]
                    break
            else:
                continue
            break

        questions_data.append((type_name, questions, answers, qtype))
    return questions_data
