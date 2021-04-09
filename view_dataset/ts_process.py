import numpy as np
import pandas as pd
import utils as tools
import json, os


DATASET = 'sequential' # 'sequential' or 'concurrent'
is_read_from_file = False
save_data_path = 'result_extracted_data'

if __name__ == '__main__':
    if DATASET == 'concurrent':
        start_time_str = '2019-11-19 16:12:13 CEST' # extracted from IMPORTANT_experiment_start_end.txt file
        end_time_str = '2019-11-20 20:45:00 CEST' # extracted from IMPORTANT_experiment_start_end.txt file
        ts_dir = r'F:\00-datasets\multi-source_micro-service_data\concurrent data\concurrent data\metrics'
        ts_dic, ts_dic_save_name = tools.read_distributed_ts(ts_dir, save_data_path, is_read_from_file, start_time_str, end_time_str, 'distributed_ts_df_concurrent') #load time series data
    else:  
        ''' sequential data'''
        start_time_str = '2019-11-19 18:38:39 CEST' # extracted from IMPORTANT_experiment_start_end.txt file
        end_time_str = '2019-11-20 02:30:00 CEST' # extracted from IMPORTANT_experiment_start_end.txt file
        ts_dir = r'F:\00-datasets\multi-source_micro-service_data\sequential_data\sequential_data\metrics'
        ts_dic, ts_dic_save_name = tools.read_distributed_ts(ts_dir, save_data_path, is_read_from_file, start_time_str, end_time_str, 'distributed_ts_df_sequential') #load time series data
    