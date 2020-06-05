"""
读取所有intend生成所有训练语料
"""

from py2neo import Graph, Node, RelationshipMatcher, NodeMatcher
import json,sys,os
root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print('当前根路径:',root_path)

class KG2Nlu(object):

    def __init__(self):
        self.list_intent = []
        self.str_nlu = ''
        self.nlu_path = os.path.join(root_path,'data/nlu.md')


    def gen_intent_list(self,individuals):
        '''
        产生KG中所有意图数据
        :return:
        '''
        for _ind in individuals:
            # print(_ind)
            _json = {
                "ID": _ind.__getitem__('name'),
                "INTEND_NO": str(_ind.__getitem__('问法')).split('/'), # list
                "PID": _ind.__getitem__('PID'),
                "RESP": _ind.__getitem__('回复')
            }
            self.list_intent.append(_json)
        return self.list_intent

    def assem_nlu_md(self):
        '''
        组装自然语言理解nlu md文件
        :return:
        '''
        for _intent in self.list_intent:
            _intent_no = _intent.get('ID')
            # print('content:', _intent.get('ex__content'))
            _content = _intent.get('INTEND_NO')

            # 组装nlu.md
            _str_nlu = '## intent:' + str(_intent_no) + '\n'
            _c_str = ''.join(['- ' + _c + '\n' for _c in _content])
            _str_nlu = _str_nlu + _c_str + '\n'
            self.str_nlu = self.str_nlu + _str_nlu

    def write_nlu(self):
        '''
        nul.md 文件导入
        :return:
        '''
        with open(self.nlu_path, "w", encoding='utf8') as f:
            f.writelines(self.str_nlu)
        f.close()

if __name__ == '__main__':
    kg = KG2Nlu()
    kg.gen_intent_list()
    kg.assem_nlu_md()
    kg.write_nlu()
    print('nul.md 文件写入成功...')

