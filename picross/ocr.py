from itertools import product

from PIL import Image
import colorsys
import numpy as np

from recognize import recognize


def pad_image(image):
    iw, ih = image.size  # 原始图像的尺寸
    w, h = 28, 28  # 目标图像的尺寸
    scale = min(float(w) / float(iw), float(h) / float(ih))  # 转换的最小比例

    # 保证长或宽，至少一个符合目标图像的尺寸
    # nw = int(iw * scale)
    # nh = int(ih * scale)

    # image = image.resize((nw, nh), Image.BICUBIC)  # 缩小图像
    # image.show()
    new_image = Image.new('L', (28, 28), (0))  # 生成灰色图像
    # 将图像填充为中间图像，两侧为灰色的样式
    new_image.paste(image, ((w - iw) // 2, (h - ih) // 2))
    # new_image.show()

    return new_image  # .convert("RGB")


CONFIG = {
    "25": {
        "side": {
            "start": (0, 500),
            "end": (215, 1400)
        },
        "top": {
            "start": (215, 225),
            "end": (1065, 500)
        }
    }
}


def row_is_black(px, col, length) -> bool:
    for i in range(length):
        if px[i, col]:
            return False
    return True


def small_col_is_black(px, p, length) -> bool:
    for i in range(length):
        if px[p[0], p[1] + i]:
            return False
    return True


def draw_box(px, p1, p2):
    lx, ly = p1
    rx, ry = p2
    for i in range(lx, rx):
        px[i, ly] = 1
        px[i, ry] = 1
    for i in range(ly, ry):
        px[lx, i] = 1
        px[rx, i] = 1


def is_single(num_img) -> bool:
    length, height = num_img.size
    px = num_img.convert('L').point(
        lambda x: 1 if x > 210 else 0, mode='1').load()
    for i in range(height):
        if not row_is_black(px, i, length):
            return False
    return True


def main():
    config = CONFIG["25"]
    side_box = (*config["side"]["start"], *config["side"]["end"])
    im = Image.open("image.png")
    # dst = im.convert('L').point(lambda x: 255 if x > 80 else 0, mode='1')
    side = im.crop(side_box)
    bin_side = side.convert('L').point(
        lambda x: 1 if x > 80 else 0, mode='1')
    x_len, y_len = side.size
    px = bin_side.load()

    rows = []
    side_hints = []

    same_row = False
    row_top = 0
    for j in range(y_len):
        if not row_is_black(px, j, x_len):
            if not same_row:
                row_top = j
            same_row = True
        else:
            if same_row:
                rows.append((row_top, j))
                same_row = False

    same_col = False
    col_left = 0
    for top, bottom in rows:
        height = bottom - top
        hints = []
        for x in range(x_len):
            if not small_col_is_black(px, (x, top), height):
                if not same_col:
                    col_left = x
                same_col = True
            else:
                if same_col:
                    hints.append(((col_left, top), (x, bottom)))
                    same_col = False
        side_hints.append(hints)

    def _unpack(t):
        return [j for i in t for j in i]

    ans = []
    for i in side_hints:
        row = []
        while len(i) != 0:
            num = i[0]
            t = _unpack(num)
            num_img = [side.crop(_unpack(num))]
            if is_single(num_img[0]):
                num_img.append(side.crop(_unpack(i[1])))
                i = i[1:]
            row.append(num_img)
            i = i[1:]
        ans.append(row)

    # for i in ans[0]:
    #     for j in i:
    #         j.show()
    #     print()
    images = [pad_image(i) for i in ans[0][0]]
    images[0].show()
    images = np.asarray([np.asfarray(i) / 255 for i in images])
    # for i in range(len(images)):
    #     np.reshape(images[i], ( 28, 28, 3))
    result = recognize(images)
    print(result)


if __name__ == "__main__":
    main()
