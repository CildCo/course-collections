# 第2课：列表与字典
# 运行：python main.py


def list_demo():
    """列表的增删改查。"""
    staff_list = ["张三", "李四", "王五", "赵六"]
    print("初始名单：", staff_list)

    staff_list.append("钱七")          # 末尾追加
    staff_list.insert(1, "孙八")       # 在第二个位置插入
    staff_list[0] = "张三丰"           # 按索引修改
    staff_list.remove("李四")          # 按内容删除
    last_one = staff_list.pop()        # 删除并返回最后一个

    print("最终名单：", staff_list)
    print("被移除的最后一人：", last_one)
    print("第一个和最后一个：", staff_list[0], staff_list[-1])


def dict_demo():
    """字典的键值对操作。"""
    employee = {
        "name": "张三",
        "department": "销售部",
        "salary": 8000,
        "is_full_time": True,
    }

    print("姓名：", employee["name"])
    print("薪资：", employee["salary"])
    print("试用期标记：", employee.get("probation", "没有这个字段"))

    employee["salary"] = 9500            # 修改已有键
    employee["email"] = "zhangsan@example.com"  # 新增键
    employee.pop("is_full_time", None)   # 删除键，不存在也不报错

    print("更新后的档案：", employee)


def customer_demo():
    """列表套字典：客户消费统计。"""
    customers = [
        {"name": "刘备", "phone": "138-0000-0001", "spend": 5000},
        {"name": "关羽", "phone": "159-1111-1112", "spend": 8000},
        {"name": "张飞", "phone": "157-2222-2225", "spend": 3000},
    ]

    # 清洗电话号码中的横杠
    for customer in customers:
        customer["phone"] = customer["phone"].replace("-", "")
        print(f"{customer['name']} 的新电话：{customer['phone']}")

    # 找出消费金额最高的人
    vip = customers[0]
    for customer in customers:
        if customer["spend"] > vip["spend"]:
            vip = customer

    print(f"消费冠军：{vip['name']}，金额：{vip['spend']} 元")


if __name__ == "__main__":
    print("=" * 30)
    print("列表练习")
    list_demo()

    print("\n" + "=" * 30)
    print("字典练习")
    dict_demo()

    print("\n" + "=" * 30)
    print("客户管理练习")
    customer_demo()
