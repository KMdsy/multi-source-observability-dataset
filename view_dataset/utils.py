# utils.py
import numpy as np
import pandas as pd
import os, sys, logging
import pickle, math
import datetime, time, pytz
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def preprocess_nxgraph(graph):
    node2idx = {}
    idx2node = []
    node_size = 0
    for node in graph.nodes():
        node2idx[node] = node_size
        idx2node.append(node)
        node_size += 1
    return idx2node, node2idx

def convert_CEST_str_to_timestamp(x):
    d_cest = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S CEST')
    d_delta = datetime.timedelta(days=0, hours=1) # CEST = UTC + 1
    d_utc = d_cest - d_delta # UTC = CEST - 1
    timestamp = (d_utc - datetime.datetime(1970, 1, 1)).total_seconds()
    timestamp = round(timestamp, 6)
    return timestamp

def convert_timestamp_to_CEST_str(x):
    # 标准时间是不使用夏令时（DST）的国家或地区的当地时间。
    d = datetime.datetime.utcfromtimestamp(x) # UTC时间
    d_delta = datetime.timedelta(days=0, hours=1) # CEST = UTC + 1
    d_cest = d + d_delta
    time_string = d_cest.strftime('%Y-%m-%d %H:%M:%S CEST')
    return time_string

def read_structed_log(file_path, save_path, is_read_from_file=False, start_time_str=None, end_time_str=None, save_name='structed_log_df'):
    '''
    从file_path(.csv file)读取结构化的日志到pandas dataframe

    input
        file_path: csv文件的路径
        is_read_from_file: 直接从已有的文件中读取
        save_path: 保存的文件夹
    output
        df: 读取到的pandas.dataframe对象
        save_name: 被保存的文件路径
    '''
    if start_time_str is not None and end_time_str is not None:
        START_TIME = convert_CEST_str_to_timestamp(start_time_str)
        END_TIME = convert_CEST_str_to_timestamp(end_time_str)
    
    save_name = os.path.join(save_path, '{}.pickle'.format(save_name))

    if is_read_from_file is True:
        if os.path.exists(save_name) is False:
            raise FileNotFoundError('{} not exists!'.format(save_name))
        else:
            with open(save_name, 'rb') as f:
                df = pickle.load(f)
                f.close()
            logger.info('Read log data from a saved pickle file: {}'.format(save_name))
    else:
        df = pd.read_csv(file_path, sep=',', header=0)

        # 插入一列，放置timestamp
        df.rename(columns = {'@timestamp':'time_tz','Timestamp':'time'} ,inplace=True)

        # 删除 Hostname为空的，Log_level为空的，时间戳time_tz为空的
        df = df.drop(df[(pd.isna(df['Hostname'])) | (pd.isna(df['log_level'])) | (pd.isna(df['time_tz']))].index.tolist(), axis=0)
        # 删除 log_level为INFO的
        df['log_level'] = df['log_level'].apply(lambda x: x.upper())
        df = df.drop(df[df['log_level']=='INFO'].index.tolist(), axis=0)



        def convert(x):
            drop_idx = x.rfind(':')
            x = x[:drop_idx] + x[(drop_idx+1):]
            d_cest = datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%f000%z') # 虽然有tzinfo，但直接使用d_utc.timetuple()作出的时间戳还是没有更改时差的时间
            d_delta = datetime.timedelta(days=0, hours=1) # UTC = CEST - 1
            d_utc = d_cest - d_delta
            timestamp = (d_utc - datetime.datetime(1970, 1, 1)).total_seconds()
            timestamp = round(timestamp, 6)
            return timestamp
        def add_cest(x):
            # 某些异常确实存在，有timestamp而没有time的情况
            y = '{} {}'.format(x, 'CEST')
            return y

        df['timestamp'] = df['time_tz'].values # 复制time_tz列
        df['timestamp'] = df['timestamp'].apply(lambda x: convert(x)) # 转为timestamp

        df['time'] = df['time'].apply(lambda x: add_cest(x)) # time列使用有CEST标志的时间来标识

        df = df.drop(['time_tz'], axis=1) # 删除带时区的time_tz列，用timestamp代替

        if start_time_str is not None and end_time_str is not None:
            # FILTER OUT THE TIMESTAMPS THAT ARE OUTSIDE OF THIS INTERVAL
            drop_index = df[(df['timestamp'] > END_TIME) & (df['timestamp'] < START_TIME)].index
            df = df.drop(drop_index)
            logger.info('Drop {} logs that outside the monitoring intervel. Number of logs: {}'.format(len(drop_index), len(df)))
            

        # save
        if os.path.exists(save_path) is False:
            os.makedirs(save_path)
        f = open(save_name, 'wb')
        pickle.dump(df, f)
        f.close()

    return df, save_name

def read_distributed_ts(file_dir, save_path, is_read_from_file=False, start_time_str=None, end_time_str=None, save_name='distributed_ts_df'):
    '''
    从文件夹中读取多源的时间序列数据

    input
        file_dir: 包含有时间序列数据的文件夹，需要从文件名来判断数据来源（可能来自不同的物理节点）
        is_read_from_file: 直接从已有的文件中读取
        save_path: 保存的文件夹
    output
        ts_dic: dict, key: 指标数据的指标名，value: 包含时间序列的dataframe
        save_path: 要存储的路径
    '''
    if start_time_str is not None and end_time_str is not None:
        START_TIME = convert_CEST_str_to_timestamp(start_time_str)
        END_TIME = convert_CEST_str_to_timestamp(end_time_str)

    save_name = os.path.join(save_path, '{}.pickle'.format(save_name))

    if is_read_from_file is True:
        if os.path.exists(save_name) is False:
            raise FileExistsError('{} is not exists!'.format(save_name))
        else:
            with open(save_name, 'rb') as f:
                ts_dic = pickle.load(f)
                f.close()
            logger.info('Read time series data from a saved pickle file: {}'.format(save_name))
            
    else:
        file_list = os.listdir(file_dir)
        file_list.sort()

        ts_dic = {}

        for idx, file_name in enumerate(file_list): 
            logger.info('File {}/{}: {}'.format(idx+1, len(file_list), file_name))

            node_name = file_name.split('.')[0].split('_')[0] # 从文件名中提取节点的名称

            file_path = os.path.join(file_dir, file_name)
            tmp_df = pd.read_csv(file_path, sep=',', header=0)

            # 插入一列，放置timestamp
            tmp_df.rename(columns = {'now':'time'},inplace=True)

            tmp_df['timestamp'] = tmp_df['time'].values.tolist()
            tmp_df['timestamp'] = tmp_df['timestamp'].apply(lambda x: convert_CEST_str_to_timestamp(x))

            if start_time_str is not None and end_time_str is not None:
                # FILTER OUT THE TIMESTAMPS THAT ARE OUTSIDE OF THIS INTERVAL
                drop_index = tmp_df[(tmp_df['timestamp'] > END_TIME) & (tmp_df['timestamp'] < START_TIME)].index
                tmp_df = tmp_df.drop(drop_index)
                logger.info('Drop {} values in file: {}. Values in this file: {}'.format(len(drop_index), file_name, len(tmp_df)))

            # 由于数据集中包含很多在同一秒内的kpi值，转化为timestamp后出现时间戳重叠的情况，因此将按照原先表的顺序，将同一秒的时间戳加上毫秒级的标识
            # 默认所有的采样均为时间轴上的均匀采样
            old_timestamp = tmp_df['timestamp'].values
            new_timestamp = []
            same_num = 0 # 重复的次数，（真实重复次数 - 1）
            for time_idx, this_time in enumerate(old_timestamp):
                if time_idx == 0:
                    new_timestamp.append(this_time)
                else:
                    # 比较是否与上一个时间戳一样
                    if this_time == old_timestamp[time_idx-1]:
                        # 本次迭代到的与上一个时刻的时间戳一样
                        same_num += 1 # 有same_num个时间戳需要被修改
                        new_timestamp.append(this_time)
                    else:
                        # 本次迭代到的是一个新的时间戳，上一个时间戳共出现了same_num+1次
                        # 修改前面的same_num个时间戳
                        add_msec = round(1/(same_num+1), 6) # 每次采样之间的间隔秒数
                        # 需要修改time_idx-1, ..., time_idx-same_num位置的数字
                        times = 1
                        for change_idx in range(int(time_idx-same_num), time_idx, 1):
                            # 第change_idx的位置要被加上add_msec*(change_idx+1)个毫秒
                            new_timestamp[change_idx] = new_timestamp[change_idx] + add_msec*times
                            times += 1

                        # 本次新轮询到的时间戳加入列表
                        new_timestamp.append(this_time)
                        # 重置重复次数
                        same_num = 0
            tmp_df['timestamp'] = new_timestamp



            ts_dic[node_name] = tmp_df

        # save
        if os.path.exists(save_path) is False:
            os.makedirs(save_path)
        f = open(save_name, 'wb')
        pickle.dump(ts_dic, f)
        f.close()

    return ts_dic, save_name


def read_csv_to_dataframe(file_path):
    tmp_df = pd.read_csv(file_path, sep=',', header=0)
    return tmp_df



def read_object_from_pickle_file(file_path):
    f = open(file_path, 'rb')
    ob = pickle.load(f)
    f.close()
    return ob






