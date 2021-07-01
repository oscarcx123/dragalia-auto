from core import Azure

class Dragalia():
    def __init__(self):
        self.user_settings()
        self.default_settings()
        self.azure = Azure(self.scale_percentage)
        self.azure.load_res("img")

    # 用户设置（只需要改动这里的东西）
    def user_settings(self):
        # 要刷的龙玉（EXCEL自动生成，手动输入也行）
        self.dragon = [0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0]

        # 分辨率设置（默认）
        '''
        1440P - 100
        1080P - 75
        720P - 50
        '''
        self.scale_percentage = 100

        # 坐标设置
        self.list_quest = (1026, 1729)      # 确认所选龙玉
        self.choose_difficulty = [(736, 786), (736, 1186)]  # H 和 VH 的坐标
        self.choose_quest_1 = (720, 1160)   # 最上面的副本（1号位）
        self.choose_quest_2 = (720, 1500)   # 中间的副本（2号位，似乎是伐由专用）
        self.set_multiple = (1230, 1760)    # 反复攻略按钮
        self.minus = (310, 1980)            # 反复攻略次数的减号
        self.multiple_ok = (1040, 2200)     # 确认并关闭反复攻略
        self.quest_return = (200, 2180)     # 从副本列表返回到大地图

    def default_settings(self):
        self.idx_vayu = 21

    def tap_tuple(self, coord):
        self.azure.tap(coord[0], coord[1])

    def click_dragon_menu(self):
        self.azure.get_img()
        if self.azure.match("dragon_menu.jpg"):
            self.azure.tap()
        else:
            print("Can't find dragon menu!")

    def click_dragon(self, idx):
        self.azure.get_img()
        idx = str(idx)
        if len(idx) < 2:
            idx = "0" + idx
        if self.azure.match(f"dragon_{idx}.jpg"):
            print(f"NOW dragon_{idx}")
            self.azure.tap()
        else:
            print(f"Failed to match dragon_{idx}.jpg")

    def main(self):
        for i in range(len(self.dragon)):
            if self.dragon[i] == 1:
                for j in range(2):
                    # 打开龙玉面板
                    self.click_dragon_menu()
                    self.azure.sleep(2)
                    
                    # 如果龙玉靠后，需要下滑翻页
                    if i > 19:
                        self.azure.swipe(670, 1860, 670, 660)
                        self.azure.sleep(2)

                    # 选择要刷的龙
                    self.click_dragon(i)
                    self.azure.sleep(2)
                    
                    # 确认刚才所选的龙
                    self.tap_tuple(self.list_quest)
                    self.azure.sleep(2)

                    # 选择难度
                    self.tap_tuple(self.choose_difficulty[j])
                    self.azure.sleep(8)

                    # 进入关卡（点击关卡，选择无支援）
                    if i == self.idx_vayu: # 伐由的龙玉副本在二号位，需要特殊处理
                        self.tap_tuple(self.choose_quest_2)
                    else:
                        self.tap_tuple(self.choose_quest_1)
                    self.azure.sleep(2)
                    self.tap_tuple(self.choose_quest_1)
                    self.azure.sleep(5)

                    # 点开反复攻略面板
                    self.tap_tuple(self.set_multiple)
                    self.azure.sleep(2)

                    # 设置反复攻略3次
                    for k in range(2):
                        self.tap_tuple(self.minus)
                        self.azure.sleep(1)

                    # 确认反复攻略
                    self.tap_tuple(self.multiple_ok)
                    self.azure.sleep(2)

                    # 开始攻略副本
                    self.tap_tuple(self.multiple_ok)
                    self.azure.sleep(2)

                    # 打完副本并点击“继续”
                    while True:
                        self.azure.get_img()
                        if self.azure.match("continue.jpg"):
                            print("Quest finished!")
                            self.azure.tap()
                            self.azure.sleep(10)
                            break
                        print("Waiting for quest to finish...")
                        self.azure.sleep(10)
                    
                    # 点击返回
                    self.tap_tuple(self.quest_return)
                    self.azure.sleep(5)
                    


dragalia = Dragalia()
dragalia.main()