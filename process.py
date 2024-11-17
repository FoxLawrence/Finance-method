import pandas as pd
import numpy as np
from glob import glob

# 读取市场指数数据
file_path = "./raw_data/market_index.csv"
market_data = pd.read_csv(file_path)

# 假设所有数据是2024年的日期，手动添加年份
market_data['日期'] = '2024.' + market_data['日期'].astype(str)

# 将 '2024.11.11' 格式的日期转换为 datetime 格式
market_data['日期'] = pd.to_datetime(market_data['日期'], format='%Y.%m.%d')

# 计算每日市场指数对数收益率
market_data['对数收益率'] = np.log(market_data['收盘指数'] / market_data['收盘指数'].shift(1))

# 打印市场数据
print(market_data.head())

# 读取所有 Excel 文件
file_paths = glob("./raw_data/*.xlsx")  # 确保路径正确
dataframes = [pd.read_excel(fp) for fp in file_paths]

# 存储最终结果
result_list = []

# 遍历每个文件
for i, df in enumerate(dataframes):
    # 获取文件名中的日期（如 1111 对应 11月11日）
    file_date = file_paths[i].split('/')[-1].split('.')[0]  # 获取文件名（如 '1111'）
    date_str = '2024.' + file_date  # 假设年份为2024
    date_obj = pd.to_datetime(date_str, format='%Y.%m%d')  # 转换为日期对象
    
    df['日期'] = date_obj  # 为每个文件添加对应的日期列
    
    df = df[['代码', '现价', '今开', '最高', '最低', '日期']].copy()  # 确保有日期列
    
    # 添加前一天的现价列
    if i > 0:
        previous_day = dataframes[i - 1][['代码', '现价', '日期']].rename(columns={'现价': '前一日现价'})
        df = df.merge(previous_day, on=['代码', '日期'], how='left')
    else:
        df['前一日现价'] = np.nan

    # 计算对数收益率
    df['对数收益率'] = np.log(df['现价'] / df['前一日现价'])
    
    # 获取当天市场对数收益率（基于日期匹配）
    df['市场对数收益率'] = df['日期'].map(market_data.set_index('日期')['对数收益率'])

    # 计算 Beta 系数：使用股票对数收益率与市场对数收益率的回归分析
    if len(df) > 1:  # 至少需要两天的数据来计算 Beta
        cov_matrix = df[['对数收益率', '市场对数收益率']].cov()
        beta = cov_matrix.loc['对数收益率', '市场对数收益率'] / cov_matrix.loc['市场对数收益率', '市场对数收益率']
        df['Beta'] = beta
    else:
        df['Beta'] = np.nan  # 第一天无法计算 Beta

    # 计算最大回撤
    df['最大回撤'] = (df['最高'] - df['最低']) / df['最高']

    # 保存结果
    result_list.append(df)

# 合并所有结果
final_result = pd.concat(result_list, ignore_index=True)

# 保存到 Excel
final_result.to_excel("result.xlsx", index=False)
