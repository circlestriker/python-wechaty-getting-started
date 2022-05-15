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
    '防守':'防守型球星多的好处:https://mp.weixin.qq.com/s/s_Qfap5motEBSm-auc2v9g',
    '膝盖伤':'盘腿治膝伤:https://mp.weixin.qq.com/s/6OvreXJz3UFwuTPqb-2Lug',
    '脚踝伤':'盘腿治膝伤:https://mp.weixin.qq.com/s/6OvreXJz3UFwuTPqb-2Lug',
    '崴脚':'盘腿治膝伤:https://mp.weixin.qq.com/s/6OvreXJz3UFwuTPqb-2Lug',
    '后卫':'众人之所恶的边后卫:https://mp.weixin.qq.com/s/qEj9wNuSLP-uwhGJxNn_pA',
    '半月板':'鼓楼医院关节科不错:https://mp.weixin.qq.com/s/JH234VpbQmW23NcBduZbJA'
    }

async def replyOnKeyword(conversation_id: str, msg: Message):
    for keyword in keyword2reply:
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
            elif keyDic.get(keyword) is None:
                print('keyDic:',keyDic.__dict__)
                print('该会话第一次回复keyword: %s' %(keyword))
                keyDic[keyword] = 1
                conversationDict[conversation_id] = keyDic
                await msg.say(reply)
                
            break #一个群一次只回复一个匹配

    
async def on_message(msg: Message):
    """
    Message Handler for the Bot
    groupId-keyword-string-cnt
    """
    room = msg.room()
    conversation_id = ''
    if room is not None:
        conversation_id = room.room_id #str
    else:
        talker = msg.talker()
        if talker is None:
            raise WechatyPayloadError('Message must be from room/contact')
        conversation_id = talker.contact_id
        
    #replyOnKeyword(conversation_id, msg)
    for keyword in keyword2reply:
        print('keyword: %s' %(keyword))
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
            elif keyDic.get(keyword) is None:
                #print('keyDic:',keyDic.__dict__)
                print('该会话第一次回复keyword: %s' %(keyword))
                keyDic[keyword] = 1
                conversationDict[conversation_id] = keyDic
                await msg.say(reply)
                
            break #一个群一次只回复一个匹配

    """    
    if msg.text() == 'ding':
        await msg.say('dong')
    elif ('失眠' in msg.text()):
        keyDic = conversationDict.get(conversation_id)
        if keyDic is None:
            print('该会话第一次回复|失眠|')
            keyDic = {}
            keyDic['失眠'] = 1
            conversationDict[conversation_id] = keyDic
            await msg.say('失眠可以参考这个-数息法治失眠:https://mp.weixin.qq.com/s/SQfaegwTa0gCu2mjfUkezg')
        elif keyDic.get('失眠') is None:
            print('该会话非第一次回复|失眠|')
            print('keyDic:',keyDic.__dict__)
            keyDic['失眠'] = 1
            conversationDict[conversation_id] = keyDic
            await msg.say('失眠可以参考这个-数息法治失眠:https://mp.weixin.qq.com/s/SQfaegwTa0gCu2mjfUkezg')
            
    elif '抑郁' in msg.text():
        keyword = '抑郁'
        keyDic = conversationDict.get(conversation_id)
        if keyDic is None:
            print('该会话第一次回复|%s|' %(keyword))
            keyDic = {}
            keyDic[keyword] = 1
            conversationDict[conversation_id] = keyDic
            await msg.say('抑郁焦虑可以参考这个-金刚经为什么可以救人:https://mp.weixin.qq.com/s/d0e0Ns7OgqqqMYhqncwLYw')
        elif keyDic.get(keyword) is None:
            print('该会话第一次回复|%s|' %(keyword))
            print('keyDic:',keyDic.__dict__)
            keyDic[keyword] = 1
            conversationDict[conversation_id] = keyDic
            await msg.say('抑郁焦虑可以参考这个-金刚经为什么可以救人:https://mp.weixin.qq.com/s/d0e0Ns7OgqqqMYhqncwLYw')
    elif '学佛' in msg.text():
        keyword = '学佛'
        keyDic = conversationDict.get(conversation_id)
        if keyDic is None:
            print('该会话第一次回复|%s|' %(keyword))
            keyDic = {}
            keyDic[keyword] = 1
            conversationDict[conversation_id] = keyDic
            await msg.say('可以参考这个-佛祖因抑郁症而觉悟:https://mp.weixin.qq.com/s/GJ4TxPYjCAiw1jqrjOH2Mg')
        elif keyDic.get(keyword) is None:
            print('该会话第一次回复|%s|' %(keyword))
            print('keyDic:',keyDic.__dict__)
            keyDic[keyword] = 1
            conversationDict[conversation_id] = keyDic
            await msg.say('可以参考这个-佛祖因抑郁症而觉悟:https://mp.weixin.qq.com/s/GJ4TxPYjCAiw1jqrjOH2Mg')
    elif '焦虑' in msg.text():
        keyword = '焦虑'
        keyDic = conversationDict.get(conversation_id)
        if keyDic is None:
            print('该会话第一次回复|%s|' %(keyword))
            keyDic = {}
            keyDic[keyword] = 1
            conversationDict[conversation_id] = keyDic
            await msg.say('焦虑可以参考这个, 看书康复的例子:https://mp.weixin.qq.com/s/kkX1I25oM5-UGcYoFqd2QA')
        elif keyDic.get(keyword) is None:
            print('该会话第一次回复|%s|' %(keyword))
            print('keyDic:',keyDic.__dict__)
            keyDic[keyword] = 1
            conversationDict[conversation_id] = keyDic
            await msg.say('焦虑可以参考这个, 看书康复的例子:https://mp.weixin.qq.com/s/kkX1I25oM5-UGcYoFqd2QA')
    """

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
