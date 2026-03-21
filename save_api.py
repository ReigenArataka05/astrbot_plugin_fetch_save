import hashlib
import base64
import zlib
import aiohttp
import asyncio
import json

def take_verify(index: str, uid: str, gameid: str, gamekey: str) -> str:
    """计算 verify 值"""
    raw = f"SDALPlsldlnSLWPElsdslSE{index}{gamekey}{uid}{gameid}PKslsO"
    md5 = hashlib.md5(raw.encode()).hexdigest()
    md5 = hashlib.md5(md5.encode()).hexdigest()
    md5 = hashlib.md5(md5.encode()).hexdigest()
    return md5

async def fetch_save_data(index: str, uid: str, gameid: str, gamekey: str) -> str:
    """获取存档数据"""
    data = {
        'uid': uid,
        'gameid': gameid,
        'gamekey': gamekey,
        'index': index,
        'verify': take_verify(index, uid, gameid, gamekey)
    }
    async with aiohttp.ClientSession() as session:
        async with session.post('https://save.api.4399.com/ranging.php/?ac=get', data=data) as response:
            return await response.text()

async def fetch_uid(username: str) -> str:
    """通过用户名获取 UID"""
    url = "https://cz.4399.com/get_role_info.php"
    params = {'ac': 'cuid', 'uname': username}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.text()

def decrypt_save_data(compressed_data: str) -> str:
    """解密存档数据"""
    data = base64.b64decode(compressed_data)
    return zlib.decompress(data)
