## AutomatedTest(提供一个平台，用于自动化测试.)
![](http://7xk7ho.com1.z0.glb.clouddn.com/automate.jpg)

##介绍
对于一款pc上的产品，为了保证每项指标(如冷启动、升级、安装与卸载、数据上报等)正确。这些每次都需要手动去测试，很是繁琐：
- 测试冷启动掐表测？误差？测试多多次启动电脑？
- 数据上报呢？使用dbgview？
- 频繁构建，版本多，每次都测试甚是累啊

所以，可以利用机器做的事情为什么要人去手动做呢？所以这里要将这些人工做的事情解放掉，那就是自动化测试平台解决的:
- 提供用例管理，开发人员要做的只是写好用例.如果用例变化，会自动推送到测试机进行更新
- 提供任务的制定、用例运行的实时监控
- 提供测试机管理，可以将所有的任务推送到特定主机也可以推送到多台测试机
- 邮件提醒
-...

##使用
打开制定页面，制定一个任务(一个多多个用例),然后就不需要管了，如果在制定任务时选择了邮件提醒， 那么任务执行完就可以收到测试结果了.

##方案

###web服务器
- 任务制定
- 用例管理
- 邮件管理
- 测试管理
- 结果管理

###任务调度器
- 推送任务至代理
- 检测用例的变化并决定代理是否更新
- 轮询检测代理控制的用例是否完成，以便决定是否继续推送任务
- 收集代理以完成用例的结果

###代理
- 使用xmlrpcsever提供服务，使得服务器可以推送用例等
- 控制用例的执行等

###用例
- 执行并更新自身状态:
	- 开始
	- 进度
	- 结束
	- 结果

##数据库设计

###挂起的用例

字段|说明
----------|------------
task_id	  |用例所属的任务id
name      |用例
version	  |表示用例执行对象的版本


###正在执行用例

字段|说明
----------|------------
task_id	  |用例所属的任务id
name      |用例
version	  |标示用例执行对象的版本
ip		  |用例所执行的测试机
###任务

字段|说明
----------|------------
task_id   |任务id
version   |标示用例执行对象的版本
case_names|用例名列表
email_flag|任务完成是否发送邮件
finished  |任务是否完成
result    |用例执行结果


##问题及解决
####当去检测代理状态的时候，比较耗时，会使其他操作卡住.而且tornado不支持一般函数的异步.
###解决:
- 请求上加上@tornado.web.asynchronous
- 使用tornado-celery，这样可以对一般函数进行异步调用. 需要注意的是中间件不支持redis,只支持ampq,而且需要运行worker、中间件、编写task.py，也是有些麻烦的啊.

##运行截图
- 主界面
![](http://7xk7ho.com1.z0.glb.clouddn.com/home.png)
- 用例管理
![](http://7xk7ho.com1.z0.glb.clouddn.com/cases.png)
- 任务管理
![](http://7xk7ho.com1.z0.glb.clouddn.com/tasks.png)
- 测试机管理
![](http://7xk7ho.com1.z0.glb.clouddn.com/machines.png)
- 结果管理
![](http://7xk7ho.com1.z0.glb.clouddn.com/results.png)
- 邮件管理
![](http://7xk7ho.com1.z0.glb.clouddn.com/email.png)

##部署
###服务器
- 启动mongodb
- 启动server目录下的server.py作为web操作界面服务器
- 启动server目录下的scheduler.py作为任务调度执行者

###测试机
- 启动proxy下的proxy.py即可

##用例格式说明
- run.py作为代理启动用例的入口，用例的输出为output.txt,这个结果最终由调度器去主动取得。
- 一个简单例子:
	- coldstart
	- coldstart\run.py
- 用例最终会打包为.zip格式,如上述例子为coldstart.zip