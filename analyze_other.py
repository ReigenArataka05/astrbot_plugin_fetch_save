import asyncio
import hashlib
import xml.etree.ElementTree as ET
from typing import Tuple

async def analyze_zuobi(xml_content):
    """分析作弊状态"""
    try:
        root = ET.fromstring(xml_content)
        main = root.find(".//s[@name='main']")
        
        if main is None:
            return None, None
        
        is_zuobi = main.find(".//s[@name='isZuobiB']")
        zuobi_reason = main.find(".//s[@name='zuobiReason']")
        
        is_zuobi_val = is_zuobi.text
        zuobi_reason_val = zuobi_reason.text
        
        return is_zuobi_val, zuobi_reason_val
        
    except Exception as e:
        return None, None

async def analyze_uid_md5(xml_content, uid, index):
    """分析UIDMD5，检测是否为复制档"""
    try:
        root = ET.fromstring(xml_content)
        main = root.find(".//s[@name='main']")
        
        if main is None:
            return None, False
        
        uid_md5_node = main.find(".//s[@name='uidMd5']")
        if uid_md5_node is None or not uid_md5_node.text:
            return None, False
        
        saved_md5 = uid_md5_node.text.upper()
        expected_md5 = hashlib.md5(f'{uid}_{index}'.encode()).hexdigest().upper()
        
        return saved_md5,expected_md5
        
    except Exception as e:
        return None, False
