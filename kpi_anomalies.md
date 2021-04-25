# 前序知识

- 虚拟机：在容器技术之前，业界的网红是虚拟机，虚拟机技术的代表，是vmware 和openstack
所谓虚拟机就是在你的操作系统里面。装一个软件，然后通过这个软件，再模拟一台甚至多台字电脑出来。字电脑里面可以和正常电脑一样运行程序。并且子电脑与子电脑之间是相互隔离的，互不影响。

- 容器技术：而容器技术恰好没有这些缺点，他不需要虚拟出整个操作系统，只需要虚拟一个小规模的环境（类似“沙箱”），它启动时间很快，几秒钟就能完成，并且，它对资源的利用率很高（一台主机可以同时运行几千个docker容器），此外，他占用的空间很小，虚拟机一般要几GB到几十GB的空间，而容器只需要MB甚至KB级

两者联系：虚拟机属于虚拟技术，而docker这样的容器技术，也是虚拟技术，属于轻量级的虚拟机

虚拟机的缺点：虚拟机虽然可以隔离出很多子电脑，但是占用空间大，启动更慢，虚拟软件可能还要花钱（如vmware）


## Openstack

- OpenStack是个虚拟化的云操作系统。它把一大块资源打碎了，每小块资源上部署操作系统甚至一些应用。拿出其中一小块，租给你用，你不用关心，也无从知道，你系统的CPU、RAM、DISK在哪台共享的服务器上。常用于IaaS云部署。
- OpenStack 社区和 Docker 的结合越来越紧密。然而正如其他回答所示，OpenStack 主要还是用来管理 VM（虚拟机）。
- OpenStack 很庞大，底层资源管理能力很强。
- Kubernetes 的强项在于容器编排，可以很好解决应用上云的问题。Kubernetes 可以运行在 OpenStack 上。Kubernetes 的好处，推荐来自浙大的这篇文章：请注意，容器技术圈已迈入后Kubernetes时代！

以下是5个OpenStack的重要构成部分：
- Nova：计算服务
- Swift：存储服务
- Glance：镜像服务
- Keystone：认证服务
- Horizon：UI服务

### Neutron

[参考这个文章](https://blog.csdn.net/weixin_45682995/article/details/104753025)

neutron是openstack中提供网路服务的组件。Neutron仅有一个主要服务进程Neutron-server，它运行于控制节点上。

### Nova

[参考这个文章](https://zhuanlan.zhihu.com/p/34594654)

Nova是Openstack云中的计算组织控制器；管理OpenStack云中实例的生命周期的所有活动；是管理计算资源、网络认证所需的可扩展性平台。
Nova组件由Nova-API，Nova-scheduler,Nova-conductor,Nova-compute以及提供消息传递的消息队列（message queue）和数据库模块（database）组成
- Nova-API：主要提供了统一风格的REST-API接口，作为Nova组件的入口，接受用户的请求
- Nova-scheduler：负责调度将实例分配到具体的计算结点
- Nova-conductor：主要负责与Nova数据库进行交互
- Nova-compute： Nova-compute的结点运行在计算节点上，用于虚拟机实例的创建和管理
- message queue：主要用于Nova各个组件之间的消息传递

Nova-API作为Nova的入口，将会接受用户的请求，然后以消息队列的方式，将请求发送给Nova-scheduler，
Nova-scheduler从消息队列中侦听到Nova-API的消息后，去数据库中去查询当前计算结点的负载和使用情况，

由于Nova-scheduler不能直接跟数据库进行交互，因此会借助于消息队列的方式，通过Nova-conductor组件进而与数据库进行交互，最后根据查询到的结果，将虚拟机实例分配到当前负载最小并且满足启动虚拟机实例的那个计算节点上

当然实际实例的创建起停工作并不是由Nova-scheduler来完成，Nova-scheduler的主要功能是实现实例的调度分配工作。最终实例的创建还是需要调用另外一个组件Nova-compute来完成，当然实例的创建也离不开镜像、网络、存储等等一些资源的配合，因此Nova-compute组件将会于Nova-valume,Nova-network等等一些组件，通过消息队列的方式实现相互的协作，最终完成虚拟机实例的创建。

![image](https://user-images.githubusercontent.com/16149619/115983030-72573d80-a5d1-11eb-962e-48a9405a39be.png)

### keystone

[参考这个文章](https://blog.csdn.net/weixin_51432789/article/details/114640411)

Keystone 组件是作为OpenStack 集群中统一认证、授权的模块，其核心功能就是针对于User（用户）、Tenant（租户）、Role（角色）、Token（令牌/凭证）的控制（手工编译部署即围绕此功能展开的）
- User：使用 openstack 的用户。
- Tenant：租户,可以理解为一个人、项目或者组织拥有的资源的合集。在一个租户中可以拥有很多个用户，这些用户可以根据权限的划分使用租户中的资源。
- Role：角色，用于分配操作的权限。角色可以被指定给用户，使得该用户获得角色对应的操作权限。
- Token：指的是一串比特值或者字符串，用来作为访问资源的记号。Token 中含有可访问资源的范围和有效时间，token 是用户的一种凭证，需要使用正确的用户名和密码向 Keystone 服务申请才能得到 token。

### Glance

[参考这个文章](https://blog.csdn.net/weixin_50344914/article/details/114020739)

镜像服务就是用来管理镜像的，让用户能够发现、获取和保存镜像。在openstack中提供提供镜像服务的是glance。（通过扫描、搜索发现镜像，想要获取要先识别和上传）。镜像英文名为image，通常是指一一系列文件或一个磁盘驱动器的精确副本。镜像文件起始和zip压缩包类似，他将特定的一系列文件按照一定的格式格式制作成单一的文件，让用户下载和使用。


------

## k8s架构

主节点 (Master node)

> API server: 是整个系统的对外接口，供客户端和其它组件调用，相当于“营业厅”
> 
> Scheduler: 负责对集群内部的资源进行调度，相当于“调度室”
> 
> Controller manager: 负责管理控制器，相当于“大总管”

node节点 (Compute node)

> Pod: 是Kubernetes最基本的操作单元。一个Pod代表着集群中运行的一个进程，它内部封装了一个或多个紧密相关的容器。除了Pod之外，K8S还有一个Service的概念，一个Service可以看作一组提供相同服务的Pod的对外访问接口。
> 
> Docker: 创建容器的
> 
> kubelet: 主要负责监视指派到它所在Node上的Pod，包括创建、修改、监控、删除等
> 
> kube-proxy: 主要负责为Pod对象提供代理
> 
> `Fluentd`: 主要负责日志收集、存储与查询
> 
> kube-dns
> 

## 微服务调用

微服务之间的通信一般都会使用一些预定义的通信格式与协议，如RESTFul, RPC, （在这个数据集中好像还包括别的，如HTTP）。



# 设备组织架构

extracted from file: `multi-source-observabil, ity-dataset/workloads/os-faults-latest.yaml`

wally113 (node, controller, ip: 130.149.249.123)

|_ wally117 (node, compute, ip: 130.149.249.127)

|_ wally122 (node, compute, ip: 130.149.249.132)

|_ wally123 (node, compute, ip: 130.149.249.133)

|_ wally124 (node, compute, ip: 130.149.249.134)

--------------

# 已核对的事件

Extracted from `Rally` HTML report -> `Task overview` -> `Input file`. Responding code are copied from Github Repositoriy https://github.com/snedelkoski/multi-source-observability-dataset

## sequential data

1. NovaServers.boot_and_delete_server (extracted from `j_boot_delete_report.html`)
	- 运行文件`action`：sh ./restart_nova_compute_nodes.sh
	- 时间`trigger`：[250, 500] iteration
	- 细节`runner`：每一次事件触发，都有`3`个进程同时测试、模拟多用户并发访问的情况。task中执行测试用例的次数：750
	- 任务成功标准`sla`：100% 成功

	- **被重启的`nova_compute`位于wally117, wally122, wally123, wally124上，但位于wally113控制节点上的也被重启了，看看有没有影响**


restart_nova_compute_nodes.sh
```shell
#!/bin/bash +x

#SSH into compute nodes and execute commands from commands-to-exec-nova-compute.sh
cat commands-to-exec-nova-compute.sh | sshpass -p 'rally' ssh rally@wally117.cit.tu-berlin.de &
cat commands-to-exec-nova-compute.sh | sshpass -p 'rally' ssh rally@wally122.cit.tu-berlin.de &
cat commands-to-exec-nova-compute.sh | sshpass -p 'rally' ssh rally@wally124.cit.tu-berlin.de &
cat commands-to-exec-nova-compute.sh | sshpass -p 'rally' ssh rally@wally123.cit.tu-berlin.de &
cat commands-to-exec-nova-compute.sh | sshpass -p 'rally' ssh rally@wally113.cit.tu-berlin.de
```

commands-to-exec-nova-compute.sh
```shell
#!/bin/bash -x
# Restarting nova_api container 5 times and sleep for 10 secs between restarts

for i in {1..2}
do
    echo "Restarting nova-container"
    docker stop nova_compute
    sleep 15
    docker start nova_compute
done
```

os-faults-latest.yaml
```
nova_compute:
	driver: docker_container
	args:
		container_name: nova_compute
	hosts:
	- 130.149.249.132
	- 130.149.249.134
	- 130.149.249.133
	- 130.149.249.127
```

2. GlanceImages.create_and_delete_image (extracted from `j_image_report.html`)
	- 运行文件`action`：sh ./restart_glance_container.sh
	- 时间`trigger`：[250, 500, 750] iteration
	- 细节`runner`：每一次事件触发，都有`3`个进程同时测试、模拟多用户并发访问的情况。task中执行测试用例的次数：1000
	- 任务成功标准`sla`：100% 成功

	- **被重启的`glance_api`位于wally113控制节点上**

restart_glance_container.sh
```shell
#!/bin/bash +x

#SSH into Wally113 controller and execute commands from commands-to-exec-glance.sh

cat commands-to-exec-glance.sh | sshpass -p 'rally' ssh rally@wally113.cit.tu-berlin.de
```

commands-to-exec-glance.sh
```shell
#!/bin/bash -x
# Restarting glance_api container 10 times and sleep for 2 secs between restarts
for i in {1..1}
do
    echo "Restarting glance-container"
    docker restart glance_api	
done
```

os-faults-latest.yaml
```
glance_api:
	driver: docker_container
	args:
		container_name: glance_api
	hosts:
	- 130.149.249.123
```

3. NeutronNetworks.create_and_delete_networks
	- 运行文件`action`：sh ./restart_neutron_container.sh
	- 时间`trigger`：[250, 500, 750] iteration
	- 细节`runner`：每一次事件触发，都有`1`个进程同时测试、模拟多用户并发访问的情况。task中执行测试用例的次数：1000
	- 任务成功标准`sla`：100% 成功

	- **被重启的下列container中，仅有`neutron_openvswitch_agent`在所有的主机上均部署，其他container只在`wally113`上部署。**

restart_neutron_container.sh
```shell
#!/bin/bash +x

#SSH into Wally113 controller and execute commands from commands-to-exec-nova.sh

cat commands-to-exec-neutron.sh | sshpass -p 'rally' ssh rally@wally113.cit.tu-berlin.de
```

commands-to-exec-neutron.sh
```shell
#!/bin/bash -x
# Restarting neutron containers and sleep for 25 secs between start and stop
for i in {1}
do
    echo "Restarting neutron-containers"
    docker stop neutron_metadata_agent &
    docker stop neutron_l3_agent &
    docker stop neutron_dhcp_agent &
    docker stop neutron_openvswitch_agent &
    docker stop neutron_openvswitch_agent &
    docker stop neutron_server
    sleep 0.1
    docker start neutron_metadata_agent &
    docker start neutron_l3_agent &
    docker start neutron_dhcp_agent &
    docker start neutron_openvswitch_agent &
    docker start neutron_openvswitch_agent &
    docker start neutron_server
done
```

--------------

# 异常总结

根据injected failures在各个KPI指标上的绘图，结合配置文件中得到的信息，列出了异常真正影响的node与KPI维度。

## sequential data

1. NovaServers.boot_and_delete_server (extracted from `j_boot_delete_report.html`)
	- 时间`trigger`：[250, 500] iteration
	- 细节`runner`：每一次事件触发，都有`3`个进程同时测试、模拟多用户并发访问的情况。task中执行测试用例的次数：750

	- 从配置文件得到的信息：被重启的`nova_compute`位于wally117, wally122, wally123, wally124上，但位于wally113控制节点上的也被重启了，看看有没有影响

	- **受影响的节点：**
		- wally113:未受影响
		- wally117:mem.used
		- wally122:mem.used
		- wally123:mem.used
		- wally124:mem.used

	- **受影响的时间：**
		- `2019-11-19 23:51:43.166326 CEST` to `2019-11-19 23:52:23.408740 CEST`
		- `2019-11-20 00:59:51.691804 CEST` to `2019-11-20 01:00:36.260246 CEST`

-----

2. GlanceImages.create_and_delete_image (extracted from `j_image_report.html`)
	- 时间`trigger`：[250, 500, 750] iteration
	- 细节`runner`：每一次事件触发，都有`3`个进程同时测试、模拟多用户并发访问的情况。task中执行测试用例的次数：1000

	- 从配置文件得到的信息：被重启的`glance_api`位于wally113控制节点上

	- **受影响的节点：**
		- wally113:mem.used, cpu.user
		- wally117:未受影响
		- wally122:未受影响
		- wally123:未受影响
		- wally124:未受影响

	- **受影响的时间：**
		- `2019-11-19 18:53:46.522151 CEST` to `2019-11-19 18:53:49.594851 CEST`
		- `2019-11-19 19:06:36.028661 CEST` to `2019-11-19 19:06:38.426867 CEST`
		- `2019-11-19 19:21:25.403098 CEST` to `2019-11-19 19:21:27.677400 CEST`

-----

3. NeutronNetworks.create_and_delete_networks
	- 时间`trigger`：[250, 500, 750] iteration
	- 细节`runner`：每一次事件触发，都有`1`个进程同时测试、模拟多用户并发访问的情况。task中执行测试用例的次数：1000

	- 从配置文件得到的信息：被重启的下列container中，仅有`neutron_openvswitch_agent`在所有的主机上均部署，其他container只在`wally113`上部署。

	- **受影响的节点：**
		- wally113:mem.used, cpu.user
		- wally117:未受影响
		- wally122:未受影响
		- wally123:未受影响
		- wally124:未受影响

	- **受影响的时间：**
		- `2019-11-19 21:07:04.786645 CEST` to `2019-11-19 21:07:25.174582 CEST`
		- `2019-11-19 21:13:34.766503 CEST` to `2019-11-19 21:13:55.707878 CEST`
		- `2019-11-19 21:20:13.881568 CEST` to `2019-11-19 21:20:36.138048 CEST`

----

Reference:

[1] k8s,docker,openstack以及容器与虚拟机之间的关系: https://blog.csdn.net/Lihuihui006/article/details/110088135
