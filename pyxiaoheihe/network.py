'''
# @Author       : Chr_
# @Date         : 2020-07-30 17:50:27
# @LastEditors  : Chr_
# @LastEditTime : 2021-11-19 11:51:55
# @Description  : 网络模块,负责网络请求
'''

import time
import random
import logging
import traceback
from typing import Tuple
from requests import Session, Response
from json import JSONDecodeError
from urllib.parse import urlparse

from .static import HEYBOX_VERSION, Android_UA, iOS_UA, URLS
from .static import CommentType, ReportType
from .utils import gen_nonce_str, encrypt_data, b64encode, rsa_encrypt, gen_random_str
from .error import ClientException, Ignore, UnknownError, TokenError, AccountLimited


class Network():
    __session = Session()
    __session.headers = {}
    __headers = {}
    __cookies = {}
    __params = {}
    __heybox_id = 0
    __sleep_interval = 1.0
    __auto_report = False
    __rpc_server = ''

    logger = logging.getLogger('-')

    def __init__(self, account: dict, hbxcfg: dict, debug: bool):
        super().__init__()

        try:
            os_type = account.get('os_type') or hbxcfg.get('os_type', 1)
            os_version = account.get('os_version') or hbxcfg.get(
                'os_version', '9')
            channel = account.get('channel') or hbxcfg.get(
                'channel', 'heybox_yingyongbao')
            sleep_interval = hbxcfg.get('sleep_interval', 1)
            auto_report = hbxcfg.get('auto_report', True)
            heybox_id = account.get('heybox_id', -1)
            imei = account.get('imei', gen_random_str(16))
            pkey = account.get('pkey', None)
        except (AttributeError, KeyError):
            raise ClientException('传入参数类型错误')

        self.__headers = {'Referer': 'http://api.maxjia.com/',
                          'User-Agent': Android_UA if os_type == 1 else (iOS_UA % os_version),
                          'Host': 'api.xiaoheihe.cn', 'Connection': 'Keep-Alive',
                          'Accept-Encoding': 'gzip'}
        if pkey:
            self.__cookies = {'pkey': pkey}
        self.__params = {'heybox_id': heybox_id, 'imei': imei,
                         'os_type': 'Android' if os_type == 1 else 'iOS',
                         'os_version': os_version, 'version': HEYBOX_VERSION, '_time': '',
                         'hkey': '', 'nonce': '', 'channel': channel}
        if os_type == 2:  # 模拟IOS客户端
            self.__params.pop('channel')

        log_level = 10 if debug else 20
        log_format = '%(asctime)s [%(levelname)s][%(name)s]%(message)s'
        log_time = '%H:%M:%S'
        logging.basicConfig(level=log_level,
                            format=log_format,
                            datefmt=log_time)

        self.__heybox_id = heybox_id
        self.__sleep_interval = sleep_interval
        self.__auto_report = auto_report
        self.__rpc_server = hbxcfg.get('rpc_server','http://localhost:9000/encode')
        self.logger = logging.getLogger(str(heybox_id))
        self.logger.debug(f'网络模块初始化完毕, 适配版本为{HEYBOX_VERSION}')

    def debug(self):
        '''
        仅供调试
        '''
        pass

    @property
    def heybox_id(self):
        '''
        获取heybox_id
        '''
        return(self.__heybox_id)

    def data_report(self, rtype: int, value: tuple = None) -> bool:
        '''
        模拟客户端汇报数据

        参数:
            rtype: 汇报模板,参见status.ReportType
            value: 根据模板不同有不同的作用
        返回:
            bool: 操作是否成功
        '''

        return False

        if rtype == ReportType.Source:
            # 并未完成
            return(False)
            p = {'type': 13}
            d = {"source": [{'pageID': '1'}, {'pageID': '12'}]}
        elif rtype == ReportType.Quit:
            # 并未完成
            return(False)
            p1 = {'type': 99}
            d1 = {"events": [{"event_id": "203", "time": str(
                int(time.time())), "type": "show"}]}
            p2 = {'type': 100}
            d2 = {"events": [{"event_id": "176", "time": str(
                int(time.time())), "value": 3096}]}
        elif rtype == ReportType.View:
            p = {'type':	9, 'viewTime'	: random.randint(1, 20),
                 'index': value[0], 'h_src': b64encode('news_feeds_-1')	,
                 'link_id':	value[1]}

        url = URLS.DATA_REPORT
        try:
            if rtype == ReportType.Source:
                self.__post_encrypt_without_report(url=url, data=d, params=p)
            elif rtype == ReportType.Quit:
                self.__post_encrypt_without_report(url=url, data=d1, params=p1)
                self.__post_encrypt_without_report(url=url, data=d2, params=p2)
            else:
                self.__get_without_report(url=url, params=p)
            self.logger.debug('模拟客户端上报数据成功')
            return(True)
        except ClientException as e:
            self.logger.error(f'上报数据出错 [{e}]')
            return(False)

    def random_sleep(self, min_t: int, max_t: int):
        '''
        随机延时

        参数:
            min_t: 最短时间
            max_t: 最长时间
        '''
        x = self.__sleep_interval
        if x:
            t = random.randint(min_t, max_t)
            t *= x
            t += random.random()
            self.logger.debug(f'随机延时 {"%.2f" % t} 秒')
            time.sleep(t)
        else:
            self.logger.debug('随机延时已禁用')

    def _login(self, phone: int, password: str) -> Tuple[int, str, str]:
        '''
        使用手机号密码登陆小黑盒,登陆失败返回False
        会把heybox_id设为-1

        参数:
            phone: 手机号
            password: 密码
        返回:
            int: heybox_id
            str: imei
            str: pkey
        '''
        url = URLS.LOGIN
        # 清除登陆凭据信息, 生成随机imei
        self.__cookies = {}
        self.__heybox_id = -1
        imei = gen_random_str(16)
        self.__params['imei'] = imei

        phone_d = rsa_encrypt(f'+86{phone}')
        password_d = rsa_encrypt(password)
        data = {'phone_num': phone_d, 'pwd': password_d}
        try:
            result = self._post(url=url, data=data)
            ad = result['account_detail']
            name = ad['username']
            heybox_id = int(ad['userid'])
            pkey = result['pkey']
            self.logger.debug(f'登录成功,[{name}]@{heybox_id}')
            # 设置登陆凭据
            self.__cookies = {'pkey': pkey}
            self.__heybox_id = heybox_id
            return((heybox_id, imei, pkey))

        except (TokenError, ValueError) as e:
            self.logger.error(f'登录失败 [{e}]')
            return(False)

    def __flash_token(self, url: str) -> int:
        '''
        根据当前时间生成time_和hkey,并存入self._parames中

        参数:
            url: url路径
        返回:
            int: 整数时间戳
        '''
        def url_to_path(url: str) -> str:
            path = urlparse(url).path
            if path and path[-1] == '/':
                path = path[:-1]
            return(path)

        def encode(url: str, nonce: str, t: int) -> str:
            try:
                resp = self.__session.get(
                    url=self.__rpc_server,
                    params={'urlpath': url, 'nonce': nonce, 'timestamp': t}
                )

                if not resp:
                    raise ValueError('访问RPC接口失败')

                return resp
            except ValueError as e:
                print(f'调用RPC服务器失败 {e}')
            ...

        t = int(time.time())
        u = url_to_path(url)
        n = gen_nonce_str(32)
        h = encode(u, n, t)

        p = self.__params
        p['_time'] = t
        p['hkey'] = h
        p['nonce'] = n

        return(t)

    def __check_status(self, jd: dict):
        '''
        检查json字典,检测到问题抛出异常

        参数:
            jd:json字典
        '''
        try:
            status = jd['status']
            if status == 'ok':
                return (True)
            elif status == 'ignore':
                raise Ignore
            elif status == 'failed':
                msg = jd['msg']
                if msg in ('操作已经完成', '不能进行重复的操作哦',
                           '不能重复赞哦', '不能给自己的评价点赞哟',
                           '自己不能粉自己哦', '您已经加入了房间',
                           '操作已完成',
                           ''):
                    raise Ignore

                elif msg in ('抱歉,没有找到你要的帖子',
                             '操作失败', 'error link_id',
                             '错误的帖子', '错误的用户',
                             '该帖已被删除', '帖子已被删除',
                             '加入房间失败，已到开奖时间',
                             '该用户已注销', '数据上报失败'):
                    raise ClientException(f'客户端出错@{msg}')

                elif msg in ('用户名格式错误', '用户名不存在'
                             '密码格式错误',
                             '用户名或密码错误或者登录过于频繁',
                             '你的账号已被限制访问，如有疑问请于管理员联系'):
                    raise TokenError(f'登录失败@{msg}')

                elif msg in ('您今日的赞赏次数已用完', '您今日的关注次数已用完'):
                    raise AccountLimited('当前账号关注次数或者点赞次数用尽')

                elif msg == '系统时间不正确':
                    raise OSError('系统时间错误')

                elif msg == '出现了一些问题，请稍后再试':
                    self.logger.error(f'返回值: {jd}')
                    self.logger.error('出现这个错误的原因未知,有可能是访问频率过快,请过一会再重新运行脚本')
                    raise UnknownError(f'返回值: {jd}')

                elif msg == '参数错误':
                    self.logger.error(f'返回值:{jd}')
                    self.logger.error('请求参数错误, 有可能是小黑盒更新了, 请更新脚本')
                    raise UnknownError(f'返回值:{jd}')

                self.logger.error(f'未知的返回值: {msg}')
                self.logger.error('请将以下内容发送到chr@chrxw.com')
                self.logger.error(f'返回值: {jd}')
                self.logger.error(f'{traceback.print_stack()}')
                raise UnknownError(f'未知的返回值: {msg}')
            elif status == 'relogin':
                raise TokenError('账号凭据过期,请重新登录')
        except (KeyError, ValueError, NameError, AttributeError):
            self.logger.debug(f'JSON格式错误')
            self.logger.debug(f'{jd}')
            self.logger.error(f'{traceback.format_exc()}')
            raise UnknownError(f'未知的返回值[{jd}]')

    def __get_json(self, resp: Response) -> dict:
        '''
        把Response对象转成json字典,出错返回{}

        参数:
            resp: Response对象
        返回:
            dict: json字典
        '''
        try:
            jd = resp.json()
            self.logger.debug(f'返回值 [{jd}]')
            self.__check_status(jd)
            return(jd)
        except JSONDecodeError:
            self.logger.warning(f'[*] JSON解析失败 [{resp.text}]')
            return({})

    def _get(self, url: str, params: dict = None,  headers: dict = None,
             cookies: dict = None, key: str = 'result') -> dict:
        '''
        GET方法发送请求

        参数:
            url: URL
            [params]: 请求参数,会添加到self._params前面
            [headers]: 请求头,会替换self._headers
            [cookies]: 请求头,会替换self._cookies
            [key]: 要返回的数据键名,默认为'result',留空表示返回原始json
        返回:
            dict: json字典
        '''
        result = self.__get_without_report(
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            key=key)

        if self.__auto_report and params:
            i = params.get('index')
            l = params.get('link_id')
            if i and l and random.random() <= 0.7:  # 70%概率触发
                self.data_report(ReportType.View, (i, l))

        return(result)

    def _post(self, url: str, params: dict = None, data: dict = None, headers: dict = None,
              cookies: dict = None, key: str = 'result') -> dict:
        '''
        POST方法发送请求

        参数:
            url: URL
            [params]: 请求参数,会添加到self._params前面
            [data]: 请求体
            [headers]: 请求头,会替换self._headers
        返回:
            Response: 请求结果
        '''
        self.__flash_token(url)
        p = {**(params or {}), **self.__params}
        d = data or {}
        h = headers or self.__headers
        c = cookies or self.__cookies
        resp = self.__session.post(
            url=url, params=p, data=d, headers=h, cookies=c
        )
        result = self.__get_json(resp)

        if self.__auto_report:
            if random.random() <= 0.1:  # 10%的概率触发
                self.data_report(ReportType.Source, None)

        if key:
            result = result.get(key)
        return(result)

    def _post_encrypt(self, url: str, data: dict, params: dict = None, headers: dict = None,
                      cookies: dict = None, key: str = 'result') -> dict:
        '''
        POST方法发送加密请求,data参数将被加密

        参数:
            url: URL
            [data]: 请求体
            [params]: 请求参数,会添加到self._params前面
            [headers]: 请求头,会替换self._headers
        返回:
            Response: 请求结果
        '''
        result = self.__post_encrypt_without_report(
            url=url,
            data=data,
            params=params,
            headers=headers,
            cookies=cookies,
            key=key)

        if self.__auto_report:
            if random.random() <= 0.1:  # 10%的概率触发
                self.data_report(ReportType.Source, None)

        if key:
            result = result.get(key)
        return(result)

    def __get_without_report(self, url: str, params: dict = None,  headers: dict = None,
                             cookies: dict = None, key: str = 'result') -> dict:
        '''
        GET方法发送请求[不自动调用report]

        参数:
            url: URL
            [params]: 请求参数,会添加到self._params前面
            [headers]: 请求头,会替换self._headers
            [cookies]: 请求头,会替换self._cookies
            [key]: 要返回的数据键名,默认为'result',留空表示返回原始json
        返回:
            dict: json字典
        '''
        self.__flash_token(url)
        p = {**(params or {}), **self.__params}
        h = headers or self.__headers
        c = cookies or self.__cookies
        resp = self.__session.get(
            url=url, params=p, headers=h, cookies=c
        )
        result = self.__get_json(resp)

        if key:
            result = result.get(key)
        return(result)

    def __post_encrypt_without_report(self, url: str, data: dict, params: dict = None, headers: dict = None,
                                      cookies: dict = None, key: str = 'result') -> dict:
        '''
        POST方法发送加密请求,data参数将被加密[不自动调用report]

        参数:
            url: URL
            [data]: 请求体
            [params]: 请求参数,会添加到self._params前面
            [headers]: 请求头,会替换self._headers
        返回:
            Response: 请求结果
        '''
        t = self.__flash_token(url)
        p = {**(params or {}), 'time_': t, **self.__params}
        h = headers or self.__headers
        c = cookies or self.__cookies
        d = encrypt_data(data, t)
        resp = self.__session.post(
            url=url, params=p, data=d, headers=h, cookies=c
        )
        result = self.__get_json(resp)
        if key:
            result = result.get(key)
        return(result)

    def _send_comment(self, linkid: int, message: str, ctype: int = 0, index: int = 0) -> bool:
        '''
        发送评论,通用

        参数:
            linkid: 文章id
            message: 文字评论内容
            [ctype]: 评论类型,参加static.CommentType
            [index]: 文章索引,模拟客户端行为
        返回:
            操作是否成功
        '''
        url = URLS.CREATE_COMMENT

        d = {'link_id': linkid, 'text': message,
             'root_id': -1, 'reply_id': -1, 'imgs': None}
        if ctype == CommentType.Roll:
            p = {}
        elif ctype in (CommentType.News, CommentType.Community):
            if ctype == CommentType.Community:
                hsrc = b64encode('bbs_app_feeds')
            elif ctype == CommentType.News:
                hsrc = b64encode('news_feeds_-1')
            p = {'h_src': hsrc, 'index': index}
        else:
            raise ValueError('ctype错误')
        try:
            result = self._post(url=url, data=d, params=p)
            self.logger.debug('发送评论成功')
            return(True)
        except ClientException as e:
            self.logger.error(f'发送评论出错 [{e}]')
            return(False)

    # def _get_comments(self, linkid: int, amount: int = 30,
    #                   author_only: bool = False) -> list:
    #     '''
    #     获取评论,通用

    #     参数:
    #         linkid: 文章id
    #         [amount]: 要拉取的数量
    #     返回:
    #         list: [(commintid,text,userid)…],评论列表
    #     '''
    #     pass

    # def _like_content(self):
    #     '''
    #     点赞,通用
    #     '''
    #     pass
