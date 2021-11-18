
'''
# @Author       : Chr_
# @Date         : 2020-07-30 13:32:04
# @LastEditors  : Chr_
# @LastEditTime : 2021-11-18 20:46:02
# @Description  : 小黑盒客户端模块
'''

from .account import Account
from .community import Community
from .game import Game
from .index import Index


class HeyBoxClient(Account, Community, Game, Index):

    '''
    Python实现的小黑盒客户端
    '''

    def __init__(self, account: dict, hbxcfg: dict, debug: bool = False, rpc_server: str = None):
        '''
        初始化

        参数:
            account: 账号字典,需要包含'pkey','imei'和'heybox_id'
            hbxcfg: 客户端设置字典,需要包含
            [debug]: 调试模式开关,打开后会输出调试日志
        '''
        super().__init__(account, hbxcfg, debug, rpc_server)

    def debug(self):
        '''
        仅供测试使用
        '''
        return super().debug()
