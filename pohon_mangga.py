#!/usr/bin/env python3
"""
Pohon Mangga - Python Turtle Animation
======================================
Animasi pertumbuhan pohon mangga dari benih sampai berbuah:
  1. Petani menanam & menyiram   5. Daun tumbuh lebat
  2. Akar tumbuh                 6. Bunga mangga bermekaran
  3. Tunas muncul                7. Bunga rontok, buah tumbuh
  4. Batang & cabang tumbuh      8. Mangga matang

Jalankan:  python3 pohon_mangga.py
Tombol  :  R = ulangi animasi,  Q = keluar  (tanpa tulisan keterangan di layar)
Hanya memakai pustaka bawaan Python (turtle), tanpa instal apa-apa.
"""
import math
import random
import time
import turtle

# ------------------------------------------------------------------ pengaturan
W, H = 900, 900
GROUND = -170          # garis tanah
SEED_Y = GROUND - 45   # letak benih di dalam tanah
DELAY = 0.03           # jeda antar-frame (detik); perbesar agar animasi lebih lambat
SEED = 7               # ganti angka ini untuk bentuk pohon yang berbeda

BG = "black"
NEON_GREEN = "#39FF14"
SOIL_TOP = "#8B5A2B"
SOIL_FILL = "#24160b"
ROOT_COLORS = ["#E0A060", "#C8874A", "#B07038"]
TRUNK = "#9A6233"
TRUNK_GLOW = "#5A3519"
LEAF_COLORS = ["#1F8A3E", "#2EAF52", "#46C965", "#17663A", "#5BD879"]
FLOWER_COLORS = ["#FFF6C2", "#FFE27A", "#FFC4D6", "#FFFFFF"]
MANGO_RAW = (110, 190, 60)     # hijau muda
MANGO_RIPE = (255, 176, 32)    # kuning-oranye
MANGO_BLUSH = (255, 80, 50)    # semburat merah

# ------------------------------------------------------------------ layar
screen = turtle.Screen()
screen.setup(W, H)
screen.bgcolor(BG)
screen.title("Pohon Mangga - Python Turtle Animation")
screen.colormode(255)
screen.tracer(0)


def pen():
    p = turtle.Turtle(visible=False)
    p.speed(0)
    p.penup()
    return p


def tick(n=1):
    screen.update()
    time.sleep(DELAY * n)


def line(p, a, b, width, color):
    p.penup()
    p.goto(a)
    p.pendown()
    p.pensize(width)
    p.pencolor(color)
    p.goto(b)
    p.penup()


def polygon(p, pts, fill, outline=None, width=1):
    p.penup()
    p.goto(pts[0])
    p.pensize(width)
    p.pencolor(outline or fill)
    p.fillcolor(fill)
    if outline:  # tanpa garis tepi = jauh lebih ringan (lebih sedikit objek di layar)
        p.pendown()
    p.begin_fill()
    for q in pts[1:]:
        p.goto(q)
    p.goto(pts[0])
    p.end_fill()
    p.penup()


def ellipse_pts(cx, cy, rx, ry, rot=0.0, n=28, bulge=0.0):
    pts = []
    c, s = math.cos(rot), math.sin(rot)
    for k in range(n):
        a = 2 * math.pi * k / n
        x = rx * math.cos(a) * (1 + bulge * math.sin(a))
        y = ry * math.sin(a)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def mix(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


def hexc(rgb):
    return "#%02X%02X%02X" % rgb


def polar(x, y, heading, length):
    a = math.radians(heading)
    return x + length * math.cos(a), y + length * math.sin(a)


# ------------------------------------------------------------------ teks
title_pen = pen()
cap_pen = pen()


def draw_title():
    title_pen.clear()
    title_pen.goto(0, 385)
    title_pen.color(NEON_GREEN)
    title_pen.write("POHON MANGGA", align="center", font=("Arial", 36, "bold"))


def caption(text, color="#FFFFFF"):
    """Penanda tahap (tanpa tulisan di layar)."""
    tick()


# ------------------------------------------------------------------ cabang (dipakai akar & pohon)
def seg_point(s, u):
    """Titik pada cabang (sedikit melengkung) di posisi u = 0..1."""
    x0, y0 = s["x"], s["y"]
    x2, y2 = polar(x0, y0, s["h"], s["len"])
    a = math.radians(s["h"])
    bend = s.get("bend", 0.0) * s["len"]
    x1 = (x0 + x2) / 2 - math.sin(a) * bend
    y1 = (y0 + y2) / 2 + math.cos(a) * bend
    v = 1 - u
    return v * v * x0 + 2 * v * u * x1 + u * u * x2, v * v * y0 + 2 * v * u * y1 + u * u * y2


def grow_layers(p, layers, steps=8, glow=None):
    """Gambar cabang per lapis; semua cabang satu lapis tumbuh bersamaan.
    Tebal cabang mengecil halus dari pangkal ke ujung (tanpa benjolan di sambungan)."""
    sub = 2  # potongan kecil per langkah supaya lengkung & pengecilan halus
    for layer in layers:
        prev = {id(s): (s["x"], s["y"]) for s in layer}
        for k in range(1, steps + 1):
            for s in layer:
                w0, w1 = s.get("w0", s["w"]), s["w"]
                for j in range(1, sub + 1):
                    u = (k - 1 + j / sub) / steps
                    pt = seg_point(s, u)
                    w = w0 + (w1 - w0) * u
                    if glow:
                        line(p, prev[id(s)], pt, w + 3, glow)
                    line(p, prev[id(s)], pt, w, s["color"])
                    prev[id(s)] = pt
            tick()


def build_tree(x, y, heading, length, width, depth, rnd, spread=(16, 34), shrink=(0.70, 0.80),
               wshrink=0.68, colors=(TRUNK,), max_children=3, max_y=None, upward=0.0):
    layers, tips, nodes = [], [], []
    level = [{"x": x, "y": y, "h": heading, "len": length, "w0": width, "w": max(1, width * (0.5 + wshrink / 2)),
              "d": 0, "color": colors[0], "bend": 0.0}]
    for d in range(depth):
        layers.append(level)
        nxt = []
        for s in level:
            ex, ey = polar(s["x"], s["y"], s["h"], s["len"])
            nodes.append((ex, ey, s["h"], d))
            if d == depth - 1:
                tips.append((ex, ey, s["h"]))
                continue
            n = 2 if rnd.random() < 0.7 or max_children < 3 else 3
            base = rnd.uniform(*spread)
            angles = [-base, base] if n == 2 else [-base, rnd.uniform(-8, 8), base]
            for a in angles:
                h = s["h"] + a + rnd.uniform(-6, 6)
                h += (90 - h) * upward  # cabang condong ke atas -> tajuk menjulang
                L = s["len"] * rnd.uniform(*shrink)
                if max_y is not None and polar(ex, ey, h, L)[1] > max_y:
                    h = -h  # akar jangan keluar dari tanah: pantulkan ke bawah
                    if polar(ex, ey, h, L)[1] > max_y:
                        h = 270
                w0 = s["w"]  # mulai setebal ujung induknya -> sambungan mulus
                nxt.append({"x": ex, "y": ey, "h": h, "len": L, "w0": w0, "w": max(1, w0 * wshrink),
                            "d": d + 1, "color": colors[min(d + 1, len(colors) - 1)],
                            "bend": rnd.uniform(-0.12, 0.12)})
        level = nxt
    return layers, tips, nodes


# ------------------------------------------------------------------ tahap-tahap
def stage_soil(p):
    polygon(p, [(-W / 2, GROUND), (W / 2, GROUND), (W / 2, -H / 2), (-W / 2, -H / 2)], SOIL_FILL)
    line(p, (-W / 2, GROUND), (W / 2, GROUND), 4, SOIL_TOP)
    rnd = random.Random(3)
    for _ in range(90):  # butiran tanah
        p.goto(rnd.uniform(-W / 2, W / 2), rnd.uniform(-H / 2 + 60, GROUND - 8))
        p.dot(rnd.choice([2, 3, 4]), rnd.choice(["#3b2614", "#4a3018", "#5c3d1f"]))
    tick()


def draw_seed(p, x, y, cracked=False):
    p.clear()
    polygon(p, ellipse_pts(x, y, 17, 11, rot=0.25, bulge=0.15), "#C68B3C", "#FFD08A", 2)
    if cracked:
        line(p, (x - 6, y + 2), (x + 1, y - 3), 2, "#3A2410")
        line(p, (x + 1, y - 3), (x + 7, y + 3), 2, "#3A2410")


SKIN = "#C68642"
SHIRT = "#2E86C1"
PANTS = "#1B2631"
HAT = "#E3C16F"
HOE_WOOD = "#8B5A2B"
HOE_BLADE = "#B0B6BB"


FARMER_SCALE = 1.3


def draw_farmer(p, x, face=1, walk=0.0, hoe=None, reach=False, can=None):
    """Petani bercaping. face=1 menghadap kanan, -1 kiri. hoe = sudut gagang cangkul (derajat)."""
    p.clear()
    S = FARMER_SCALE
    real_line, real_poly, real_goto, real_dot = line, polygon, p.goto, p.dot
    T = lambda q: (x + (q[0] - x) * S, GROUND + (q[1] - GROUND) * S)
    line_ = lambda pp, a, b, w, c: real_line(pp, T(a), T(b), w * S, c)
    poly_ = lambda pp, pts, f, o=None, w=1: real_poly(pp, [T(q) for q in pts], f, o, w)
    goto_ = lambda q, y=None: real_goto(T(q if y is None else (q, y)))
    dot_ = lambda sz, c: real_dot(sz * S, c)
    _draw_farmer_body(p, x, face, walk, hoe, reach, line_, poly_, goto_, dot_, can)


def _draw_farmer_body(p, x, face, walk, hoe, reach, line, polygon, goto, dot, can=None):
    g = GROUND
    hip = (x, g + 62)
    sh = (x + 4 * face, g + 112)
    # kaki (berayun saat berjalan)
    sw = 16 * math.sin(walk)
    for k, sgn in ((0, 1), (1, -1)):
        foot = (x + sgn * sw, g + 2)
        knee = (x + sgn * sw * 0.5 + 4 * face, g + 32)
        line(p, hip, knee, 9, PANTS)
        line(p, knee, foot, 8, PANTS)
        line(p, foot, (foot[0] + 12 * face, foot[1]), 6, "#3E2723")
    # badan
    polygon(p, [(x - 13, g + 60), (x + 13, g + 60), (x + 15 + 4 * face, g + 115), (x - 11 + 4 * face, g + 115)],
            SHIRT, "#1B4F72", 2)
    # kepala & caping
    head = (x + 6 * face, g + 128)
    goto(head)
    dot(26, SKIN)
    goto(head[0] + 6 * face, head[1] + 2)
    dot(4, "#2B1B10")
    polygon(p, [(head[0] - 30, head[1] + 7), (head[0] + 30, head[1] + 7), (head[0], head[1] + 32)], HAT, "#8A6D2F", 2)
    # tangan & cangkul
    if hoe is not None:
        hands = (x + 22 * face, g + 92)
        line(p, sh, hands, 7, SHIRT)
        a = math.radians(hoe)
        tip = (hands[0] + 100 * math.cos(a) * face, hands[1] + 100 * math.sin(a))
        tail = (hands[0] - 20 * math.cos(a) * face, hands[1] - 20 * math.sin(a))
        line(p, tail, tip, 5, HOE_WOOD)
        # mata cangkul tegak lurus gagang, mengarah ke badan petani
        bx, by = -math.sin(a) * face, math.cos(a)
        if by > 0:
            bx, by = -bx, -by
        blade_end = (tip[0] + bx * 26, tip[1] + by * 26)
        polygon(p, [(tip[0] - 5 * face * 0, tip[1]), (blade_end[0] - 7 * face, blade_end[1]),
                    (blade_end[0] + 7 * face, blade_end[1])], HOE_BLADE, "#5D6D7E", 2)
        goto(hands)
        dot(10, SKIN)
    elif can is not None:
        hand = (x + 26 * face, g + 84)
        line(p, sh, hand, 7, SHIRT)
        body, spout_base, spout_tip = can_shape(x, face, can)
        polygon(p, body, "#3A8FB7", "#1F5F7A", 2)
        line(p, spout_base, spout_tip, 4, "#3A8FB7")
        line(p, body[3], (body[3][0] - 6 * face, body[3][1] + 10), 3, "#1F5F7A")  # pegangan
        goto(hand)
        dot(10, SKIN)
    else:
        hand = (x + (30 if reach else 10) * face, g + (95 if reach else 70))
        line(p, sh, hand, 7, SHIRT)
        goto(hand)
        dot(10, SKIN)


def can_shape(x, face, tilt):
    """Gembor (koordinat petani sebelum diskalakan). tilt = derajat condong ke depan."""
    g = GROUND
    cx, cy = x + 30 * face, g + 74
    a = math.radians(-tilt * face)
    rot = lambda q: (cx + (q[0] * math.cos(a) - q[1] * math.sin(a)), cy + (q[0] * math.sin(a) + q[1] * math.cos(a)))
    f = face
    body = [rot((-10 * f, -12)), rot((14 * f, -12)), rot((14 * f, 10)), rot((-10 * f, 10))]
    spout_base = rot((14 * f, 4))
    spout_tip = rot((40 * f, 16))
    return body, spout_base, spout_tip


def spout_world(x, face, tilt):
    _, _, tip = can_shape(x, face, tilt)
    S = FARMER_SCALE
    return (x + (tip[0] - x) * S, GROUND + (tip[1] - GROUND) * S)


def draw_hole(p, size, mound):
    p.clear()
    if size > 0:
        polygon(p, ellipse_pts(0, GROUND - 3, 9 + 14 * size, 4 + 7 * size, n=20), "#120a04")
    if mound > 0:
        polygon(p, [(22, GROUND), (30 + 10 * mound, GROUND + 9 * mound), (44 + 16 * mound, GROUND)], "#5c3d1f", "#7a5230", 1)


def dirt_burst(p, rnd, n=10):
    pts = [(rnd.uniform(-10, 10), GROUND + 2, rnd.uniform(-3, 3), rnd.uniform(3, 7)) for _ in range(n)]
    for f in range(10):
        p.clear()
        for (x, y, vx, vy) in pts:
            p.goto(x + vx * f, y + vy * f - 0.6 * f * f)
            p.dot(5, "#7a5230")
        yield


def stage_seed(p, rnd):
    caption("1. Petani menanam benih mangga", "#FFD08A")
    farmer, hole, dirt = pen(), pen(), pen()
    stand = -78
    # berjalan masuk sambil memanggul cangkul
    for k in range(60):
        x = -500 + (stand + 500) * k / 59
        draw_farmer(farmer, x, 1, walk=k * 0.45, hoe=115)
        tick()
    # mencangkul 3 kali, lubang makin dalam
    for swing in range(3):
        for k in range(10):  # angkat cangkul
            draw_farmer(farmer, stand, 1, hoe=-62 + (115 + 62) * k / 9)
            tick()
        for k in range(6):  # ayun ke tanah
            draw_farmer(farmer, stand, 1, hoe=115 - (115 + 62) * (k + 1) / 6)
            tick()
        draw_hole(hole, (swing + 1) / 3, (swing + 1) / 3)
        for _ in dirt_burst(dirt, rnd):
            tick()
        dirt.clear()
    # memasukkan benih ke lubang
    draw_farmer(farmer, stand, 1, hoe=None, reach=True)
    hand = (stand + 30 * FARMER_SCALE, GROUND + 95 * FARMER_SCALE)
    for k in range(30):
        u = k / 29
        y = hand[1] - (hand[1] - SEED_Y) * u * u
        x = hand[0] + (0 - hand[0]) * min(1, u * 1.6)
        draw_seed(p, x, y)
        tick()
    tick(10)
    # menutup lubang
    for k in range(10):
        draw_farmer(farmer, stand, 1, hoe=-62 + (115 + 62) * k / 9)
        tick()
    for k in range(6):
        draw_farmer(farmer, stand, 1, hoe=115 - (115 + 62) * (k + 1) / 6)
        tick()
    for k in range(8):
        draw_hole(hole, 1 - (k + 1) / 8, 1 - (k + 1) / 8)
        tick()
    hole.clear()
    polygon(hole, [(-14, GROUND), (0, GROUND + 5), (14, GROUND)], "#5c3d1f", "#7a5230", 1)  # gundukan kecil
    # menyiram benih dengan gembor
    water = pen()
    wx = stand - 8
    for k in range(12):  # angkat gembor
        draw_farmer(farmer, wx, 1, can=k * 4)
        tick()
    drops = []
    wet = 0.0
    for f in range(70):
        tilt = 48 + 4 * math.sin(f * 0.3)
        draw_farmer(farmer, wx, 1, can=tilt)
        sx, sy = spout_world(wx, 1, tilt)
        if f < 55:
            for _ in range(3):
                drops.append([sx + rnd.uniform(-2, 2), sy, rnd.uniform(0.6, 1.6), rnd.uniform(-1, 0)])
        water.clear()
        for d in drops:
            d[3] -= 0.9  # gravitasi
            d[0] += d[2]
            d[1] += d[3]
        drops = [d for d in drops if d[1] > GROUND + 2]
        for d in drops:
            water.goto(d[0], d[1])
            water.dot(4, "#7FD3FF")
        wet = min(1.0, wet + 0.02)
        hole.clear()
        polygon(hole, ellipse_pts(4, GROUND - 4, 14 + 22 * wet, 3 + 4 * wet, n=18), "#1a0f06")  # tanah basah
        polygon(hole, [(-14, GROUND), (0, GROUND + 5), (14, GROUND)], "#4a2f16", "#6a4526", 1)
        tick()
    water.clear()
    for k in range(10):  # turunkan gembor
        draw_farmer(farmer, wx, 1, can=40 - k * 4)
        tick()
    # petani pergi
    for k in range(60):
        x = wx - (wx + 520) * k / 59
        draw_farmer(farmer, x, -1, walk=k * 0.45, can=0)
        tick()
    farmer.clear()
    draw_seed(p, 0, SEED_Y, cracked=True)
    tick(25)
    return hole


def stage_roots(p, rnd):
    caption("2. Akar tumbuh ke dalam tanah", "#E0A060")
    layers, _, _ = build_tree(0, SEED_Y - 7, 270, 38, 4, 6, rnd, spread=(25, 50), shrink=(0.72, 0.86), max_y=GROUND - 8,
                              wshrink=0.75, colors=ROOT_COLORS)
    grow_layers(p, layers, steps=10)


def stage_sprout(p):
    caption("3. Tunas muncul ke permukaan", "#7CFC00")
    base = (0, SEED_Y + 6)
    top_y = GROUND + 55
    for k in range(1, 46):
        p.clear()
        y = base[1] + (top_y - base[1]) * min(1, k / 30)
        line(p, base, (2 * math.sin(k / 6), y), 5, "#6FBF3A")
        if k > 18:  # dua daun lembaga membuka
            s = min(1, (k - 18) / 16)
            for side in (-1, 1):
                pts = leaf_pts(0, y, 90 + side * 55, 30 * s, 10 * s)
                polygon(p, pts, "#5BD879", "#9CFF9C", 1)
        tick()
    tick(15)


def leaf_pts(x, y, heading, length, width, n=10):
    """Daun mangga: lonjong meruncing."""
    pts_l, pts_r = [], []
    a = math.radians(heading)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    for k in range(n + 1):
        u = k / n
        half = width / 2 * math.sin(math.pi * u) ** 0.8
        cx, cy = x + ux * length * u, y + uy * length * u
        pts_l.append((cx + vx * half, cy + vy * half))
        pts_r.append((cx - vx * half, cy - vy * half))
    return pts_l + pts_r[::-1]


def stage_trunk(p, sprout_pen, rnd):
    caption("4. Batang dan cabang tumbuh", "#D9A066")
    layers, tips, nodes = build_tree(0, GROUND, 90, 105, 26, 7, rnd, spread=(20, 34), shrink=(0.78, 0.88), upward=0.2,
                                     wshrink=0.66, colors=(TRUNK, TRUNK, "#8A5530", "#7B4A2A", "#6E4426"))
    # dua dahan besar tambahan di kiri & kanan batang -> sisi tajuk lebih rimbun
    for heading in (152, 28):
        sl, st, sn = build_tree(0, GROUND + 72, heading, 88, 15, 6, rnd, spread=(18, 32), shrink=(0.76, 0.86),
                                upward=0.12, wshrink=0.66, colors=(TRUNK, "#8A5530", "#7B4A2A", "#6E4426"))
        for d, layer in enumerate(sl):
            layers[d + 1].extend(layer)
        tips += st
        nodes += [(x, y, h, d + 1) for (x, y, h, d) in sn]
    # batang cokelat tumbuh dari tengah tunas hijau, menutupinya perlahan; tunas baru hilang setelah tertutup
    below = [[{"x": 0, "y": SEED_Y, "h": 90, "len": GROUND - SEED_Y, "w0": 6, "w": 26, "d": 0, "color": TRUNK}]]
    first = [[dict(s, w0=min(s["w0"], 8)) for s in layers[0]]]
    grow_layers(p, below + first, steps=18)
    grow_layers(p, layers[:1], steps=6)  # batang menebal menutup seluruh tunas
    sprout_pen.clear()
    grow_layers(p, layers[1:], steps=12)
    return tips, nodes


def stage_big_roots(p, rnd):
    caption("Akar ikut membesar menopang pohon", "#E0A060")
    # akar utama menjalar lebar ke samping (dangkal) + akar tunggang ke bawah
    mains = [(194, 100), (208, 92), (228, 75), (250, 55), (270, 65), (290, 55), (312, 75), (332, 92), (346, 100)]
    merged = []
    for heading, length in mains:
        layers, _, _ = build_tree(0, SEED_Y, heading + rnd.uniform(-5, 5), length * rnd.uniform(0.9, 1.1), 12, 4, rnd,
                                  spread=(14, 32), shrink=(0.62, 0.78), wshrink=0.6, max_children=2, max_y=GROUND - 8,
                                  colors=("#B07038", "#C8874A", "#D89A5A", "#E0A060"))
        for d, layer in enumerate(layers):
            if d >= len(merged):
                merged.append([])
            merged[d].extend(layer)
    grow_layers(p, merged, steps=9)


def stage_leaves(p, tips, nodes, rnd):
    caption("5. Daun tumbuh lebat", "#46C965")
    base = [(x, y, h) for (x, y, h, d) in nodes if d >= 2] + tips
    spots = []
    for (x, y, h) in base:  # tambah titik di sekitar tiap ranting supaya tajuk rimbun
        spots.append((x, y, h))
        for _ in range(2):  # daun menumpuk ke atas -> tajuk lebat menjulang
            spots.append((x + rnd.uniform(-22, 22), y + rnd.uniform(-8, 38), h + rnd.uniform(-40, 40)))
        if abs(x) > 60:  # sisi kiri-kanan tajuk: tambah daun ke samping & sedikit ke bawah
            side = 1 if x > 0 else -1
            for _ in range(3):
                spots.append((x + side * rnd.uniform(10, 40), y + rnd.uniform(-38, 10),
                              (0 if side > 0 else 180) + rnd.uniform(-50, 50)))
    rnd.shuffle(spots)
    dark = ["#0F4A24", "#145A2E", "#1A6B36"]
    for i, (x, y, h) in enumerate(spots):
        # lapisan belakang: daun gelap lebih besar mengisi celah tajuk
        for _ in range(2):
            ang = h + rnd.uniform(-90, 90)
            L = rnd.uniform(30, 42)
            polygon(p, leaf_pts(x, y, ang, L, L * 0.32, n=6), rnd.choice(dark))
        # lapisan depan: daun terang dengan tulang daun
        for _ in range(rnd.choice([3, 4, 5])):
            ang = h + rnd.uniform(-80, 80)
            L = rnd.uniform(24, 36)
            col = rnd.choice(LEAF_COLORS)
            polygon(p, leaf_pts(x, y, ang, L, L * 0.28, n=7), col)
            line(p, (x, y), polar(x, y, ang, L * 0.85), 1, "#9CFFB0")  # tulang daun
        if i % 40 == 0:
            tick()
    tick(8)


def stage_flowers(p, tips, nodes, rnd):
    caption("6. Bunga mangga bermekaran", "#FFE27A")
    chosen = list(tips) + [(x, y, h) for (x, y, h, d) in nodes if d >= 4 and rnd.random() < 0.6]
    rnd.shuffle(chosen)
    petals = []
    for i, (x, y, h) in enumerate(chosen):
        # malai bunga mangga: kerucut kecil berisi titik-titik
        for k in range(18):
            u = rnd.random()
            spread = 12 * (1 - u)
            fx = x + rnd.uniform(-spread, spread)
            fy = y + 4 + u * 26
            size, col = rnd.choice([4, 5, 6]), rnd.choice(FLOWER_COLORS)
            p.goto(fx, fy)
            p.dot(size, col)
            petals.append((fx, fy, size, col))
        if i % 2 == 0:
            tick()
    tick(40)
    return petals


def draw_mangoes(p, fruits, size_k, ripe_k):
    p.clear()
    for (x, y, rot) in fruits:
        stem_end = (x, y - 18 * min(1, size_k * 2))
        line(p, (x, y), stem_end, 2, "#6B4A2A")
        rx, ry = 13 * size_k, 20 * size_k
        if rx < 1:
            continue
        cy = stem_end[1] - ry
        body = mix(MANGO_RAW, MANGO_RIPE, ripe_k)
        polygon(p, ellipse_pts(stem_end[0], cy, rx, ry, rot=rot, bulge=0.18), hexc(body), "#203010", 1)
        if ripe_k > 0.05:  # semburat merah saat matang
            blush = mix(body, MANGO_BLUSH, 0.8 * ripe_k)
            polygon(p, ellipse_pts(stem_end[0] - rx * 0.35, cy + ry * 0.3, rx * 0.5, ry * 0.45, rot=rot),
                    hexc(blush))
        p.goto(stem_end[0] + rx * 0.35, cy + ry * 0.45)
        p.dot(max(2, int(4 * size_k)), "#FFFFFF")  # kilau


def stage_fruits(flower_pen, fruit_pen, flowers, tips, rnd):
    caption("7. Bunga menjadi buah mangga", "#9CFF5C")
    lower = sorted(tips, key=lambda t: t[1])  # pilih ujung cabang di bagian luar-bawah tajuk
    cand = lower[: max(26, len(lower) * 2 // 3)]
    rnd.shuffle(cand)
    fruits = [(x, y, rnd.uniform(-0.25, 0.25)) for (x, y, h) in cand[:26]]
    # bunga rontok tanpa layu: kelopak melayang dengan warna aslinya lalu berserakan di tanah
    allf = [(x, y, size, col) for (x, y, size, col) in flowers]
    falls, stays = [], []
    for (x, y, size, col) in allf:
        if rnd.random() < 0.3:
            falls.append({"x0": x, "y0": y, "size": size * 0.8, "col": col, "start": rnd.randint(0, 45),
                          "dur": rnd.randint(40, 70), "drift": rnd.uniform(-40, 40), "amp": rnd.uniform(5, 14),
                          "freq": rnd.uniform(0.15, 0.28), "phase": rnd.uniform(0, 6.28),
                          "land": GROUND + rnd.uniform(1, 7), "done": False})
        else:
            stays.append((x, y, size, col, rnd.randint(3, 60)))
    flower_pen.clear()
    branch, air = pen(), pen()
    for f in range(120):
        if f % 4 == 0:  # bunga di dahan yang tidak jatuh hilang satu per satu
            branch.clear()
            for (x, y, size, col, gone) in stays:
                if f < gone:
                    branch.goto(x, y)
                    branch.dot(size, col)
            for d in falls:
                if f < d["start"]:
                    branch.goto(d["x0"], d["y0"])
                    branch.dot(d["size"], d["col"])
        air.clear()
        for d in falls:
            if d["done"] or f < d["start"]:
                continue
            u = (f - d["start"]) / d["dur"]
            y = d["y0"] - (d["y0"] - d["land"]) * min(1.0, u ** 1.25)
            x = d["x0"] + d["drift"] * min(1.0, u) + d["amp"] * math.sin(f * d["freq"] + d["phase"]) * min(1.0, u * 4)
            if u >= 1:  # mendarat: berserakan warna-warni di tanah
                flower_pen.goto(x, d["land"])
                flower_pen.dot(d["size"], d["col"])
                d["done"] = True
                continue
            air.goto(x, y)
            air.dot(d["size"], d["col"])
        tick()
    branch.clear()
    air.clear()
    for k in range(1, 26):  # buah membesar
        draw_mangoes(fruit_pen, fruits, k / 25, 0.0)
        tick()
    tick(8)
    return fruits


def stage_ripen(fruit_pen, fruits):
    caption("8. Mangga matang, siap dipanen!", "#FFB020")
    for k in range(1, 31):
        draw_mangoes(fruit_pen, fruits, 1.0, k / 30)
        tick()


# ------------------------------------------------------------------ jalankan
pens = []


def run():
    for p in pens:
        p.clear()
    pens.clear()
    soil, roots, sprout, tree, leaves, flowers, fruits, seed = (pen() for _ in range(8))
    pens.extend([soil, roots, sprout, tree, leaves, flowers, fruits, seed, title_pen, cap_pen])
    rnd = random.Random(SEED)
    stage_soil(soil)
    mound = stage_seed(seed, rnd)
    stage_roots(roots, rnd)
    stage_sprout(sprout)
    mound.clear()
    tips, nodes = stage_trunk(tree, sprout, rnd)
    seed.clear()
    stage_big_roots(roots, rnd)
    stage_leaves(leaves, tips, nodes, rnd)
    fl = stage_flowers(flowers, tips, nodes, rnd)
    fr = stage_fruits(flowers, fruits, fl, tips, rnd)
    stage_ripen(fruits, fr)
    tick()


running = {"busy": False}


def replay():
    if running["busy"]:
        return
    running["busy"] = True
    try:
        run()
    finally:
        running["busy"] = False


screen.onkey(replay, "r")
screen.onkey(replay, "R")
screen.onkey(screen.bye, "q")
screen.onkey(screen.bye, "Q")
screen.listen()

if __name__ == "__main__":
    replay()
    screen.mainloop()
