
import pickle
import typing
from typing import Type
from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.training_data import Message, TrainingData
from py2neo import Graph
import os,sys
import logging
from typing import Text, List, Dict, Any, Optional
logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata

class MyComponent(Component):
    """A new component"""

    # Which components are required by this component.
    # Listed components should appear before the component itself in the pipeline.
    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        """Specify which components need to be present in the pipeline."""

        return []

    # Defines the default configuration parameters of a component
    # these values can be overwritten in the pipeline configuration
    # of the model. The component should choose sensible defaults
    # and should be able to create reasonable results with the defaults.
    defaults = {}

    requires = []
    # Defines what language(s) this component can handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    language_list = None

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)
        # print("component_config:",component_config)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        pass

    def find_intent_id(self,pid):
        """
        查询以上一轮对话意图为PID的意图ID
        pid:上一轮对话意图id
        :return:
        """
        with open('stories.pkl', 'rb') as f:
            data = pickle.load(f)
        pid_res_list = []
        for d in data:
            for intent in d['意图']:
                _ID = intent['意图ID']
                _PID = intent['PID']
                # print('所有意图：',_ID,_PID)
                if _PID == pid:
                    pid_res_list.append(_ID)
        return pid_res_list

    def process(self, message: Message, **kwargs: Any) -> None:

        sender_id_intent_dict = {}
        last_turn_intent = 'None'
        try:
            # 读取历史对话记录
            with open('111.pkl', 'rb') as file:
                sender_id_intent_dict = pickle.load(file)
        except Exception as e:
            print(e)

        _sender_id = message.get('sender_id')
        """
        rasa源码更改地方：
        rasa.core.processor.py
        
        rasa.core.interpreter
            
        rasa.core.training.dsl
            parse_data = await self.interpreter.parse(message,'')
            
        rasa.nlu.model.py
        """
        text = message.text
        intent = message.get("intent")
        print('用户id：',_sender_id)
        print('意图初步分类结果：',intent)
        # 该问句的所有分类结果概率
        all_possible_intents =  message.get("intent_ranking")
        confidence = intent['confidence']
        intent_ranking = []

        if confidence < 0.8 :
            # 该sender_id的上一轮意图，从mysql中提取
            try:
                # 如果该sender_id下有历史对话记录
                last_turn_intent = sender_id_intent_dict[_sender_id]
            except Exception as e:
                print(e)
            print('上一轮对话意图：', last_turn_intent)

            if last_turn_intent != 'None':
                # neo4j连接查找pid意图
                # graph = Graph('http://{}:{}'.format(NEO4J_CONFIG.config_dict['ip'],NEO4J_CONFIG.config_dict['port']),
                #               username = NEO4J_CONFIG.config_dict['username'],
                #               password = NEO4J_CONFIG.config_dict['password'])
                # search_pid = "match (n) where n.PID ='{0}' return n.name".format(last_turn_intent)
                # # print("search_pid:",search_pid)
                # # 以上一轮对话意图为PID的意图
                # pid_res = list(graph.run(search_pid))
                # pid_res_list = [res.values()[0] for res in pid_res]

                # 读取stories.pkl文件查找pid意图
                pid_res_list = self.find_intent_id(pid=last_turn_intent)
                print('以上一轮对话意图为PID的意图:')
                print(pid_res_list)
                # 在分类模型结果中，pid为上一轮为对话意图的意图名称
                for possible_intent in all_possible_intents:
                    # print("possible_intent:",possible_intent,type(possible_intent))
                    possible_intent_name = possible_intent['name']
                    if possible_intent_name in pid_res_list:
                        # print("possible_intent_name:", possible_intent_name)
                        # 保存纠正后的对话意图
                        sender_id_intent_dict[_sender_id] = possible_intent_name
                        with open('111.pkl', 'wb') as file:
                            pickle.dump(sender_id_intent_dict, file)
                        intent = {"name": possible_intent_name, "confidence": 1.0}
                        print('意图纠正：', intent)
                        intent_ranking.append(intent)
                        message.set("intent", intent, add_to_output=True)
                        message.set("intent_ranking", intent_ranking, add_to_output=True)
                        break

        else:
            # 保存当前对话意图
            sender_id_intent_dict[_sender_id] = intent['name']
            with open('111.pkl', 'wb') as file:
                pickle.dump(sender_id_intent_dict, file)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading."""

        pass

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["Component"] = None,
        **kwargs: Any,
    ) -> "Component":
        """Load this component from file."""

        if cached_component:
            return cached_component
        else:
            return cls(meta)