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
    # 读取数据 stock_info 储存权重等相关信息，price_data储存开盘价，收盘价，最高价，最低价，交易量，交易额等信息
    stock_info = pd.read_csv(f"./raw_data/hs300stocks_{year}.csv")
    price_data = pd.read_csv(f"./raw_data/hs300stocks_kdata_{year}.csv")
    
    #
    price_data['time'] = pd.to_datetime(price_data['time'])

    # 按 code 和 date 合并数据
    stock_data = pd.merge(price_data, stock_info, how='inner', left_on='code', right_on='code')
    
    #调试数据，将处理好的数据写入文件
    stock_data.to_csv("merged_data_{year}.csv")
    
    
    # 计算每只股票的收益率
    stock_data['yield'] = stock_data.groupby('code').apply(
        lambda x: (x['close'].iloc[-1] - x['close'].iloc[0]) / x['close'].iloc[0] * 100
    ).reset_index(drop=True)

    print(f"{year}年{stock_data.groupby('code')}的收益率：{stock_data['yield']}")
    # 计算加权平均收益率
    weighted_return = (stock_data['yield'] * stock_data['weight']).sum() / stock_data['weight'].sum()

    print(f"{year}年加权平均收益率: {weighted_return:.2f}%")
