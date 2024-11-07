#
#//  data_analysis.py
#//  stock
#//
#//  Created by 王中杰 on 2024/11/5.
#//

import pandas as pd
import glob

#新建一张空表，加入编码，权重，收益率等信息
final_table = pd.DataFrame(columns=['code', 'return', 'weight'])

#因为2014年的表权重为0，所以可以忽略不计，从2015年计算到2024年
for year in range(2015, 2025):
    stock_info = pd.read_csv(f"./raw_data/hs300stocks_{year}.csv")

    price_current = pd.read_csv(f"./raw_data/hs300stocks_kdata_{year}.csv")
    price_previous = pd.read_csv(f"./raw_data/hs300stocks_kdata_{year-1}.csv")
    #时间标准化，方便排序
    price_current['time'] = pd.to_datetime(price_current['time'])
    price_previous['time'] = pd.to_datetime(price_previous['time'])

    #将price按照code和时间进行排序
    price_current.sort_values(by=['code', 'time'])
    price_previous.sort_values(by=['code', 'time'])

    #获取price_current和price_previous的每一个股票在其年份的最后一个交易日的收盘价
    last_close_price_current = price_current.groupby('code').last()[['close']].reset_index()
    last_close_price_previous = price_previous.groupby('code').last()[['close']].reset_index()

    # 获取当前year的每只股票的第一个交易日的收盘价
    first_close_price_current = price_current.groupby('code').first()[['close']].reset_index()

    #合并last_close_price_current和last_close_price_previous，将数据整合到一起
    merged = pd.merge(last_close_price_current, last_close_price_previous, on='code', how='left', suffixes=('_last', '_first'))
    merged = pd.merge(merged, first_close_price_current, on='code', how='left')
    #如果last_close_price_price的code没有出现在last_close_price_current即成分股调入，使用price_current第一天的收盘价first_close_price_current
    merged['close_first'] = merged['close_first'].fillna(first_close_price_current['close'])
    #合并数据
    final_result = merged[['code', 'close_first', 'close_last']]
    #处理price_current中的amount和volume的平均值，作为市场流动性的指标    
    aggregated = price_info.groupby('code').agg(
    avg_amount=('amount', 'mean'),   # 计算每个 code 的平均 amount
    avg_volume=('volume', 'mean')    # 计算每个 code 的平均 volume
    ).reset_index()
	
    #将计算出的平均amount和volume数据与stock_info合并，方便进行加权平均
    merged = pd.merge(aggregated, stock_info, on='code', how='left')

    #计算amount和volume的加权平均
    weighted_avg_amount = (merged['avg_amount'] * merged['weight']).sum() / merged['weight'].sum()
    weighted_avg_volume = (merged['avg_volume'] * merged['weight']).sum() / merged['weight'].sum()
    
    print(f"{year}年加权平均交易量为: {weighted_avg_volume:.2f}\n{year}年加权平均交易额为: {weighted_avg_amount:.2f}")
    #计算收益率
    final_result['return'] = (final_result['close_last'] - final_result['close_first']) / final_result['close_first']
    final_result = final_result[['code', 'return']]

    #将结果保存为csv文件
    
    final_result.to_csv(f"./processed_data/calculated_returns_{year}.csv", index=False)
    merged_result = pd.merge(final_result, stock_info, on='code', how='left')
    final_table = pd.concat([final_table, merged_result], ignore_index=True)
	#计算权重之和，方便归一化
    weight_sum = stock_info['weight'].sum()
    weighted_return = (merged_result['return'] * merged_result['weight']).sum() / weight_sum
	
    print(f"{year}年加权平均收益率: {weighted_return:.2f}%")

final_table.to_csv(f"./processed_data/all_return_weight.csv", index=False)
