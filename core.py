'''
core.py的全部内容都来自我的开源项目：https://github.com/oscarcx123/afk-arena-tools
以前已经实现过这么一套API，就不再重复造轮子了。
部分API可能没什么用，我也懒得删。
普通用户不需要看这个文件。
'''
import os
import cv2
import time
import random
import traceback
import subprocess
import numpy as np
import concurrent.futures

class Azure():
    def __init__(self, scale_percentage):
        self.scale_percentage = scale_percentage
        self.threshold = 0.9
        self.debug = False

    # 加载图像资源
    def load_res(self, file_dir):
        # 匹配对象的字典
        self.res = {}
        temp_list = os.listdir(file_dir)
        for item in temp_list:
            self.res[item] = {}
            res_path = os.path.join(file_dir, item)
            self.res[item]["img"] = cv2.imread(res_path)
            # 如果不是原尺寸（1440P），进行对应缩放操作
            if self.scale_percentage != 100:
                self.res[item]["width"] = int(self.res[item]["img"].shape[1] * self.scale_percentage / 100) 
                self.res[item]["height"] = int(self.res[item]["img"].shape[0] * self.scale_percentage / 100)
                self.res[item]["img"] = cv2.resize(self.res[item]["img"], (self.res[item]["width"], self.res[item]["height"]), interpolation=cv2.INTER_AREA)
            else:
                self.res[item]["height"], self.res[item]["width"], self.res[item]["channel"] = self.res[item]["img"].shape[::]
            self.write_log(f"Loaded {item}")

    # 获取截图
    def get_img(self, pop_up_window=False, save_img=False, file_name='screenshot.png'):
        image_bytes = self.exec_cmd("adb exec-out screencap -p")

        if image_bytes == b'':
            self.write_log(f"截图失败！请检查adb是否已经跟手机连接！")
        else:
            self.target_img = cv2.imdecode(np.fromstring(image_bytes, dtype='uint8'), cv2.IMREAD_COLOR)
            if save_img:
                cv2.imwrite(file_name, self.target_img)
            if pop_up_window:
                self.show_img()

    def show_img(self):
        cv2.namedWindow("screenshot", cv2.WINDOW_NORMAL)
        cv2.resizeWindow('screenshot', 360, 640)
        cv2.imshow("screenshot", self.target_img)
        cv2.waitKey(0)
        cv2.destroyWindow("screenshot")


    # 匹配并获取中心点
    def match(self, img_name):
        # 从加载好的图像资源中获取数据
        find_img = self.res[img_name]["img"]
        find_height = self.res[img_name]["height"]
        find_width = self.res[img_name]["width"]

        # 匹配
        try:
            result = cv2.matchTemplate(self.target_img, find_img, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        except:
            self.write_log(f"OpenCV对比失败！请使用杂项中的截图功能来测试能否正常截图！")
        print(f"{img_name}最大匹配度：{max_val}")
        if max_val < self.threshold:
            return False
        
        # 计算位置
        self.pointUpLeft = max_loc
        self.pointLowRight = (int(max_loc[0] + find_width), int(max_loc[1] + find_height))
        self.pointCentre = (int(max_loc[0] + (find_width / 2)), int(max_loc[1] + (find_height / 2)))
        if self.debug:
            self.draw_circle()
        self.write_log(f"匹配到{img_name}，匹配度：{max_val}")
        return True

    # 匹配多个结果
    def multiple_match(self, img_name):
        # 用于存放匹配结果
        match_res = []
        # 从加载好的图像资源中获取数据
        find_img = self.res[img_name]["img"]
        find_height = self.res[img_name]["height"]
        find_width = self.res[img_name]["width"]

        # OpenCV匹配多个结果
        # https://stackoverflow.com/a/58514954/12766614
        try:
            result = cv2.matchTemplate(self.target_img, find_img, cv2.TM_CCOEFF_NORMED)
            # max_val设置为1，从而能够进入循环
            max_val = 1
            cnt = 0
            while max_val > self.threshold:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if max_val > self.threshold:
                    # 抹除最大值周围的数值，从而可以在下一次找到其它位置的（第二）最大值
                    result[max_loc[1]-find_height//2:max_loc[1]+find_height//2+1, max_loc[0]-find_width//2:max_loc[0]+find_width//2+1] = 0
                    # 计算位置
                    pointUpLeft = max_loc
                    pointLowRight = (int(max_loc[0] + find_width), int(max_loc[1] + find_height))
                    pointCentre = (int(max_loc[0] + (find_width / 2)), int(max_loc[1] + (find_height / 2)))
                    # image = cv2.rectangle(image, (max_loc[0],max_loc[1]), (max_loc[0]+find_width+1, max_loc[1]+find_height+1), (0,0,0))
                    # cv2.imwrite(f'output_{cnt}.png', 255*result) 灰阶输出，越亮匹配度越高
                    cnt += 1
                    match_res.append(pointCentre)
                    print(f"{img_name}找到{cnt}个，匹配度：{max_val}")
        except:
            self.write_log(f"OpenCV对比失败！请使用杂项中的截图功能来测试能否正常截图！")
        return match_res


    # 立即截图，然后匹配，返回boolean
    def current_match(self, img_name):
        self.get_img()
        return self.match(img_name)

    # 立即截图，然后匹配多个，返回数组，内含若干匹配成功的tuple
    def current_multiple_match(self, img_name):
        self.get_img()
        return self.multiple_match(img_name)
    
    # 点击（传入坐标）
    # 也可以接受比例形式坐标，例如(0.5, 0.5, percentage=True)就是点屏幕中心
    # 可以传入randomize=False来禁用坐标的随机偏移
    def tap(self, x_coord=None, y_coord=None, percentage=False, randomize=True):
        if x_coord is None and y_coord is None:
            x_coord, y_coord = self.get_coord(randomize=randomize)
        if percentage:
            x_coord = int(x_coord * self.screen_width * (self.scale_percentage / 100))
            y_coord = int(y_coord * self.screen_height * (self.scale_percentage / 100))
            x_coord = self.randomize_coord(x_coord, 5)
            y_coord = self.randomize_coord(y_coord, 5)
        self.write_log(f"点击坐标：{(x_coord, y_coord)}")
        cmd = f"adb shell input tap {x_coord} {y_coord}"
        self.exec_cmd(cmd)

    # 滑动 / 长按
    # 本函数仅用于debug
    def swipe(self, fromX=None, fromY=None, toX=None, toY=None, swipe_time=200):
        if toX is None and toY is None:
            swipe_time = 500
            self.write_log(f"长按坐标：{(fromX, fromY)}")
            cmd = f"adb shell input swipe {fromX} {fromY} {fromX} {fromY} {swipe_time}"
        else:
            self.write_log(f"滑动：从{(fromX, fromY)}到{(toX, toY)}")
            cmd = f"adb shell input swipe {fromX} {fromY} {toX} {toY} {swipe_time}"       
        self.exec_cmd(cmd)
    
    # 执行指令
    def exec_cmd(self, cmd, new_thread=False, show_output=False):
        def do_cmd(cmd):
            pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
            return pipe.stdout.read()
                   
        if new_thread:
            if show_output:
                self.write_log(f"执行{cmd}")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(do_cmd, cmd)
                ret_val = future.result()
        else:
            if show_output:
                self.write_log(f"执行{cmd}")
            ret_val = do_cmd(cmd)
        if show_output:
            self.write_log(ret_val.decode("utf-8"))
        return ret_val

    # 控制台显示执行次数
    def show_cnt(self):
        self.write_log(f"已重试{self.cnt}次！")

    # adb连接（WIFI）
    def adb_connect(self):
        self.exec_cmd(f"adb connect {self.wifi_adb_addr}", new_thread=True, show_output=True)

    # adb devices（验证设备是否连接）
    def adb_devices(self):
        self.exec_cmd("adb devices", new_thread=True, show_output=True)

    # 查看adb版本
    def adb_version(self):
        self.exec_cmd("adb --version", new_thread=True, show_output=True)

    # 画点（测试用）
    def draw_circle(self):
        cv2.circle(self.target_img, self.pointUpLeft, 10, (255, 255, 255), 5)
        cv2.circle(self.target_img, self.pointCentre, 10, (255, 255, 255), 5)
        cv2.circle(self.target_img, self.pointLowRight, 10, (255, 255, 255), 5)
        self.show_img()

    # 获取匹配到的坐标
    def get_coord(self, randomize=True):
        x_coord = self.pointCentre[0]
        y_coord = self.pointCentre[1]
        if randomize:
            x_coord = self.randomize_coord(x_coord, 20)
            y_coord = self.randomize_coord(y_coord, 15)
        return x_coord, y_coord

    # 坐标进行随机偏移处理
    def randomize_coord(self, coord, diff):
        return random.randint(coord - diff, coord + diff)

    def write_log(self, text):
        timestamp = time.strftime("[%H:%M:%S] ", time.localtime())
        print(timestamp + text)

    # 判断文件是否为空
    def is_file_empty(self, file_name):
        return os.stat(file_name).st_size == 0

    def sleep(self, sec):
        print(f"Sleep: {sec}s")
        time.sleep(sec)