from py2neo import Graph, Node, RelationshipMatcher, NodeMatcher
import json
import re
from treelib import Node, Tree
import json,sys,os
root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print('当前根路径:',root_path)

class KG2Stroies(object):

    def __init__(self,graph):
        self.re_cols = []
        self.root_set = set()
        self.list_intent = []
        self.stories_path = os.path.join(root_path,'data/stories.md')
        self.id_to_name = {}
        self.graph = graph


    def gen_intent_list(self,individuals):
        '''
        产生KG中所有意图数据
        :return:
        '''
        # list_intent = []
        for _ind in individuals:
            _json = {
                "identity": _ind.identity,
                "_intent_no": _ind.__getitem__('name'),
                "ex__content": _ind.__getitem__('问法'),
                "ex__answer": _ind.__getitem__('回复')
            }
            self.id_to_name[_ind.__getitem__('name')] =  _ind.identity
            self.list_intent.append(_json)
        return self.list_intent

    def get_intent_relations(self):
        '''
        获取所有意图关系数据：  34 --> 35   意图之间的层级关系
        :return: [（34,35）,(56,57)]
        '''
        re_matcher = RelationshipMatcher(self.graph)
        re_list = list(re_matcher.match(r_type='ex_context'))
        for _r in re_list:
            name_to_id = []
            _re_unit = tuple(re.findall('\((.*?)\)', str(_r))) # 匹配数字
            for _name in _re_unit:
                _id = self.id_to_name[_name]
                name_to_id.append(str(_id))
            _tuple = tuple(name_to_id)
            self.re_cols.append(_tuple)
        print("self.re_cols:",self.re_cols)
        return self.re_cols

    def get_intent_root(self):
        '''
        获取所有意图数据根节点：将[（34,35）,(56,57)]中的非根节点删除
        :return:
        '''
        node_set = set()
        # 构造根节点
        for _o in self.re_cols:
            # 将所有父节点取出
            node_set.add(_o[0])   # _0 -> (34,35)
        # 找到根节点
        # 如果在node_set中的元素有父节点，那么删除，因为它一定不是根节点
        self.root_set = node_set.copy()
        for _s in node_set:
            for _g in self.re_cols:
                if _s == _g[1]:
                    self.root_set.remove(_s)
        # print("self.root_set:",self.root_set)
        return self.root_set

    def get_intent_trees(self, intent_root):
        '''
        获取KG中所有意图树信息  查找根节点的下一级节点
        :param intent_root:
        :return: [['143159', '143133'], ['143195', '143169'], ['143194', '138864', '139663']] 如“143194”的下一级就有两个节点，也就意味着故事应该有两个
        '''
        intent_re_list = [] # 所有意图树列表
        for _i in intent_root:
            '''
            构建查询cypher，查询所有意图根节点的路径
            '''
            # [r:ex_context*1..9]中的 *1..9 代表意图层级
            _cypher = ' MATCH (n1:INTEND)-[r:ex_context*1..9]->(n2:INTEND)' + '\n'
            _cypher = _cypher + 'where id(n1) =' + str(_i) + '\n'
            _cypher = _cypher + ' RETURN id(n2)'
            df_intent_id = self.graph.run(_cypher).to_data_frame()
            _intent_id = df_intent_id.values.tolist()
            print("_intent_id:",_intent_id)
            intent_id_list = [_i]
            # 将意图路径组装成list
            for _id_list in _intent_id:
                for _id in _id_list:
                    intent_id_list.append(str(_id))
            intent_re_list.append(intent_id_list)
        print("intent_re_list:",intent_re_list)
        return intent_re_list


    def find_intent_tree_list(self, re_cols, intent_re_list):
        '''
        获取意图树集合  构成意图树
        :param re_cols: 所有的上下级节点
        :param intent_re_list: 根节点与下一级节点，可能有多个，也就对应着多个故事，要进行判断
        :return:
        '''
        # 生成意图关系列表
        intent_rank_list = []
        for _intent_id_list in intent_re_list:
            intent_rank = []
            for _intent_id in _intent_id_list:
                for _re in re_cols:
                    # TODO:通过这样的遍历找到根节点，根节点的下一级，根节点的下一级的下一级这样的三层级节点列表，但是第四层级的节点怎么办呢？
                    if(_intent_id == _re[0] or _intent_id == _re[1]):
                        intent_rank.append(_re)
            intent_rank_list.append(intent_rank)
        print("intent_rank_list:",intent_rank_list)
        # 意图关系集合去重
        intent_rank_rel_list = []
        for rank_list in intent_rank_list:
            intent_rank_rel = []
            for rank in rank_list:
                if(not rank in intent_rank_rel):
                    intent_rank_rel.append(rank)
            intent_rank_rel_list.append(intent_rank_rel)
        print("intent_rank_rel_list:",intent_rank_rel_list)
        return intent_rank_rel_list

    def find_single_intend_node(self):
        _cypher = 'MATCH (n1:SCENE)-[r1]->(n2:TOPIC)-[r2]->(n3:STORY)-[r3]->(n4:INTEND)'
        _cypher = _cypher + "where n1.name = 'fzdh'" + '\n'
        _cypher = _cypher + ' RETURN n4.name'
        df_intent = self.graph.run(_cypher).to_data_frame()
        common_intent_name = df_intent.values.tolist()
        # print(common_intent_name)
        return common_intent_name

    def intent_tree_cons(self, intent_rank_rel_list, intent_root):
        '''
        生成意图树
        :param intent_rank_rel_list:  三层级关系树，第四层级怎么办的？
        :return:
        '''
        # print('intent_root:', intent_root)
        # print('intent_rank_rel_list:', intent_rank_rel_list)
        # 先创建根节点列表
        intent_stroies_tree_list = []
        for _root in intent_root:
            tree = Tree()
            tree.create_node(tag=_root, identifier=_root)  # root node
            intent_stroies_tree_list.append(tree)

        intent_stroies_tree = intent_stroies_tree_list.copy()

        # 从每个根节点出发建立意图树
        _tree_list = []  # 层级关系节点列表，用于后面生成故事线
        for _root_tree in intent_stroies_tree:
            # print('_root_tree:', _root_tree)
            _root = _root_tree.root  # 根节点
            # print('_root:', _root)
            # 迭代意图关系列表
            for rank_rel_list in intent_rank_rel_list:
                _temp_tree_list = []
                # 找到了以_root为根节点的路径
                if _root == rank_rel_list[0][0]:
                    # 迭代意图关系
                    for rank_index,rank_rel in enumerate(rank_rel_list):
                        parent = rank_rel[0]
                        node = rank_rel[1]
                        # 通过意图之间的上下位关系创建节点
                        _root_tree.create_node(tag=node, identifier=node, parent=parent)
                    break
        return intent_stroies_tree


    def assem_stories_md(self, intent_stroies_tree_list):
        '''
        组装意图故事线md文件
        :param intent_stroies_tree_list: 整棵树，所有意图的关系树，但是只有三层级
        :return:
        '''
        str_storeis = ''
        for _intent_tree in intent_stroies_tree_list:
            # 树展开，_tree_list: ['143194', '138864', '139663']
            # _paths_to_leaves得到的是整颗树的层级关系,paths_to_leaves()方法可以直接打印出根节点到叶子结点的路径，返回的是一个list
            _paths_to_leaves = _intent_tree.paths_to_leaves()
            print("paths_to_leaves:",_paths_to_leaves)
            for _tree_list in _paths_to_leaves:
                str_storeis = str_storeis + '## ' + ' ' + _intent_tree.identifier + '\n'
                # 定义话术业务含义
                # print("_tree_list:",_tree_list)
                # 根据层级去提取相应的数据信息
                for _id in _tree_list:
                    for _intent in self.list_intent:
                        _identity = _intent.get('identity')
                        _intent_no = _intent.get('_intent_no')
                        # busi = _intent_no.split('_')[1]
                        # # print('_intent_no:', _intent.get('_intent_no'))
                        # # print('answer:', _intent.get('ex__answer'))
                        _answer = _intent.get('ex__answer')

                        if (int(_id) == _identity):
                            str_storeis = str_storeis + '* ' + _intent_no + '\n'
                            str_storeis = str_storeis + '  - ' + 'utter_' + _intent_no  + '\n'

                # str_storeis = '## ' + ' ' + busi + '\n' + str_storeis
                str_storeis = str_storeis + '\n'
        # 加入通用对话话术
        common_intent_names = self.find_single_intend_node()
        for c_i_n in common_intent_names:
            c_story = ''
            c_story = c_story + '## ' + ' ' + 'common_stories' + '\n'
            c_story = c_story + '* ' + c_i_n[0] + '\n'
            c_story = c_story + '  - ' + 'utter_' + c_i_n[0] + '\n'
            str_storeis = str_storeis + c_story + '\n'
        return str_storeis


    def write_stories(self, str_storeis):
        '''
        stories.md文件写入
        :return:
        '''
        with open(self.stories_path, "w", encoding='utf8') as f:
            f.writelines(str_storeis)
        f.close()



if __name__ == '__main__':
    kg = KG2Stroies()
    kg.gen_intent_list()
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
        # print(_tree.to_json(with_data=True))
        # print('expand_tree:', ','.join([_tree[node].tag for node in \
        #                                _tree.expand_tree(mode=Tree.DEPTH)]))
        # print('nodes:', _tree.nodes)
    str_storeis = kg.assem_stories_md(intent_stroies_tree_list)
    # print('str_storeis:', str_storeis)
    kg.write_stories(str_storeis)
    print('stories.md 文件写入成功...')





