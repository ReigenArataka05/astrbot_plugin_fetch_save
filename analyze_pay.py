import asyncio
import xml.etree.ElementTree as ET
import os

def load_good_items(csv_path='good_items_1.0.csv'):
    import pandas as pd
    """加载消费物品映射表"""
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, csv_path)
        
        # 如果相对路径找不到，尝试当前工作目录
        if not os.path.exists(full_path):
            full_path = csv_path
        
        if not os.path.exists(full_path):
            print(f"警告: 文件 {full_path} 未找到")
            return {}
        
        df = pd.read_csv(full_path, encoding='gbk')
        items_map = {}
        for _, row in df.iterrows():
            record_id = str(row.get('记录ID', ''))
            if record_id:
                items_map[record_id] = {
                    'name': row.get('物品', f'未知物品'),
                    'price': int(row.get('金额', 0)) if str(row.get('金额', '')).isdigit() else 0,
                    'category': row.get('分类', ''),
                    'remark': row.get('备注', '')
                }
        print(f"成功加载 {len(items_map)} 条物品数据，文件路径: {full_path}")
        return items_map
    except FileNotFoundError:
        print(f"警告: 文件 {csv_path} 未找到")
        return {}
    except Exception as e:
        print(f"加载物品数据失败: {e}")
        return {}

async def analyze_pay(xml_content, items_map):
    """分析消费数据"""
    try:
        root = ET.fromstring(xml_content)
        pay = root.find(".//s[@name='pay']")
        if pay is None:
            return "无消费记录"
        
        obj = pay.find(".//s[@name='obj']")
        if obj is None:
            return "无消费记录"
        
        purchases = []
        total_price = 0
        
        for child in obj:
            item_id = child.get('name')
            quantity = int(child.text) if child.text else 0
            
            if quantity <= 0:
                continue
            
            item_info = items_map.get(item_id, {'name': f'未知物品({item_id})', 'price': 0})
            unit_price = item_info['price']
            total = unit_price * quantity
            
            purchases.append({
                'id': item_id,
                'name': item_info['name'],
                'unit_price': unit_price,
                'quantity': quantity,
                'total': total
            })
            total_price += total
        
        if not purchases:
            return '无消费记录',0
        
        # 按价格排序
        purchases.sort(key=lambda x: x['total'], reverse=True)
        
        # 格式化输出
        result = "消费ID\t物品名\t\t单价\t数量\t价格\n"
        
        for p in purchases[:10]:
            name = p['name']
            if len(name) > 7:
                name = name[:7] + ".."
            else:
                name = name.ljust(12)
            result += f"{p['id']}\t{name}\t\t{p['unit_price']}\t{p['quantity']}\t{p['total']}\n"
        
        if len(purchases) > 10:
            result += f"\n共 {len(purchases)} 条记录，仅显示前10条\n"

        return result,total_price
        
    except Exception as e:
        return f"分析失败: {e}"
