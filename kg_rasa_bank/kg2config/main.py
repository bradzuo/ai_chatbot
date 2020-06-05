# coding:utf-8

"""
将mysql中的数据导入neo4j，模型训练配置再从neo4j中自动获取
"""
from EnvConfig.neo4j_config import Neo4jConfig
from kg2domain import KG2Domain
from kg2nlu import KG2Nlu
from kg2stories import KG2Stroies
from mysql2neo4j import begin_to_start
from py2neo import Graph, Node, RelationshipMatcher, NodeMatcher

class ConfFromNeo4j():

    def __init__(self):
        self._con_neo4j()

    def _con_neo4j(self):
        """
        连接neo4j
        :return:
        """
        self.graph = Graph("http://{}:7474".format(Neo4jConfig().config_dict['ip']), auth=("neo4j", "neo4j007"))
        matcher = NodeMatcher(self.graph)
        # individuals = list(matcher.match("owl__NamedIndividual").where("_.uri =~ '.*intent_demand.*'"))
        self.individuals = list(matcher.match("INTEND"))

    def load_domain(self):
        """
        导出domain
        :return:
        """
        kg = KG2Domain()
        kg.gen_intent_list(individuals=self.individuals)
        kg.assem_domain_md()
        kg.write_domain()
        print('domain.md 文件写入成功...')

    def load_nlu(self):
        """
        导出nlu。md
        :return:
        """
        kg = KG2Nlu()
        kg.gen_intent_list(individuals=self.individuals)
        kg.assem_nlu_md()
        kg.write_nlu()
        print('nul.md 文件写入成功...')

    def load_stories(self):
        """
        导出故事线
        :return:
        """
        kg = KG2Stroies(graph=self.graph)
        kg.gen_intent_list(individuals=self.individuals)
        # 获取所有意图之间的关系
        re_cols = kg.get_intent_relations()
        intent_root = kg.get_intent_root()
        # print('re_cols:', re_cols)
        print('intent_root:', intent_root)
        intent_re_list = kg.get_intent_trees(intent_root)
        print('intent_re_list:', intent_re_list)
        intent_rank_rel_list = kg.find_intent_tree_list(re_cols, intent_re_list)
        # print('intent_rank_rel_list:', intent_rank_rel_list)
        intent_stroies_tree_list = kg.intent_tree_cons(intent_rank_rel_list, intent_root)
        # print('intent_stroies_tree_list:', intent_stroies_tree_list)
        print('size:', len(intent_stroies_tree_list))
        # os.exit()
        for _tree in intent_stroies_tree_list:
            _tree.show()
        str_storeis = kg.assem_stories_md(intent_stroies_tree_list)
        # print('str_storeis:', str_storeis)
        kg.write_stories(str_storeis)
        print('stories.md 文件写入成功...')

def load_conf_from_neo4j():
    """
    从neo4j中导出对话模型的配置，训练数据及故事线
    :return:
    """
    # 导出mysql，导入neo4j
    begin_to_start()
    # 导出配置
    cfn = ConfFromNeo4j()
    cfn.load_domain()
    cfn.load_nlu()
    cfn.load_stories()

if __name__ == '__main__':


    """
    intent_root: {'189', '169', '303', '506', '249', '190', '463', '126', '283', '251', '5', '130', '185', '238'}
    _intent_id: [[112]]
    _intent_id: [[309], [394], [480]]
    _intent_id: [[138]]
    _intent_id: [[430], [199], [532]]
    _intent_id: [[200]]
    _intent_id: [[490]]
    _intent_id: [[266], [205]]
    _intent_id: [[505], [166], [196], [509], [295], [342], [236], [128]]
    _intent_id: [[395]]
    _intent_id: [[206], [281], [67], [284], [382], [4], [467], [252]]
    _intent_id: [[285], [170]]
    _intent_id: [[511]]
    _intent_id: [[6], [144]]
    _intent_id: [[510], [168]]

    """
    load_conf_from_neo4j()