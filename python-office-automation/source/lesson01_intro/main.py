# 第1课：Python 四个核心概念
# 运行：python main.py

# 1. 变量：给数据贴标签
employee_name = "张三"
salary = 8000

print("员工：", employee_name)
print("工资：", salary)

# 2. 列表：把一组数据放在一起
employees = ["张三", "李四", "王五", "赵六"]
print("员工名单：", employees)

# 3. 循环：对列表里的每个人做同一件事
for name in employees:
    print(f"给 {name} 发工资条")

# 4. 判断：根据条件做不同的事
sales = 12000
if sales > 10000:
    bonus = 1000
else:
    bonus = 500
print("奖金：", bonus)

# 组合练习：工资计算器
staff = [
    {"name": "张三", "role": "经理", "base": 8000},
    {"name": "李四", "role": "员工", "base": 6000},
    {"name": "王五", "role": "员工", "base": 5000},
]

for person in staff:
    if person["role"] == "经理":
        final_salary = person["base"] + 2000
    else:
        final_salary = person["base"] + 500
    print(f"{person['name']} 的最终工资：{final_salary} 元")
