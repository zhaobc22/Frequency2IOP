import pandas as pd

def read_first_two_columns(file_path, sheet_name='Sheet1'):
    # 读取Excel文件
    data = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', usecols="A:B")

    # 将前两列数据转换为列表
    column1_list = data.iloc[:, 0].tolist()  # 第一列
    column2_list = data.iloc[:, 1].tolist()  # 第二列

    return column1_list, column2_list

# 文件路径
file_path = 'D:/zhenshi.xlsx'

# 读取数据
column1, column2 = read_first_two_columns(file_path)



def calculate_average_of_smallest_elements(values, start_index, num_elements, bottom_n):
    # 从 start_index 开始，获取 num_elements 个元素
    if start_index + num_elements <= len(values):
        subset = values[start_index:start_index + num_elements]
        # 找到最小的 bottom_n 个元素
        sorted_elements = sorted(subset)[:bottom_n]
        # 计算这些元素的平均值
        selected_elements = sorted_elements[0:bottom_n]
        # 计算这些元素的平均值
        average = sum(selected_elements) / len(selected_elements)
        # average = sum(smallest_elements) / bottom_n
        return average
    else:
        # 超出范围时返回None或其他合适的值
        return None

def create_new_list(values, num_elements, bottom_n):
    new_list = []
    # 依次计算每个元素对应范围内的平均值
    for i in range(len(values) - num_elements + 1):  # 确保范围有效
        average = calculate_average_of_smallest_elements(values, i, num_elements, bottom_n)
        if average is not None:
            new_list.append(average)
    return new_list

# 假设 column2 是你之前从Excel中读取的第二列数据

# 创建新列表
new_list = create_new_list(column2, 300, 3)
# for list in new_list:
#     print(list)
for list in new_list:
    if list >= 505:
        print((7.5-(list-505)/65*7.5))
    elif list<505 and list>=498.8:
        print((7.5 + (505-list) / 6.2 * 7.5))
    elif list<498.8 and list>=493.8:
        print((15 + (498.8-list) / 5 * 7.5))
    elif list<493.8 and list>=490.2:
        print((22.5 + (493.8-list) / 3.6 * 7.5))
    elif list<490.2 and list>=487.8:
        print((30 + (490.2-list) / 2.4 * 7.5))
    elif list<487.8 and list>=484.8:
        print((37.5 + (487.8-list) / 3 * 7.5))
    elif list<484.8:
        print((45 + (484.8-list) / 3 * 7.5))
# #





