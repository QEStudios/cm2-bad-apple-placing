import cv2
import autoit
import pyautogui
import mouse
import keyboard
import time
import numpy
import random

def patch_asscalar(a):
    return a.item()
setattr(numpy, "asscalar", patch_asscalar)

screenX = 1920
screenY = 1080

size = (64,48)
filename = "badapple.mp4"
framerate = 10
maxLength = 9999999

def click(x,y):
    autoit.mouse_click("left",int(x),int(y),speed=5)

def move(x,y):
    autoit.mouse_move(int(x),int(y),speed=3)

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    """
    return (1 - t) * a + t * b

vidcap = cv2.VideoCapture(filename)
framerate = float(framerate)
inputFramerate = vidcap.get(cv2.CAP_PROP_FPS)
inputSize = (int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)),
             int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
outputLength = int(length / inputFramerate * framerate)

click(screenX/2,screenY/2)
time.sleep(0.1)
keyboard.send("6")

corners = []

for c in range(0,4):
    print(f"click on corner {c}")
    mouse.wait(target_types=mouse.UP)
    corners.append(mouse.get_position())

print(corners)

# input("press enter to validate")

# click(screenX/2,screenY/2)
# time.sleep(0.1)
# keyboard.send("6")
# time.sleep(0.1)
# for y in range(size[1]-1,-1,-(size[1]//5)):
#     for x in range(0,size[0],size[0]//5):
#         xPosTop = lerp(corners[0][0], corners[1][0], x/size[0])
#         xPosBottom = lerp(corners[2][0], corners[3][0], x/size[0])
#         yPosTop = lerp(corners[0][1], corners[1][1], x/size[0])
#         yPosBottom = lerp(corners[2][1], corners[3][1], x/size[0])

#         xPos = lerp(xPosTop, xPosBottom, y/size[1])
#         yPos = lerp(yPosTop, yPosBottom, y/size[1])

#         click(xPos, yPos)

# keyboard.send("z")
# time.sleep(0.1)
# for y in range(size[1]-1,-1,-(size[1]//5)):
#     for x in range(0,size[0],size[0]//5):
#         xPosTop = lerp(corners[0][0], corners[1][0], x/size[0])
#         xPosBottom = lerp(corners[2][0], corners[3][0], x/size[0])
#         yPosTop = lerp(corners[0][1], corners[1][1], x/size[0])
#         yPosBottom = lerp(corners[2][1], corners[3][1], x/size[0])

#         xPos = lerp(xPosTop, xPosBottom, y/size[1])
#         yPos = lerp(yPosTop, yPosBottom, y/size[1])

#         click(xPos, yPos)

input("press enter to confirm")

time.sleep(1)

click(screenX/2,screenY/2)
time.sleep(1)
keyboard.send("6")

lastState = numpy.full(size,255,numpy.uint8)
currentTool = True
inFrame = 3676
outFrame = 1227
displayFrame = 3680
running = True
for i in range(inFrame+1):
    vidcap.grab()
while True:
    if (outFrame+1)/framerate > maxLength:
        click(1880,530)
        keyboard.send("ctrl+a")
        keyboard.write("Done!")
        break
    success = vidcap.grab()
    if not success:
        click(1880,530)
        keyboard.send("ctrl+a")
        keyboard.write("Done!")
        break
    inFrame += 1

    due = int(inFrame / inputFramerate * framerate)
    
    if due > outFrame:
        success, frame = vidcap.retrieve()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if not success:
            break
        outFrame += 1

        resized = cv2.resize(frame, size, interpolation=cv2.INTER_CUBIC)

        click(1700,900)
        time.sleep(0.05)
        while displayFrame < inFrame:
            keyboard.send("right")
            displayFrame += 1
        
        time.sleep(0.1)
        
        click(screenX/2,screenY/2)
        time.sleep(0.05)

        changes = []

        for y in range(size[1]-1,-1,-1):
            for x in range(0,size[0]):
                pixel = resized[y,x][0] > 127
                last = lastState[x][y] > 127
                
                xPosTop = lerp(corners[0][0], corners[1][0], x/size[0])
                xPosBottom = lerp(corners[2][0], corners[3][0], x/size[0])
                yPosTop = lerp(corners[0][1], corners[1][1], x/size[0])
                yPosBottom = lerp(corners[2][1], corners[3][1], x/size[0])

                xPos = lerp(xPosTop, xPosBottom, y/size[1])
                yPos = lerp(yPosTop, yPosBottom, y/size[1])

                if pixel != last:
                    if pixel:
                        changes.append(['z', xPos, yPos])
                    else:
                        changes.append(['6', xPos, yPos])
                    lastState[x][y] = resized[y,x][0]

        for pixel in changes:
            if keyboard.is_pressed("esc"):
                exit()
            keyboard.send(pixel[0])
            time.sleep(0.01)
            click(pixel[1],pixel[2])
            time.sleep(0.01)
        click(1880,530)
        time.sleep(0.05)
        keyboard.send("end, left, left, left, left, left, backspace, backspace, backspace, backspace")
        for c in "%04d" % (outFrame,):
            keyboard.send(c)
        
        time.sleep(0.05)
        
        click(screenX/2,screenY/2)
        time.sleep(0.05)
        keyboard.send("v")
        time.sleep(0.01)
        screenshot = pyautogui.screenshot()
        screenshot.save(f'screenshots/frame{"%04d" % (outFrame,)}.png')
