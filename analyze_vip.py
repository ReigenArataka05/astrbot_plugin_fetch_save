import asyncio
import xml.etree.ElementTree as ET

VIP_MAP = {
    100: 1, 200: 2, 500: 3, 1000: 4, 2000: 5,
    5000: 6, 8000: 7, 10000: 8, 20000: 9, 50000: 10
}
VALID_VIP_AMOUNTS = set(VIP_MAP.keys())
AMOUNT_TO_VIP = {amount: level for amount, level in VIP_MAP.items()}

def analyze_vip_object(obj_node, obj_name, current_level):
    """分析单个VIP对象"""
    if obj_node is None:
        return 0, []
    
    max_level = 0
    max_name = ""
    anomalies = []
    
    for child in obj_node:
        name = child.get('name')
        value = child.text
        
        if value != 'true':
            continue
        
        if name.startswith('m'):
            try:
                amount = int(name[1:])
            except:
                anomalies.append(f"[{obj_name}] 无效金额标识: {name}")
                continue
            
            if amount not in VALID_VIP_AMOUNTS:
                anomalies.append(f"[{obj_name}] 无效数值: {name}")
            else:
                expected_vip = AMOUNT_TO_VIP[amount]
                if expected_vip > max_level:
                    max_level = expected_vip
                    max_name = name
    
    if max_level > current_level:
        anomalies.append(f"[{obj_name}] 等级错误： {max_name} 对应VIP{max_level}，但当前等级为VIP{current_level}")
    
    return max_level, anomalies

async def analyze_vip(xml_content):
    """分析VIP数据"""
    try:
        root = ET.fromstring(xml_content)
        vip = root.find(".//s[@name='vip']")
        
        if vip is None:
            return "未找到VIP数据"
        
        level_node = vip.find(".//s[@name='level']")
        current_level = int(level_node.text) if level_node is not None else 0
        
        up_level_obj = vip.find(".//s[@name='upLevelObj']")
        obj = vip.find(".//s[@name='obj']")
        no = vip.find(".//s[@name='nO']")
        
        up_level, up_anomalies = analyze_vip_object(up_level_obj, "upLevelObj", current_level)
        obj_level, obj_anomalies = analyze_vip_object(obj, "obj", current_level)
        no_level, no_anomalies = analyze_vip_object(no, "nO", current_level)
        
        anomalies = up_anomalies + obj_anomalies + no_anomalies

        level = {
            'upLevelObj': up_level,
            'obj': obj_level,
            'nO': no_level,
            'vipLevel': current_level
        }

        return anomalies,level
        
    except Exception as e:
        return f"分析失败: {e}"
