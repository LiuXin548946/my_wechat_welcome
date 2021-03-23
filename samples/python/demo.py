# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import wechat
import json
import time
from wechat import WeChatManager, MessageType
import re

wechat_manager = WeChatManager(libs_path='../../libs')


# 这里测试函数回调
@wechat.CONNECT_CALLBACK(in_class=False)
def on_connect(client_id):
    print('[on_connect] client_id: {0}'.format(client_id))


@wechat.RECV_CALLBACK(in_class=False)
def on_recv(client_id, message_type, message_data):
    print('[on_recv] client_id: {0}, message_type: {1}, message:{2}'.format(client_id,
                                                                            message_type,
                                                                            json.dumps(message_data, ensure_ascii=False)))


@wechat.CLOSE_CALLBACK(in_class=False)
def on_close(client_id):
    print('[on_close] client_id: {0}'.format(client_id))


# 这里测试类回调， 函数回调与类回调可以混合使用
class LoginTipBot(wechat.CallbackHandler):
    # 当前账号的wxid
    my_wxid = str()
    # 所有群信息
    room_data_list = []
    # 所有好友
    firend_data_list = []

    @wechat.RECV_CALLBACK(in_class=True)
    def on_message(self, client_id, message_type, message_data):
        # 判断登录成功后，就向文件助手发条消息
        if message_type == MessageType.MT_USER_LOGIN:
            time.sleep(2)
            wechat_manager.send_text(client_id, 'filehelper', '😂😂😂\uE052该消息通过wechat_pc_api项目接口发送')
            
            wechat_manager.send_link(client_id, 
            'filehelper', 
            'wechat_pc_api项目', 
            'WeChatPc机器人项目', 
            'https://github.com/smallevilbeast/wechat_pc_api', 
            'https://www.showdoc.com.cn/server/api/attachment/visitfile/sign/0203e82433363e5ff9c6aa88aa9f1bbe?showdoc=.jpg)')
            # public = wechat_manager.get_publics(client_id)
            # print("公众号：", type(public), public)
            # friends = wechat_manager.get_friends(client_id)
            # print("好友：", type(friends))
            room = wechat_manager.get_chatrooms(client_id)
            print("群：", type(room))

    def update_rooms(self, message_data):
        self.room_data_list = message_data
        print("All群组更新完毕！")

    def update_friends(self, message_data):
        self.firend_data_list = message_data
        print("All好友更新完毕！")

    def get_room_wxid(self, room_name):
        room_wxid = ""
        for i in self.room_data_list:
            if i["nickname"] == room_name:
                room_wxid = i["wxid"]
        return room_wxid

    @wechat.RECV_CALLBACK(in_class=True)
    def on_recv(self, client_id, message_type, message_data):
        # 存自己wxid
        if message_type == MessageType.MT_USER_LOGIN:
            self.my_wxid = message_data["wxid"]
            return
        # 存群
        if message_type == MessageType.MT_DATA_CHATROOMS_MSG:
            self.update_rooms(message_data)
            return
        # 存人
        if message_type == MessageType.MT_DATA_FRIENDS_MSG:
            self.update_friends(message_data)
            return

        # 通用消息-文本
        if message_type == MessageType.MT_RECV_TEXT_MSG:
            my_class_id = self.get_room_wxid("金枝玉叶")
            if message_data["room_wxid"] == my_class_id:
                if message_data["from_wxid"] != self.my_wxid:
                    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    wechat_manager.send_text(client_id, my_class_id,
                    '\uE052该消息通过wechat_pc_api项目自动发送！\ncurrent_time：【{}】\nmsg:【{}】'.format(str_time, message_data["msg"]))
            return

        # 通用消息-系统
        if message_type == MessageType.MT_RECV_SYSTEM_MSG:
            self.new_welcome(client_id, message_data)
            return

    def new_welcome(self, client_id, message_data):
        tmp_room_name = "长春招聘人力资源8群"
        # 欢迎语
        welcome_str =  "热烈欢迎【{}】加入本群！\n1.本群不定期发布各大：\n企事业、国企、私企、个企人才招聘岗位。🎉\n2.致力于岗位招聘，人才就业，协调咨询，落实保障等人力资源业务。💪\n3.企业加群管理全平台免费发布招聘岗位信息。[爱你]\n4.欢迎各位老板、高管、高材前来洽谈合作。[握手]\n5.本群为业务群，禁止说话，有事请咨询私信群管理。[闭嘴]\n6.本群会经常发福利红包！！！💰\n7.禁止互加好友，防止上当受骗！⚠\n（企事业？高薪？五险一金？铁饭碗？想进某单位无渠道？☞☞☞来找我这些都不是问题，都给你安排到位）"
        # 判断群
        if message_data["room_name"] == tmp_room_name:
            raw_msg = message_data["raw_msg"]
            # 判断加入群聊消息
            if all([x in raw_msg for x in ["加入", "群聊"]]):
                # 获取新人名字
                name = "未知"
                # 自己的邀请需提前特殊处理
                if "你邀请" in raw_msg:
                    tmp_l = list(raw_msg)
                    tmp_l.insert(0, '"')
                    tmp_l.insert(2, '"')
                    raw_msg = ''.join(tmp_l)
                elif "通过扫描你" in raw_msg:
                    tmp_l = list(raw_msg)
                    tmp_l.insert(raw_msg.find("通过扫描你") + 4, '"')
                    tmp_l.insert(raw_msg.find("通过扫描你") + 4 + 2, '"')
                    raw_msg = ''.join(tmp_l)
                    pass
                # 两种邀请方式
                if "邀请" in raw_msg:
                    # ['', 'A58同城招聘经理郝成双18943964112', '邀请', 'A小许13614437993', '加入了群聊']
                    name = re.split("\"", raw_msg)[3]
                elif "通过扫描" in raw_msg:
                    # ['', ' 伱是莪此生不變的堅持丶', '通过扫描', '五哥', '分享的二维码加入群聊']
                    name = re.split("\"", raw_msg)[1]
                # 发消息
                wechat_manager.send_text(client_id, message_data["room_wxid"], welcome_str.format(name))


if __name__ == "__main__":
    bot = LoginTipBot()

    # 添加回调实例对象
    wechat_manager.add_callback_handler(bot)
    wechat_manager.manager_wechat(smart=True)

    # 阻塞主线程
    while True:
        time.sleep(0.5)
