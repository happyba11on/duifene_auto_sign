import argparse
import configparser
import os.path
import re
import sys
import time
from datetime import datetime
import requests
import urllib3
from bs4 import BeautifulSoup
import random


tk = None
messagebox = None
ttk = None


class Course:
    id = '0'
    class_id = '0'
    flag = True
    check_list = []
    class_list = []


def on_combo_change(event):
    select_course_by_index(combo.current())


def is_gui_mode():
    return app_mode == "gui"


def show_info(title, message):
    if is_gui_mode():
        messagebox.showinfo(title, message)
    else:
        print(message)


def show_warning(title, message):
    if is_gui_mode():
        messagebox.showwarning(title, message)
    else:
        print(f"[WARN] {message}")


def show_error(title, message):
    if is_gui_mode():
        messagebox.showerror(title, message)
    else:
        print(f"[ERROR] {message}", file=sys.stderr)


def clear_output():
    global cli_status_active
    if is_gui_mode():
        text_box.delete("1.0", "end")
    else:
        if cli_status_active:
            print()
            cli_status_active = False


def append_log(message, transient=False):
    global cli_status_active
    if is_gui_mode():
        text_box.insert(tk.END, message)
        text_box.see(tk.END)
        return

    if transient:
        print(f"\r{message}", end="", flush=True)
        cli_status_active = True
        return

    if cli_status_active:
        print()
        cli_status_active = False
    print(message, end="", flush=True)


def get_sign_seconds():
    if is_gui_mode():
        try:
            return int(seconds_entry.get())
        except ValueError:
            return 10
    return cli_seconds


def select_course_by_index(index):
    if index is None or index < 0 or index >= len(Course.class_list):
        return False

    selected_course = Course.class_list[index]
    Course.id = selected_course["CourseID"]
    Course.class_id = selected_course["TClassID"]
    Course.check_list = []

    if is_gui_mode():
        combo.current(index)
    return True


def list_courses_for_cli():
    print("课程列表：")
    for index, course in enumerate(Course.class_list, start=1):
        print(f"{index}. {course['CourseName']} (CourseID={course['CourseID']}, TClassID={course['TClassID']})")


def prompt_course_index():
    while True:
        raw_value = input("请输入课程编号: ").strip()
        if not raw_value.isdigit():
            print("请输入有效的数字编号。")
            continue

        course_index = int(raw_value) - 1
        if select_course_by_index(course_index):
            return course_index
        print("课程编号超出范围，请重新输入。")


def save_cookie(_x):
    config['INFO'] = {
        'cookie': _x.request.headers.get("cookie")
    }
    with open(filename, 'w') as f:
        config.write(f)


def login_link(link=None):
    link = link if link is not None else link_entry.get()
    code = re.search(r"(?<=code=)\S{32}", link)
    if code is not None:
        x.cookies.clear()
        code = code[0]
        _r = x.get(url=host + f"/P.aspx?authtype=1&code={code}&state=1")
        if get_class_list():
            save_cookie(_r)
            return True
    else:
        show_error("error", "链接有误")
    return False


def login(login_name=None, login_password=None):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.duifene.com/AppGate.aspx"
    }
    login_name = login_name if login_name is not None else username.get()
    login_password = login_password if login_password is not None else password.get()
    params = f'action=loginmb&loginname={login_name}&password={login_password}'
    x.cookies.clear()
    x.get(host)
    _r = x.post(url=host + "/AppCode/LoginInfo.ashx", data=params, headers=headers)
    if _r.status_code == 200:
        clear_output()
        msg = _r.json()["msgbox"]
        append_log(f"\n{msg}\n")
        if msg == "登录成功":
            if get_class_list():
                save_cookie(_r)
                return True
    else:
        show_error("错误提示", "登录失败")
    return False


def select_tab(event):
    tab_id = tab_control.index(tab_control.select())
    text_box.delete("1.0", "end")
    if tab_id == 0:
        text = '''
        1、打开电脑端微信，复制如下链接到文件传输助手并发送\n
        【https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx1b5650884f657981&redirect_uri=https://www.duifene.com/_FileManage/PdfView.aspx?file=https%3A%2F%2Ffs.duifene.com%2Fres%2Fr2%2Fu6106199%2F%E5%AF%B9%E5%88%86%E6%98%93%E7%99%BB%E5%BD%95_876c9d439ca68ead389c.pdf&response_type=code&scope=snsapi_userinfo&connect_redirect=1#wechat_redirect】\n\n
        2、点击进入链接，点击微信浏览器窗口右上角三个点，点击复制链接，并把微信链接粘贴到左侧输入框。\n
        '''
        text_box.insert(tk.END, text)
        tab_frame2.pack_forget()
        tab_frame1.pack(side=tk.LEFT, fill=tk.BOTH, pady=(40, 0))
    elif tab_id == 1:
        tab_frame1.pack_forget()
        tab_frame2.pack(side=tk.LEFT, fill=tk.BOTH, pady=(40, 0))


def get_user_id():
    _r = x.get(url=host + "/_UserCenter/MB/index.aspx")
    if _r.status_code == 200:
        soup = BeautifulSoup(_r.text, "lxml")
        stu_id = soup.find(id="hidUID").get("value")
        return stu_id


def sign(sign_code):
    # 签到码
    if len(sign_code) == 4:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://www.duifene.com/_CheckIn/MB/CheckInStudent.aspx?moduleid=16&pasd="
        }
        params = f"action=studentcheckin&studentid={get_user_id()}&checkincode={sign_code}"
        _r = x.post(
            url=host + "/_CheckIn/CheckIn.ashx", data=params, headers=headers)
        if _r.status_code == 200:
            msg = _r.json()["msgbox"]
            append_log(f"\t{msg}\n\n")
            if msg == "签到成功！":
                return True
    # 二维码
    else:
        _r = x.get(url=host + "/_CheckIn/MB/QrCodeCheckOK.aspx?state=" + sign_code)
        if _r.status_code == 200:
            soup = BeautifulSoup(_r.text, "lxml")
            msg = soup.find(id="DivOK").get_text()
            if "签到成功" in msg:
                append_log(f"\t{msg}\n\n")
            else:
                append_log(f"\t非微信链接登录，二维码无法签到\n\n")
            return True


def sign_location(longitude, latitude):
    longitude = str(round(float(longitude) + random.uniform(-0.000089, 0.000089), 8))
    latitude = str(round(float(latitude) + random.uniform(-0.000089, 0.000089), 8))

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.duifene.com/_CheckIn/MB/CheckInStudent.aspx?moduleid=16&pasd="
    }
    params = f"action=signin&sid={get_user_id()}&longitude={longitude}&latitude={latitude}"
    _r = x.post(
        url=host + "/_CheckIn/CheckInRoomHandler.ashx", data=params, headers=headers)
    if _r.status_code == 200:
        msg = _r.json()["msgbox"]
        append_log(f"\t{msg}\n\n")
        if msg == "签到成功！":
            return True


def update_watch_status(current_time):
    if is_gui_mode():
        line_count = int(text_box.index('end-1c').split('.')[0])
        text_box.delete(f"{line_count}.0", f"{line_count}.end")
        text_box.insert(tk.END, f"持续监控：{current_time}")
        text_box.see(tk.END)
    else:
        append_log(f"持续监控：{current_time}", transient=True)


def watching_sign_once():
    if not is_login():
        return

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_watch_status(current_time)

    _r = x.get(url=host + f"/_CheckIn/MB/TeachCheckIn.aspx?classid={Course.class_id}&temps=0&checktype=1&isrefresh=0"
                          f"&timeinterval=0&roomid=0&match=")
    if _r.status_code == 200:
        if "HFChecktype" in _r.text:
            status = False
            soup = BeautifulSoup(_r.text, "lxml")
            
            HFSeconds = soup.find(id="HFSeconds").get("value")
            HFChecktype = soup.find(id="HFChecktype").get("value")
            HFCheckInID = soup.find(id="HFCheckInID").get("value")
            HFClassID = soup.find(id="HFClassID").get("value")
            if Course.class_id in HFClassID:
                if HFCheckInID not in Course.check_list:
                    # 数字签到
                    if HFChecktype == '1':
                        sign_code = soup.find(id="HFCheckCodeKey").get("value")
                        if sign_code is not None and int(HFSeconds) <= get_sign_seconds():
                            append_log(f"\n\n{current_time} 签到ID：{HFCheckInID} 开始签到\t签到码：{sign_code}")
                            status = sign(sign_code)
                        else:
                            append_log(f"\t签到码签到\t未到签到时间\t倒计时：{HFSeconds}秒\t签到码：{sign_code}")
                    # 二维码签到
                    elif HFChecktype == '2':
                        if HFCheckInID is not None and int(HFSeconds) <= get_sign_seconds():
                            append_log(f"\n\n{current_time} 签到ID：{HFCheckInID} 开始签到\t二维码签到")
                            status = sign(HFCheckInID)
                        else:
                            append_log(f"\t二维码签到\t未到签到时间\t倒计时：{HFSeconds}秒")
                    # 定位签到
                    elif HFChecktype == '3':
                        HFRoomLongitude = soup.find(id="HFRoomLongitude").get("value")
                        HFRoomLatitude = soup.find(id="HFRoomLatitude").get("value")
                        if HFRoomLongitude is not None and HFRoomLatitude is not None and int(HFSeconds) <= get_sign_seconds():
                            append_log(f"\n\n{current_time} 签到ID：{HFCheckInID} 开始签到\t定位签到")
                            status = sign_location(HFRoomLongitude, HFRoomLatitude)
                        else:
                            append_log(f"\t定位签到\t未到签到时间\t倒计时：{HFSeconds}秒")
                    if status:
                        Course.check_list.append(HFCheckInID)
            else:
                append_log(f"\t 检测到非本班签到")


def watching_sign():
    watching_sign_once()
    if Course.flag:
        root.after(1000, watching_sign)


def start_sign_monitor():
    if not Course.id or Course.id == '0':
        show_error("错误提示", "请先选择课程")
        return
    headers = {
        "Referer": "https://www.duifene.com/_UserCenter/MB/index.aspx"
    }
    _r = x.get(url=host + "/_UserCenter/MB/Module.aspx?data=" + Course.id, headers=headers)
    if _r.status_code == 200:
        if Course.id in _r.text:
            clear_output()
            soup = BeautifulSoup(_r.text, "lxml")
            CourseName = soup.find(id="CourseName").text
            append_log(f"正在监听【{CourseName}】的签到活动\n\n")
            if is_gui_mode():
                watching_sign()
            else:
                while Course.flag:
                    watching_sign_once()
                    time.sleep(1)


def go_sign():
    if combo.get() is None or combo.get() == '':
        show_error("错误提示", "请先登录")
        return
    start_sign_monitor()


def get_class_list():
    # 获取用户课程列表
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.duifene.com/_UserCenter/PC/CenterStudent.aspx"
    }
    params = "action=getstudentcourse&classtypeid=2"
    _r = x.post(url=host + "/_UserCenter/CourseInfo.ashx", data=params, headers=headers)
    if _r.status_code == 200:
        _json = _r.json()
        if _json is not None:
            if isinstance(_json, dict) and "msgbox" in _json:
                msg = _json["msgbox"]
                show_error("", f"{msg} 请重新登录。")
                x.cookies.clear()
                return []

            show_info("提示", "登录成功")
            Course.class_list = _json
            if not Course.class_list:
                show_warning("提示", "未获取到课程列表")
                return []

            select_course_by_index(0)
            if is_gui_mode():
                class_name_list = []
                for index, course in enumerate(_json, start=1):
                    class_name_list.append(f"{index}. {course['CourseName']}")
                combo['values'] = tuple(class_name_list)
                combo.current(0)
            return Course.class_list
    return []


def is_login():
    headers = {
        "Referer": "https://www.duifene.com/_UserCenter/PC/CenterStudent.aspx",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    _r = x.get(host + "/AppCode/LoginInfo.ashx", data="Action=checklogin", headers=headers)
    if _r.status_code == 200:
        if _r.json()["msg"] == "1":
            return True
        else:
            show_warning("登录状态失效", "请重新登录账号")
            x.cookies.clear()
            Course.flag = False
            return False


def init():
    try:
        if not os.path.exists(filename):
            config['INFO'] = {
                'cookie': '1=1'
            }
            with open(filename, 'w') as configfile:
                config.write(configfile)
            x.get(host)
        else:
            try:
                config.read(filename)
                cookie = config.get('INFO', 'cookie')
                cookies = {}
                for pair in cookie.split('; '):
                    key, value = pair.split('=')
                    cookies[key] = value
                x.cookies.update(cookies)
                get_class_list()
            except Exception as e:
                pass
    except (requests.ConnectionError, requests.Timeout):
        # 如果请求失败，则没有互联网连接
        show_warning("网络状态", "未检测到互联网连接，请检查你的网络设置。")
        if is_gui_mode():
            root.destroy()
        else:
            raise SystemExit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="堆分儿自动签到")
    parser.add_argument("--cli", action="store_true", help="使用命令行模式运行")
    parser.add_argument("--link", help="微信授权链接")
    parser.add_argument("--username", help="账号密码登录的用户名")
    parser.add_argument("--password", help="账号密码登录的密码")
    parser.add_argument("--seconds", type=int, default=10, help="倒计时小于等于该秒数时自动签到")
    parser.add_argument("--course-index", type=int, help="课程编号，从 1 开始")
    return parser.parse_args()


def run_cli(args):
    global cli_seconds
    cli_seconds = args.seconds

    if args.link:
        if not login_link(args.link):
            raise SystemExit(1)
    elif args.username and args.password:
        if not login(args.username, args.password):
            raise SystemExit(1)
    elif not Course.class_list:
        login_mode = input("选择登录方式 [1] 微信链接 [2] 账号密码: ").strip() or "1"
        if login_mode == "1":
            if not login_link(input("请输入微信授权链接: ").strip()):
                raise SystemExit(1)
        elif login_mode == "2":
            login_name = input("请输入账号: ").strip()
            login_password = input("请输入密码: ").strip()
            if not login(login_name, login_password):
                raise SystemExit(1)
        else:
            print("不支持的登录方式。", file=sys.stderr)
            raise SystemExit(1)

    if not Course.class_list:
        print("未获取到课程列表，程序退出。", file=sys.stderr)
        raise SystemExit(1)

    list_courses_for_cli()
    if args.course_index is not None:
        if not select_course_by_index(args.course_index - 1):
            print("课程编号超出范围。", file=sys.stderr)
            raise SystemExit(1)
    else:
        prompt_course_index()

    start_sign_monitor()


if __name__ == '__main__':
    host = "https://www.duifene.com"
    UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
         'Mobile/15E148 MicroMessenger/8.0.40(0x1800282a) NetType/WIFI Language/zh_CN '
    urllib3.disable_warnings()
    x = requests.Session()
    x.headers['User-Agent'] = UA
    # x.proxies = {"https": "127.0.0.1:8888"}
    x.verify = False
    filename = 'duifenyi.ini'
    config = configparser.ConfigParser()
    app_mode = "gui"
    cli_seconds = 10
    cli_status_active = False

    args = parse_args()
    if args.cli:
        app_mode = "cli"
        init()
        run_cli(args)
    else:
        import tkinter as tk
        from tkinter import messagebox, ttk

        # 创建UI
        root = tk.Tk()
        # 标题
        root.title("2024.9.18")
        # 禁用窗口的调整大小
        root.resizable(False, False)

        # tab控制
        tab_control = ttk.Notebook(root)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        # 添加选项卡
        tab_control.add(tab1, text="微信链接登录")
        tab_control.add(tab2, text="账号密码登录")
        # 当选项卡被选中时，调用select_tab函数
        tab_control.bind("<<NotebookTabChanged>>", select_tab)
        tab_control.pack(fill=tk.BOTH, side=tk.LEFT)

        # tab选项卡中的内容_链接登录
        tab_frame1 = tk.Frame(tab_control)
        tab_frame1.pack(side=tk.LEFT, fill=tk.BOTH, pady=(40, 0))
        tk.Label(tab_frame1, text="支持二维码和签到码\n查看右侧说明进行登录", font=('宋体', 10)).pack(pady=5)
        tk.Label(tab_frame1, text="登录链接", font=('宋体', 10)).pack(pady=5)
        link_entry = tk.Entry(tab_frame1, font=('宋体', 12))
        link_entry.pack(pady=5, padx=10)
        tk.Button(tab_frame1, text="登录", command=login_link, font=('宋体', 14)).pack(pady=5)

        # tab选项卡中的内容_密码登录
        tab_frame2 = tk.Frame(tab_control)
        tk.Label(tab_frame2, text="不支持二维码签到", font=('宋体', 10)).pack(padx=5)
        tk.Label(tab_frame2, text="账号", font=('宋体', 14)).pack(padx=10)
        username = tk.Entry(tab_frame2, font=('宋体', 12))
        username.pack(padx=10)
        tk.Label(tab_frame2, text="密码", font=('宋体', 14)).pack(padx=10)
        password = tk.Entry(tab_frame2, show="*", font=('宋体', 12))
        password.pack(padx=10)
        tk.Label(tab_frame2, text="剩余倒计时X秒后签到", font=('宋体', 10)).pack(pady=5)
        seconds_entry = tk.Entry(tab_frame2, font=('宋体', 12), width=5)
        seconds_entry.insert(0, "10")
        seconds_entry.pack(pady=5)
        tk.Button(tab_frame2, text="登录", command=login, font=('宋体', 14)).pack(pady=5)

        # 右边frame_选择课程
        frame_mid = tk.Frame(root)
        frame_mid.pack(side=tk.TOP)
        tk.Label(frame_mid, text="选择课程").pack(side=tk.TOP, fill=tk.BOTH, pady=(10, 0))
        combo_var = tk.StringVar()
        combo = ttk.Combobox(frame_mid, textvariable=combo_var, state="readonly")
        combo.bind("<<ComboboxSelected>>", on_combo_change)
        combo.pack(side=tk.LEFT)
        btn = tk.Button(frame_mid, text="开始监听签到", command=go_sign)
        btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # 输出框
        frame_right = tk.Frame(root)
        frame_right.pack(side=tk.RIGHT)
        text_box = tk.Text(frame_right, width=90, height=20, font=('宋体', 9))
        text_box.pack(pady=(0, 10), padx=(0, 10))

        # 初始化
        init()
        root.mainloop()
