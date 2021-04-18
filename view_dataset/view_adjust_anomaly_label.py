# Run this app with `python view_dataset.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import utils as tools
import numpy as np
import os


DATASET = 'sequential' # 'sequential' or 'concurrent'
MAX_ROW = 100 # 限制显示的条目
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

if DATASET == 'sequential':
    '''sequential data'''
    extract_gt_file = os.path.join('anomaly_label', 'anomaly_label_sequential.csv')
    ts_pickle_file = os.path.join('result_extracted_data', 'distributed_ts_df_sequential.pickle')
    adjust_gt_file = os.path.join('anomaly_label','adjust_anomaly_label_sequential.csv')
    run_time_file = os.path.join('anomaly_label', 'run_time.csv')
else:
    '''concurrent data'''
    extract_gt_file = 'anomaly_label_concurrent.csv'
    ts_pickle_file = os.path.join('result_extracted_data', 'distributed_ts_df_concurrent.pickle')


gt_df = tools.read_csv_to_dataframe(extract_gt_file)
adjust_gt_df = tools.read_csv_to_dataframe(adjust_gt_file)
ts_dict = tools.read_object_from_pickle_file(ts_pickle_file)
run_time = tools.read_csv_to_dataframe(run_time_file)

# 节点列表
node_list = list(ts_dict.keys())
node_list.sort()

metric_list = ts_dict[node_list[0]].columns.tolist()
metric_list.sort()
metric_list.remove('time')
metric_list.remove('timestamp')

# 异常列表
anomaly_type = list(set(gt_df['anomaly_type'].values.tolist()))
anomaly_type.sort()

# 一个全生命周期的class
class Record():
    def __init__(self, help):
        self.anomaly_event = {}
        self.help = help
    def update_anomaly_event(self, name, value):
        self.anomaly_event[name] = value
    def get_anomaly_event(self, name):
        return self.anomaly_event[name]
    def search_anomaly_event(self, name):
        if name in self.anomaly_event.keys():
            return True
        else:
            return False

df_record = Record('Record the anomaly_event dataframe.')

# 下拉菜单
app.layout = html.Div([
    html.Div([
        html.H1(children='KPI metrics in multi-source micro-service data.'),
        # 下拉菜单，选择节点名
        html.Div([
            html.Label('Select the compute node:'),
            dcc.Dropdown(
                id='crossfilter_node_name',
                options=[{'label': i, 'value': i} for i in node_list],
                value=node_list[0] # 默认的数值
            ),

            html.Label('Select the KPI metric name'),
            dcc.Dropdown(
                id='crossfilter_metric_name',
                options=[{'label': i, 'value': i} for i in metric_list],
                value=metric_list[0] # 默认的数值
            ),

            html.Label('Select one or more injected anomaly types'),
            dcc.Checklist(
                id='crossfilter_anomaly_name',
                options=[{'label': i, 'value': i} for i in anomaly_type],
                value=anomaly_type,
                labelStyle={'display': 'inline-block'}
            ),

            html.Label('Show the curve using:'),
            dcc.RadioItems(
                id='crossfilter_value_type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '90%', 'display': 'inline-block', 'float': 'center'}),

    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        html.H4(children='KPI'),
        dcc.Markdown(children='''The **colored dots** represent the data points during the anomaly injection period, 
        but they may *not* be anomalies because they are not affected by the injected anomaly.'''),
        dcc.Markdown(children='''The **light blue area** represents the periods during that anomaly injection scipt is runing.'''),
        dcc.Markdown(children='''The **light red area** indicates the abnormal periods, in which the data points are affected by the injected anomalies. 
        These data points should be considered as *positive samples* when evaluating anomaly detection algorithms.'''),
        dcc.Graph(id='x-time-series'),
    ], style={'display': 'inline-block', 'width': '90%', 'height': '70%'}),

    html.Div([
        html.H4(children='Adjust anomaly periods'),
        html.Label(id='hor_row_num'),
        html.Div(id='adjust_anoamly_table')
    ]),

    html.Div([
        html.H4(children='Details about the anomaly events'),
        html.Label(id='row_num'),
        html.Div(id='anoamly_table')
    ])
])

def create_time_series(dff, axis_type, title, run_horizon_list=None, anomaly_horizon_list=None):
    '''
    dff: dataframe of metrics, ['time', 'timestamp', metric_name, 'type']
    true_anomaly_index: list of index, in which are indexes of labeled anomalies
    run_horizon_list: list of run_horizon, [[start_timestamp, end_timestanp], ...]
    '''

    time = dff.columns.tolist()[0] # time
    tsp = dff.columns.tolist()[1] # timestamp
    y = dff.columns.tolist()[2] # value
    label = dff.columns.tolist()[3] # normal or anomaly type
    str_tsp = [str(i) for i in dff[tsp].values]
    dff['str_timestamp'] = str_tsp
    # print(dff)
    # value
    fig = px.scatter(dff, x=tsp, y=y, hover_data=[time, 'str_timestamp'], color=label)
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')
    # 运行异常脚本的时间
    if run_horizon_list is not None:
        for horizon in run_horizon_list:
            fig.add_vrect(x0=horizon[0], x1=horizon[1],
                            fillcolor="LightBlue", opacity=0.5,
                            layer="below", line_width=0)
    if anomaly_horizon_list is not None:
        # print(anomaly_horizon_list)
        for horizon in anomaly_horizon_list:
            fig.add_vrect(x0=horizon[0], x1=horizon[1],
                            fillcolor="LightCoral", opacity=0.5,
                            layer="below", line_width=0)       
    # title
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)
    fig.update_layout(height=500, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})

    return fig

@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    dash.dependencies.Input('crossfilter_node_name', 'value'),
    dash.dependencies.Input('crossfilter_metric_name', 'value'),
    dash.dependencies.Input('crossfilter_anomaly_name', 'value'),
    dash.dependencies.Input('crossfilter_value_type', 'value'))
def update_showed_timeseries(node_name, metric_name, anomaly_name, axis_type):# 这里的三个输入即为@app后的三个输入，输出为output能接受的输出
    print('selected anomaly_type: {}'.format(anomaly_name))
    # 节点的数据
    node_data = ts_dict[node_name]
    # 目标metric
    metric_df = node_data[metric_name]
    # 时间轴
    time = node_data['time']
    timestamp = node_data['timestamp']

    # label
    label = ['normal'] * len(node_data)
    label = np.array(label)

    # 统计显示数据的范围用的
    min_timestamp = 1e20
    max_timestamp = 0

    anomaly_events = gt_df.iloc[0:0]
    run_horizon_list = []
    adjust_anomaly_horizon = []
    if len(anomaly_name) != 0:
        for name in anomaly_name:
            tmp_events =  gt_df[gt_df['anomaly_type']==name]
            anomaly_events = pd.concat([anomaly_events, tmp_events], axis=0)
            # 加载运行脚本的时间
            run_horizon_info = run_time[run_time['anomaly_type']==name]
            run_horizon_list.append([run_horizon_info.iloc[0]['start_timestamp'], run_horizon_info.iloc[0]['end_timestamp']])
            # 加载调整后的异常时间
            adjust_anomaly_horizon_df = adjust_gt_df[(adjust_gt_df['anomaly_type']==name) & (adjust_gt_df['node_name']==node_name) & (adjust_gt_df['metric_name']==metric_name)]
            for row_idx in range(len(adjust_anomaly_horizon_df)):
                event = adjust_anomaly_horizon_df.iloc[row_idx]
                adjust_anomaly_horizon.append([event['start_timestamp'], event['end_timestamp']])
        for row_idx in range(len(anomaly_events)):
            event = anomaly_events.iloc[row_idx]
            if event['start_timestamp'] < min_timestamp: min_timestamp = event['start_timestamp']
            if event['end_timestamp'] > max_timestamp: max_timestamp = event['end_timestamp']
            anomaly_idxes = node_data[(node_data['timestamp']<=event['end_timestamp']) & (node_data['timestamp']>=event['start_timestamp'])].index
            label[anomaly_idxes] = event['anomaly_type'] # 目的是标注异常
        
        # 没有选择任何异常的时候，全为正常, 展示所有数据
        # print('???',adjust_anomaly_horizon)
        label_df = pd.DataFrame(data={'type': label})
        dff = pd.concat([time, timestamp, metric_df, label_df], axis=1)

        # 显示的区间比异常出现的区间前后浮动xh，画图时候用的，Dash可视化的时候没什么用
        min_timestamp -= 3600*48
        max_timestamp += 3600*48
        index_hor = node_data[(node_data['timestamp']<max_timestamp) & (node_data['timestamp']>min_timestamp)].index
        index_hor = list(index_hor)

        showed_df = dff.iloc[min(index_hor):max(index_hor)]
        print('original: {}, now: {}, min: {}, max: {}'.format(len(dff), len(showed_df), min(index_hor), max(index_hor)))

    else:
        label_df = pd.DataFrame(data={'type': label})
        dff = pd.concat([time, timestamp, metric_df, label_df], axis=1)
        showed_df = dff
        run_horizon_list = None
        adjust_anomaly_horizon = None

    title = '<b>{}</b><br>{}'.format(node_name, metric_name)
    return create_time_series(showed_df, axis_type, title, run_horizon_list, adjust_anomaly_horizon)    




def create_table_using_dataframe(df, to_id, max_rows=None):
    if max_rows is not None:
        return_obj = html.Table(id=to_id, children=[html.Thead(html.Tr([html.Th(col) for col in df.columns])),
                                                            html.Tbody([
                                                                html.Tr([
                                                                    html.Td(df.iloc[i][col]) for col in df.columns
                                                                    ]) for i in range(min(len(df), max_rows))
                                                                        ])
                                                            ])
    else:
        return_obj = html.Table(id=to_id, children=[html.Thead(html.Tr([html.Th(col) for col in df.columns])),
                                                            html.Tbody([
                                                                html.Tr([
                                                                    html.Td(df.iloc[i][col]) for col in df.columns
                                                                    ]) for i in range(len(df))
                                                                        ])
                                                            ])       
    return return_obj

def get_anomaly_event(anomaly_type_list):
    anomaly_events = gt_df.iloc[0:0] # showed dataframe
    if len(anomaly_type_list) != 0:
        # 先找找有没有查询过
        # anomaly_type_list.sort()
        # search_name = '_'.join(anomaly_type_list)
        # if df_record.search_anomaly_event(search_name) is True:
        #     return df_record.get_anomaly_event(search_name)
        # else:
        #     for anomaly_type in anomaly_type_list:
        #         tmp_events =  gt_df[gt_df['anomaly_type']==anomaly_type]
        #         anomaly_events = pd.concat([anomaly_events, tmp_events], axis=0)
        #     df_record.update_anomaly_event(search_name, anomaly_events)
        # return anomaly_events
        for anomaly_type in anomaly_type_list:
            tmp_events =  gt_df[gt_df['anomaly_type']==anomaly_type]
            anomaly_events = pd.concat([anomaly_events, tmp_events], axis=0)
        return anomaly_events

@app.callback(
    dash.dependencies.Output('anoamly_table', 'children'), # 指定输出在object的什么位置，这里是html.Table的children属性
    dash.dependencies.Output('row_num', 'children'),
    dash.dependencies.Input('crossfilter_anomaly_name', 'value'))
def update_anomaly_event(anomaly_type_list):
    # 要返回的obj
    return_obj_list = []
    max_row = MAX_ROW
    # 查询dataframe
    anomaly_events = get_anomaly_event(anomaly_type_list)
    return_obj = create_table_using_dataframe(anomaly_events, 'anomaly_table', max_rows=max_row)
    return_obj_list.append(return_obj)

    # 关于显示的说明
    if len(anomaly_events) == 0:
        return_str = 'No matched anomaly event.'
    elif len(anomaly_events) != 0 and len(anomaly_events) <= max_row:
        return_str = 'There {} anomaly events in ground truth file.'.format(len(anomaly_events))
    elif len(anomaly_events) != 0 and len(anomaly_events) > max_row:
        return_str = 'There {} anomaly events in ground truth file, list top {} events here'.format(len(anomaly_events), max_row)
    return return_obj_list, return_str

@app.callback(
    dash.dependencies.Output('adjust_anoamly_table', 'children'), # 指定输出在object的什么位置，这里是html.Table的children属性
    dash.dependencies.Output('hor_row_num', 'children'),
    dash.dependencies.Input('crossfilter_node_name', 'value'),
    dash.dependencies.Input('crossfilter_metric_name', 'value'),
    dash.dependencies.Input('crossfilter_anomaly_name', 'value'))
def update_adjust_anomaly_horizon(node_name, metric_name, anomaly_type_list):
    # 要返回的obj
    return_df_list = []
    max_row = MAX_ROW
    # 查询dataframe
    adjust_anomaly_events = adjust_gt_df.iloc[0:0]
    for anomaly_type in anomaly_type_list:
        tmp_df = adjust_gt_df[(adjust_gt_df['anomaly_type']==anomaly_type) & (adjust_gt_df['node_name']==node_name) & (adjust_gt_df['metric_name']==metric_name)]
        adjust_anomaly_events = pd.concat([adjust_anomaly_events, tmp_df], axis=0)
    obj = create_table_using_dataframe(adjust_anomaly_events, 'adjust_anoamly_table', max_rows=max_row)
    return_df_list.append(obj)
    # print(adjust_anomaly_events)

    # 关于显示的说明
    if len(adjust_anomaly_events) == 0:
        return_str = 'No matched anomaly period.'
    elif len(adjust_anomaly_events) != 0 and len(adjust_anomaly_events) <= max_row:
        return_str = 'There {} anomaly periods in ground truth file.'.format(len(adjust_anomaly_events))
    elif len(adjust_anomaly_events) != 0 and len(adjust_anomaly_events) > max_row:
        return_str = 'There {} anomaly periods in ground truth file, list top {} periods here'.format(len(adjust_anomaly_events), max_row)
    return return_df_list, return_str



if __name__ == '__main__':
    app.run_server(debug=True)