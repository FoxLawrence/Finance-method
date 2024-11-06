#
#//  data_analysis.py
#//  stock
#//
#//  Created by 王中杰 on 2024/11/5.
#//

import pandas as pd
import glob

# 导入数据文件,原始的文件储存在./raw_data中
stock_files = glob.glob("./raw_data/hs300stocks_kdata_*.csv")  # 包含股票信息的文件
price_files = glob.glob("./raw_data/hs300stocks_kdata_*.csv")  # 包含价格数据的文件

final_table = pd.DataFrame(columns=['code', 'return', 'weight'])

for year in range(2014, 2024):
    # 读取数据 stock_info 储存权重等相关信息，price_info储存开盘价，收盘价，最高价，最低价，交易量，交易额等信息
  
    stock_info = pd.read_csv(f"./raw_data/hs300stocks_{year}.csv")
    stock_info['date'] = pd.to_datetime(stock_info['date'])
    if year == 2014:
        price_info = pd.read_csv(f"./raw_data/hs300stocks_kdata_{year}.csv")
        price_info['time'] = pd.to_datetime(price_info['time'])
        # 按 'code' 和 'time' 排序，确保数据按时间顺序
        price_info = price_info.sort_values(by=['code', 'time'])

        # 获取price_info 中每个 'code' 的第一天和最后一天的 'close'
        first_close_price_info = price_info.groupby('code').first()[['close']].reset_index()
        last_close_price_info = price_info.groupby('code').last()[['close']].reset_index()

        # 合并第一天的 close 和 最后一天的 close
        final_result = pd.merge(first_close_price_info, last_close_price_info, on='code', suffixes=('_first', '_last'))

    else:
        price_current = pd.read_csv(f"./raw_data/hs300stocks_kdata_{year}.csv")
        price_previous = pd.read_csv(f"./raw_data/hs300stocks_kdata_{year-1}.csv")
        price_current['time'] = pd.to_datetime(price_current['time'])
        price_previous['time'] = pd.to_datetime(price_previous['time'])

        #按代码和日期进行排序
        price_current.sort_values(by=['code', 'time'])
        price_previous.sort_values(by=['code', 'time'])

        #获取price_current和price_previous的每一个股票该年度的收盘价
        last_close_price_current = price_current.groupby('code').last()[['close']].reset_index()
        last_close_price_previous = price_previous.groupby('code').last()[['close']].reset_index()

        # 获取当前文件每个 code 的第一个日期的 close
        first_close_price_current = price_current.groupby('code').first()[['close']].reset_index()

        #合并last_close_price_current和last_close_price_previous，
        merged = pd.merge(last_close_price_current, last_close_price_previous, on='code', how='left', suffixes=('_last', '_first'))
        #如果last_close_price_price的code没有出现在last_close_price_current即成分股调入，使用price_current第一天的收盘价first_close_price_current
        merged['close_first'] = merged['first_close'].fillna(first_close_price_current['close'])
        #合并数据
        final_result = merged[['code', 'close_first', 'close_last']])
    #计算收益率
    final_result['return'] = (final_result['close_last'] - final_result['close_first']) / final_result['close_first']
    final_result = final_result[['code', 'return']]

    #将结果保存为csv文件
    
    final_result.to_csv(f"./calculated_returns_{year}.csv", index=False)
    merged_result = pd.merge(final_result, stock_info, on='code', how='left')
    final_table = pd.concat([final_table, merged_result], ignore_index=True)
    weight_sum = stock_info['weight'].sum()
    if weight_sum == 0:
        print("Warning: Total weight is zero. Weighted return cannot be calculated.")
        weighted_return = 0  # 或者其他处理方式
    else:
        weighted_return = (final_result['return'] * stock_info['weight']).sum() / weight_sum
    # 计算加权平均收益率
    weighted_return = (final_result['return'] * stock_info['weight']).sum() / stock_info['weight'].sum()

    print(f"{year}年加权平均收益率: {weighted_return:.2f}%")
final_table.to_csv(f"./all_return_weight.csv", index=False)
