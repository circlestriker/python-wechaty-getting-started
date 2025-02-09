"""
Python Wechaty - https://github.com/wechaty/python-wechaty
Authors:    Huan LI (李卓桓) <https://github.com/huan>
            Jingjing WU (吴京京) <https://github.com/wj-Mcat>
2020 @ Copyright Wechaty Contributors <https://github.com/wechaty>
Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import asyncio
import time
import threading
import pymysql
import json
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler


import MySQLdb
import json

import base64


#import logging

from urllib.parse import quote

from dataclasses import asdict
from wechaty_puppet import MessageType
from wechaty import (
    Contact,
    FileBox,
    Message,
    Wechaty,
    MiniProgram,
    ScanStatus,
    Room,
)


scheduler = AsyncIOScheduler()

conversationDict = {}
keyword2reply = {
    #'婚宴酒店':'欢迎预订滨江花园婚宴酒店: https://mp.weixin.qq.com/s/A0FTDhL69znSE7tAsPu4wQ',
    '段永平':'段永平投资理念摘要: https://mp.weixin.qq.com/s/72920b6lPy_vK3VFxD6Hfw',
    '投资理念':'段永平投资理念摘要: https://mp.weixin.qq.com/s/72920b6lPy_vK3VFxD6Hfw',
    '睡不好':'建文帝常遇春10-运动治疗失眠:https://mp.weixin.qq.com/s/hBGViksSWDIFNOqxSju6mg',
    '医生':'医人和医电脑的异同:https://mp.weixin.qq.com/s/N_mv53U5lV7HxGwLeeUiQA',
    '凤凰涅槃':'湘江血战之凤凰涅槃: https://mp.weixin.qq.com/s/eIfjWgIPx0GHnk9UYbmzlw',
    '湘江':'湘江血战之凤凰涅槃: https://mp.weixin.qq.com/s/eIfjWgIPx0GHnk9UYbmzlw',
    '情为何物':'问世间情(钱)为何物? https://mp.weixin.qq.com/s/BawHmnXKdlQmRox-Jf-FJg',
    '网瘾':'乔峰援助7-网瘾少女沉迷抖音(上):https://mp.weixin.qq.com/s/Jhev3vesiO2ZU1DGSF6tMw',
    '沉迷':'乔峰援助7-网瘾少女沉迷抖音(上):https://mp.weixin.qq.com/s/Jhev3vesiO2ZU1DGSF6tMw',
    '本泽马':'都怪佛陀, 都怪本泽马: https://mp.weixin.qq.com/s/zY-RZnaoRkUNt0SSoE4Oww',

    '救人':'救人难-大舅和佛祖、孔子打牌 https://mp.weixin.qq.com/s/BKc16fKFWZ8Qk5MObJDzRg',
    '阎王':'阎王见乔峰https://mp.weixin.qq.com/s/vZaMIXcVYCfoY9OwQ_dCPA',
    '恋爱':'悟空图书馆-林黛玉贾宝玉的美好感情https://mp.weixin.qq.com/s/6f3Japv1VNWFBTixYUBdHQ',
    '老家公益':'公益悟空图书馆-老家可以更团结点https://mp.weixin.qq.com/s/JuBVLMuR2I7Fjc_pjTloXw',
    '乔峰原型':'乔峰的原型是谁:https://mp.weixin.qq.com/s/Pvip07l6tPRftJo3JS7XkQ',
    '总统':'扫大街不一定比当总统差 https://mp.weixin.qq.com/s/DDSoOrfDl3N-6f6Mq1HNng',
    '扫大街':'扫大街不一定比当总统差 https://mp.weixin.qq.com/s/DDSoOrfDl3N-6f6Mq1HNng',
    '地狱':'地狱是天堂的必由之路-悟空图书馆<<金刚经>> https://mp.weixin.qq.com/s/QYByIooVzZEfbSrm4brPSw',
    '佛祖':'宝宝是怎么把爸妈逼成佛祖的? https://mp.weixin.qq.com/s/J-mk7H71G_10kYP-qlyMKA',
    '性格':'悟空图书馆-性格决定命运? https://mp.weixin.qq.com/s/bQS7B_9wFSFg-LlrAq-j1w',
    '心经':'谁能狂过观音? 观音是谁? https://mp.weixin.qq.com/s/E49FA0e1rOBQv-iQ1H_9IA',
    '观音':'谁能狂过观音? 观音是谁? https://mp.weixin.qq.com/s/E49FA0e1rOBQv-iQ1H_9IA',
    '霍去病':'舍生忘死的霍去病-匈奴未灭何以家为:https://mp.weixin.qq.com/s/Mgpjxi_l87S2r0_hWumomw',
    '双相':'佛祖99%是因抑郁症而觉悟:https://mp.weixin.qq.com/s/GJ4TxPYjCAiw1jqrjOH2Mg',
    '躁狂':'仁心济世, 度一切苦厄--向世界级难题宣战:https://mp.weixin.qq.com/s/IEOMHOFeWSTE9J8C6Fjsaw',
    '英雄':'那些舍己为人的英雄们:https://mp.weixin.qq.com/s/K7aPrJIl07nvVUJ8BaFuzQ',
    '武则天':'武则天的好色和她的<<金刚经>>开经偈:https://mp.weixin.qq.com/s/sHobaBPxpkI5vqXV_cUnmw',
    '安贫乐道':'安贫乐道：人生信仰的至高境界:https://mp.weixin.qq.com/s/A06F1obGVsnZYH7tegyFTw',
    '夜王':'"夜王"对决"地藏王":https://mp.weixin.qq.com/s/pIlNEKVt5vx3rQjloOiolg',
    '地藏王':'"夜王"对决"地藏王":https://mp.weixin.qq.com/s/pIlNEKVt5vx3rQjloOiolg',
    '色即是空':'公益“悟空图书馆”—天龙八部“王霸雄图，色即是空”:https://mp.weixin.qq.com/s/e7OY4M7CpPewkrpfMSD7iA',
    '天龙八部':'天龙八部之为什么大苦大卑之人达最高境界:https://mp.weixin.qq.com/s/zfdrjUXpqjbW26WLSTIfPw',
    '西域':'公益“悟空图书馆”—好书之<<大唐西域记>>:https://mp.weixin.qq.com/s/yANO3CwmiyYyq7XEYjXoBw',
    '段正淳':'中大出了个"段正淳"? https://mp.weixin.qq.com/s/BfuLESVNvoHoY2tgV0CjYA',
    '怕鬼':'不少人经历过怕鬼，多少人希望遇见鬼? https://mp.weixin.qq.com/s/i4A3JsRNg61xgCtFghpjpw',
    '姜大卫':'一手三把刀:https://mp.weixin.qq.com/s/rGTy8LHJ0ANjJr3nmsXO_Q',
    '西游记':'西游记里的无字真经也是真经:https://mp.weixin.qq.com/s/7Toz-NdW_pTBQrbeINQVWg',
    '大悲咒':'大悲咒的殊胜以及和国歌的异曲同工:https://mp.weixin.qq.com/s/3hiCu9px42oVq7eds6HimQ',

#这辈子, 我的大学https://mp.weixin.qq.com/s/lvSCrG6V4Z9fWGAVFp-q9g

    '刘邦':'刘邦之不怕死和"知人者智，自知者明"https://mp.weixin.qq.com/s/vuSqhez6G2eASr7N8J3qlA',
    
    #悟空援助
    '孔子':'救人难-大舅和佛祖、孔子打牌:https://mp.weixin.qq.com/s/BKc16fKFWZ8Qk5MObJDzRg',
    '蚊子':'蚊子不咬谁:https://mp.weixin.qq.com/s/iMP-MJr4SYSw6nCMb09xsw',
    '鬼神':'初九祭祖-何为鬼神:https://mp.weixin.qq.com/s/NDRrjhqYL37TZQj0XodqxA',
    '祭祖':'初九祭祖-何为鬼神:https://mp.weixin.qq.com/s/NDRrjhqYL37TZQj0XodqxA',
    '剃光头':'创业和出家人为什么要剃光头:https://mp.weixin.qq.com/s/_anmJ2qAvJE5zdhRZHDgsQ',
    '创业难':'创业和出家人为什么要剃光头:https://mp.weixin.qq.com/s/_anmJ2qAvJE5zdhRZHDgsQ',
    '出家人':'创业和出家人为什么要剃光头:https://mp.weixin.qq.com/s/_anmJ2qAvJE5zdhRZHDgsQ',
    '考研':'执着考研和家庭冲突(上):https://mp.weixin.qq.com/s/6GBQkqS-hyEM1NNWawVpwg',
    '家庭冲突':'执着考研和家庭冲突(上):https://mp.weixin.qq.com/s/6GBQkqS-hyEM1NNWawVpwg',
    '状态不好':'帮助状态不好朋友的错误言行:https://mp.weixin.qq.com/s/3WvrpRB1-AjUao7d7-MJ5A',
    '爱情':'老家的爱情故事https://mp.weixin.qq.com/s/FMG_M15ncgo-xe6mc58GHA',
    '坑爹':'有人救爹，有人坑爹:https://mp.weixin.qq.com/s/Kd7d7Kd-ANaNHs6eSLvOMQ',
    '仗义':'仗义每从屠狗辈:https://mp.weixin.qq.com/s/NbHWlEOqro6h6gGD8bVLqg',
    '狭义':'如何发掘宝宝的侠义精神:https://mp.weixin.qq.com/s/LjIugX_FrDv65pyVPTRb2Q',
    '马云':'马云和阿里到底懂不懂金庸侠义精神？https://mp.weixin.qq.com/s/pW_7jnz98Nqrl1nBj08LrQ',
    #编程
    '观察者模式':'C++实现观察者模式:https://mp.weixin.qq.com/s/fQ3BFGoiTvb4mKQueb7hWQ',
    '腾讯加班':'囧该复活吗-从应届生反映腾讯加班说起:https://mp.weixin.qq.com/s/-26Dbt-ydxJdbWRyxy8LJw',
    '狮岩':'初一游狮岩之保平安书:https://mp.weixin.qq.com/s/_2ARdiHwCRcmPaoizHTYxw',
    #文化
    '武平一中':'静以修身，俭以养德-纪念母校武平一中老师:https://mp.weixin.qq.com/s/DTZCtVGlkvfLuEAAvj5JdQ',
    '静以修身':'静以修身，俭以养德-纪念母校武平一中老师:https://mp.weixin.qq.com/s/DTZCtVGlkvfLuEAAvj5JdQ',
    '达摩':'达摩九年面壁助力科研:https://mp.weixin.qq.com/s/XpfwRBT3-GsD_SCtD80E-g',
    '踢法':'不累的踢法:https://mp.weixin.qq.com/s/QUt0t7k0ZeJOL6VF8y8_vQ',
    '刘备':'刘备超越了刘邦:https://mp.weixin.qq.com/s/tw3s4AbtivBS1KYEFDxlRg',
    '菩萨':'母亲节之父母犹如子女的菩萨:https://mp.weixin.qq.com/s/v-dE_X2SQMVnZVNy0fVA0g',
    '佛祖':'佛陀的悲泣: 谁最希望没有宗教崇拜?: https://mp.weixin.qq.com/s/bcXmgClhHpasxVGPNPdNOQ',
    '阿弥陀佛':'佛陀的悲泣: 谁最希望没有宗教崇拜?: https://mp.weixin.qq.com/s/bcXmgClhHpasxVGPNPdNOQ',
    '职称':'高级职称和三甲:https://mp.weixin.qq.com/s/Cf1FO7L9UH_Gllgb9Wt-8Q',
    '佛陀':'马克思和佛陀:https://mp.weixin.qq.com/s/OWhQL3i3bqYf9cHiqD0cYA',
    '中山大学':'中山大学的风水:https://mp.weixin.qq.com/s/dwxl_7LuzjX_VuAuBzoQnQ',
    '离婚':'离婚大魔王和甩手掌柜:https://mp.weixin.qq.com/s/gA7sGgFzb01jcHrFrcEEyg',
    '孔子':'孔子的遗憾-人生不够苦:https://mp.weixin.qq.com/s/ZdFeyqHdisdlArz1p6D6CQ',
    '无畏':'公益悟空图书馆-无畏布施:https://mp.weixin.qq.com/s/_xUjz1sWzJ183tqAVOdCAQ',
    '布施':'公益悟空图书馆-无畏布施:https://mp.weixin.qq.com/s/_xUjz1sWzJ183tqAVOdCAQ',
    '长夜':'[悟空图书馆]-新冠如长夜:https://mp.weixin.qq.com/s/hvtpV04KHq25sXvWO7pJXA',
    '观世音':'比特币和观世音:https://mp.weixin.qq.com/s/dAjozxD7B90BpY7WLmnasg',
    '道法自然':'[花魂黛玉]道法自然，把握阴阳:https://mp.weixin.qq.com/s/1xOiudL2S0R2n_Qblo_k5w',
    '顽疾':'传统文化解决多年顽疾:https://mp.weixin.qq.com/s/BfeYHVFCx40ApIkr0wk9Ig',
    '比特币':'红楼梦和比特币:https://mp.weixin.qq.com/s/-uJDmUmE8-z0egupBQzhUA',
    '圣贤':'一点实践: 圣贤思想如何帮助人？:https://mp.weixin.qq.com/s/tVPmb9spfr8Zq0pkB8HUrQ',
    '传统文化':'传统文化救人的又一例子:https://mp.weixin.qq.com/s/IY4t0cz1gLob82p6Etx24Q',
    '尊重老师':'老师如再生父母，学生如生命延续:https://mp.weixin.qq.com/s/xLQlFfumIqzWDV0oBzUf5w',
    '悟空的原型':'[悟空图书馆]-悟空的原型是谁:https://mp.weixin.qq.com/s/PUvgZzbxq6NN-F5GEMlk0w',
    '慧能':'慧能神秀和诸葛亮司马懿:https://mp.weixin.qq.com/s/lmJ69lWD7dkF4pU5_5IjJg',
    '司马懿':'慧能神秀和诸葛亮司马懿:https://mp.weixin.qq.com/s/lmJ69lWD7dkF4pU5_5IjJg',
    '医德':'德不近佛者不可以为医在说什么？:https://mp.weixin.qq.com/s/6edwtylKmsZmQ7Zg_6MRvg',
    '雪诺':'黑暗牙签和光明使者:https://mp.weixin.qq.com/s/FyfAF2DNnn5NvPVOZBl1Zg',
    '光明使者':'黑暗牙签和光明使者:https://mp.weixin.qq.com/s/FyfAF2DNnn5NvPVOZBl1Zg',
    '黄帝内经':'黄帝内经之不妄作劳:https://mp.weixin.qq.com/s/f0z9e6i0swFjKwqJNYchkA',
    #金庸武侠
    '张三丰':'太极张三丰:https://mp.weixin.qq.com/s/W5yH_H8aG8TC_KQAHMgEYw',
    '段誉':'段誉的舍和慕容复的求:https://mp.weixin.qq.com/s/3NF4RhvCFs9PIWpQmAKC2A',
    '恋爱':'神仙姐姐恋爱之离苦得乐:https://mp.weixin.qq.com/s/PMAxqZ6ElwSMnHtMyilDUg',
    '神仙姐姐':'神仙姐姐恋爱之离苦得乐:https://mp.weixin.qq.com/s/PMAxqZ6ElwSMnHtMyilDUg',
    #红楼梦
    '布施':'悟空图书馆之红楼梦-细公公布施和宝玉化缘:https://mp.weixin.qq.com/s/JvPVqZ3Bh8zShnVik8chkw',
    '啦啦队':'林黛玉尤三姐的牺牲和啦啦队鼻祖:https://mp.weixin.qq.com/s/YsiPcEgeaadlsJHSIaImMg',
    '李德胜':'悟空图书馆之红楼梦-警幻仙子是李德胜的引路人? https://mp.weixin.qq.com/s/zsRiSxP_8ntDHaWZWBUHJQ',
    '警幻仙子':'悟空图书馆之红楼梦-警幻仙子是李德胜的引路人? https://mp.weixin.qq.com/s/zsRiSxP_8ntDHaWZWBUHJQ',
    '张国荣':'张国荣遇见宝玉能不能逆天改命:https://mp.weixin.qq.com/s/w5vzBJDMSdU2oJp5hZpoIA',
    '尤三姐':'红楼梦最俊美的女子为何要吃斋?: https://mp.weixin.qq.com/s/GrzkWiLmHuIutIshT4evWA',
    '吃素':'红楼梦最俊美的女子为何要吃斋?: https://mp.weixin.qq.com/s/GrzkWiLmHuIutIshT4evWA',
    '吃斋':'红楼梦最俊美的女子为何要吃斋?: https://mp.weixin.qq.com/s/GrzkWiLmHuIutIshT4evWA',
    '曹雪芹':'曹雪芹暮年苦不苦？:https://mp.weixin.qq.com/s/Sk5QErgtiwXh475UiZRZXw',
    '黛玉':'黛玉的美是怎样的？:https://mp.weixin.qq.com/s/otEsaw2YZk1QKKrO2PeCjg',
    '凤姐':'红楼梦算命之凤姐:https://mp.weixin.qq.com/s/0yYnnSxPv_-cYycp26zRZg',
    '妙玉':'妙玉不妙在哪里？:https://mp.weixin.qq.com/s/dcj_crsMdSOVn8KuQvmQxQ',
    '恋爱':'林黛玉贾宝玉的美好感情:https://mp.weixin.qq.com/s/6f3Japv1VNWFBTixYUBdHQ',
    '拍拖':'林黛玉贾宝玉的美好感情:https://mp.weixin.qq.com/s/6f3Japv1VNWFBTixYUBdHQ',
    #焦虑#
    '绝望':'以毒攻毒:绝望中寻找希望:https://mp.weixin.qq.com/s/WlSeqHjVj4id6odDWGQeXQ',
    '父母吵架':'慕容复骂老爹:https://mp.weixin.qq.com/s/0XlKT4lsIpVvHGyACZHkvQ',
    '慕容复':'宝玉和慕容复为什么都魔怔?:https://mp.weixin.qq.com/s/A4glTxB6omaBddUFcD4eFg',
    '玄奘':'唐太宗心理咨询玄奘:https://mp.weixin.qq.com/s/XtplxMxYVlaSFKE6Qbw3Nw',
    #'桂林':'桂林遇神医:https://mp.weixin.qq.com/s/kqt9pr_bJ-wImkOdqPmF6w',
    '神医':'桂林遇神医:https://mp.weixin.qq.com/s/kqt9pr_bJ-wImkOdqPmF6w',
    '加班太多':'加班太多，本来谁可能帮到毛星云?: https://mp.weixin.qq.com/s/MZuuCL9QUkyIFdw6tXT4Hg',
    #'抑郁症':'可以参考这个-佛祖因抑郁症而觉悟:https://mp.weixin.qq.com/s/GJ4TxPYjCAiw1jqrjOH2Mg',
    '抑郁症':'世外高人治抑郁-曹政的知见障:https://mp.weixin.qq.com/s/CMFAGjhDv_6UH8w16aN7hQ',
    '跳楼':'谁来帮助医学院逝去的学生? https://mp.weixin.qq.com/s/U9MdAbw8958MTVh9KeAoAQ',
    '抑郁':'供参考-康复的例子: 顿悟和康复:https://mp.weixin.qq.com/s/Qdlm3eb_J482jmo5eMvrCA',
    #'抑郁':'谁来帮助医学院逝去的学生? https://mp.weixin.qq.com/s/U9MdAbw8958MTVh9KeAoAQ',
    #'抑郁':'帮助状态不好朋友的错误言行:https://mp.weixin.qq.com/s/3WvrpRB1-AjUao7d7-MJ5A',
    # '抑郁':'抑郁焦虑可以参考这个-金刚经为什么可以救人:https://mp.weixin.qq.com/s/d0e0Ns7OgqqqMYhqncwLYw',
    # '焦虑':'焦虑可以参考这个, 看书康复的例子:https://mp.weixin.qq.com/s/kkX1I25oM5-UGcYoFqd2QA',
    #'焦虑':'供参考-不放弃，就有康复的希望:https://mp.weixin.qq.com/s/O2nb-450640ankJqKkjsDA',
     '焦虑':'抑郁焦虑可以参考这个-金刚经为什么可以救人:https://mp.weixin.qq.com/s/d0e0Ns7OgqqqMYhqncwLYw',
    '学佛':'可以参考这个-佛祖因抑郁症而觉悟:https://mp.weixin.qq.com/s/GJ4TxPYjCAiw1jqrjOH2Mg',
    '失眠':'失眠可以参考这个-数息法治失眠:https://mp.weixin.qq.com/s/SQfaegwTa0gCu2mjfUkezg',
    #足球#
    '伤病':'伤病左右的友谊赛:https://mp.weixin.qq.com/s/tVPmb9spfr8Zq0pkB8HUrQ',
    '齐达内':'球场师徒缘:https://mp.weixin.qq.com/s/wq5M7busUmL8h1skLPuJ5Q',
    '无间道':'绿茵无间道:https://mp.weixin.qq.com/s/ntJIW4UZhSDQBnuw9Lgsag',
    '绿茵':'绿茵无间道:https://mp.weixin.qq.com/s/ntJIW4UZhSDQBnuw9Lgsag',
    '少林足球':'少林足球之无所住踢球:https://mp.weixin.qq.com/s/yOhLvqbUJ1IbaevDISKtlA',
    '无所住':'少林足球之无所住踢球:https://mp.weixin.qq.com/s/yOhLvqbUJ1IbaevDISKtlA',
    '传球':'舍得—费曼学习法和传球:https://mp.weixin.qq.com/s/rTpG5qMfhChXQ_PjGlrxuw',
    '登山':'寒啸登山龙思踢球之亢龙有悔:https://mp.weixin.qq.com/s/gTA_hsU66JKiSyTl9RHdxQ',
    '余地':'寒啸登山龙思踢球之亢龙有悔:https://mp.weixin.qq.com/s/gTA_hsU66JKiSyTl9RHdxQ',
    '射门':'降龙十八掌和大罗的射门:https://mp.weixin.qq.com/s/QIBL9OHiDjGsWTF-mDjflg',
    '大罗':'降龙十八掌和大罗的射门:https://mp.weixin.qq.com/s/QIBL9OHiDjGsWTF-mDjflg',
    '内马尔':'内马尔之钱太多不是好事:https://mp.weixin.qq.com/s/MxxGYp6YzOFtr5AXJUodHQ',
    '河西球星':'兄弟缘之河西球星录(上):https://mp.weixin.qq.com/s/_FMHlNfj9IWJYLLfTOVHyA',
    '苏神':'从苏牙到苏神https://mp.weixin.qq.com/s/PC18UGOs5YxZrhvCDI_IMw',
    '防守':'防守型球星多的好处:https://mp.weixin.qq.com/s/s_Qfap5motEBSm-auc2v9g',
    '膝盖伤':'盘腿治膝伤:https://mp.weixin.qq.com/s/6OvreXJz3UFwuTPqb-2Lug',
    '脚踝伤':'盘腿治膝伤:https://mp.weixin.qq.com/s/6OvreXJz3UFwuTPqb-2Lug',
    '崴脚':'盘腿治膝伤:https://mp.weixin.qq.com/s/6OvreXJz3UFwuTPqb-2Lug',
    '后卫':'众人之所恶的边后卫:https://mp.weixin.qq.com/s/qEj9wNuSLP-uwhGJxNn_pA',
    '半月板':'鼓楼医院关节科不错:https://mp.weixin.qq.com/s/JH234VpbQmW23NcBduZbJA'
    }

#连接数据库
connEs = pymysql.connect(host="127.0.0.1", user="root", passwd="Qlcx1997", db='keywords', charset='utf8', port=3306)  #和mysql服务端设置格式一样（还可设置为gbk, gb2312）
conn = pymysql.connect(host="120.77.62.108", user="hscl", passwd="Huishuchuanglian2022banzhu", db='banzhutest', charset='utf8', port=3306)  #和mysql服务端设置格式一样（还可设置为gbk, gb2312）
#创建游标
cursor = conn.cursor()
cursorEs = connEs.cursor()

banzhuRoom = None

bot: Optional[Wechaty] = None

# 生成活动文本链接
def gen_action_textlink(db, actionId):
    action = _load_action_byid(db, actionId)
    baolist = _load_action_baolist(db, action['comboId'])
    textlink = _gen_action_textlink(action, baolist)
    return textlink

# 生成圈子里可用活动s的文本链接
def gen_circle_actions_textlink(db, circleId):
    textlinks = []
    actions = _load_circle_active_actions(db, circleId)
    for action in actions:
        baolist = _load_action_baolist(db, action['comboId'])
        textlink = _gen_action_textlink(action, baolist)
        textlinks.append(textlink)
    return textlinks

# 根据活动信息和报名名单生成活动的文本链接
def _gen_action_textlink(action, baolist):
    title, address, addressName, peopleNum = action['title'], action['address'], action['addressName'], action['peopleNum']
    actionTime, actionEndTime, signUpEndTime = action['actionTime'], action['actionEndTime'], action['signUpEndTime']
    feeType, condition, description = action['feeType'], action['condition'], action['description']
    actionTimeStr = _fmt_datetimes(actionTime, actionEndTime)
    addressStr = '📍%s\n📍%s'%(address, addressName) if address>'' else '线下活动'
    feeStr = _fmt_fees(feeType, condition)
    text_action = '【%s】\n⏱%s\n%s\n%s\n'%(title, actionTimeStr, addressStr, feeStr)
    bao_len = len(baolist)
    bao_limit = '不限' if (peopleNum <= 0 or peopleNum >= 9999) else peopleNum
    text_baohead = '【报名 %d/%s】'%(bao_len, bao_limit)
    text_baolist = ''
    for bao in baolist:
        baono, nick = bao['baono'], bao['nick']
        text_baolist = text_baolist+'%d、%s\r\n'%(baono, nick)
    endTimeStr = signUpEndTime.strftime("%m月%d日 %H点%M分")
    text_endtime = '❗报名截止时间：%s'%(endTimeStr)
    text_desc = '【活动说明】\r\n%s'%(description)
    text_more = '\n更多内容点击下方链接👇👇👇\n\n（请勿直接接龙）打开链接报名：'
    text_more += _fetch_urllink(action['actionId'])
    text_link = '%s\n%s\n%s\n%s\n\n%s\n%s'%(text_action, text_baohead, text_baolist, text_endtime, text_desc, text_more)
    return text_link

#
def _fmt_datetimes(actionTime, actionEndTime):
    weeks = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    fmt = "%m月%d日（{week}） %H:%M"
    timeStr = actionTime.strftime(fmt).format(week=weeks[actionTime.weekday()])
    sameday = (actionTime.year == actionEndTime.year and actionTime.month == actionEndTime.month and actionTime.day == actionEndTime.day)
    timeStr += ' ~ ' + (actionEndTime.strftime("%H:%M") if sameday else actionEndTime.strftime(fmt).format(week=weeks[actionEndTime.weekday()]))
    return timeStr

# 生成费用文本信息
def _fmt_fees(feeType, condition):
    feeStr = '免费' if feeType==2 \
        else '报名后付费' if feeType==1 \
        else '报名时付费'
        # else '💰' if condition<2 \
    return '💰'+feeStr


# 根据活动id获取活动信息
def _load_action_byid(db, actionId):
    fields = ['actionId', 'comboId', 'title', 'address', 'addressName', 'peopleNum'
    , 'createTime', 'actionTime', 'actionEndTime', 'signUpEndTime'
    ,'feeType' , 'condition', 'enableTeam', 'description']
    sql = '''
SELECT ac.actionId, ac.id AS comboId, ac.title, ac.address, ac.addressName, ac.peopleNum
     , ac.createTime, ac.actionTime, ac.actionEndTime, ac.signUpEndTime
     , ac.type as feeType, ac.condition, ac.enableTeam, i.description
FROM banzhu_action a
JOIN banzhu_action_combo ac ON a.id = ac.actionId AND ac.sub = 0 #只要主活动
LEFT JOIN banzhu_action_introduction i ON i.comboId = ac.id AND i.delete = 0 AND i.description > ''
WHERE a.delete = 0 AND a.isdraft = 0 AND ac.delete = 0 AND ac.hasCancel = 0 #有效的活动
  AND ac.actionEndTime > NOW() #未结束的活动
  AND a.id = %d
ORDER BY ac.createTime;    
'''%(actionId)
    cursor = db.cursor()
    row = {}
    try:
        res = cursor.execute(sql)
        print('banzhu._load_action_byid(actionId=%d)'%(actionId), res)
        tup = cursor.fetchone()
        row = {fields[i]: tup[i] for i in range(len(tup))}
    except Exception as err:
        print('Got error {!r}, errno is {}'.format(err, err.args[0]))
    return row

# 根据圈子id获取未结束的活动
def _load_circle_active_actions(db, circleId):
    fields = ['circleId', 'actionId', 'comboId', 'title', 'address', 'addressName', 'peopleNum'
    , 'createTime', 'actionTime', 'actionEndTime', 'signUpEndTime'
    ,'feeType' , 'condition', 'enableTeam', 'description']
    sql = '''
SELECT a.circleId, ac.actionId, ac.id AS comboId, ac.title, ac.address, ac.addressName, ac.peopleNum
     , ac.createTime, ac.actionTime, ac.actionEndTime, ac.signUpEndTime
     , ac.type as feeType, ac.condition, ac.enableTeam, i.description
FROM banzhu_circle c 
JOIN banzhu_action a ON c.id = a.circleId
JOIN banzhu_action_combo ac ON a.id = ac.actionId AND ac.sub = 0 #只要主活动
LEFT JOIN banzhu_action_introduction i ON i.comboId = ac.id AND i.delete = 0 AND i.description > ''
WHERE a.delete = 0 AND a.isdraft = 0 AND ac.delete = 0 AND ac.hasCancel = 0 #有效的活动
  AND ac.actionEndTime > NOW() #未结束的活动
  AND c.id = %d #圈子id
ORDER BY ac.createTime;    
'''%(circleId)
    cursor = db.cursor()
    rows = []
    try:
        res = cursor.execute(sql)
        print('banzhu._load_circle_active_actions(circleId=%d)'%(circleId), res)
        for tup in cursor:
            row = {fields[i]: tup[i] for i in range(len(tup))}
            rows.append(row)
    except Exception as err:
        print('Got error {!r}, errno is {}'.format(err, err.args[0]))
    return rows

# 根据活动卡片id获取报名名单
def _load_action_baolist(db, comboId):
    fields = ['s', 'createTime', 'id', 'uid', 'nick', 'gender', 'forUid', 'forName', 'forGender', 'inviter', 'baono', 'delete', 'candidate']
    sql = '''
SELECT IF(b.delete, 2, b.candidate) AS s #状态: 0-正常报名, 1-候补, 2-取消报名
     , b.createTime, b.id, b.uid, u.nick, u.gender, b.forUid, b.forName, b.forGender, b.inviter
     , IF(b.delete>0, RANK() OVER (ORDER BY b.delete DESC, b.updateTime, b.id), IF(b.candidate>0, RANK() OVER (ORDER BY IF(b.delete>0,0,b.candidate) DESC, b.createtime DESC, b.id DESC), RANK() OVER (ORDER BY b.candidate, b.delete, b.createtime, b.id))) baono #报名顺序号
     , b.delete, b.candidate
FROM banzhu_action_bao_combo b
LEFT JOIN banzhu_action_combo ac ON ac.id=b.comboid
LEFT JOIN banzhu_user u ON b.uid=u.uid
WHERE b.comboId = %d #活动卡片id
  AND b.delete = 0 #是否取消报名
ORDER BY  s, baono, b.createtime, b.id;
'''%(comboId)
    cursor = db.cursor()
    try:
        res = cursor.execute(sql)
        print('banzhu._load_action_baolist(comboId=%d)'%(comboId),  res)
        rows = []
        for tup in cursor:
            row = {fields[i]: tup[i] for i in range(len(tup))}
            rows.append(row)
        return rows
    except Exception as err:
        print('Got error {!r}, errno is {}'.format(err, err.args[0]))
    return []

# 生成活动url链接
def _fetch_urllink(actionId):
    url = 'https://banzhu.udinovo.com/banzhu/weixin/getUrllink'
    data = {
        'path': '/pages/index/index',
        'query': 'share=activityDetail&params='+requests.utils.quote('actionId=%d&type=0'%(actionId))
    }
    try:
        res = requests.post(url, data = data, timeout=5)
        print('banzhu._fetch_urllink(actionId=%d)'%(actionId), res)
        json = res.json()
        return json['url_link']
    except Exception as err:
        print('Got error {!r}, errno is {}'.format(err, err.args[0]))
        return ''

def parseCircleBindRoom():
    selectSql = """select name, circleId, circleCode, chatGroupCode, timing->'$[0]', timing->'$[1]',timing->'$[2]',keywords from banzhu_circle_chatgroup where enable = 1 ORDER BY id DESC
    """
    #selectSql = """select name, circleId, circleCode, chatGroupCode, timing->'$[0]', timing->'$[1]',timing->'$[2]',keywords, from banzhu_circle_chatgroup where enable = 1 ORDER BY id DESC
    cursor.execute(selectSql)
    rows = cursor.fetchall()
    for row in rows:
        print(f'{row[0]}|circleId: {row[1]}|circleCode: {row[2]}')
        roomId = row[3]
        print(roomId)
        hour0 = int(row[4])
        hour1 = int(row[5])
        hour2 = int(row[6])
        print(f"{roomId}要发的小时节点:{hour0}|{hour1}|{hour2}")
        # scheduler.add_job(sendMiniProgram, "cron", day="*", minute=18, hour=hour0+4, misfire_grace_time=30, args=[roomId]) #ok
        # scheduler.add_job(sendMiniProgram, "cron", day="*", minute=3, hour=hour1+9, misfire_grace_time=30, args=[roomId]) #ok
        # scheduler.add_job(sendMiniProgram, "cron", day="*", minute=50, hour=hour2+2, misfire_grace_time=30, args=[roomId]) #ok

    scheduler.add_job(sendMiniProgram, "cron", day="*", minute=21, hour=11, misfire_grace_time=30, args=['19893951839@chatroom']) 
    scheduler.start() #needed

            
def getActivityId(room_id):
    #属于这个群的有效的活动, 暂取最后一个
    selectSql = """select activity_id from mini_program where group_id = %s ORDER BY id DESC LIMIT 1
    """
    selectData = (room_id)
    cursor.execute(selectSql, selectData)
    resRow = cursor.fetchone()
    activityId = None
    if resRow is not None:
        activityId = resRow[0]
    return activityId 


def getMiniProgram(room_id):
    #属于这个群的有效的活动, 暂取最后一个
    selectSql = """select json_str from mini_program where group_id = %s ORDER BY id DESC LIMIT 1
    """
    selectData = (room_id)
    cursor.execute(selectSql, selectData)
    resRow = cursor.fetchone()
    miniJsonStr = None
    if resRow is not None:
        miniJsonStr = resRow[0]
    conn.commit()
    miniProgram = None
    if miniJsonStr is not None:
        print('mini:', miniJsonStr)
        miniJsonDict = json.loads(miniJsonStr)
        miniProgram = bot.MiniProgram.create_from_json(
            payload_data= miniJsonDict #mini_program_data
        )
    return miniProgram

def replyInLastHour(room_id):
    selectReply = """select id from room_reply_record where room_id = %s and date(update_time) > (CURDATE() - INTERVAL 1 HOUR)  order by cnt limit 1""" # 7天内是否发过
    selectData = (room_id)
    localtime = time.asctime( time.localtime(time.time()) )
    print(f"{localtime}|check之前1小时是否有回复改群|replyInLastHour|roomId:{room_id}")
    cursorEs.execute(selectReply, selectData)
    rowRes = cursorEs.fetchone()
    if rowRes is not None:
        print(f"{localtime}|之前1小时有回复改群|replyInLastHour|roomId:{room_id}")
        return True
    return False 

#无记录or7天过了都可以发
def updateReplyRecord(room_id, reply_id):
    selectReply = """select id from room_reply_record where room_id = %s and reply_id = %s and date(update_time) > (CURDATE() - INTERVAL 7 DAY)  order by cnt limit 1""" # 7天内是否发过
    selectData = (room_id, reply_id)
    localtime = time.asctime( time.localtime(time.time()) )
    print(f"{localtime}|updateReplyRecord|replyId:{reply_id}")
    cursorEs.execute(selectReply, selectData)
    rowRes = cursorEs.fetchone()
    if rowRes is not None:
        print(f"updateReplyRecord|最近7天发过不能再发|replyId:{reply_id}")
        return False 
    updateReply = """update room_reply_record set cnt = cnt+1, update_time = NOW() where room_id = %s and reply_id = %s""" 
    updateData = (room_id, reply_id)
    cursorEs.execute(updateReply, updateData)
    connEs.commit()
    if cursorEs.rowcount < 1: # update failed
        sql = """INSERT INTO room_reply_record(room_id, reply_id, cnt, add_time, update_time) VALUES(%s, %s, %s, now(), now())"""
        data = (room_id, reply_id, 1)
        cursorEs.execute(sql, data)
        connEs.commit()
    IncreKeywordReplyCnt(reply_id)
    return True
    
def getAndUpdateWukongReply(groupType): #该group_type最少发的那个reply
    print(f"getAndUpdateWukongReply|groupType:{groupType}")
    selectReply = """select id, reply from keyword_reply where group_type = %s order by cnt limit 1"""
    selectData = (groupType)
    cursorEs.execute(selectReply, selectData)
    rowRes = cursorEs.fetchone()
    print(f"{rowRes}")
    if rowRes is not None:
        IncreKeywordReplyCnt(rowRes[0])
        return rowRes[1]
    else:
        return None;

def getAndUpdateWukongReplyWithGroupType(group_type):
    print(f"getAndUpdateWukongReplyWithGroupType|group_type:%d" % (group_type))
    selectReply = """select id, reply from keyword_reply where group_type = %s order by cnt limit 1"""
    selectData = (group_type)
    cursorEs.execute(selectReply, selectData)
    rowRes = cursorEs.fetchone()
    return rowRes

def getAndUpdateWukongReplyWithKeyword(room_id, keyword):
    print(f"getAndUpdateWukongReplyWithKeyword|room_id:%s|keyword:%s" % (room_id, keyword))
    selectReply = """select id, reply from keyword_reply where keyword = %s"""
    selectData = (keyword)
    cursorEs.execute(selectReply, selectData)
    rowRes = cursorEs.fetchall()
    for row in rowRes:
        if updateReplyRecord(room_id, row[0]):
            return row[1] 
    print(f"{keyword} 对应的回复最近7天发过，不再发。")
    return None
    
def getWukongReplyById(replyId):
    selectReply = """select reply from keyword_reply where id = %s"""
    selectData = (replyId)
    cursorEs.execute(selectReply, selectData)
    rowRes = cursorEs.fetchone()
    if rowRes is None:
        return None
    else:
        return rowRes[0]
    
async def sendWukongReply(roomId, reply):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"准备|定时发悟空援助url|{roomId}|{reply}")
    # 等待登入
    tmpRoom = await bot.Room.find(roomId)  # 可以根据 room 的 topic 和 id 进行查找
    if tmpRoom is None:
        print(f"room{roomId} is null !!!")
        return
    #await msg.say(reply)
    if reply is not None: # and roomId == "17923822738@chatroom":
        print(f"确认|定时发悟空援助url|{roomId}|{reply}")
        await tmpRoom.say(reply)

async def SendWukongAtTime():
    selectSql = """select group_id from group_info
    """
    cursorEs.execute(selectSql)
    rows = cursorEs.fetchall()
    for row in rows:
        roomId = row[0]
        reply = getAndUpdateWukongReply(0) #getWukongReply(roomId)
        if reply is not None:
            await sendWukongReply(roomId, reply)

#cnt+1
def IncreKeywordReplyCnt(replyId):
    updateReply = """update keyword_reply set cnt = cnt+1, update_time = NOW() where id = %s""" 
    updateData = (replyId)
    cursorEs.execute(updateReply, updateData)
    connEs.commit()
    
    
def InsertGroupInfo(room_id, room_name):
    if "公益" in room_name or "书香" in room_name or "渡过" in room_name or '悟空援助' in room_name or '一休' in room_name or '郁金香' in room_name or '七日离苦' in room_name\
        or "抑郁症" in room_name or "走向开心" in room_name:
        print(f"InsertGroupInfo|群: {room_name}")
        # 先查询，有就不insert
        selectSql = """select * from group_info where group_id = %s"""
        selectData = (room_id)
        cursorEs.execute(selectSql, selectData)
        resRow = cursorEs.fetchone()
        if resRow is not None:
            print(f"insert before!! | {room_id}")
            return
        
        try:
            sql = """INSERT INTO group_info(group_id, group_name, add_time, update_time) VALUES(%s, %s, now(), now())"""
            data = (room_id, room_name)
            cursorEs.execute(sql, data)
            connEs.commit()
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            print("db insert error")
            print(e)
            connEs.rollback()

def InsertKeywordReply(keyword, reply):   
    # 插入keyword-reply
    try:
        sql = """INSERT INTO keyword_reply(keyword, reply) VALUES(%s, %s)"""
        data = (keyword, reply)
        cursorEs.execute(sql, data)
        connEs.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print("db insert error")
        print(e)
        connEs.rollback()
            
async def on_message(msg: Message):
    """
    Message Handler for the Bot
    groupId-keyword-string-cnt
   """
    room = msg.room()
    conversation_id = ''
    if room is not None:
        conversation_id = room.room_id #str
        room_name = await room.topic()
        talker: Contact = msg.talker()
        await talker.ready()
        if "郁金香" in talker.name or "寒啸" in talker.name or room_name == "7线内部群" or "TDD" in room_name or "中大深圳" in room_name or '2002届高三' in room_name:
            localtime = time.asctime( time.localtime(time.time()) )
            print(f"{localtime}|发消息的是郁金香等, 直接return")
            return
        
        InsertGroupInfo(room.room_id, room_name)

        #if "斑猪" in room_name:
        if msg.type() == MessageType.MESSAGE_TYPE_MINI_PROGRAM:
            mini_program = await msg.to_mini_program()
            # save the mini-program data as string
            mini_program_data = asdict(mini_program.payload)
            localtime = time.asctime( time.localtime(time.time()) )
            print(f"{localtime}|str of mini:", mini_program_data)
            appName = mini_program_data.get('description')
            if "斑猪活动圈" in appName: #斑猪小程序才入db
                # 插入db
                try:
                    sql = """INSERT into mini_program(group_id,group_name,json_str,activity_id) values (%s, %s, %s, %s)"""
                    json_str = json.dumps(mini_program_data)
                    activityIdStart = json_str.find('actionId%3D')
                    activityIdStart += 11 #len of 'actionId%3D'
                    activityId = 0
                    print(f"activityId start at: %d" %(activityIdStart))
                    if activityIdStart != -1:
                        activityIdEnd = json_str.find('%', activityIdStart)
                        print(f"activityId end at: %d" %(activityIdEnd))
                        if activityIdEnd != -1:
                            activityId = int(json_str[activityIdStart:activityIdEnd])

                    print(f"activityId is: %d" %(activityId))
                    data = (room.room_id, room_name, json_str, activityId)
                    # 先查询，有就不insert
                    selectSql = """select * from mini_program where group_id = %s and activity_id = %s"""
                    selectData = (room.room_id, activityId)
                    cursor.execute(selectSql, selectData)
                    resRow = cursor.fetchone()
                    if resRow is not None:
                        print("insert before!!")
                        return

                    cursor.execute(sql, data)
                    conn.commit()
                except (MySQLdb.Error, MySQLdb.Warning) as e:
                    # Rolling back in case of error
                    print("db insert error")
                    print(e)
                    conn.rollback()

        if msg.text().startswith("bd-"):
            bindCircleAndRoom(circleIdStr, strRoomId)
                    
                    
        if "斑猪" in room_name and "活动" in msg.text():
            print(f"斑猪活动报名")
            miniProgram = getMiniProgram(room.room_id)
            if miniProgram is not None:
                global banzhuRoom
                if banzhuRoom is None:
                    banzhuRoom = room
                await room.say(miniProgram)
            return
    else:
        talker = None
        if msg.is_self():
            talker = msg.to()
        else:
            talker = msg.talker()
        if talker is None:
            raise WechatyPayloadError('Message must be from room/contact')
        conversation_id = talker.contact_id
        
    if room is not None: #群才启用
        if replyInLastHour(room.room_id):
            return 
        #replyOnKeyword(conversation_id, msg)
        time.sleep(3) #避免太快回复
        for keyword in keyword2reply:
            #reply0 = keyword2reply.get(keyword)
            #InsertKeywordReply(keyword, reply0)
            if (keyword in msg.text()):
                #该群1小时内回复过其他keyword，不再回复
                reply = getAndUpdateWukongReplyWithKeyword(room.room_id, keyword)
                if reply is None:
                    continue
                #reply = keyword2reply.get(keyword)
                print('找到keyword: %s | %s' %(keyword, reply))
                await msg.say(reply)
                break #一个群一次只回复一个匹配
                
            
async def on_scan(
        qrcode: str,
        status: ScanStatus,
        _data,
):
    """
    Scan Handler for the Bot
    """
    print('Status: ' + str(status))
    print('View QR Code Online: https://wechaty.js.org/qrcode/' + quote(qrcode))


async def on_login(user: Contact):
    """
    Login Handler for the Bot
    """
    print(user)
    # TODO: To be written

    
#<Room <22958121966@chatroom - 斑猪运营群>> set payload more than once
async def sendMiniProgram(roomId):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"定时发活动...{roomId}")
    # 等待登入
    tmpRoom = await bot.Room.find(roomId)  # 可以根据 room 的 topic 和 id 进行查找
    if tmpRoom is None:
        print(f"room {roomId} is null !!!")
        return
    #activityId = getActivityId(roomId)
    activityId = 6886
    if activityId is not None:
        print(f"现在发小程序|{roomId}|活动id: {activityId}")
        textlink = gen_action_textlink(conn, activityId)
        await tmpRoom.say(textlink)
        #await tmpRoom.say("请打开链接报名：https://wxaurl.cn/tIZgboNm2Zm")
        #await tmpRoom.say(miniProgram)
    else:
        print(f"miniProgram of room {roomId} is null !!!")

#circleIdStr: bd-xxxxxxx . xxxxxxx是circleId的base64编码
def bindCircleAndRoom(circleIdStr, strRoomId):
    print(f"bindCircleAndRoom|circle:%s|roomId:%s" %(strCircle, strRoomId))
    circleIdStart = 3
    circleIdBase64 = circleIdStr[circleIdStart:]
    strCircleId = base64.b64decode(circleIdBase64)
    circleId = int(strCircleId) 
    if circleId == -1:
        print(f"circleId == -1 !!!|{strRoomId}|{circleIdStr}")
        return
    try:
        sql = """INSERT INTO banzhu_circle_chatgroup(circleId, chatGroupCode) VALUES(%s, %s)"""
        data = (circleId, strRoomId)
        cursor.execute(sql, data)
        conn.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print("db insert error")
        print(e)
        conn.rollback()
    
async def main():
    #
    # Make sure we have set WECHATY_PUPPET_SERVICE_TOKEN in the environment variables.
    # Learn more about services (and TOKEN) from https://wechaty.js.org/docs/puppet-services/
    #
    # It is highly recommanded to use token like [paimon] and [wxwork].
    # Those types of puppet_service are supported natively.
    # https://wechaty.js.org/docs/puppet-services/paimon
    # https://wechaty.js.org/docs/puppet-services/wxwork
    # 
    # Replace your token here and umcommt that line, you can just run this python file successfully!
    # os.environ['token'] = 'puppet_paimon_your_token'
    # os.environ['token'] = 'puppet_wxwork_your_token'
    #     

    if 'WECHATY_PUPPET_SERVICE_TOKEN' not in os.environ:
        print('''
            Error: WECHATY_PUPPET_SERVICE_TOKEN is not found in the environment variables
            You need a TOKEN to run the Python Wechaty. Please goto our README for details
            https://github.com/wechaty/python-wechaty-getting-started/#wechaty_puppet_service_token
        ''')

    #bot = Wechaty()
    global bot
    bot = Wechaty()

    bot.on('scan',      on_scan)
    bot.on('login',     on_login)
    bot.on('message',   on_message)
    print('[Python Wechaty] Ding Dong Bot started.')

    scheduler.add_job(SendWukongAtTime, "cron", day="*", minute=26, hour=19, misfire_grace_time=30)  #ok
    
    #scheduler.add_job(sendMiniProgram, "interval", seconds=120, args=['19893951839@chatroom']) #ok
    #scheduler.add_job(sendMiniProgram, "cron", day="*", minute=59, hour=10, misfire_grace_time=30, args=['19893951839@chatroom']) 
    parseCircleBindRoom()

    await bot.start()


asyncio.run(main())

