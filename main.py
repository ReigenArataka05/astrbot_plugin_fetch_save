from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import json
from .save_api import fetch_save_data, fetch_uid, decrypt_save_data

GAMEID = "100027788"
GAMEKEY = "34008a2844a1a569"

@register("save_query", "lingyi", "爆枪突击存档查询、分析机器人", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        pass

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        pass

@filter.command("select")
async def select(self, event: AstrMessageEvent, username: str): 
    yield event.plain_result(f"开始查询用户 {username}:")
    logger.info(f"正在查询用户: {username}")
    uid = await fetch_uid(username)

    if not uid or uid.strip() == "":
        yield event.plain_result(f"❌ 未找到用户: {username}")
        return

    result = '✅ 查询成功！\n'
    result += f"用户名：{username}，UID: {uid}\n"

    for i in range(0, 8):
        try:
            save_data = await fetch_save_data(i, uid, GAMEID, GAMEKEY)

            # 添加数据验证
            if not save_data:
                result += f'存档 {i}: 数据为空\n'
                continue
                
            data = json.loads(save_data)
            title = data.get('title', '空存档')
            content = data['data']
            create_time = data.get('create_time', '')
            update_time = data.get('update_time', '')
            content = decrypt_save_data(content)

            result += f'{i}\t{title}\t{create_time}\t{update_time}\t{len(content)}\n'

        except Exception as e:
            result += f'存档 {i}: 空存档\n'
            continue

    yield event.plain_result(result)