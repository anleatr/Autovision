import cv2
import pyautogui
import numpy as np
import time


def vision_init():
    curr_page = pyautogui.screenshot()
    curr_page = np.array(curr_page)
    curr_page = cv2.cvtColor(curr_page, cv2.COLOR_RGB2BGR)

    # 先把屏幕左半部分掩盖住
    h, w = curr_page.shape[:2]
    curr_page[:, : w // 2] = 0

    """执行模板匹配,获取章节目标"""
    n = 7

    results = []    # 当前界面所有章节坐标
    for i in range(n):
        template = cv2.imread(f'./template/{i+1}.png')

        result = cv2.matchTemplate(curr_page, template, cv2.TM_CCOEFF_NORMED)   # 返回的是一个掩码
        threshold = 0.9
        rows, cols = np.where(result >= threshold)   # rows:[], cols: []
        coordinates = list(zip(cols, rows)) # exract coordinates from mask
        results.extend(coordinates)

    """检测每个章节是否已完成"""
    is_finish = [0] * len(results)  # set 0 for each passage
    finish = cv2.imread("./template/finish.png")

    for idx,coordinate in enumerate(results):
        x, y = coordinate   #注意 行，列 和x,y 不一样
        mask = np.zeros_like(curr_page)

        # 计算保留区域的边界
        top = max(0, y - 10)  # 上边界
        bottom = min(h, y + 50)  # 下边界
        left = x  # 左边界
        right = w  # 右边界

        # 在掩膜中将保留区域设置为白色（255）
        mask[top:bottom, left:right] = 255
        masked_image = cv2.bitwise_and(curr_page, mask)

        # 检测
        result = cv2.matchTemplate(masked_image, finish, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        location = np.where(result > threshold)

        if len(location[0]) >= 1:
            is_finish[idx] = 1
        else:
            continue

    print("检测到章节坐标", results)
    print("章节完成情况", is_finish)

    return results, is_finish

def moveTo_latest_page():
    while True:
        print("正在检测当前页面")
        coordinates, is_finish = vision_init()
        # 如果当前不在智慧树页面,等待
        for i in range(5):
            if len(is_finish) == 0:
                print(f"当前页面未检测到章节，正在重试-- {i+1} / 5")
                time.sleep(0.5)
                coordinates, is_finish = vision_init()
            else:
                break

        curr_page_finished = all(x==1 for x in is_finish)

        if curr_page_finished is True:
            # 移动鼠标
            print("当前界面章节已全部完成")
            print("-------------------检测下一页-----------------------")
            pyautogui.moveTo(coordinates[0])
            pyautogui.scroll(-200)
            time.sleep(1)   # 要留给浏览器一定的渲染时间

        else:
            print("当前界面未完成")
            break

    return coordinates, is_finish


def select_passage(coordinates, is_finish):
    is_finish = np.array(is_finish)
    idx = np.where(is_finish == 0)[0][0]    # 没有的章节索引
    # 移动鼠标到指定位置
    pyautogui.moveTo(coordinates[idx])
    pyautogui.click()


def click_start():
    pyautogui.moveTo(33, 953)
    pyautogui.click()

def mid_check():
    curr_page = pyautogui.screenshot()
    curr_page = np.array(curr_page)
    curr_page = cv2.cvtColor(curr_page, cv2.COLOR_RGB2BGR)
    button = cv2.imread("./template/button.png")
    popup_win = cv2.imread("./template/shutdown.png")

    # 在当前页面匹配
    result = cv2.matchTemplate(curr_page, popup_win, cv2.TM_CCOEFF_NORMED)  # 返回的是一个掩码
    threshold = 0.8
    rows, cols = np.where(result >= threshold)  # rows:[], cols: []

    if len(rows)==0: # 没有弹窗
        return False
    else:
        # 如果有弹窗，需要做一个选择题
        # 防止有多选题，需要把每个选项都点一遍
        print("检测到弹窗，正在摧毁目标")
        result1 = cv2.matchTemplate(curr_page, button, cv2.TM_CCOEFF_NORMED)  # 返回的是一个掩码
        threshold1 = 0.8
        rows1, cols1 = np.where(result1 >= threshold1)  # rows:[], cols: []
        coordinates = list(zip(cols1,rows1))

        for idx,coordinate in enumerate(coordinates):
            pyautogui.moveTo(coordinate)
            pyautogui.click()
            time.sleep(0.5)

        # 答完题，关闭
        x, y = cols[0], rows[0]
        pyautogui.moveTo(x+50, y+25)
        pyautogui.click()

        # 重新点击开始
        time.sleep(1)
        click_start()


def end_check():
    curr_page = pyautogui.screenshot()
    curr_page = np.array(curr_page)
    curr_page = cv2.cvtColor(curr_page, cv2.COLOR_RGB2BGR)
    end_temp = cv2.imread("./template/end.png")

    result = cv2.matchTemplate(curr_page, end_temp, cv2.TM_CCOEFF_NORMED)  # 返回的是一个掩码
    threshold = 0.8
    rows, cols = np.where(result >= threshold)  # rows:[], cols: []
    if len(rows)==0:
        return False

    print("当前章节已完成")
    return True


def main():

    while True:
        coordinates, is_finish = moveTo_latest_page()
        select_passage(coordinates=coordinates, is_finish=is_finish)
        time.sleep(2)   # 等待页面响应，若网速慢可稍微调大一点
        click_start()
        while True:
            mid_check()
            is_end = end_check()
            if is_end:
                time.sleep(2)
                break
            else:
                time.sleep(2)   # 每两秒检测一次

if __name__ == "__main__":
    main()
