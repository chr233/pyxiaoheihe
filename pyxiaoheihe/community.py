'''
# @Author       : Chr_
# @Date         : 2020-07-30 22:21:56
# @LastEditors  : Chr_
# @LastEditTime : 2021-11-18 20:46:21
# @Description  : 社区模块,负责[社区]TAB下的内容
'''

from typing import Tuple
from .network import Network
from .static import URLS, EMPTY_RETRYS, ERROR_RETRYS, CommentType
from .utils import ex_extend
from .error import ClientException


class Community(Network):

    def __init__(self, account: dict, hbxcfg: dict, debug: bool, rpc_server: str):
        super().__init__(account, hbxcfg, debug, rpc_server)

    def debug(self):
        super().debug()
        # self.send_community_comment(43817628,'test')

    def get_recommend_post(self, amount: int = 8) -> list:
        '''
        获取[推荐]下的文章

        参数:
            [amount]: 需要拉取的数量
        成功返回:
            list: 文章id列表,[(linkid,title,desc,userid),……]
        '''
        def get(lastval: str, pull: int = 0) -> Tuple[list, str]:
            params = {'pull': pull, 'use_history': 0, 'lastval': lastval}
            if not lastval:
                params.pop('lastval')
                params.pop('use_history')
            result = self._get(url=url, params=params)
            tmp = []
            val = result.get('lastval')
            for l in result['links']:
                title = l['title']
                desc = l['description']
                linkid = l['linkid']
                userid = l['user']['userid']
                tmp.append((linkid, title, desc, userid))
            self.logger.debug(f'拉取了{len(tmp)}条帖子')
            return((tmp, val))
        # ==========================================
        url = URLS.GET_RECOMMEND_POST
        postlist = []
        empty = 0
        error = 0
        lastval = None
        for i in range(0, amount//8 + 2):
            try:
                self.logger.debug(f'拉取第[{i+1}]批帖子')
                tmp, lastval = get(lastval, 1 if i == 0 else 0)
                if tmp:
                    postlist = ex_extend(postlist, tmp)
                else:
                    self.logger.debug('[*] 帖子列表为,可能遇到错误')
                    empty += 1
                    if empty > EMPTY_RETRYS:
                        self.logger.debug('[*] 空结果达到上限,停止操作')
                        break
                if len(postlist) >= amount:
                    break
            except ClientException as e:
                self.logger.debug(f'[*] 拉取推荐帖子列表出错 [{e}]')
                error += 1
                if error > ERROR_RETRYS:
                    self.logger.debug('[*] 错误次数达到上限,停止操作')
                    break
        postlist = postlist[:amount]
        if len(postlist) > 0:
            self.logger.debug(f'操作完成,拉取了[{len(postlist)}]条帖子')
        else:
            self.logger.warning('[*] 拉取完毕,帖子列表为空,请检查参数')
        return(postlist)

    def get_recommend_post_id(self, amount: int = 8) -> list:
        '''
        获取首页文章id列表

        参数:
            [amount]: 需要拉取的数量
        成功返回:
            list: 文章id列表,[linkid,……]
        '''
        postlist = self.get_recommend_post(amount)
        idlist = [x[0] for x in postlist]
        return(idlist)

    def send_community_comment(self, linkid: int, message: str) -> bool:
        '''
        发送社区评论

        参数:
            linkid: 文章id
            message: 文字评论内容
        返回:
            操作是否成功
        '''
        result = self._send_comment(
            linkid, message, CommentType.Community, 0)
        return(result)
