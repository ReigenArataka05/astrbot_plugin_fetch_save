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
    yield event.plain_result(f"查询 {username} 中，请耐心等待...")
    logger.info(f"正在查询用户: {username}")
    uid = await fetch_uid(username)

    if not uid or uid.strip() == "":
        yield event.plain_result(f"❌ 未找到用户: {username}")
        return

    result = '✅ 查询成功！\n'
    result += f"用户名：{username} UID: {uid}\n"
    result += f'{"索引"}\t{"昵称":<16}\t{"创建时间":<20}  {"更新时间":<20} {"更新次数":<6}  {"数据大小":<10}\n'

    global selected_uid
    selected_uid = uid

    for i in range(0, 8):
        try:
            save_data = await fetch_save_data(i, uid, GAMEID, GAMEKEY)
            # 添加数据验证
            if not save_data:
                result += f'存档 {i+1}: 数据为空\n'
                continue
                
            data = json.loads(save_data)
            title = data.get('title', '空存档')
            title = ' '.join(title.split()[:-1]) #去掉等级之类的

            content = data['data']
            create_time = data.get('create_time', '') #创建时间
            update_times = data.get('update_times', '') #更新次数
            datetime = data.get('datetime', '') #更新时间
            content = decrypt_save_data(content)

            result += f'{i+1:<6}\t{title:<16}\t{create_time:<20}  {datetime:<20}  {update_times:<6}  {round(len(content)/1024/1024,2)}MB\n'

        except Exception as e:
            result += f'{i+1:<6}\t{"空存档":<16}\n'
            continue
    
    result+='当前UID已被记录，可对其进行<下载存档>与<分析异常>操作。'
    yield event.plain_result(result)

@filter.command("download")
async def download(self, event: AstrMessageEvent, index: int): 

    if not selected_uid:
        yield event.plain_result('请先使用select或selectuid命令查询存档！')
    if index<=0 or index>8:
        yield event.plain_result('索引错误！请输入1-8之间的数字。')

    save_data = await fetch_save_data(index, selected_uid, GAMEID, GAMEKEY)
    data = json.loads(save_data)
    content = decrypt_save_data(data['data'])
    yield event.plain_result(f'正在下载存档 {index}，请耐心等待...')

    # 保存为文件并发送
    file_path = f"{selected_uid}_{index}.xml"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    yield event.file_result(file_path)