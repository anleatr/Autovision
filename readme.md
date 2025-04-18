## Autovision：简易智慧树自动刷课助手
基于纯视觉的自动化键鼠模拟实现自动刷课
### Setup
1. 下载源码(zip或git clone)
2. 配置环境
```commandline
conda create -n autovision python=3.9
cd
pip install -i requirements.txt
```
3. 登录到要刷的课程界面，把下面这个小机器人拖到上面，不要遮挡目录信息

![](./fig/robot.png)
4. 在ide启动脚本，然后切换到课程界面，就可以去睡觉了

### 目前实现的功能

- 选择第一个没有看过的课程逐个播放
- 视频小测自动答题
