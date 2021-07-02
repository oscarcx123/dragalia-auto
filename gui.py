from tkinter import *
from tkinter import messagebox
from threading import Thread
from functools import partial
import json
import os

VERSION = "1.1"
text_font = ("Microsoft YaHei", 12)


# https://www.python-course.eu/tkinter_checkboxes.php
class Checkbar(Frame):
    def __init__(self, parent=None, picks=[], side=LEFT, anchor=W):
        Frame.__init__(self, parent)
        self.vars = []
        for pick in picks:
            var = IntVar()
            chk = Checkbutton(self, text=pick, variable=var, font=text_font, command=self.on_clicked)
            chk.pack(side=side, anchor=anchor, expand=YES)
            self.vars.append(var)
    
    def get_state(self):
        return map((lambda var: var.get()), self.vars)

    def set_state(self, lst):
        for idx in range(len(self.vars)):
            self.vars[idx].set(lst[idx])

    def on_clicked(self):
        self.show_stamina()
        self.save_conf()

    # 下面这些从AzureGUI类手动继承
    def show_stamina(self):
        pass

    def save_conf(self):
        pass

class AzureGUI():
    def __init__(self):
        self.title = f"dragalia-auto V{VERSION} by Azure"
        self.checkbar_func()
        self.init_data()
        self.build_ui()
        self.load_conf()
        self.show_ui()
        

    def checkbar_func(self):
        Checkbar.show_stamina = self.show_stamina
        Checkbar.save_conf = self.save_conf

    def init_data(self):
        self.flame_data = [['阿格尼', '5'], ['普罗米修斯', '5'], ['坎贝萝丝', '5'], ['木花开耶', '5'], ['阿尔库特斯', '5'], ['阿波罗', '5'], ['迦具土', '5'], ['荷鲁斯', '5']]
        self.water_data = [['利维坦', '4'], ['波塞冬', '4'], ['塞壬', '4'], ['思摩夫', '4'], ['神威', '5'], ['咕噜曼', '5'], [' 兔子', '5'], ['斯堤克斯', '5']]
        self.wind_data = [['瓦基扬', '4'], ['迦楼罗', '4'], ['龙龙', '4'], ['帕祖祖', '5'], ['芙蕾雅', '5'], ['伐由', '5'], ['哈斯塔', '5'], ['AC-011', '5']]
        self.light_data = [['丘比特', '5'], ['贞德', '5'], ['吉尔伽美什', '5'], ['雷牙', '5'], ['建御雷', '5'], ['光塞壬', '5'], ['神圣菲尼克斯', '5'], ['铁扇公主', '5']]
        self.shadow_data = [['普鲁托', '5'], ['尼德霍格', '5'], ['奈亚拉托提普', '5'], ['忍', '5'], ['埃庇米修斯', '5'], ['安德洛莫达', '5'], ['阿撒兹勒', '5'], ['拉米艾尔', '5']]
        self.all_data = self.flame_data + self.water_data + self.wind_data + self.light_data + self.shadow_data
        self.curr_func = None

    def build_ui(self):
        self.root = Tk()
        self.root.title(self.title)
        self.elements = []
        self.flame = Checkbar(self.root, [x[0] for x in self.flame_data])
        self.water = Checkbar(self.root, [x[0] for x in self.water_data])
        self.wind = Checkbar(self.root, [x[0] for x in self.wind_data])
        self.light = Checkbar(self.root, [x[0] for x in self.light_data])
        self.shadow = Checkbar(self.root, [x[0] for x in self.shadow_data])
        self.elements.extend([self.flame, self.water, self.wind, self.light, self.shadow])
        
        for el in self.elements:
            el.pack(side=TOP, fill=X)
            # 边框（类型GROOVE，border=2）
            # 边框图例可以看这个：https://www.tutorialspoint.com/python/tk_relief.htm
            el.config(relief=GROOVE, bd=2)
        
        self.l1_text = StringVar()
        self.l1_text.set("所需体力：0")
        self.l1 = Label(self.root, textvariable=self.l1_text, font=text_font)
        self.l1.pack(side=LEFT)
        self.b1 = Button(self.root, text="退出", command=self.root.quit, font=text_font)
        self.b1.pack(side=RIGHT)
        self.b2 = Button(self.root, text="开刷", command=self.exec_script, font=text_font)
        self.b2.pack(side=RIGHT)

    def show_ui(self):
        self.root.mainloop()

    def debug_cb_status(self):
        for el in self.elements:
            print(list(el.get_state()))

    def get_cb_status(self):
        res = []
        for el in self.elements:
            res.extend(list(el.get_state()))
        return res

    def calc_stamina(self):
        stamina = 0
        all_cb = self.get_cb_status()
        for idx in range(len(all_cb)):
            if all_cb[idx]:
                stamina += int(self.all_data[idx][1]) * 6
        return stamina

    def show_stamina(self):
        self.l1_text.set(f"所需体力：{self.calc_stamina()}")

    # https://stackoverflow.com/questions/752308/split-list-into-smaller-lists-split-in-half
    def split_list(self, alist, wanted_parts=1):
        length = len(alist)
        return [alist[i*length // wanted_parts: (i+1)*length // wanted_parts] for i in range(wanted_parts)]

    def save_conf(self):
        with open("conf.json", "w") as f:
            json.dump(self.get_cb_status(), f)

    def load_conf(self):
        try:
            with open("conf.json", "r") as f:
                conf = json.load(f)
            conf = self.split_list(conf, 5)
            for idx in range(len(self.elements)):
                self.elements[idx].set_state(conf[idx])
        except FileNotFoundError:
            pass
        finally:
            self.show_stamina()

    def exec_script(self):
        if self.curr_func is not None:
            if self.curr_func.is_alive():
                messagebox.showwarning(title="点那么多下干啥？", message="程序已经开始执行了！")
                return
        self.curr_func = Thread(target=self.run_dragalia)
        self.curr_func.start()
    
    def run_dragalia(self):
        os.system(f'python dragalia.py "{self.get_cb_status()}"')

mw = AzureGUI()