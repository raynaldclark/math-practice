# File: question_generator.py
# Version: 1.0-Flet
# Last Updated: 2026-03-27
# Changes: 适配 Flet 版本，从原 question_generator 重命名而来
# Status: COMPLETE

import random

# ============ 题型分类（三年级专用） ============
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

# ============ 题型规则说明 ============
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


# ============ 题目生成函数 ============
class QuestionGenerator:
    """数学题目生成器"""

    @staticmethod
    def gen_vert_addsub(count):
        q = []
        for _ in range(count):
            if random.choice([True, False]):
                a = random.randint(1000, 50000)
                b = random.randint(100, 99999 - a)
                q.append(f"{a} + {b} =")
            else:
                a = random.randint(5000, 99999)
                b = random.randint(100, a - 100)
                q.append(f"{a} - {b} =")
        return q

    @staticmethod
    def gen_vert_mul(count):
        q = []
        for _ in range(count):
            b = random.randint(2, 9)
            a = random.randint(100, 99999 // b)
            q.append(f"{a} × {b} =")
        return q

    @staticmethod
    def gen_vert_div(count):
        q = []
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
            q.append(f"{a} ÷ {b} =")
        return q

    @staticmethod
    def gen_mixed_all(count):
        q = []
        for _ in range(count):
            if random.choice([True, False]):
                a = random.randint(1000, 30000)
                b = random.randint(100, 10000)
                c = random.randint(100, 5000)
                result = a + b - c
                if 0 < result <= 99999:
                    q.append(f"{a} + {b} - {c} =")
                else:
                    q.append(f"{a} - {b} + {c} =")
            else:
                a = random.randint(100, 9999)
                b = random.randint(2, 9)
                c = random.randint(2, 9)
                result = a * b // c
                if 0 < result <= 99999:
                    q.append(f"{a} × {b} ÷ {c} =")
        return q

    @staticmethod
    def gen_mixed_bracket(count):
        """带括号混合运算 — 三年级水平：括号内≤99，乘数1位数，结果≤999"""
        q = []
        for _ in range(count):
            typ = random.randint(1, 3)
            if typ == 1:
                # (a ± b) × c，括号内 [40, 99]，c 为 1 位数
                c = random.randint(2, 9)
                ab = random.randint(40, min(99, 999 // c))  # 括号内 40~99
                b = random.randint(20, ab - 20)  # 括号结果 [20, ab-20]
                if random.choice([True, False]):
                    if ab + b <= 999 // c:
                        q.append(f"({ab} + {b}) × {c} =")
                    else:
                        q.append(f"({ab} - {b}) × {c} =")
                else:
                    q.append(f"({ab} - {b}) × {c} =")
            elif typ == 2:
                # (a - b) ÷ c，括号内≤99，c 为 1 位数，结果为整数
                while True:
                    c = random.randint(2, 9)
                    result = random.randint(2, 99)  # 商 ≤ 99
                    b = random.randint(1, 9)
                    a = result * c + b
                    if a <= 999 and b < result * c:
                        q.append(f"({a} - {b}) ÷ {c} =")
                        break
            else:
                # a × (b ± c)，括号内≥20，a 为 1 位数
                a = random.randint(2, 9)
                bc = random.randint(20, 999 // a)  # 括号内 ≥ 20
                if random.choice([True, False]):
                    # (bc - c)：bc - c ≥ 20
                    c = random.randint(1, bc - 20) if bc > 20 else 1
                    q.append(f"{a} × ({bc} - {c}) =")
                else:
                    # (bc + c)：bc + c ≤ 99
                    c_max = max(1, 99 - bc)
                    c = random.randint(1, min(c_max, 9))
                    q.append(f"{a} × ({bc} + {c}) =")
        return q

    @staticmethod
    def gen_solve_tri(count):
        """求未知数△ — 两步计算：先做×÷，再做±，△为2位数（10~99）"""
        q = []
        for _ in range(count):
            typ = random.randint(1, 5)

            if typ == 1:
                # (△ + a) × b = c  → 第一步：c ÷ b = △ + a，第二步：△ + a = 某数 → △
                a = random.randint(10, 30)
                tri = random.randint(10, 75)         # △ 在 [10, 75]
                b = random.randint(2, 9)
                bracket = tri + a                    # 括号内 [20, 105]
                c = bracket * b
                q.append(f"(△ + {a}) × {b} = {c}")

            elif typ == 2:
                # (a - △) × b = c  → 第一步：c ÷ b = a - △，第二步：a - △ = 某数 → △
                a = random.randint(50, 89)
                tri = random.randint(10, min(69, a - 20))
                b = random.randint(2, 9)
                bracket = a - tri                     # 括号内 [20, a-10]
                c = bracket * b
                q.append(f"({a} - △) × {b} = {c}")

            elif typ == 3:
                # a × (△ + b) = c  → 第一步：c ÷ a = △ + b，第二步：△ + b = 某数 → △
                a = random.randint(2, 9)
                b = random.randint(10, 30)
                tri = random.randint(10, 80)         # △ 在 [10, 80]
                bracket = tri + b                    # 括号内 [20, 110]
                c = a * bracket
                q.append(f"{a} × (△ + {b}) = {c}")

            elif typ == 4:
                # a × (b - △) = c  → 第一步：c ÷ a = b - △，第二步：b - △ = 某数 → △
                a = random.randint(2, 9)
                b = random.randint(30, 89)
                tri = random.randint(10, b - 20)     # b - △ ≥ 20
                bracket = b - tri                     # 括号内 [20, b-10]
                c = a * bracket
                q.append(f"{a} × ({b} - △) = {c}")

            else:
                # (△ + a) + b = c  → 第一步先算括号，第二步求 △
                a = random.randint(10, 40)
                tri = random.randint(10, 90)
                bracket = tri + a                     # [20, 130]
                b = random.randint(10, 199 - bracket)
                c = bracket + b
                q.append(f"(△ + {a}) + {b} = {c}")

        return q
        return q

    @staticmethod
    def gen_rmb_exchange(count):
        """人民币换算（来自 model.xlsx 模板）"""
        items = ["铅笔", "橡皮擦", "直尺", "三角尺", "圆规", "量角器", "彩笔",
                 "胶水", "剪刀", "笔记本", "书包", "转笔刀", "修正带", "笔袋", "故事书", "足球"]
        # 每个模板：(题目模板, {参数名: (最小, 最大)}, {额外参数名: [可选列表]})
        templates = [
            ("小明有{value}元硬币，相当于多少角？",
             {"value": (1, 99)}, {}),
            ("小红拿了{value}角钱去买{item}，相当于(   )元(   )角？",
             {"value": (1, 999)}, {"item": items}),
            # 找零 = 付出的元 - 单价×数量（需确保找零 >= 0）
            ("一个{item}{value}角，小明买了{value2}个，总共付了{value3}元，应该找回(   )元(   )角？",
             {"value": (1, 9), "value2": (1, 9), "value3": (11, 99)}, {"item": items}),
            ("一个{item}{value}元{value2}角，相当于多少角？",
             {"value": (1, 9), "value2": (1, 9)}, {"item": items}),
            ("一个{item}{value}元，小红付了{value2}元，应找回多少元？",
             {"value": (1, 59), "value2": (61, 999)}, {"item": items}),
            ("老师买了{value}元{value2}角的{item}，付了{value3}元，应找回多少元？",
             {"value": (1, 300), "value2": (1, 9), "value3": (11, 9999)}, {"item": items}),
            # 小明各买 value3 个，总价 = value1 + value2×10，付了 value3×10，找零
            ("一个笔记本{value1}元，一支铅笔{value2}角，小明各买{value3}个，一共要(   )元(   )角？",
             {"value1": (1, 99), "value2": (1, 9), "value3": (1, 10)}, {}),
            ("小红买{item}{value1}元{value2}角，买本子{value3}元{value4}角，一共要付多少元？",
             {"value1": (1, 199), "value2": (1, 9), "value3": (1, 299), "value4": (1, 9)}, {"item": items}),
            ("一个{item}{value}元，小明可以怎么付钱？",
             {"value": (1, 199)}, {"item": items}),
            ("一个{item}{value}元，小华要付多少张10元？",
             {"value": (1, 99)}, {"item": items}),
            ("小明的妈妈买了{value}元的蛋糕，付了100元，找回多少元？",
             {"value": (1, 69)}, {}),
            ("小芳有10元，买了{value}元{value2}角的贴纸，还剩(   )元(   )角？",
             {"value": (1, 9), "value2": (1, 9)}, {}),
            ("小明有{value}元，每本故事书{value2}元，最多可以买几本？",
             {"value": (50, 200), "value2": (3, 9)}, {}),
        ]
        q = []
        for _ in range(count):
            tpl, ranges, extras = random.choice(templates)
            vals = {k: random.randint(*v) for k, v in ranges.items()}
            vals.update({k: random.choice(v) for k, v in extras.items()})
            q.append(tpl.format(**vals))
        return q

    @staticmethod
    def gen_time_exchange(count):
        """时间换算（来自 model.xlsx 模板）"""
        templates = [
            ("{value}小时等于多少分钟？", {"value": (10, 50)}),
            ("{value}小时{value2}分钟等于(   )分钟？", {"value": (1, 20), "value2": (1, 59)}),
            ("小明早上{value}时{value2}分起床，洗漱用了{value3}分钟，他(   )时(   )分准备好？",
             {"value": (6, 9), "value2": (30, 59), "value3": (1, 20)}),
            ("小华{value}时{value2}分开始写作业，写了{value3}分钟，他(   )时(   )分写完？",
             {"value": (16, 19), "value2": (1, 59), "value3": (30, 180)}),
            ("图书馆{value}时开门，小红{value2}时{value3}分到，还要等多少分钟？",
             {"value": (9, 18), "value2": (8, 17), "value3": (1, 59)}),
            ("小华从家到学校走了{value}分钟，从学校到图书馆走了{value2}分钟，一共走了(   )小时(   )分钟？",
             {"value": (40, 120), "value2": (20, 120)}),
            ("第1节课8时开始，第{value}节课{value2}时{value3}分下课，课间休息10分钟，一节课多少分钟？",
             {"value": (3, 5), "value2": (8, 12), "value3": (30, 50)}),
            ("早上{value}时{value2}分上学，下午{value}时{value2}分放学，小明在学校待了(   )小时(   )分钟？",
             {"value": (7, 9), "value2": (20, 59)}),
        ]
        q = []
        for _ in range(count):
            tpl, ranges = random.choice(templates)
            vals = {k: random.randint(*v) for k, v in ranges.items()}
            # 处理特殊条件
            if "value3" in vals and "value" in vals and tpl.startswith("图书馆"):
                vals["value2"] = random.randint(max(8, vals["value"] - 2), vals["value"] - 1)
                vals["value3"] = random.randint(1, 59)
            q.append(tpl.format(**vals))
        return q

    @staticmethod
    def gen_length_exchange(count):
        """长度换算（来自 model.xlsx 模板）"""
        templates = [
            ("{value}米等于多少分米？", {"value": (1, 40)}),
            ("{value}分米等于多少厘米？", {"value": (10, 300)}),
            ("{value}厘米等于多少毫米？", {"value": (1, 40)}),
            ("{value}米{value2}分米等于多少分米？", {"value": (1, 20), "value2": (1, 9)}),
            ("小明的身高是{value}厘米，比小红高{value2}厘米，小红身高(   )米(   )厘米？",
             {"value": (140, 190), "value2": (15, 40)}),
            ("绳子长{value}米，用掉了{value2}厘米，还剩多少分米？", {"value": (2, 10), "value2": (50, 2000)}),
            ("{value}厘米和{value2}毫米相差多少？", {"value": (10, 100), "value2": (1, 999)}),
            ("小华跳远跳了{value}米{value2}厘米，小明跳了{value3}米{value4}厘米，谁跳得远？远多少？",
             {"value": (2, 4), "value2": (1, 99), "value3": (2, 4), "value4": (1, 99)}),
            ("一根绳子{value}米，第一次用掉{value2}分米，第二次用掉{value3}厘米，还剩多少厘米？",
             {"value": (3, 10), "value2": (5, 20), "value3": (40, 100)}),
        ]
        q = []
        for _ in range(count):
            tpl, ranges = random.choice(templates)
            vals = {k: random.randint(*v) for k, v in ranges.items()}
            q.append(tpl.format(**vals))
        return q

    @staticmethod
    def gen_weight_exchange(count):
        """质量换算（来自 model.xlsx 模板）"""
        templates = [
            ("{value}千克等于多少克？", {"value": (1, 20)}),
            ("{value}克等于多少千克？", {"value": (1000, 20000)}),
            ("{value}千克{value2}克等于多少克？", {"value": (1, 10), "value2": (1, 999)}),
            ("一袋大米重{value}千克{value2}克，一袋面粉重{value3}千克{value4}克，一共多少千克？",
             {"value": (1, 5), "value2": (1, 999), "value3": (1, 5), "value4": (1, 999)}),
            ("一个西瓜重{value}千克，吃掉一半后还剩多少克？", {"value": (4, 10)}),
            ("一箱牛奶重{value}千克，拿出{value2}袋后，剩下的牛奶重{value3}千克，每袋牛奶多少克？",
             {"value": (4, 20), "value2": (1, 10), "value3": (2, 18)}),
            ("一袋面粉{value}千克，做馒头用了{value2}克，还剩多少克？",
             {"value": (2, 10), "value2": (50, 2000)}),
            ("一筐苹果{value}千克，拿走一半后，剩下的苹果连筐一起重{value2}克，筐重多少克？",
             {"value": (5, 20), "value2": (100, 18000)}),
        ]
        q = []
        for _ in range(count):
            tpl, ranges = random.choice(templates)
            vals = {k: random.randint(*v) for k, v in ranges.items()}
            # 克转千克时 value 是克的整数倍
            if tpl.startswith("{value}克等于") and "千克" in tpl:
                vals["value"] = (vals["value"] // 1000) * 1000
                vals["value"] = max(1000, vals["value"])
            q.append(tpl.format(**vals))
        return q

    @staticmethod
    def gen_perimeter(count):
        q = []
        for _ in range(count):
            l = random.randint(10, 99)
            w = random.randint(10, 99)
            q.append(f"长方形长{l}cm，宽{w}cm，周长是（  ）cm")
        return q

    @staticmethod
    def gen_area(count):
        q = []
        for _ in range(count):
            l = random.randint(5, 30)
            w = random.randint(5, 30)
            q.append(f"长方形长{l}m，宽{w}m，面积是（  ）平方米")
        return q

    @staticmethod
    def gen_area_unit(count):
        q = []
        for _ in range(count):
            sqm = random.randint(1, 50)
            q.append(f"{sqm}平方米 = （  ）平方分米")
        return q

    @staticmethod
    def gen_pattern(count):
        q = []
        for _ in range(count):
            typ = random.randint(1, 4)
            if typ == 1:
                start = random.randint(1, 20)
                diff = random.randint(2, 5)
                nums = [start + i * diff for i in range(4)]
                q.append(f"{nums[0]}, {nums[1]}, {nums[2]}, ________")
            elif typ == 2:
                a = random.randint(2, 5)
                nums = [a, a*2, a*3, a*4]
                q.append(f"{nums[0]}, {nums[1]}, {nums[2]}, ________")
            elif typ == 3:
                a = random.randint(1, 3)
                b = random.randint(1, 3)
                q.append(f"{a}, {b}, {a}, {b}, ________")
            else:
                n = random.randint(1, 10)
                nums = [n, n+2, n+4, n+6]
                q.append(f"{nums[0]}, {nums[1]}, {nums[2]}, ________")
        return q

    @staticmethod
    def gen_times(count):
        """倍的认识 - 求一个数的几倍是多少，或求一个数是另一个数的几倍"""
        q = []
        for _ in range(count):
            typ = random.randint(1, 3)
            if typ == 1:
                a = random.randint(2, 9)
                b = random.randint(2, 9)
                q.append(f"{a}的{b}倍是（  ）")
            elif typ == 2:
                a = random.randint(2, 9) * random.randint(2, 9)
                b = random.randint(2, 9)
                q.append(f"{a}是{b}的（  ）倍")
            else:
                a = random.randint(1, 9)
                b = a * random.randint(2, 5)
                names = [("小明", "小红"), ("爸爸", "儿子"), ("哥哥", "弟弟"), ("小红", "小丽")]
                name1, name2 = random.choice(names)
                q.append(f"{name1}有{a}本书，{name2}有{b}本书，{name2}的书的数量是{name1}的（  ）倍")
        return q

    @staticmethod
    def gen_decimal(count):
        q = []
        for _ in range(count):
            a = round(random.randint(1, 100) + random.random(), 1)
            b = round(random.randint(1, 50) + random.random(), 1)
            if a + b < 200:
                q.append(f"{a} + {b} =")
            else:
                a, b = max(a, b), min(a, b)
                q.append(f"{a} - {b} =")
        return q

    @staticmethod
    def gen_direction(count):
        dirs = {"东": "西", "南": "北", "西": "东", "北": "南"}
        q = []
        for _ in range(count):
            if random.choice([True, False]):
                d = random.choice(list(dirs.keys()))
                q.append(f"{d}的相反方向是（  ）")
            else:
                q.append("地图上通常上面是（  ），右面是（  ）")
        return q


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
    """根据选择的题型生成题目数据

    Args:
        selected: List of (type_key, count) tuples

    Returns:
        List of (section_name, questions, qtype) tuples
    """
    questions_data = []
    for type_key, count in selected:
        generator = GENERATORS[type_key]
        questions = generator(count)

        type_name = type_key
        qtype = type_key
        for cat_name, cat_types in QUESTION_CATEGORIES.items():
            for t in cat_types:
                if t[1] == type_key:
                    type_name = t[0]
                    qtype = type_key
                    break
                if t[0] == type_key:
                    # Chinese name was passed as key (reverse lookup)
                    type_name = t[0]
                    qtype = t[1]
                    break
            else:
                continue
            break

        questions_data.append((type_name, questions, qtype))
    return questions_data
