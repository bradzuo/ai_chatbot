# coding:utf-8
"""
从mysql中提取出来，存入neo4j中
1.从mysql中提取出数据
2.按格式构造数据
3.存入neo4j

"""
import pickle
from collections import defaultdict
from Utils.OPMysql import Op_Mysql
from gen_schema import info2neo
from stories_to_neo4j import BatchToNeo4j
import os,sys

def neo4j_datafrom(topic_id,topic_name):
    """
    按格式构造数据，方便传入neo4j
    :return:
    """
    # 根据主题ID去mysql中查询故事线
    stories = Op_Mysql().Select_Query(tablename='cb_ms_stories',
                            output=['ID_','NAME_'],
                            where="TOPIC_ID_= " + "'" + topic_id + "'" + "and TOPIC_NAME_="+ "'" + topic_name + "'")
    STORIES_LIST = []
    if stories:
        for story in stories:
            story_id = story[0]
            story_name = story[1].replace('\n','')
            print('mysql中故事线ID，名称:',story_id,story_name)
            # 根据故事线查询意图数据，并拼接成json格式数据输出
            intents = Op_Mysql().Select_Query(tablename='cb_ms_intent',
                                              output=['ID_', 'PID_','INTENT_','REPLY_'],
                                              where="STORY_ID_= " + "'" + story_id + "'")
            STORIES_DICT = {}
            INTENDS = defaultdict(list)
            if intents:
                for intent in intents:
                    intent_id = intent[0]
                    intent_pid = intent[1]
                    if not intent_pid:
                        intent_pid = 'None'
                    try:
                        intent_cont = eval(intent[2])
                    except Exception as e:
                        print(e)
                        print('mysql数据错误...')
                    intent_reply = eval(intent[3])
                    intent_cont = '/'.join(intent_cont.values())
                    intent_reply = '/'.join(intent_reply.values())
                    # print('当前故事线包含的意图：',intent_id,intent_pid,intent_cont,intent_reply)
                    """
                    data = [
                        {'故事线ID': '1ab1853a-89fc-11ea-8c27-f4d108568a73',
                         '故事线名称': '问候',
                         '意图': [{'意图ID': 'f14275f0-7d5f-11ea-9bb0-f4d108568a73_f1433728-7d5f-11ea-8f7d-f4d108568a73',
                                 'PID': 'none',
                                 '意图': '我要存活期/存活期/我想存活期/我想存点活期/我要存点活期存款/存点活期',
                                 '回复': '请问您在我行有账户吗？',
                                 '下标': [7, 1]}]
                         },
                         {
                         '故事线ID': '1ab1853a-89fc-11ea-8c27-f4d108568a73',
                         '故事线名称': '问候',
                         '意图': [
                         ...
                         ]
                         }
                    ]
                    """
                    INTENDS['意图'].append(
                        {
                            '意图ID': intent_id,
                            'PID': intent_pid,
                            '意图': intent_cont,
                            '回复': intent_reply,
                        }
                    )
            else:
                break
            STORIES_DICT['故事线ID'] = story_id
            STORIES_DICT['故事线名称'] = story_name
            STORIES_DICT.update(INTENDS)
            # print('当前故事线包含的意图：', STORIES_DICT)
            # print()
            STORIES_LIST.append(STORIES_DICT)
    # print('当前主题包含的所有故事线：')
    # print(STORIES_LIST)
    return STORIES_LIST


def mysql_to_neo4j(bank_neo4j,scene_id,scene_name,topic_id,topic_name):
    """
    数据存入neo4j中
    :return:
    """
    # 建场景和主题
    bank_neo4j.schema_init(
        scene_id=scene_id,
        scene_name=scene_name,
        topic_id=topic_id,
        topic_name=topic_name
    )
    # 构建该场景和主题下的数据，便于传入neo4j
    STORIES_LIST = neo4j_datafrom(topic_id = topic_id,
                                 topic_name = topic_name)
    # 传入该场景和主题下的所有故事线和意图，生成图数据
    BatchToNeo4j(data=STORIES_LIST,scene_id=scene_id,topic_id=topic_id).mysql_to_neo4j()
    return STORIES_LIST

def begin_to_start():
    """
    主调度程序
    :return:
    """
    bank_neo4j = info2neo()
    # 清空neo4j
    bank_neo4j.delet_all_schema()
    # 查出mysql中一共有多少场景
    scenes = Op_Mysql().Select_Query(tablename='cb_ms_scenes',output=['ID_','NAME_'])
    print('场景：',scenes)

    # 所有故事线
    STORIES_LIST = []

    for scene in scenes:
        scene_id = scene[0]
        scene_name = scene[1]
        print()
        print('mysql中场景ID，名称：',scene_id,scene_name)
        # 查询该场景下在mysql中有哪些主题ID及名称
        topics = Op_Mysql().Select_Query(tablename='cb_ms_topic', output=['ID_', 'NAME_'],where="SCENES_ID_="+"'"+scene_id+"'")
        if topics:
            for topic in topics:
                topic_id = topic[0]
                topic_name = topic[1]
                print('mysql中主题ID及名称：',topic_id,topic_name)
                STORIES_LIST_PARTIAL = mysql_to_neo4j(
                    bank_neo4j = bank_neo4j,
                    scene_id=scene_id,
                    scene_name=scene_name,
                    topic_id=topic_id,
                    topic_name=topic_name
                )
                if STORIES_LIST_PARTIAL:
                    STORIES_LIST = STORIES_LIST + STORIES_LIST_PARTIAL
    # 保存故事线为pkl
    stories_pkl_path = os.path.join(os.path.dirname(sys.path[0]), 'stories.pkl')
    with open(stories_pkl_path, 'wb') as file:
        pickle.dump(STORIES_LIST, file)
    print('故事线pkl保存完毕...')

if __name__ == '__main__':
    begin_to_start()