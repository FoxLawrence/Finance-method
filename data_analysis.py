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

for year in range(2014, 2024):
    # 读取数据 stock_info 储存权重等相关信息，price_info储存开盘价，收盘价，最高价，最低价，交易量，交易额等信息
  
    stock_info = pd.read_csv(f"./raw_data/hs300stocks_{year}.csv")
    stock_info['time'] = pd.to_datetime(stock_info['time'])
    if year == 2014:
        price_info = pd.read_csv(f"./raw_data/hs300stocks_kdata_{year}.csv")
        price_info['Date'] = pd.to_datetime(price_info['Date'])
        # 按 'Code' 和 'Date' 排序，确保数据按时间顺序
        price_info = price_info.sort_values(by=['Code', 'Date'])

        # 获取price_info 中每个 'Code' 的第一天和最后一天的 'Close'
        first_close_price_info = price_info.groupby('Code').first()[['Close']].reset_index()
        last_close_price_info = price_info.groupby('Code').last()[['Close']].reset_index()

        # 合并第一天的 Close 和 最后一天的 Close
        final_result = pd.merge(first_close_df2, last_close_df2, on='Code', suffixes=('_first', '_last'))

    else:
        price_current = pd.read_csv(f"./raw_data/hs300stocks_kdata_{year}.csv")
        price_previous = pd.read_csv(f"./raw_data/hs300stocks_kdata_{year-1}.csv")
        price_current['Date'] = pd.to_datetime(df_current['Date'])
        price_previous['Date'] = pd.to_datetime(df_previous['Date'])

        #按代码和日期进行排序
        price_current.sort_values(by=['Code', 'Date'])
        price_previous.sort_values(by=['Code', 'Date'])

        #获取price_current和price_previous的每一个股票该年度的收盘价
        last_close_price_current = price_current.groupby('Code').last()[['Close']].reset_index()
        last_close_price_previous = price_previous.groupby('Code').last()[['Close']].reset_index()

        # 获取当前文件每个 Code 的第一个日期的 Close
        last_close_price_current = price_current.groupby('Code').last().reset_index()

        #合并last_close_price_current和last_close_price_previous，
        merged = pd.merge(last_close_df2, first_close_df2, on='Code', how='left', suffixes=('_last', '_first'))
        #如果last_close_price_price的Code没有出现在last_close_price_current即成分股调入，使用price_current第一天的收盘价
        merged['first_close'] = merged['Close_first'].fillna(merged['Close_last'])
        #合并数据
        final_result = merged[['Code', 'first_close', 'Close_last']].rename(columns={'first_close': 'first_close', 'Close_last': 'second_close'})
    #计算收益率
    final_result['return'] = (final_result['Close_last'] - final_result['Close_first']) / final_result['Close_first']
    final_result = final_result[['Code', 'return']]

    #将结果保存为csv文件
    final_result.to_csv("calculated_returns_{year}.csv", index=False)

    # 计算加权平均收益率
    weighted_return = (final_result['return'] * stock_info['weight']).sum() / stock_info['weight'].sum()

    print(f"{year}年加权平均收益率: {weighted_return:.2f}%")
