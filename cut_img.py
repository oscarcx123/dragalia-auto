'''
这是用来切龙玉图的工具，开发用的。
'''
from PIL import Image

im = Image.open("screenshot.png")

cut_pos = []
length = 120

h_start = 130
h_end = 1230
h_cnt = 5
h_gap = (h_end - h_start - length * h_cnt) / (h_cnt - 1)
pos_left = [h_start + x * (length + h_gap) for x in range(h_cnt)]
pos_right = [x + length for x in pos_left]

v_start = 690
v_end = 1800
v_cnt = 4
v_gap = (v_end - v_start - length * v_cnt) / (v_cnt - 1)
pos_top = [v_start + x * (length + v_gap) for x in range(v_cnt)]
pos_bottom = [x + length for x in pos_top]

for i in range(len(pos_top)):
    for j in range(len(pos_left)):
        cut_pos.append((pos_left[j], pos_top[i], pos_right[j], pos_bottom[i]))


for idx in range(len(cut_pos)):
    im_cut = im.crop(cut_pos[idx])
    if len(str(idx)) < 2:
        idx = "0" + str(idx)
    im_cut.save(f"img_{idx}.jpg")
