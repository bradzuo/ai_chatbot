# encoding: utf-8
from Utils.ParseYaml import DBConfigParser
# from SystemLog.SystemLog import SystemLog
import pymysql
import traceback
from Utils.Log import Logger

class Static_Config:

    def __init__(self,host=None,port=None,user=None,password=None,dbanme=None):
        if host is None and port is None and user is None and password is None and dbanme is None:
            #self.config = DBConfigParser().get_config(server='mysql',key='43conn')
            self.config = DBConfigParser().get_config(server='mysql', key='localhostconn')
            #self.config = DBConfigParser().get_config(server='mysql', key='222conn')
            # self.config = DBConfigParser().get_config(server='mysql',key='48conn')
            #self.config = DBConfigParser().get_config(server='mysql', key='41conn_test')
            # self.config = DBConfigParser().get_config(server='mysql', key='67.25connai')
            self.config['cursorclass'] = pymysql.cursors.DictCursor
        else:
            self.config = {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'db': dbanme,
                'charset': 'utf8',
                'cursorclass': pymysql.cursors.DictCursor,
            }

        # self.log = SystemLog(name='spider').save

class Op_Mysql(Static_Config):
    # 返回可用于multiple rows的sql拼装值
    def multipleRows(self,params):
        ret = []
        # 根据不同值类型分别进行sql语法拼装
        for param in params:
            if isinstance(param, (int,  float, bool)):
                ret.append(str(param))
            elif isinstance(param, (str, 'utf-8')):
                param=param.replace('"','\\"')
                ret.append( '"' + param + '"' )
            else:
                print('unsupport value: %s ' % param)
        return '(' + ','.join(ret) + ')'

    def Insert_Query(self,tablename,column, datas):
        try:
            connection = pymysql.connect(**self.config)
        except pymysql.err.OperationalError as e:
            # self.log.error('pymysql.err.OperationalError:%s' %str(e))
            raise e
        except Exception as e:
            # self.log.error(e)
            raise e
        count=0
        try:
            with  connection.cursor() as cursor:
                v = ','.join(["%s" for i in range(len(column))])
                if isinstance(column,list):
                     column = ','.join(column)

                try:
                    if len(datas) == 1:
                        query_sql = 'INSERT INTO ' + tablename + '(' + column + ') VALUES%s' %self.multipleRows(datas[0])
                        cursor.execute(query_sql)
                    else:
                        query_sql = 'INSERT INTO ' + tablename + '(' + column + ') VALUE(' + v + ')'
                        cursor.executemany(query_sql,datas)
                    count=count+1
                    connection.commit()
                except pymysql.err.IntegrityError as e:
                       # self.log.info(e)
                       # self.log.info(datas)
                       # errorcode = eval(str(e))[0]
                       # if errorcode == 1062:
                       #     print('主键重复')
                       pass
                except Exception as e:
                    traceback.print_exc()
                    #print(e,datas)
                    connection.rollback()
                     #print('需要特殊处理','INSERT INTO %s(%s) VALUES (%s)',datas)
        finally:
            connection.close()

        #print('本次共插入%d条' %count)

    def Select_Query(self,tablename,output=None,where='1=1',dict_=False):
        try:
            connection = pymysql.connect(**self.config)
        except pymysql.err.OperationalError as e:
            # self.log.error('pymysql.err.OperationalError:%s' %str(e))
            raise e
        except Exception as e:
            # self.log.error(e)
            raise e

        try:
            with  connection.cursor() as cursor:
                outputlist = []
                if not output:
                    sql = 'select * from %s where %s' % (tablename, where)

                if isinstance(output, list):
                    sql = 'select %s from %s where %s' %(','.join(output),tablename,where)

                if isinstance(output,str):
                    sql = 'select %s from %s where %s' % (output, tablename, where)
                # print('查询数据库：',sql)
                cursor.execute(sql)
                result = cursor.fetchall()

                if dict_:
                    return result

                if result is None or isinstance(result,tuple):
                    return None

                for res_ in result:
                    r = []
                    if isinstance(output, list):
                        for item in output:
                            r.append(res_[item])
                        outputlist.append(r)
                    if isinstance(output, str):
                        outputlist.append(res_[output])

                if not output:
                    outputlist = result


                # if len(outputlist)==1 and isinstance(outputlist[0],str):
                #     return outputlist[0]
                # else:
                return outputlist
        except Exception as e:
            print(e)
        finally:
            connection.close()

    def u_data(self,  code='test2010', tablename='ait_training', status='COMPLETE'):

        this_is_log = Logger(code).logger
        try:
            connection = pymysql.connect(**self.config)
        except pymysql.err.OperationalError as e:
            this_is_log.error('pymysql.err.OperationalError:%s' %str(e))
            raise e
        except Exception as e:
            # self.log.error(e)
            this_is_log.error(e)
            raise e
        query_sql = " update {tablename} set STATUS_=\'{status}\' where CODE_ = \'{code}\'" \
                    "".format(tablename=tablename, status=status, code=code)
        print('执行mysql语句:',query_sql)
        count = 1
        try:
            with connection.cursor() as cursor:
                try:
                    if count < 10:
                        print('第{}次更新'.format(count))
                        connection.ping(reconnect=True)
                        cursor.execute(query_sql)
                        print('执行mysql执行语句')
                        connection.commit()
                        print('更新mysql状态成功')
                        this_is_log.info('更新mysql状态成功')
                    else:
                        print('更新mysql状态失败')
                        this_is_log.info('更新mysql状态失败')
                        connection.close()
                except Exception as e:
                    this_is_log.error(e)
                    connection.rollback()
        except:
            count += 1
        finally:
            connection.close()

    def Updata_Query(self, table_name, data, condition=None):
        """
        更新列表中的数据
        :param table_name: 表名
        :param data: 更新数据
        :param condition: 条件
        :return:
        """
        if condition:
            sql = "update {} set {} where {};".format(table_name, data, condition)
        else:
            sql = "update {} set {};".format(table_name, data)

        print(sql)
        try:
            connection = pymysql.connect(**self.config)
        except pymysql.err.OperationalError as e:
            # self.log.error('pymysql.err.OperationalError:%s' % str(e))
            raise e
        except Exception as e:
            # self.log.error(e)
            raise e
        with  connection.cursor() as cursor:
            try:
                connection.ping(reconnect=True)
                cursor.execute(sql)
                connection.commit()
            except Exception as e:
                # self.log.info(e)
                connection.rollback()
        connection.close()

    def delet_data(self,table_name,column=None,data=None,where=None):

        try:
            connection = pymysql.connect(**self.config)
        except pymysql.err.OperationalError as e:
            # self.log.error('pymysql.err.OperationalError:%s' % str(e))
            raise e
        except Exception as e:
            # self.log.error(e)
            raise e
        with  connection.cursor() as cursor:
            try:
                connection.ping(reconnect=True)
                sql = ''
                if isinstance(data, list) and column and not where:
                    sql = "delete from {0} where {1} = %s".format(table_name, column)
                    print(sql)
                    cursor.executemany(sql,data)
                if where:
                    sql = "delete from {0} where {1}".format(table_name, where)
                    print(sql)
                    cursor.execute(sql)
                connection.commit()
            except Exception as e:
                # self.log.info(e)
                connection.rollback()
        connection.close()

if __name__ == '__main__':
    def multipleRows(params):
        ret = []
        # 根据不同值类型分别进行sql语法拼装
        for param in params:
            if isinstance(param, (int, float, bool)):
                ret.append(str(param))
            elif isinstance(param, (str, 'utf-8')):
                param = param.replace('"', '\\"')
                ret.append('"' + param + '"')
            else:
                print('unsupport value: %s ' % param)
        return '(' + ','.join(ret) + ')'
    # Op_Mysql().Insert_Query('cb_ms_intent',["ID_","PID_","STORY_ID_",'INTENT_','REPLY_'],
    #                         [('321','XXX','3','HELLO','SHIT')])

    # res = Op_Mysql().Select_Query(tablename='cb_ms_stories',output='ID_',where="TOPIC_ID_= %s and TOPIC_NAME_= %s " % ('"wh"','"问候"'))
    #
    # print(res)
    # if res:
    #     Op_Mysql().delet_data(table_name='cb_ms_intent',column='STORY_ID_',data=res)
    #     Op_Mysql().delet_data(table_name='cb_ms_stories',where="TOPIC_ID_='wh' and TOPIC_NAME_='问候'")
    #     print('complete')
    # column = ','.join(['PID_','STORY_ID','INTENT_','REPLY_'])
    # datas = [('XXX','3','HELLO','SHIT')]
    # if len(datas) == 1:
    #     query_sql = 'INSERT INTO ' + 'cb_ms_intent' + '(' + column + ') VALUES%s' % multipleRows(datas[0])
    #     print(query_sql)
    last_turn_intent = Op_Mysql().Select_Query(tablename='events', output='intent_name',
                                               where='sender_id=' + "'" + 'RasaWSHH' + "'")
    print()