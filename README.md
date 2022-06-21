# PYXIAOHEIHE

[![Codacy Badge][codacy_b]][Codacy] [![PyPI][pypi_v_b]][pypi] [![License][license_b]][License]  

停止维护本仓库，可以试试 C# 实现的小黑盒客户端 [Xiaoheihe_CShape](https://app.codacy.com/gh/chr233/Xiaoheihe_CShape)

一个使用requests库完成的小黑盒客户端, 覆盖了30%左右的客户端功能.

例程: [XHH_AUTO][xhh_auto]

> 使用第三方客户端有封号风险, 后果自负.

## 安装

```bash
>$ pip install pyxiaoheihe
```

## 使用

```python
from pyxiaoheihe import HeyBoxClient

account={'heybox_id': 1234, 'imei': '0000', 'pkey': 'TEST'}
hbxcfg= {'channel': 'heybox_yingyongbao', 'os_type': 1, 'os_version': '10', 'sleep_interval': 1.0, 'auto_report': True}
debug=False

hbc = HeyBoxClient(account,hbxcfg,debug)

# 获取首页新闻
rs = hbc.get_news(5)
print(rs)
# [(44856495, '8月28日20：00，《原神》公测前瞻直播即将开启', '旅行者们大家好~又到了预告时间。……', 21569078),
#  (44837161, 'steam商店限时免费领取《Destin...Fate/命运之幽》', '领取链接：《Destiny or Fa……', 7386593),
#  (44855908, '剧场版《Fate[HF]》最终章票房突破...藤惠生日联动活动公开', '剧场版《Fate[HF]》……', 20495862),
#  (44741441, '关于盒友杂谈的杂谈', '我已经不记得使用小黑盒多久了，从签到天数...兴趣的小标题……', 16243337),
#  (44856136, '[Wallpaper Engine][东...ect]视频壁纸推荐', '个人觉得比较好康的视频壁纸，名字……', 18852508)]
```

> 部分`API`需要真实的账号信息才可用
> 有关`heybox_id`, `imei`, `pkey`的获取方法可以参考[XHH_AUTO][xhh_auto]中的教程
> 或者使用`HeyBoxClient._login()`方法自动获取（会顶掉原客户端的登陆）

[codacy_b]: https://app.codacy.com/project/badge/Grade/ec2842e7b7a94265869679c6620fb109
[codacy]: https://www.codacy.com/manual/chr233/pyxiaoheihe?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=chr233/pyxiaoheihe&amp;utm_campaign=Badge_Grade
[pypi_v_b]: https://img.shields.io/pypi/v/pyxiaoheihe
[pypi]: https://pypi.org/project/pyxiaoheihe/
[license]: https://github.com/chr233/pyxiaoheihe/blob/master/license
[license_b]: https://img.shields.io/github/license/chr233/pyxiaoheihe
[xhh_auto]: ttps://github.com/chr233/xhh_auto
