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
import pymysql

#import logging

from urllib.parse import quote

from wechaty import (
    Contact,
    FileBox,
    Message,
    Wechaty,
    ScanStatus,
    Room,
)

conversationDict = {}
keyword2reply = {
    '滨江花园':'欢迎预订滨江花园婚宴酒店: https://mp.weixin.qq.com/s/A0FTDhL69znSE7tAsPu4wQ',
    '婚宴酒店':'欢迎预订滨江花园婚宴酒店: https://mp.weixin.qq.com/s/A0FTDhL69znSE7tAsPu4wQ',
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
    '公益图书馆':'公益悟空图书馆-老家可以更团结点https://mp.weixin.qq.com/s/JuBVLMuR2I7Fjc_pjTloXw',
    '乔峰':'乔峰的原型是谁:https://mp.weixin.qq.com/s/Pvip07l6tPRftJo3JS7XkQ',
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
    '足球场':'绿茵兄弟情-我们的青春:https://mp.weixin.qq.com/s/805glGFtJpDJiig4YmNPIQ',
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
    '新冠':'[悟空图书馆]-新冠如长夜:https://mp.weixin.qq.com/s/hvtpV04KHq25sXvWO7pJXA',
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
    '加班':'黄帝内经之不妄作劳:https://mp.weixin.qq.com/s/f0z9e6i0swFjKwqJNYchkA',
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
    '抑郁':'谁来帮助医学院逝去的学生? https://mp.weixin.qq.com/s/U9MdAbw8958MTVh9KeAoAQ',
    '抑郁':'帮助状态不好朋友的错误言行:https://mp.weixin.qq.com/s/3WvrpRB1-AjUao7d7-MJ5A',
    # '抑郁':'抑郁焦虑可以参考这个-金刚经为什么可以救人:https://mp.weixin.qq.com/s/d0e0Ns7OgqqqMYhqncwLYw',
    #'抑郁':'供参考-康复的例子: 顿悟和康复:https://mp.weixin.qq.com/s/Qdlm3eb_J482jmo5eMvrCA',
    # '焦虑':'焦虑可以参考这个, 看书康复的例子:https://mp.weixin.qq.com/s/kkX1I25oM5-UGcYoFqd2QA',
    '焦虑':'供参考-不放弃，就有康复的希望:https://mp.weixin.qq.com/s/O2nb-450640ankJqKkjsDA',
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
#conn = pymysql.connect(host="127.0.0.1", user="root", passwd="Qlcx1997", db='keys', charset='utf8', port=3306)  #和mysql服务端设置格式一样（还可设置为gbk, gb2312）
#创建游标
#cursor = conn.cursor()


async def on_message(msg: Message):
    """
    Message Handler for the Bot
    groupId-keyword-string-cnt
    """
    time.sleep(3) #避免太快回复
    room = msg.room()
    conversation_id = ''
    if room is not None:
        conversation_id = room.room_id #str
        room_name = await room.topic()
        talker: Contact = msg.talker()
        if "郁金香" in talker.name or "润鑫" in talker.name:
            print(f"发消息的是郁金香, 直接return")
            return
        
        # print(f"群聊名: {room_name}")
        # if "研究院核心团队" in room_name or "江苏鸿程大数据研究院" in room_name:
        #     print(f"鸿程, return")
        #     return
    else:
        talker = None
        if msg.is_self():
            talker = msg.to()
        else:
            talker = msg.talker()
        if talker is None:
            raise WechatyPayloadError('Message must be from room/contact')
        conversation_id = talker.contact_id
        
    #replyOnKeyword(conversation_id, msg)
    for keyword in keyword2reply:
        #print('keyword: %s' %(keyword))
        if (keyword in msg.text()):
            reply = keyword2reply.get(keyword)
            print('找到keyword: %s | %s' %(keyword, reply))
            keyDic = conversationDict.get(conversation_id)
            if keyDic is None:
                print('该会话之前未回复')
                keyDic = {}
                keyDic[keyword] = 1
                conversationDict[conversation_id] = keyDic
                await msg.say(reply)
                if(keyword == '滨江花园'):
                    #imgFile = FileBox.fromLocal('/home/dev/py/wangning.jpeg')
                    imgFile = FileBox.from_file('/home/dev/py/wangning.jpeg')
                    await msg.say(imgFile)

                break #一个群一次只回复一个匹配
            elif keyDic.get(keyword) is None:
                #print('keyDic:',keyDic.__dict__)
                print('该会话第一次回复keyword: %s' %(keyword))
                keyDic[keyword] = 1
                conversationDict[conversation_id] = keyDic
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


async def main():
    """
    Async Main Entry
    """
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

    bot = Wechaty()

    bot.on('scan',      on_scan)
    bot.on('login',     on_login)
    bot.on('message',   on_message)

    await bot.start()

    print('[Python Wechaty] Ding Dong Bot started.')


asyncio.run(main())
