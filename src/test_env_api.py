import random

import requests
import json

BASE_URL = "http://localhost:10086"

def run_epoch(epoch_num=1):
    response = requests.post(f"{BASE_URL}/run_epoch", json={"epoch_num": epoch_num})
    return response.json()

def get_current_requests():
    response = requests.get(f"{BASE_URL}/getCurrentRequests")
    return response.json()

def get_current_vehicles():
    response = requests.get(f"{BASE_URL}/getCurrentVehicles")
    return response.json()

def get_scaned_requests():
    response = requests.get(f"{BASE_URL}/getScanedRequests")
    return response.json()

def get_uv_loc_prompt():
    response = requests.get(f"{BASE_URL}/get_uv_loc_prompt")
    return response.json()

def get_dt_w2_loc(origin, destination):
    data = {
        "origin": origin,
        "destination": destination
    }
    response = requests.post(f"{BASE_URL}/get_dt_w2_loc", json=data)
    return response.json()
def getUVinfo():
    response = requests.get(f"{BASE_URL}/getUVinfo")

    return response.json()
def getDemandNeed():
    response = requests.get(f"{BASE_URL}/getDemandNeed")
    return response.json()
def implement_action(decision):
    action = {"decisions": decision}
    response = requests.post(f"{BASE_URL}/implementDecision", json=action)
    return response.json()
def decision_multi_random():
    response = requests.get(f"{BASE_URL}/randomAction")
    return response.json()
def decision_pairs_random(u_ids, v_ids,least_matched=0.6):
    pairs = []
    # the number of requests that can be matched, at least 0.6
    num_matched_u = int(len(u_ids) * min(1.0, random.random() + least_matched))
    # choose v randomly withou replacement
    random.shuffle(v_ids)
    random.shuffle(u_ids)
    for i in range(num_matched_u):
        pairs.append((u_ids[i], v_ids[i]))
    return pairs
def test_get_dt_w2_loc():
    # 获取两个位置之间的距离和时间
    origin = (104.0412682, 30.6669185)
    destination = (104.0562247, 30.6223237)
    print(get_dt_w2_loc(origin, destination))
def test_random_pairs():
    for i in range(100):
        uv_json = getUVinfo()

        Uinfo, Vinfo = uv_json["Passengers"], uv_json["Taxis"]
        u_ids, v_ids = list(Uinfo.keys()), list(Vinfo.keys())

        pairs = decision_pairs_random(u_ids, v_ids)
        implement_action(pairs)
def test_random_multi():
    for i in range(300):
        uv_json = getDemandNeed()

        Uinfo, Vinfo, U2MultiV, V2MultiU = uv_json["Passengers"], uv_json["Taxis"], uv_json["U2MultiV"],uv_json["V2MultiU"]
        pairs = []
        for  u_id, v_ids in U2MultiV.items():
            pair = decide_multiV_singleU(u_id, v_ids)
            pairs.append(pair)

        implement_action(pairs)
def decide_multiV_singleU(u_id, v_ids):
    # 一个乘客匹配多个车辆
    v_id = random.choice(v_ids) # 随机选择一个车辆
    pair = (u_id, v_id)
    return pair
def reset_env():
    response = requests.get(f"{BASE_URL}/reset")
    return response.json()
# 使用示例
if __name__ == "__main__":
    test_random_multi()
    # # 获取当前请求
    # print(get_current_requests())
    #
    # # 获取当前车辆 TypeError: Object of type Vehicle is not JSON serializable
    # print(get_current_vehicles())
    #
    # # 获取扫描的请求
    # print(get_scaned_requests())
    #
    # # 获取UV位置提示
    # print(get_uv_loc_prompt())



