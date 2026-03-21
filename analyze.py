from .analyze_pay import analyze_pay,load_good_items
from .analyze_vip import analyze_vip
from .analyze_other import analyze_uid_md5,analyze_zuobi
import asyncio
async def analyze_all(xml_content, uid, index):
    """完整分析存档"""

    report = '✅分析完成！\n'

    report += '①存档异常分析'
    is_zuobi, zuobi_reason = await analyze_zuobi(xml_content)
    if is_zuobi == True or zuobi_reason is not None:
        report += f"\nisZuobi：{is_zuobi}\nzuobiReason：{zuobi_reason}\n"
    else:
        report += "：通过\n"
    
    report += '②复制档分析'
    saved_md5, md5_valid = await analyze_uid_md5(xml_content, uid, index)
    if saved_md5 == '5E20663DADD1E483AC628951DD582EA8':
        report += "：MD5获取失败！可能为旧版本。\n"
    elif saved_md5 != md5_valid:
        report += "：MD5校验失败，有复制档可能性！\n"
        report += f"MD5：{saved_md5}\nMD5验证：{md5_valid}\n"
    else:
        report += "：MD5校验通过！\n"
        report += f"MD5：{saved_md5}\n"
    
    report += '③VIP分析'
    amanomalies, level = await analyze_vip(xml_content)
    
    if amanomalies is not None and len(amanomalies) > 0:
        report += f'：有{len(amanomalies)}条异常VIP记录\n'
        for anomaly in amanomalies:
            report += f"{anomaly}\n"
    else:
        report += f"：通过，无异常记录\n"
    report += f"Lv:{level['vipLevel']},upLevelObj:{level['upLevelObj']},obj:{level['obj']},nO:{level['nO']}\n"

    report += '④消费记录分析,请自行判断\n'
    items_map = load_good_items('good_items.csv')
    if len(items_map) == 0:
        report += "加载物品数据失败！请检查good_items.csv文件是否存在！\n"
        pay_info = ""
        total_price = 0
    else:
        pay_info, total_price = await analyze_pay(xml_content, items_map)

    VIP_MAP = {
        1: 100, 2: 200, 3: 500, 4: 1000, 5: 2000,
        6: 5000, 7: 8000, 8: 10000, 9: 20000, 10: 50000
    }

    if level.get('vipLevel') in VIP_MAP:
        max_amount = VIP_MAP[level['vipLevel']]
        if total_price > max_amount:
            report += f"【消费金额异常】\n消费金额超过VIP等级限制:{max_amount}\n"

    report += f"总消费金额：{total_price}\n{pay_info}"

    return report
