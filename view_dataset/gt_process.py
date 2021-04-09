import json, os, datetime
import pandas as pd

DATASET = 'sequential' # 'sequential' or 'concurrent'


def convert_timestamp_to_CEST_str(x):
    # 标准时间是不使用夏令时（DST）的国家或地区的当地时间。
    d_utc = datetime.datetime.utcfromtimestamp(x) # UTC时间
    d_delta = datetime.timedelta(days=0, hours=1) # CEST = UTC + 1
    d_cest = d_utc + d_delta
    time_string = d_cest.strftime('%Y-%m-%d %H:%M:%S.%f CEST')
    return time_string


if __name__ == '__main__':
    if DATASET == 'concurrent':
        gt_file_list = [r'F:\00-datasets\multi-source_micro-service_data\concurrent data\concurrent data\reports\output_boot.json', 
                        r'F:\00-datasets\multi-source_micro-service_data\concurrent data\concurrent data\reports\output_image.json',
                        r'F:\00-datasets\multi-source_micro-service_data\concurrent data\concurrent data\reports\output_network.json']
    elif DATASET == 'sequential':
        gt_file_list = [r'F:\00-datasets\multi-source_micro-service_data\sequential_data\sequential_data\reports\j_boot_delete_report.json', 
                        r'F:\00-datasets\multi-source_micro-service_data\sequential_data\sequential_data\reports\j_image_report.json',
                        r'F:\00-datasets\multi-source_micro-service_data\sequential_data\sequential_data\reports\j_network_output.json']

    total_label_df = pd.DataFrame(columns=['anomaly_type', 'start_time', 'end_time', 'start_timestamp', 'end_timestamp'])

    for json_file in gt_file_list:
        with open(json_file, 'r', encoding='utf-8') as f:
            configs = json.load(f)
        hook_list = configs['tasks'][0]['subtasks'][0]['workloads'][0]['hooks'][0]['results']

        anomaly_type = json_file.split(os.sep)[-1].split('.')[0].split('_')[1]
        for info in hook_list:
            tmp_df = pd.DataFrame(columns=['anomaly_type', 'start_time', 'end_time', 'start_timestamp', 'end_timestamp'])
            tmp_df['anomaly_type'] = [anomaly_type]
            tmp_df['start_timestamp'] = [info['started_at']]
            tmp_df['end_timestamp'] = [info['finished_at']]
            tmp_df['start_time'] = [convert_timestamp_to_CEST_str(info['started_at'])] 
            tmp_df['end_time'] = [convert_timestamp_to_CEST_str(info['finished_at'])]
            total_label_df = pd.concat([total_label_df, tmp_df], axis=0)

    total_label_df.to_csv('anomaly_label_{}.csv'.format(DATASET), index=False)
