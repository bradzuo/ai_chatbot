from py2neo import Graph

graph = Graph('http://172.22.67.25:7474', username='neo4j', password='neo4j007')
search_pid = "match (n) where n.PID ='{0}' return n.name".format('f356f990-90d6-11ea-883f-f4d108568a73_f38ac9b6-90d6-11ea-873c-f4d108568a73')
# print("search_pid:",search_pid)
# 以上一轮对话意图为PID的意图
pid_res = list(graph.run(search_pid))
pid_res = [res.values()[0] for res in pid_res]
print('以上一轮对话意图为PID的意图:')
print(pid_res)