
# read csv has lowest .5 decimal but csv has 7 decimal
def exact_pos_resolution(requests_raw):
    pass
# 删除重复的订单 ID
def remove_duplicate_orders(requests_raw):
    duplicates = requests_raw[requests_raw.duplicated(subset='order_id', keep=False)]
    max_order_id = requests_raw['order_id'].max()
    # 遍历重复的订单 ID
    for order_id in duplicates['order_id'].unique():
        same_id_orders = requests_raw[requests_raw['order_id'] == order_id]
    
        # 检查 OD 经纬度 是否相同
        unique_orders = same_id_orders.drop_duplicates(subset=['origin_lat', 'origin_lng', 'dest_lat', 'dest_lng'])
    
        if len(unique_orders) == 1:
            # 如果经纬度相同，保留一条记录，删除其他记录
            requests_raw = requests_raw.drop(same_id_orders.index[1:])
        else:
            # 如果经纬度不同，为重复订单分配新的 order_id
            for i, index in enumerate(same_id_orders.index[1:], start=1):
                max_order_id += 1
                requests_raw.loc[index, 'order_id'] = max_order_id
    # print(len(requests_raw['order_id'].unique()) == len(requests_raw) )
    return requests_raw