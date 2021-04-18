# Multi-Source Distributed System Data for AI-powered Analytics

This fork records some data processing and visualizing code, including:

- some information about "Impact of injection exception on KPI", which are extracted from config file: [link](kpi_anomalies.md)
- some processed data and visualization code & page, view [this page](./view_dataset/readme.md)

Files in `result_extracted_data`
- `distributed_ts_df_concurrent.zip` and `distributed_ts_df_sequential.zip`: dataframe extract from original dataset. they have been processed.

Files in `anomaly_label`
- `anomaly_label_concurrent.csv` and `anomaly_label_sequential.csv`: periods during that anomalies are injected. It is extracted from `report` in original dataset.
- `run_time.csv`: periods during that anomaly injection scipts are runing.
- `adjust_anomaly_label_sequential.csv`: anomaly periods in which data points of KPI is affected by injected anomalies. 

以下是原readme file。

----------------
*THE ORIGINAL README FILE*

This repository contains the simple scripts for data statistics, and link to the multi-source distributed system dataset.

You may find details of this dataset from the original paper: 

*Sasho Nedelkoski, Jasmin Bogatinovski, Ajay Kumar Mandapati, Soeren Becker, Jorge Cardoso, Odej Kao, "Multi-Source Distributed System Data for AI-powered Analytics".*


<pre><code>
@inproceedings{nedelkoski2020multi,
  title={Multi-source Distributed System Data for AI-Powered Analytics},
  author={Nedelkoski, Sasho and Bogatinovski, Jasmin and Mandapati, Ajay Kumar and Becker, Soeren and Cardoso, Jorge and Kao, Odej},
  booktitle={European Conference on Service-Oriented and Cloud Computing},
  pages={161--176},
  year={2020},
  organization={Springer}
}
  </code></pre>

<b>If you use the data, implementation, or any details of the paper, please cite!</b>

General Information:

This repository contains the simple scripts for data statistics, and link to the multi-source distributed system dataset.

The multi-source/multimodal dataset is composed of `distributed traces`, `application logs`, and `metrics` produced from running a complex distributed system (Openstack). In addition, we also provide the `workload` and `fault scripts` together with the `Rally report` which can serve as ground truth (all at the Zenodo link below). We provide two datasets, which differ on how the workload is executed. The sequential_data is generated via executing workload of sequential user requests. The concurrent_data is generated via executing workload of concurrent user requests.

Important: The logs and the metrics are synchronized with respect time and they are both recorded on CEST (central european standard time). The traces are on UTC (Coordinated Universal Time -2 hours). They should be synchronized if the user develops multimodal methods. Please read the IMPORTANT_experiment_start_end.txt file before working with the data.

If you are interested in these data, please request the data via <a href="url">Zenodo</a>. Kindly note that the affiliation, and information about the utilization of the dataset. If you do not receive any response from Zenodo within one week, please check your spam mailbox or consider to resubmit your data request with the required information.
