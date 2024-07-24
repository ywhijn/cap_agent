# # global memory for region success requests and time success requests
# # smooth path for pooling, which direction to go to offer a lift: position $ direction pair
# # individual experience for each vehicle
import osmnx as ox
import subprocess

# 加载 OSMnx 路网
network_file_path = '/Users/yangwenhan/Desktop/final/code/Ride-sharing-Simulator-main/data/chengdu.graphml'


# # 将 OSMnx 图形数据保存为 OSM 文件
# osm_file_path = 'network.osm'
# ox.save_graphml(G, filepath=osm_file_path)
import osmnx as ox
import xml.etree.ElementTree as ET
from pyproj import Proj, transform


G = ox.load_graphml(network_file_path)

# 创建 OSM XML 根元素
osm = ET.Element("osm", version="0.6", generator="OSMnx")

# 投影转换设置（假设 GraphML 使用的是 WGS84 坐标系）
in_proj = Proj(init='epsg:4326')
out_proj = Proj(init='epsg:4326')

# 添加节点到 OSM XML
for node_id, data in G.nodes(data=True):
    lat, lon = data['y'], data['x']  # OSMnx 默认使用 WGS84 坐标系
    osm_node = ET.SubElement(osm, "node", id=str(node_id), lat=str(lat), lon=str(lon))
    # 添加其他节点属性（如果有）
    for key, value in data.items():
        if key not in ['x', 'y']:
            ET.SubElement(osm_node, "tag", k=key, v=str(value))

# 添加边到 OSM XML
way_id = 1  # 初始化 way_id
for u, v, data in G.edges(data=True):
    osm_way = ET.SubElement(osm, "way", id=str(way_id))
    ET.SubElement(osm_way, "nd", ref=str(u))
    ET.SubElement(osm_way, "nd", ref=str(v))
    # 添加其他边属性（如果有）
    for key, value in data.items():
        ET.SubElement(osm_way, "tag", k=key, v=str(value))
    way_id += 1  # 递增 way_id


# 写入 OSM 文件
osm_file_path = 'network.osm'
tree = ET.ElementTree(osm)
tree.write(osm_file_path, encoding='utf-8', xml_declaration=True)

print(f'Successfully converted to {osm_file_path}')

# 使用 osm2sumo 工具将 OSM 文件转换为 SUMO 网格文件
# sumo_network_file_path = 'network.net.xml'
# cmd = [
#     'netconvert',
#     '--osm-files', osm_file_path,
#     '--output-file', sumo_network_file_path
# ]
#
# # 运行命令
# subprocess.run(cmd)
#
# print(f'Successfully converted to {sumo_network_file_path}')
# import gdal
# import osmnx as ox
#
# print(gdal.__version__)
# print(ox.__version__)
