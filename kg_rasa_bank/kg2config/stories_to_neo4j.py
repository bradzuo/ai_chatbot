# coding:utf-8
'''
excel故事线导入neo4j

安装py2neo v3 :pip install py2neo==3.1.1
最新py2neo为v4,感觉太难用了
'''
from py2neo import Node, Relationship, NodeMatcher
from gen_schema import info2neo,time_cost
import os
root_path = os.path.dirname(os.path.realpath(__file__))

class BatchToNeo4j(info2neo):
    def __init__(self,data,scene_id,topic_id):
        super().__init__()
        self.data = data
        self.scene_id = scene_id
        self.topic_id = topic_id

    def schema_init(self,scene_id ,scene_name,topic_id,topic_name):
        pass

    def judge_scence_and_topic_if_exsists(self):
        """
        # 在批量导入之前，判断一下是否有该场景和主题
        :return:
        """
        scene_flag = self.look_entity(entity_name=self.scene_id,entity_type='SCENE')
        if not scene_flag:
            raise Exception('无场景{}'.format(self.scene_id))

        topic_flag = self.look_entity(entity_name=self.topic_id,entity_type='TOPIC')
        if not topic_flag:
            raise Exception('无主题{}'.format(self.topic_id))
        # duplicate_execute_line = "match (n)-[r]->(b) where n.name='{}' return r;".format(self.topic_id)
        # results = self.graph.run(duplicate_execute_line)
        return topic_flag

    def duplicate_topic_stories(self):
        pass

    def look_and_create(self, name, entity_type):
        """
        # 查找节点是否不存在，不存在就创建一个
        :param name:
        :param entity_type:
        :return:
        """
        matcher = NodeMatcher(self.graph)
        end = matcher.match(entity_type,name=name).first()
        if end == None:
            # 创建节点
            # print('没有节点{}'.format(name),'，开始创建新节点..')
            end = Node(entity_type, name=name)  # Node(不需要加label=)
        return end

    def build_node(self,start_node,node_ID,node_type,node_name):
        """
        # 新建节点
        :param start_node: 前置节点
        :param node_ID: 节点ID
        :param node_type: 节点schema
        :param node_name: 节点名称
        :return:
        """
        end_node = self.look_and_create(name=node_ID, entity_type=node_type)
        r = Relationship(start_node, node_name, end_node, name=node_name)  # 实体三元组的关系,指定开始节点和结束节点以及关系名称
        # 当存在该关系时不会创建新的
        self.graph.create(r)  # 创建实体三元组
        return end_node

    def build_Hierarchical_Relation(self):
        """
        建意图之间的层级关系
        :return:
        """
        # 找出所有意图
        # matcher = NodeMatcher(self.graph)
        # _intends = list(matcher.match("INTEND"))
        # 遍历查询PID
        # for _intend in _intends:
        for _data in self.data:
            _intends = _data['意图']
            for _intend in _intends:
                _pid =  _intend['PID']
                # 若PID为none，跳过；不为none，构建关系
                if _pid != 'None':
                    _id = _intend['意图ID']
                    # 要新建关系，传入的需要是node格式
                    matcher = NodeMatcher(self.graph)
                    start = matcher.match('INTEND', name=_pid).first()
                    if not start:
                        print('不存在节点{}'.format(_pid))
                        break
                    end = matcher.match('INTEND', name=_id).first()
                    if not end:
                        print('不存在节点{}'.format(_id))
                        break
                    # print('start:',start)
                    # print('end:',end)
                    r = Relationship(start,'ex_context', end, name='ex_context')  # 实体三元组的关系,指定开始节点和结束节点以及关系名称
                    # 当存在该关系时不会创建新的
                    self.graph.create(r)  # 创建实体三元组

    @time_cost
    def mysql_to_neo4j(self):
        """
        # excel的故事线导入neo4j
        :return:
        """
        # 判断一下是否有该场景和主题，必须要有该场景和主题才能进行后续导入
        topic_node = self.judge_scence_and_topic_if_exsists()
        for data in self.data:
            story_id = data['故事线ID']
            story_name = data['故事线名称'].strip().replace('\n','')
            print('故事线入neo4j：',story_id,story_name)
            # 新建故事线节点
            story_node = self.build_node(start_node=topic_node,node_ID=story_id,node_type='STORY',node_name='故事线')
            # 插入故事线属性
            self.insert_property(properties=[story_id, '名称', story_name])

            for intend in data['意图']:
                intend_id = intend['意图ID'].strip().replace('\n','')
                PID = intend['PID']
                if PID:
                    PID = PID.strip().replace('\n','')
                intend_name = intend['意图'].strip().replace('\n','')
                intend_resp = intend['回复'].strip().replace('\n','')
                # 新建意图
                self.build_node(start_node=story_node,node_ID=intend_id,node_type='INTEND',node_name='意图')
                # 插入故事线属性
                self.insert_property(properties=[intend_id, 'PID', PID])
                self.insert_property(properties=[intend_id, '问法', intend_name])
                self.insert_property(properties=[intend_id, '回复', intend_resp])
        self.build_Hierarchical_Relation()

if __name__ == '__main__':

    data = [
        {'故事线ID': '1ab1853a-89fc-11ea-8c27-f4d108568a73',
         '故事线名称': '问候',
         '意图': [{'意图ID': 'f14275f0-7d5f-11ea-9bb0-f4d108568a73_f1433728-7d5f-11ea-8f7d-f4d108568a73',
                 'PID': 'none',
                 '意图': '我要存活期/存活期/我想存活期/我想存点活期/我要存点活期存款/存点活期',
                 '回复': '请问您在我行有账户吗？',
                 '下标': [7, 1]}]
         }
        ]

    scene_id = 'fzdh'
    topic_id = 'whzj'
    BatchToNeo4j(data,scene_id,topic_id).mysql_to_neo4j()