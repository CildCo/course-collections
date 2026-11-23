# 第3课：循环、函数与类
# 运行：python main.py


class Employee:
    """员工类：姓名、部门、薪资。"""

    def __init__(self, name, department, salary):
        self.name = name
        self.department = department
        self.salary = salary

    def work(self):
        return f"{self.name} 正在 {self.department} 工作"

    def get_raise(self, amount):
        self.salary += amount
        return f"{self.name} 涨薪了，当前工资：{self.salary}"

    def calc_tax(self, rate=0.1):
        return self.salary * rate


def calculate_bonus(base_salary, performance_score, rate=0.2):
    """按绩效计算奖金。"""
    if performance_score >= 90:
        return base_salary * rate
    if performance_score >= 60:
        return base_salary * (rate / 2)
    return 0


def send_email(to_user, subject="请假申请", content="我想请假"):
    """模拟发送邮件。"""
    print(f"发送给：{to_user}")
    print(f"主题：{subject}")
    print(f"内容：{content}")


def loop_demo():
    """遍历员工名单并模拟发工资条。"""
    staff = ["张三", "李四", "王五", "赵六"]
    for person in staff:
        print(f"亲爱的 {person}，您的工资条已发送，请查收！")


def raise_demo():
    """根据工资高低执行不同涨幅。"""
    salaries = [4000, 6000, 4500, 8000, 3000]
    new_salaries = []
    for money in salaries:
        if money < 5000:
            new_salaries.append(money * 1.2)
        else:
            new_salaries.append(money * 1.05)
    print("原工资：", salaries)
    print("新工资：", new_salaries)


def payroll_demo():
    """批量计算税后工资。"""
    staff = [
        Employee("刘备", "销售部", 10000),
        Employee("关羽", "技术部", 12000),
        Employee("张飞", "技术部", 9000),
    ]

    print("开始结算本月工资")
    for person in staff:
        tax = person.calc_tax()
        real_pay = person.salary - tax
        print(f"姓名：{person.name} 税前：{person.salary} 扣税：{tax} 实发：{real_pay}")
    print("结算完成")


if __name__ == "__main__":
    print("=" * 30)
    loop_demo()

    print("\n" + "=" * 30)
    raise_demo()

    print("\n" + "=" * 30)
    zhang = Employee("张三", "销售部", 5000)
    li = Employee("李四", "技术部", 8000)
    print(zhang.work())
    print(li.get_raise(1000))
    print(f"张三的工资还是：{zhang.salary}")

    print("\n" + "=" * 30)
    print("张三的奖金：", calculate_bonus(5000, 95))
    print("李四的奖金：", calculate_bonus(6000, 55))
    send_email("hr@example.com")

    print("\n" + "=" * 30)
    payroll_demo()
