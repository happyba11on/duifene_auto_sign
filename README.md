# duifene_auto_sign
对分易自动签到
https://www.duifene.com/

## 登录后监控课程签到
支持二维码和签到码签到、位置签到。
![1715853160414](https://github.com/liuzhijie443/duifene_auto_sign/assets/25584923/12fce0f7-f0ac-4920-8315-b39efc1ec1ae)

## 使用说明

### 1. 下载项目

```bash
git clone https://github.com/liuzhijie443/duifene_auto_sign.git
cd duifene_auto_sign
```


### 2. 用 pip 安装依赖

```bash
pip install -r requirements.txt
```

如果你的环境使用 `pip3`，则执行：

```bash
pip3 install -r requirements.txt
```

### 3. 用 uv 安装依赖

在项目目录执行：

```bash
uv sync
```

## 命令行参数

```text
usage: main.py [-h] [--cli] [--link LINK] [--print-login-url] [--username USERNAME] [--password PASSWORD] [--seconds SECONDS] [--course-index COURSE_INDEX]

堆分儿自动签到

options:
  -h, --help            show this help message and exit
  --cli                 使用命令行模式运行
  --link LINK           微信授权链接
  --print-login-url     输出生成微信授权链接所需的 URL 后退出
  --username USERNAME   账号密码登录的用户名
  --password PASSWORD   账号密码登录的密码
  --seconds SECONDS     倒计时小于等于该秒数时自动签到
  --course-index COURSE_INDEX
                        课程编号，从 1 开始
```
