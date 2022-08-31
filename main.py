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
    return {"x": pt.x, "y": pt.y}


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

# код мсс, захват картинки

HSV_RANGES = {
    'blue': [
        {
            'lower': np.array([101, 60, 45]),
            'upper': np.array([250, 60, 64])
        },
        {
            'lower': np.array([101, 60, 64]),
            'upper': np.array([250, 60, 64])
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
    'green': [
        {
            'lower': np.array([41, 39, 64]),
            'upper': np.array([80, 255, 255])
        }
    ],
    # cyan is a minor color
    'cyan': [
        {
            'lower': np.array([81, 39, 64]),
            'upper': np.array([100, 255, 255])
        }
    ],
    # blue is a major color
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
            'lower': np.array([0, 0, 229]),
            'upper': np.array([180, 38, 255])
        }
]
}
monitor1 = {"top": 917, "left": 1756, "width": 40, "height": 40}
monitor2 = {"top": 937, "left": 1733, "width": 40, "height": 40}
monitor3 = {"top": 937, "left": 1781, "width": 40, "height": 40}
monitor_drone = {"top": 918, "left": 1737, "width": 100, "height": 100}

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

    N = 100000  # the number of iterationsq

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
            red_mask = create_mask(img_hsv, ['red'])
            mask_img = cv2.bitwise_and(img_hsv, img_hsv, mask=red_mask)
            hasRed = np.sum(mask_img)
            if hasRed > 200:
                print('Blue', hasRed)
                ReleaseKey(0x10)
                PressKey(0x10)
                time.sleep(random.uniform(1,2))
            else:
                print('neblue', hasRed)
                time.sleep(random.uniform(1,2))
            cv2.imshow("OpenCV/Numpy", img)
#ww
            img = sct.grab(monitor1)
            img = np.array(img)
            processed_image = process_image(img)
            img2 = sct.grab(monitor2)
            img2 = np.array(img2)
            processed_image2 = process_image(img2)
            img3 = sct.grab(monitor3)
            img3 = np.array(img3)
            processed_image3 = process_image(img3)

            # Посчитать среднее арифметическое всех границ. Если это значение отличается от 0,
            # то на нашей картинке есть препятствие. А значит его нужно перепрыгнуть.
            mean1 = np.mean(processed_image)
            print('down mean1 = ', mean1) #frontw
            last_time = time.time()

            mean2 = np.mean(processed_image2) #left
            print('down mean2 = ', mean2)
            last_time = time.time()
            mean3 = np.mean(processed_image3) #right
            print('down mean3 = ', mean3)
            last_time = time.time()
            mean1_df.append(mean1)
            mean2_df.append(mean2)
            mean3_df.append(mean3)
            if mean1<float(6):
                ReleaseKey(0x20) #D
                ReleaseKey(0x1E) #A
                PressKey(0x11) #W
                time.sleep(random.uniform(0.1,0.2))
            else:
                if mean2>float(6):
                    ReleaseKey(0x1E) #A
                    PressKey(0x11)
                    PressKey(0x20) #D
                    time.sleep(random.uniform(0.05, 0.125))
                if mean3>float(6):
                    ReleaseKey(0x20)
                    PressKey(0x11)
                    PressKey(0x1E) #A
                    time.sleep(random.uniform(0.05, 0.125))

                if i >= 3:
                    if mean1 != 0 or mean2 != 0 or mean3 != 0:
                        if mean1==mean1_df[i-1]==mean1_df[i-2] or mean2==mean2_df[i-1]==mean2_df[i-2] or mean3==mean3_df[i-1]==mean3_df[i-2]:
                            ReleaseKey(0x1E)
                            ReleaseKey(0x20)
                            ReleaseKey(0x11)
                            PressKey(0x1F)  # S
                            if i % 2 == 0:
                                PressKey(0x20) #D
                            else:
                                PressKey(0x1E) #Awdwdwd
                            time.sleep(0.5)


            print('loop took {} seconds'.format(time.time() - last_time))
            last_time = time.time()

if __name__ == '__main__':
    screen_record()

#