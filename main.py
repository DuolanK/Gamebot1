import ctypes
import time
from ctypes import windll, Structure, c_long, byref
import random
import cv2
import mss
import numpy as np
import pyautogui as pg

cap = cv2.VideoCapture(0)


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]



def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return {"x": pt.x, "y": pta.y}


def click():
    pg.mouseDown()
    time.sleep(0.01)
    pg.mouseUp()

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# код мсс, захват картинки #69 116 84, 49 186 104

HSV_RANGES = {
    'green': [
        {
            'lower': np.array([0, 0, 229]),
            'upper': np.array([180, 38, 255])
        },
        {
            'lower': np.array([0, 0, 229]),
            'upper': np.array([180, 38, 255])
        }

],  # orange is a minor colorцц
    'orange': [
        {
            'lower': np.array([0, 69, 255]),
            'upper': np.array([80, 155, 255])
        }
    ],
    # yellow is a minor color
    'yellow': [
        {
            'lower': np.array([21, 39, 64]),
            'upper': np.array([40, 255, 255])
        }
    ],
    # green is a major color
    'blue': [
        {
            'lower': np.array([101, 60, 45]),
            'upper': np.array([250, 60, 64])
        }
    ],
    # cyan is a minor color
    'cyan': [
        {
            'lower': np.array([81, 39, 64]),
            'upper': np.array([100, 255, 255])
        }
    ],
    # blue is a major colorw
    'red': [
        {
            'lower': np.array([0, 50, 50]),
            'upper': np.array([10, 255, 255])
        }
    ],
    # violet is a minor color
    'violet': [
        {
            'lower': np.array([141, 39, 64]),
            'upper': np.array([160, 255, 255])
        }
    ],
    # next are the monochrome ranges
    # black is all H & S values, but only the lower 25% of V
    'black': [
        {
            'lower': np.array([0, 0, 0]),
            'upper': np.array([180, 255, 63])
        }
    ],
    # gray is all H values, lower 15% of S, & between 26-89% of V
    'gray': [
        {
            'lower': np.array([0, 0, 64]),
            'upper': np.array([180, 38, 228])
        }
    ],
    # white is all H values, lower 15% of S, & upper 10% of V
    'white': [
        {
            'lower': np.array([60, 39, 10]),
            'upper': np.array([69, 116, 84])
        },
]
}
monitor1 = {"top": 875, "left": 1756, "width": 40, "height": 40}
monitor2 = {"top": 900, "left": 1749, "width": 20, "height": 40}
monitor3 = {"top": 900, "left": 1781, "width": 20, "height": 40}
monitor4 = {"top": 860, "left": 1756, "width": 40, "height": 30}
monitor_drone = {"top": 998, "left": 1350, "width": 115, "height": 10} #left 1320



def process_image(original_image):
    # Создать копию входящей картинки в оттенках серого
    processed_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
    # Найти границы всех объектов на картинке.
    # Используется алгоритм https://ru.wikipedia.org/wiki/Оператор_Кэнни
    processed_image = cv2.Canny(processed_image, threshold1=200, threshold2=300)
    return processed_image

def process_drone(original_image):
    processed_drone = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
    return processed_drone




def create_mask(hsv_img, colors):
    """
    Creates a binary mask from HSV image using given colors.
    """

    # noinspection PyUnresolvedReferences
    mask = np.zeros((hsv_img.shape[0], hsv_img.shape[1]), dtype=np.uint8)

    for color in colors:
        for color_range in HSV_RANGES[color]:
            # noinspection PyUnresolvedReferences
            mask += cv2.inRange(
                hsv_img,
                color_range['lower'],
                color_range['upper']
            )

        return mask

def screen_record():
    # Подготовить класс для снятия скриншотов
    sct = mss.mss()
    time.sleep(5)

    N = 100000  # the number of iterations

    while True:
        # Проверить нижнюю область.
        # Сделать скриншот заданной области экрана (прямоугольник перед персонажем)
        mean1_df = []
        mean2_df = []
        mean3_df = []
        for i in range(N):
            img = sct.grab(monitor_drone)
            alpha = 1
            beta = 80
            img = np.array(img)
            img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            red_mask = create_mask(img_hsv, ['green'])
            mask_img = cv2.bitwise_and(img_hsv, img_hsv, mask=red_mask)
            hasRed = np.sum(mask_img)
            if hasRed < 91000:
                print('DAMAGE', hasRed)
                ReleaseKey(0x10)
                PressKey(0x10)
            if hasRed == 0:
                time.sleep(5)
                pg.moveTo(1700, 800)  # {"top": 350, "left": 1360, "width": 100, "height": 50}
                pg.click()
            else:
                print('notdamage', hasRed)
                time.sleep(random.uniform(1, 2))
            cv2.imshow("OpenCV/Numpy", img)


            #wwцыфй
            img = sct.grab(monitor1)
            img = np.array(img)
            processed_image = process_image(img)
            img2 = sct.grab(monitor2)
            img2 = np.array(img2)
            processed_image2 = process_image(img2)
            img3 = sct.grab(monitor3)
            img3 = np.array(img3)
            processed_image3 = process_image(img3)
            img4 = sct.grab(monitor4)
            img4 = np.array(img4)
            processed_image4 = process_image(img4)

            # Посчитать среднее арифметическое всех границ. Если это значение отличается от 0,
            # то на нашей картинке есть препятствие. А значит его нужно перепрыгнуть.
            mean1 = round(np.mean(processed_image),0)
            print('down mean1 = ', mean1) #frontw
            last_time = time.time()
            mean2 = round(np.mean(processed_image2),0) #left
            print('down mean2 = ', mean2)
            last_time = time.time()
            mean3 = round(np.mean(processed_image3),0) #rightwdwaq
            print('down mean3 = ', mean3)
            last_time = time.time()
            mean4 = round(np.mean(processed_image4), 0)  # rightwdwaq
            print('down mean4 = ', mean4)
            last_time = time.time()

            mean1_df.append(mean1)
            mean2_df.append(mean2)
            mean3_df.append(mean3)
            koef_prepyatstsvie = 2
            PressKey(0x11)
            if mean1*koef_prepyatstsvie>mean4+mean1 or mean1<10:
                PressKey(0x11)
                ReleaseKey(0x1F)
                ReleaseKey(0x20)
                ReleaseKey(0x1E)
                print('forward')
                PressKey(0x13)  # R
                if i >= 5:
                    if mean1 != 0 or mean2 != 0 or mean3 != 0:
                        if mean1 == mean1_df[i - 2] == mean1_df[i - 3] and mean2 == mean2_df[i - 2] == mean2_df[
                            i - 3] and mean3 == mean3_df[i - 2] == mean3_df[i - 3]:
                            PressKey(0x13)  # R
                            ReleaseKey(0x11)
                            PressKey(0x1F)  # Sa
                            if mean3 > mean2:
                                PressKey(0x20)  # D
                                time.sleep(2)
                                ReleaseKey(0x20)
                            else:
                                PressKey(0x1E)  # A
                                time.sleep(2)
                                ReleaseKey(0x1E)  # A
                            print('nazad')
            elif (mean1+mean4)*koef_prepyatstsvie > mean2 and mean1+mean4 > mean3 and mean2 > mean3 and mean2>10:
                PressKey(0x20)  #D
                PressKey(0x11) #W
                ReleaseKey(0x1E) #A
                ReleaseKey(0x1F)
                print('vpravo')
                PressKey(0x13)  # R


            elif (mean1+mean4)*koef_prepyatstsvie > mean2 and mean1+mean4 > mean3 and mean3>mean2 and mean3>10:
                PressKey(0x1E) #A
                PressKey(0x11)
                ReleaseKey(0x20) #D
                ReleaseKey(0x1F)
                print('vlevo')
                PressKey(0x13)  # R


            if i >= 1:
                if mean1 != 0 or mean2 != 0 or mean3 != 0:
                    if mean1 == mean1_df[i - 1] == mean1_df[i - 2] and mean2 == mean2_df[i - 1] == mean2_df[
                        i - 2] and mean3 == mean3_df[i - 1] == mean3_df[i - 2]and mean1+mean4>0:
                        PressKey(0x13)  # R
                        ReleaseKey(0x11)
                        PressKey(0x1F)  # Sa
                        if mean3 > mean2:
                            PressKey(0x20)  # D
                            time.sleep(2)
                            ReleaseKey(0x20)
                        else:
                            PressKey(0x1E)  # A
                            time.sleep(2)
                            ReleaseKey(0x1E)  # A
                        print('nazad')

                #if mean1==0 and mean2==0 and mean3==q0:
                #    pg.moveTo(1700, 800)  # {"top": 350, "left": 1360, "width": 100, "height": 50}
                #    pg.click()
                print('loop took {} seconds'.format(time.time() - last_time))
                last_time = time.time()
            else:
                PressKey(0x11)  # Wdw
                time.sleep(random.uniform(0.05, 0.1))



if __name__ == '__main__':
    screen_record()

#q