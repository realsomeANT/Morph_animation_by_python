import numpy as np
from scipy.special import comb
from OpenGL.GL import *
from OpenGL.GLUT import *
import time

t = 0.0
direction = 2
wait_counter = 0

def bezier_interp(points, t):
    n = len(points) - 1
    result = np.zeros_like(points[0])
    for i, p in enumerate(points):
        result += comb(n, i) * ((1 - t) ** (n - i)) * (t ** i) * p
    return result

def diamonds_points_120():
    cx, cy = 0.5, 0.5
    w, h = 0.28, 0.38
    corners = np.array([
        [cx, cy + h/2],
        [cx + w/2, cy],
        [cx, cy - h/2],
        [cx - w/2, cy],
    ])
    points = []
    for i in range(4):
        start = corners[i]
        end = corners[(i+1)%4]
        for t in np.linspace(0, 1, 30, endpoint=False):
            points.append(start * (1-t) + end * t)
    return np.array(points)

def heart_points_120():
    points = []
    # Heart parametric equation
    for t in np.linspace(0, 2 * np.pi, 120, endpoint=False):
        x = 0.5 + 0.16 * np.sin(t) ** 3
        y = 0.5 + 0.13 * np.cos(t) - 0.07 * np.cos(2 * t) - 0.02 * np.cos(3 * t) - 0.02 * np.cos(4 * t)
        points.append([x, y])
    return np.array(points)

def spades_points_120():
    points = []
    # หัวโพดำ (spade head): คล้ายหัวใจแต่กลับหัวและแหลมกว่า
    for t in np.linspace(0, 2 * np.pi, 100, endpoint=False):
        x = 0.5 + 0.16 * np.sin(t) ** 3
        y = 0.58 - 0.13 * np.cos(t) + 0.07 * np.cos(2 * t) + 0.02 * np.cos(3 * t) + 0.02 * np.cos(4 * t)
        points.append([x, y])
    # ก้าน (ฐานโพดำ): วงรีเล็กด้านล่าง
    for t in np.linspace(np.pi, 2 * np.pi, 20, endpoint=False):
        x = 0.5 + 0.05 * np.cos(t)
        y = 0.34 + 0.08 * np.sin(t)
        points.append([x, y])
    return np.array(points)

def morph_shape(t):
    heart = heart_points_120()
    diamonds = diamonds_points_120()
    spades = spades_points_120()
    # 3 เฟส: diamond -> heart -> spade -> diamond
    if t < 1/3:
        t2 = t * 3
        return np.array([bezier_interp([d, h], t2) for d, h in zip(diamonds, heart)])
    elif t < 2/3:
        t2 = (t - 1/3) * 3
        return np.array([bezier_interp([h, s], t2) for h, s in zip(heart, spades)])
    else:
        t2 = (t - 2/3) * 3
        return np.array([bezier_interp([s, d], t2) for s, d in zip(spades, diamonds)])

def get_morph_color(t):
    # 3 เฟส: diamond->heart (ฟ้า->แดง), heart->spade (แดง->ดำ), spade->diamond (ดำ->ฟ้า)
    if t < 1/3:
        t2 = t * 3
        # ฟ้า (0.2,0.6,1.0) -> แดง (1.0,0.2,0.2)
        r = 0.2 + (1.0 - 0.2) * t2
        g = 0.6 + (0.2 - 0.6) * t2
        b = 1.0 + (0.2 - 1.0) * t2
        return (r, g, b)
    elif t < 2/3:
        t2 = (t - 1/3) * 3
        # แดง (1.0,0.2,0.2) -> ดำ (0,0,0)
        r = 1.0 * (1-t2)
        g = 0.2 * (1-t2)
        b = 0.2 * (1-t2)
        return (r, g, b)
    else:
        t2 = (t - 2/3) * 3
        # ดำ (0,0,0) -> ฟ้า (0.2,0.6,1.0)
        r = 0.2 * t2
        g = 0.6 * t2
        b = 1.0 * t2
        return (r, g, b)

def update(value):
    global t, direction, wait_counter
    if wait_counter > 0:
        wait_counter -= 1
    else:
        t += 0.005 * direction
        if t >= 1.0:
            t = 1.0
            direction = -1
            wait_counter = 60
        elif t <= 0.0:
            t = 0.0
            direction = 1
            wait_counter = 60
        # เพิ่มการหยุดพักที่แต่ละจุดสำคัญ
        elif abs(t - 1/3) < 0.005 or abs(t - 2/3) < 0.005:
            wait_counter = 60
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    shape = morph_shape(t)
    r, g, b = get_morph_color(t)
    glColor3f(r, g, b)
    glBegin(GL_POLYGON)
    for v in shape:
        glVertex2f(*v)
    glEnd()
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b"Morph Animation: Diamond to Club")
    glClearColor(1, 1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 1, 0, 1, -1, 1)
    glutDisplayFunc(display)
    glutTimerFunc(0, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
