# duifene_auto_sign
对分易自动签到
https://www.duifene.com/
## 登录后监控课程签到
支持二维码和签到码签到、位置签到
![1715853160414](https://github.com/liuzhijie443/duifene_auto_sign/assets/25584923/12fce0f7-f0ac-4920-8315-b39efc1ec1ae)

```
usage: main.py [-h] [--cli] [--link LINK] [--username USERNAME] [--password PASSWORD] [--seconds SECONDS] [--course-index COURSE_INDEX]

堆分儿自动签到

options:
  -h, --help            show this help message and exit
  --cli                 使用命令行模式运行
  --link LINK           微信授权链接
  --username USERNAME   账号密码登录的用户名
  --password PASSWORD   账号密码登录的密码
  --seconds SECONDS     倒计时小于等于该秒数时自动签到
  --course-index COURSE_INDEX
                        课程编号，从 1 开始
```
