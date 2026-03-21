from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import json
from .save_api import fetch_save_data, fetch_uid, decrypt_save_data
from .analyze import analyze_all

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
    async def selectuid(self, event: AstrMessageEvent, uid): 

        global selected_uid
        
        result = '✅ 查询成功！\n'
        result += f"UID: {uid}\n"
        result += f'{"索引"}\t {"昵称":<12}\t\t{"保存时间":<12}\n'
        
        selected_uid = uid
        
        for i in range(0, 8):
            try:
                save_data = await fetch_save_data(i, uid, GAMEID, GAMEKEY)
                
                if not save_data or save_data.strip() == "":
                    result += f'{i:<6}\t {"空存档":<12}\n'
                    continue
                
                data = json.loads(save_data)
                
                if not isinstance(data, dict):
                    result += f'{i:<6}\t {"空存档":<12}\n'
                    continue
                
                # 获取标题并去掉等级
                title = data.get('title', '空存档')
                if title and title != '空存档':
                    title_parts = title.split()
                    if len(title_parts) > 1:
                        title = ' '.join(title_parts[:-1])
                
                # 获取时间
                datetime = data.get('datetime', '')
                if datetime and len(datetime) > 2:
                    datetime = datetime[2:10]
                else:
                    datetime = '未知'
                
                result += f'{i:<6}\t {title}\t\t{datetime:<12}\n'
                
            except Exception as e:
                logger.error(f"获取存档{i}时发生错误: {e}")
                result += f'{i:<6}\t {"获取失败"}\t\t{"错误":<12}\n'
                continue
        
        result += '\n当前UID已被记录，可对其进行<detail>与<check>操作。'
        yield event.plain_result(result)
    @filter.command("select",alias={'查询','查询用户'})
    async def select(self, event: AstrMessageEvent, username: str): 
        yield event.plain_result(f"查询 {username} 中，请耐心等待...")
        
        uid = await fetch_uid(username)
        
        if not uid or uid.strip() == "" or uid == "0":
            yield event.plain_result(f"❌ 未找到用户: {username}")
            return
        
        # 使用 async for 来遍历异步生成器
        async for result in self.selectuid(event, uid):
            yield result

    @filter.command("selectu",alias={'selectuid','查询uid'})
    async def selectu(self, event: AstrMessageEvent, uid: str):
        yield event.plain_result(f"查询uid {uid} 中，请耐心等待...")

        if not uid or not uid.isdigit():
            yield event.plain_result(f"❌ UID格式错误，请输入数字")
            return
        
        # 使用 async for 来遍历异步生成器
        async for result in self.selectuid(event, uid):
            yield result
    @filter.command("detail",alias={'详情','查看详情'})
    async def detail(self, event: AstrMessageEvent, index:str): 

        global selected_uid
        
        if index.find('_') != -1:
            parts = index.split('_')
            selected_uid = parts[0]
            index = parts[1]

        try:
            if not selected_uid or selected_uid.strip() == "":
                yield event.plain_result('请先使用select命令查询存档！')
                return
        except NameError:
            yield event.plain_result('请先使用select命令查询存档！')
            return

        try:
            idx = int(index)
            if idx < 0 or idx > 7:
                yield event.plain_result('索引错误！请输入0-7之间的数字。')
                return
        except ValueError:
            yield event.plain_result('索引格式错误！')
            return
        
        save_data = await fetch_save_data(idx, selected_uid, GAMEID, GAMEKEY)
        data = json.loads(save_data)
        
        result = f'📊 存档 {selected_uid}_{idx} 详细信息\n'

        title=data.get("title", "空存档")
        result += f'标题: {title}\n'
        result += f'昵称: {' '.join(title.split()[:-1])}\n'

        result += f'创建时间: {data.get("create_time", "未知")[:19]}\n'
        result += f'更新时间: {data.get("datetime", "未知")[:19]}\n'
        result += f'更新次数: {data.get("update_times", 0)}\n'
        save_data = decrypt_save_data(data['data'])
        result += f'数据长度: {round(len(save_data)/1024/1024,2)}MB\n'

        yield event.plain_result(result)
    @filter.command("check",alias={'查','检查','查异常'})
    async def check(self, event: AstrMessageEvent, index: str):

        global selected_uid
        
        if index.find('_') != -1:
            parts = index.split('_')
            selected_uid = parts[0]
            index = parts[1]

        try:
            if not selected_uid or selected_uid.strip() == "":
                yield event.plain_result('请先使用select命令查询存档！')
                return
        except NameError:
            yield event.plain_result('请先使用select命令查询存档！')
            return

        try:
            idx = int(index)
            if idx < 0 or idx > 7:
                yield event.plain_result('索引错误！请输入0-7之间的数字。')
                return
        except ValueError:
            yield event.plain_result('索引格式错误！')
            return

        yield event.plain_result(f'检查 {selected_uid}_{idx} 中，请耐心等待...')
        save_data = await fetch_save_data(idx, selected_uid, GAMEID, GAMEKEY)
        data = json.loads(save_data)
        content = decrypt_save_data(data['data'])

        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        content = content[content.find('<saveXml'):]

        report = await analyze_all(content, selected_uid, index)

        yield event.plain_result(f'UID: {selected_uid} index：{idx}\n{report}')

    @filter.command("readuid",alias={'读','read'})
    async def detail(self, event: AstrMessageEvent, uid:str): 

        global selected_uid
        selected_uid = uid
        result += '\n当前UID已被记录，可对其进行<detail>与<check>操作。'
        yield event.plain_result(await analyze_uid_md5(content, uid, index))