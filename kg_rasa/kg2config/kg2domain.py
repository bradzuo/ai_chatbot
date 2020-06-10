# coding:utf-8
import json,sys,os
root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print('当前根路径:',root_path)

class KG2Domain(object):

    def __init__(self):
        self.list_intent = []
        self.domain_path = os.path.join(root_path,'domain.yml')
        self.str_domain = ''
        self.str_domain_intent = 'intents:' + '\n'
        self.str_domain_actions = 'actions:' + '\n'
        self.str_domain_response = 'responses:' + '\n'


    def gen_intent_list(self,individuals):
        '''
        产生KG中所有意图数据
        :return:
        '''
        for _ind in individuals:
            _json = {
                "ID": _ind.__getitem__('name'),
                "INTEND_NO": str(_ind.__getitem__('问法')).split('/'),  # list
                "PID": _ind.__getitem__('PID'),
                "RESP": _ind.__getitem__('回复')
            }
            self.list_intent.append(_json)
        return self.list_intent

    def assem_domain_md(self):
        '''
        组装domain md文件
        :return:
        '''
        for _intent in self.list_intent:

            _intent_ID = _intent.get('ID')
            # print('_intent_ID:', _intent_ID)
            _answer = _intent.get('RESP')
            # print('_answer:', _answer)
            # 组装domain.yml intents
            self.str_domain_intent = self.str_domain_intent + '- ' + _intent_ID + '\n'

            _domain_response = ''
            # 组装domain.yml actions
            self.str_domain_actions = self.str_domain_actions + '- ' + 'utter_' + _intent_ID +  '\n'
            # 组装domain.yml responses
            _domain_response = _domain_response + '  ' + 'utter_' + _intent_ID + ':' + '\n'
            _domain_response = _domain_response + '  ' + '- text: ' + _answer + '\n'
            self.str_domain_response = self.str_domain_response + _domain_response

        # domain_resonse中加入utter_out_of_scope
        utter_out_of_scope_answer = '对不起，不懂，我就是这么高冷。'
        self.str_domain_response = self.str_domain_response + '  ' + 'utter_out_of_scope' + ':' + '\n'
        self.str_domain_response = self.str_domain_response  + '  ' + '- text: ' + utter_out_of_scope_answer + '\n'
        self.str_domain = self.str_domain + self.str_domain_intent + self.str_domain_actions + self.str_domain_response

    def write_domain(self):
        '''
        domain.md 文件导入
        :return:
        '''
        with open(self.domain_path, "w", encoding='utf8') as f:
            f.writelines(self.str_domain)
        f.close()

if __name__ == '__main__':
    kg = KG2Domain()
    kg.gen_intent_list()
    kg.assem_domain_md()
    kg.write_domain()
    print('domain.md 文件写入成功...')

