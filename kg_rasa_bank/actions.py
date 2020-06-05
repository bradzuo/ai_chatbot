# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
import sys,os
sys.path.append(os.path.dirname(__file__))

class ActionGreetUser(Action):
    """Revertible mapped action for utter_greet"""

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher, tracker, domain):
        print('action_greet......')
        dispatcher.utter_template("utter_greet", tracker)
        return [UserUtteranceReverted()]


# intent_demand_{0_0_a_1}
# class intent_demand_0_0_a_1(Action, entityCode, tableCode):
#     """Revertible mapped action for intent_demand_0_0_a_1"""
#
#     def name(self) -> Text:
#         return "intent_demand_0_0_a_1"
#
#     def run(self, dispatcher, tracker, domain):
#         print('intent_demand_0_0_a_1......')
#         dispatcher.utter_template("intent_demand_0_0_a_1", tracker)
#         return [UserUtteranceReverted()]


class ActionByeUser(Action):
    """Revertible mapped action for utter_greet"""

    def name(self):
        return "action_goodbye"

    def run(self, dispatcher, tracker, domain):
        print('action_greet......')
        dispatcher.utter_template("utter_goodbye", tracker)
        return [UserUtteranceReverted()]

class ExplanKeyWord(Action):
    """Revertible mapped action for utter_greet"""

    def __init__(self):
        self.keywords = self.load_keywords()

    def load_keywords(self):
        keywords_dict = {}
        with open('data/bank/explan_keywords.txt', 'r', encoding='utf-8') as f:
            keywords = f.readlines()
        for keyword in keywords:
            k,v = keyword.split(',')
            keywords_dict[k] = v.replace('\n','')
        return keywords_dict

    def name(self):
        return "to_explan_keyword"

    def run(self, dispatcher, tracker, domain):
        keyword = tracker.get_slot('keyword')
        print("to_explan_keyword")
        print("keyword:",keyword)
        if keyword == None:
            dispatcher.utter_message("能再说一下你要查询的关键词是什么吗？")
            return []
        else:
            if keyword in self.keywords.keys():
                dispatcher.utter_message(self.keywords[keyword])
                return []
            else:
                dispatcher.utter_message("能再说一下你要查询的关键词是什么吗？")
                return []



class SearchForQuality(Action):
    """Revertible mapped action for utter_greet"""

    def __init__(self):
        self.quality = self.load_quality()

    def load_quality(self):
        quality_hash = {}
        with open('data/bank/quality.txt', 'r', encoding='utf-8') as f:
            qualities = f.readlines()
        for quality in qualities:
            k,q,v = quality.split(',')
            quality_hash[k + q] = v.replace('\n','')
        return quality_hash

    def name(self):
        return "to_search_quality"

    def run(self, dispatcher, tracker, domain):
        print("to_search_quality")
        keyword = tracker.get_slot('keyword')
        quality = tracker.get_slot('quality')

        if keyword and quality:
            try:
                resp = self.quality[keyword + quality]
                dispatcher.utter_message(resp)
                return []
            except Exception as e:
                print('查询quality时出错:',e)
                dispatcher.utter_message('您确定要查询{}的{}吗？因为小辉辉绞尽脑汁也没有想起咱'
                                         '有这项业务啊，如果不是，请再说一遍您要查询的内容。'.format(keyword,quality))
                return []
        else:
            dispatcher.utter_message("对不起，我可能太累了，没听清，您能再说一下你"
                                     "要查询的内容？您可以这样问我:大额存单的利息如何计算")
            return []
