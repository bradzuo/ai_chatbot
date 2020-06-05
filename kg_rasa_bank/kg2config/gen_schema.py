"""
# 根据用户定义的场景和主题先在neo4j中生成schema
"""
import re
from py2neo import Node, Relationship, Graph,NodeMatcher
from Utils.Log import Logger
import datetime
from EnvConfig.neo4j_config import Neo4jConfig
import argparse
logger = Logger().logger

def time_cost(func):
    """
    # 计算函数运行时间
    :param func:
    :return:
    """
    def func_cost_time(self,*args,**kwargs):
        start_time = datetime.datetime.now()
        result = func(self,*args,**kwargs)
        end_time = datetime.datetime.now()
        cost_time = (end_time - start_time).total_seconds()
        print(func.__name__,'耗时：',cost_time)
        return result
    return func_cost_time

class info2neo(object):
    def __init__(self):
        # ap = argparse.ArgumentParser(description='neo4j账号和密码')
        # ap.add_argument('-a','--account',default='neo4j',help='25服务器上neo4j账号')
        # ap.add_argument('-c','--passwd',default='neo4j007',help='25服务器上neo4j密码')
        # self.args = vars(ap.parse_args())
        # print('初始化neo4j参数：',self.args)
        self.connect_neo4j()

    def connect_neo4j(self):
        """
        # 连接neo4j
        :return:
        """
        # 写入公司25服务器(两种连接方式)
        # self.graph = Graph('http://172.22.67.25:7474',username='neo4j',password='neo4j007')
        # 写入本地
        self.graph = Graph('http://{}:7474'.format(Neo4jConfig().config_dict['ip']),username='neo4j',password='neo4j007')
        # self.delet_all_schema()
        logger.info('连接neo4j成功》》》》》')

    def delet_all_schema(self):
        """
        # 清空neo4j
        :return:
        """
        self.graph.delete_all()

    @time_cost
    def schema_init(self,scene_id ,scene_name,topic_id,topic_name):
        """
        # 建场景和主题
        :return:
        """
        scene_execute_line = "create (n:SCENE {name: '%s'}) return n;" % (scene_id)
        flag = self.look_entity(entity_name=scene_id, entity_type='SCENE')
        if not flag:
            self.graph.run(scene_execute_line)
        self.insert_property(properties=[scene_id,'名称',scene_name])

        topic_execute_line = "create (n:TOPIC {name: '%s'}) return n;" % (topic_id)
        flag = self.look_entity(entity_name=topic_id, entity_type='TOPIC')
        if not flag:
            self.graph.run(topic_execute_line)
        self.insert_property(properties=[topic_id,'名称',topic_name])

        start = self.look_entity(entity_name=scene_id,entity_type='SCENE')
        end = self.look_entity(entity_name=topic_id,entity_type='TOPIC')
        r = Relationship(start, '主题', end, name='主题')  # 实体三元组的关系,指定开始节点和结束节点以及关系名称
        self.graph.create(r)  # 创建实体三元组

    def look_entity(self,entity_name,entity_type):
        """
         # 查询节点
        :param entity_name:
        :param entity_type:
        :return:
        """
        matcher = NodeMatcher(self.graph)
        return matcher.match(entity_type, name=entity_name).first()
        # return self.graph.find_one(label="{}".format(entity_type), property_key="name", property_value=entity_name)

    def insert_property(self,properties):
        """
        # 插入属性
        :param line:
        :return:
        """
        execute_line = "match (n) where n.name='{0}'set n.{1} = '{2}'return n;".format(properties[0],properties[1],properties[2])
        # print('插入属性语句:',execute_line)
        self.graph.run(execute_line)

if __name__ == '__main__':

    scene_id = 'cxck'
    scene_name = '储蓄存款'
    topic_id = 'lczq'
    topic_name = '零存整取'
    bank_neo4j = info2neo()
    bank_neo4j.schema_init(
                scene_id = scene_id,
                scene_name = scene_name,
                topic_id = topic_id,
                topic_name = topic_name
                )
