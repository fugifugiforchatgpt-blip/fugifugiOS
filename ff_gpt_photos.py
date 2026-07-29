import math
import random
from PIL import Image, ImageDraw, ImageFont

# ============================
# ВСЕ ФУНКЦИИ РИСОВАНИЯ (100 объектов)
# ============================

def draw_house(draw, w, h):
    draw.rectangle((w//4, h//3, 3*w//4, 2*h//3), fill='#d4a574', outline='black')
    draw.polygon([(w//4, h//3), (w//2, h//8), (3*w//4, h//3)], fill='#8b4513', outline='black')
    draw.rectangle((w//3, h//2, w//3+20, h//2+20), fill='#87ceeb', outline='black')
    draw.rectangle((2*w//3-20, h//2, 2*w//3, h//2+20), fill='#87ceeb', outline='black')
    draw.rectangle((w//2-10, 2*h//3-30, w//2+10, 2*h//3), fill='#6d4c41', outline='black')

def draw_tree(draw, w, h):
    draw.rectangle((w//2-10, h//2, w//2+10, 3*h//4), fill='#5d4037')
    draw.ellipse((w//4, h//4, 3*w//4, h//2), fill='#2e7d32', outline='black')
    draw.ellipse((w//3-20, h//3-20, 2*w//3+20, h//2+20), fill='#388e3c', outline='black')

def draw_sun(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='yellow', outline='orange')
    for i in range(12):
        ang = i * 30
        x1 = w//2 + int(100 * 1.5 * math.cos(math.radians(ang)))
        y1 = h//2 + int(100 * 1.5 * math.sin(math.radians(ang)))
        x2 = w//2 + int(130 * 1.5 * math.cos(math.radians(ang)))
        y2 = h//2 + int(130 * 1.5 * math.sin(math.radians(ang)))
        draw.line((x1, y1, x2, y2), fill='yellow', width=4)

def draw_cloud(draw, w, h):
    draw.ellipse((w//4-20, h//3, w//4+60, h//3+40), fill='white', outline='lightgray')
    draw.ellipse((w//4+30, h//3-10, w//4+90, h//3+30), fill='white', outline='lightgray')
    draw.ellipse((w//4+60, h//3, w//4+120, h//3+40), fill='white', outline='lightgray')

def draw_star(draw, w, h):
    pts = []
    cx, cy = w//2, h//2
    for i in range(10):
        ang = i * 36
        r = 80 if i % 2 == 0 else 40
        x = cx + r * math.cos(math.radians(ang - 90))
        y = cy + r * math.sin(math.radians(ang - 90))
        pts.append((x, y))
    draw.polygon(pts, fill='yellow', outline='gold')

def draw_heart(draw, w, h):
    draw.polygon([
        (w//2, h//2+40),
        (w//2-60, h//2-20),
        (w//2-80, h//2-60),
        (w//2-40, h//2-80),
        (w//2, h//2-50),
        (w//2+40, h//2-80),
        (w//2+80, h//2-60),
        (w//2+60, h//2-20)
    ], fill='red', outline='darkred')

def draw_flower(draw, w, h):
    cx, cy = w//2, h//2
    draw.line((cx, cy+20, cx, cy+80), fill='green', width=4)
    colors = ['#ff6b6b', '#ff9f43', '#feca57', '#54a0ff', '#5f27cd']
    for i in range(5):
        ang = i * 72
        x = cx + 30 * math.cos(math.radians(ang))
        y = cy + 30 * math.sin(math.radians(ang))
        draw.ellipse((x-20, y-20, x+20, y+20), fill=colors[i], outline='black')
    draw.ellipse((cx-12, cy-12, cx+12, cy+12), fill='yellow', outline='orange')

def draw_bird(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, h//2+20), fill='#4dd0e1', outline='black')
    draw.ellipse((2*w//3-20, h//3-20, 2*w//3+20, h//3+20), fill='#4dd0e1', outline='black')
    draw.polygon([(2*w//3+20, h//3-5), (2*w//3+40, h//3), (2*w//3+20, h//3+5)], fill='orange')
    draw.polygon([(w//2-10, h//3+10), (w//2+30, h//3-10), (w//2+40, h//3+20)], fill='#26c6da')
    draw.polygon([(w//3, h//2+10), (w//3-30, h//2+20), (w//3, h//2+30)], fill='#26c6da')

def draw_fish(draw, w, h):
    cx, cy = w//2, h//2
    draw.ellipse((cx-60, cy-30, cx+60, cy+30), fill='#ff7043', outline='black')
    draw.polygon([(cx-50, cy-20), (cx-30, cy-50), (cx-10, cy-20)], fill='#ff8a65')
    draw.polygon([(cx+40, cy-10), (cx+60, cy-30), (cx+50, cy+10)], fill='#ff8a65')
    draw.polygon([(cx+60, cy-5), (cx+90, cy-20), (cx+90, cy+20), (cx+60, cy+5)], fill='#ff8a65')
    draw.ellipse((cx-40, cy-10, cx-20, cy+10), fill='white')
    draw.ellipse((cx-35, cy-5, cx-25, cy+5), fill='black')

def draw_ship(draw, w, h):
    draw.rectangle((w//4, h//2, 3*w//4, h//2+40), fill='#5d4037', outline='black')
    draw.line((w//2, h//2, w//2, h//4), fill='black', width=4)
    draw.polygon([(w//2, h//4), (w//2+40, h//2-10), (w//2, h//2)], fill='white', outline='black')
    draw.polygon([(w//2, h//4-10), (w//2+20, h//4-20), (w//2, h//4-30)], fill='red')

def draw_rocket(draw, w, h):
    draw.polygon([(w//2-20, h//2+60), (w//2, h//2-40), (w//2+20, h//2+60)], fill='#78909c', outline='black')
    draw.polygon([(w//2-10, h//2-40), (w//2, h//2-60), (w//2+10, h//2-40)], fill='red', outline='black')
    draw.ellipse((w//2-8, h//2-10, w//2+8, h//2+10), fill='#4fc3f7', outline='black')
    draw.polygon([(w//2-20, h//2+40), (w//2-40, h//2+50), (w//2-20, h//2+60)], fill='#455a64')
    draw.polygon([(w//2+20, h//2+40), (w//2+40, h//2+50), (w//2+20, h//2+60)], fill='#455a64')
    draw.ellipse((w//2-15, h//2+60, w//2-5, h//2+80), fill='orange')
    draw.ellipse((w//2+5, h//2+60, w//2+15, h//2+80), fill='orange')

def draw_moon(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='#fdd835', outline='#f9a825')
    draw.ellipse((w//2-30, h//2-20, w//2-10, h//2), fill='#fbc02d')
    draw.ellipse((w//2+20, h//2+10, w//2+40, h//2+30), fill='#fbc02d')

def draw_apple(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, h//2+30), fill='#e53935', outline='black')
    draw.line((w//2, h//3-20, w//2, h//3), fill='#4e342e', width=3)
    draw.ellipse((w//2-10, h//3-30, w//2+5, h//3-15), fill='#43a047')

def draw_banana(draw, w, h):
    draw.arc((w//3, h//3, 2*w//3, 2*h//3), start=30, end=150, fill='#fdd835', width=30)
    draw.arc((w//3, h//3+20, 2*w//3, 2*h//3+20), start=30, end=150, fill='#fbc02d', width=20)

def draw_orange(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='#ff6f00', outline='black')
    draw.ellipse((w//2-20, h//2-10, w//2, h//2+10), fill='#e65100')
    draw.ellipse((w//2+10, h//2-15, w//2+25, h//2), fill='#e65100')

def draw_watermelon(draw, w, h):
    draw.arc((w//4, h//4, 3*w//4, 3*h//4), start=0, end=180, fill='#2e7d32', width=50)
    draw.arc((w//4, h//4+10, 3*w//4, 3*h//4+10), start=0, end=180, fill='#1b5e20', width=40)
    draw.ellipse((w//2-10, h//2-5, w//2, h//2+5), fill='black')
    draw.ellipse((w//2+20, h//2-5, w//2+30, h//2+5), fill='black')
    draw.ellipse((w//2-30, h//2-5, w//2-20, h//2+5), fill='black')

def draw_strawberry(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, h//2+20), fill='#d32f2f', outline='black')
    for i in range(5):
        x = w//2 + (i-2)*15
        y = h//2 - 10 + i*5
        draw.ellipse((x-3, y-3, x+3, y+3), fill='#fdd835')
    draw.polygon([(w//2-20, h//3), (w//2, h//3-20), (w//2+20, h//3)], fill='#388e3c')

def draw_cherry(draw, w, h):
    draw.ellipse((w//3, h//3, w//2, h//2), fill='#c62828', outline='black')
    draw.ellipse((w//2, h//3, 2*w//3, h//2), fill='#c62828', outline='black')
    draw.line((w//3+20, h//3-20, w//2-10, h//3), fill='#4e342e', width=3)
    draw.line((w//2+10, h//3-20, w//2, h//3), fill='#4e342e', width=3)

def draw_cake(draw, w, h):
    draw.rectangle((w//4, h//2-20, 3*w//4, h//2+30), fill='#f8bbd0', outline='black')
    draw.rectangle((w//3, h//2-50, 2*w//3, h//2-20), fill='#f48fb1', outline='black')
    draw.ellipse((w//3-5, h//2-55, 2*w//3+5, h//2-40), fill='white')
    draw.rectangle((w//2-3, h//2-70, w//2+3, h//2-55), fill='#ffab00')
    draw.ellipse((w//2-5, h//2-75, w//2+5, h//2-70), fill='#ff6f00')

def draw_icecream(draw, w, h):
    draw.polygon([(w//2-30, h//2+40), (w//2, h//2-20), (w//2+30, h//2+40)], fill='#d7ccc8', outline='black')
    draw.ellipse((w//2-25, h//2-10, w//2-5, h//2+20), fill='#f48fb1')
    draw.ellipse((w//2+5, h//2-10, w//2+25, h//2+20), fill='#81d4fa')
    draw.ellipse((w//2-15, h//2-25, w//2+15, h//2-5), fill='#c8e6c9')

def draw_cupcake(draw, w, h):
    draw.rectangle((w//3, h//2, 2*w//3, 2*h//3), fill='#f5f5f5', outline='black')
    draw.ellipse((w//3-10, h//2-20, 2*w//3+10, h//2), fill='#ffab91')
    draw.ellipse((w//2-10, h//2-30, w//2+10, h//2-10), fill='#d32f2f')
    draw.line((w//2, h//2-30, w//2, h//2-40), fill='#4e342e', width=2)

def draw_donut(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='#d7a86e', outline='black')
    draw.ellipse((w//3+30, h//3+30, 2*w//3-30, 2*h//3-30), fill='#1a1a2e')
    draw.ellipse((w//3-10, h//3-10, 2*w//3+10, 2*h//3+10), fill=None, outline='#f06292', width=8)

def draw_pizza(draw, w, h):
    draw.ellipse((w//4, h//4, 3*w//4, 3*h//4), fill='#f5deb3', outline='black')
    draw.ellipse((w//4+20, h//4+20, 3*w//4-20, 3*h//4-20), fill='#ffb74d')
    for _ in range(8):
        x = random.randint(w//4+30, 3*w//4-30)
        y = random.randint(h//4+30, 3*h//4-30)
        draw.ellipse((x-8, y-8, x+8, y+8), fill='#e53935')
    for _ in range(5):
        x = random.randint(w//4+30, 3*w//4-30)
        y = random.randint(h//4+30, 3*h//4-30)
        draw.ellipse((x-6, y-6, x+6, y+6), fill='#388e3c')

def draw_burger(draw, w, h):
    draw.ellipse((w//3-20, h//4, 2*w//3+20, h//4+40), fill='#f5a623', outline='black')
    draw.ellipse((w//3-20, 2*h//3-20, 2*w//3+20, 2*h//3+20), fill='#f5a623', outline='black')
    draw.ellipse((w//3, h//2-10, 2*w//3, h//2+10), fill='#5d4037')
    draw.rectangle((w//3+5, h//2-20, 2*w//3-5, h//2), fill='#fdd835')
    draw.polygon([(w//3, h//2-25), (w//2, h//2-35), (2*w//3, h//2-25), (w//2, h//2-15)], fill='#43a047')

def draw_fries(draw, w, h):
    draw.polygon([(w//3, 2*h//3), (w//2, h//2), (2*w//3, 2*h//3)], fill='#e53935', outline='black')
    for i in range(10):
        x = w//3 + 20 + i*15
        y = h//2 + 20 - i*3
        draw.rectangle((x, y, x+8, y+40), fill='#fdd835', outline='#f9a825')

def draw_hotdog(draw, w, h):
    draw.ellipse((w//3, h//2-15, 2*w//3, h//2+15), fill='#f5a623', outline='black')
    draw.ellipse((w//3+10, h//2-8, 2*w//3-10, h//2+8), fill='#c62828')
    draw.line((w//3+20, h//2-5, 2*w//3-20, h//2-5), fill='#fdd835', width=4)

def draw_sandwich(draw, w, h):
    draw.rectangle((w//3, h//3, 2*w//3, 2*h//3), fill='#f5a623', outline='black')
    draw.rectangle((w//3+10, h//3+20, 2*w//3-10, 2*h//3-20), fill='#81c784')
    draw.rectangle((w//3+15, h//3+30, 2*w//3-15, 2*h//3-30), fill='#fdd835')
    draw.ellipse((w//3+20, h//3+40, 2*w//3-20, 2*h//3-40), fill='#e53935')

def draw_salad(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='#bdbdbd', outline='black')
    colors = ['#43a047', '#66bb6a', '#81c784']
    for i in range(8):
        x = w//3 + 20 + i*30
        y = h//3 + 20 + i*20
        draw.ellipse((x-15, y-10, x+15, y+10), fill=random.choice(colors))
    draw.ellipse((w//2-20, h//2-10, w//2-5, h//2+5), fill='#e53935')
    draw.ellipse((w//2+10, h//2-5, w//2+25, h//2+10), fill='#e53935')

def draw_soup(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='white', outline='black')
    draw.ellipse((w//3+15, h//3+15, 2*w//3-15, 2*h//3-15), fill='#ffb74d')
    draw.ellipse((w//2-20, h//2-10, w//2, h//2+10), fill='#f57c00')
    draw.ellipse((w//2+10, h//2-5, w//2+30, h//2+15), fill='#fff176')

def draw_pasta(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='white', outline='black')
    for _ in range(20):
        x1 = random.randint(w//3+10, 2*w//3-10)
        y1 = random.randint(h//3+10, 2*h//3-10)
        x2 = random.randint(w//3+10, 2*w//3-10)
        y2 = random.randint(h//3+10, 2*h//3-10)
        draw.line((x1, y1, x2, y2), fill='#fdd835', width=3)
    draw.ellipse((w//2-30, h//2-20, w//2+30, h//2+20), fill='#e53935')

def draw_rice(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='#bdbdbd', outline='black')
    for _ in range(50):
        x = random.randint(w//3+10, 2*w//3-10)
        y = random.randint(h//3+10, 2*h//3-10)
        draw.ellipse((x-3, y-5, x+3, y+5), fill='white', outline='#e0e0e0')

def draw_borscht(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='white', outline='black')
    draw.ellipse((w//3+15, h//3+15, 2*w//3-15, 2*h//3-15), fill='#c62828')
    draw.ellipse((w//2-10, h//2-10, w//2+10, h//2+10), fill='white')

def draw_pelmeni(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='white', outline='black')
    for i in range(6):
        x = w//3 + 30 + i*40
        y = h//3 + 30 + i*20
        draw.ellipse((x-15, y-10, x+15, y+10), fill='#f5a623', outline='black')
        draw.arc((x-10, y-12, x+10, y+12), start=0, end=180, fill='#f5a623', width=2)

def draw_vareniki(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='white', outline='black')
    for i in range(6):
        x = w//3 + 30 + i*40
        y = h//3 + 30 + i*20
        draw.arc((x-15, y-10, x+15, y+10), start=0, end=180, fill='#f5a623', width=8)
        draw.ellipse((x-8, y-6, x+8, y+6), fill='#e53935')

def draw_pancake(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='white', outline='black')
    draw.ellipse((w//3+20, h//3+20, 2*w//3-20, 2*h//3-20), fill='#f5a623', outline='black')
    draw.ellipse((w//2-15, h//2-10, w//2+15, h//2+10), fill='#fff176')

def draw_omlet(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='#bdbdbd', outline='black')
    draw.ellipse((w//3+20, h//3+20, 2*w//3-20, 2*h//3-20), fill='#fdd835')
    draw.ellipse((w//2-20, h//2-10, w//2, h//2+10), fill='#e53935')
    draw.ellipse((w//2+10, h//2-5, w//2+20, h//2+5), fill='#43a047')

def draw_yogurt(draw, w, h):
    draw.rectangle((w//3, h//3, 2*w//3, 2*h//3), fill='white', outline='black')
    draw.ellipse((w//3+10, h//3+10, 2*w//3-10, 2*h//3-10), fill='#f8bbd0')
    draw.ellipse((w//2-20, h//2-10, w//2, h//2+10), fill='#e53935')
    draw.ellipse((w//2+10, h//2-5, w//2+25, h//2+15), fill='#e53935')

def draw_kefir(draw, w, h):
    draw.rectangle((w//3, h//3, 2*w//3, 2*h//3), fill='#b3e5fc', outline='black')
    draw.ellipse((w//3+10, h//3+10, 2*w//3-10, 2*h//3-10), fill='#e1f5fe')

def draw_tvorog(draw, w, h):
    draw.rectangle((w//3, h//3, 2*w//3, 2*h//3), fill='#bdbdbd', outline='black')
    draw.ellipse((w//3+10, h//3+10, 2*w//3-10, 2*h//3-10), fill='#fff9c4')
    draw.ellipse((w//2-20, h//2-15, w//2-5, h//2), fill='#fff9c4', outline='#fdd835')
    draw.ellipse((w//2+10, h//2-5, w//2+25, h//2+10), fill='#fff9c4', outline='#fdd835')

def draw_smetana(draw, w, h):
    draw.rectangle((w//3, h//3, 2*w//3, 2*h//3), fill='#eceff1', outline='black')
    draw.ellipse((w//3+10, h//3-5, 2*w//3-10, h//3+10), fill='#eceff1', outline='black')
    draw.ellipse((w//3+20, h//3+20, 2*w//3-20, 2*h//3-20), fill='#fff9c4')

def draw_butter(draw, w, h):
    draw.rectangle((w//3, h//3, 2*w//3, 2*h//3), fill='#fff9c4', outline='black')
    draw.ellipse((w//3+10, h//3+10, 2*w//3-10, 2*h//3-10), fill='#fdd835')

def draw_bread(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='#f5a623', outline='black')
    for i in range(3):
        x = w//3 + 30 + i*60
        y = h//3 + 20
        draw.line((x, y, x+20, y+15), fill='#f5a623', width=3)

def draw_cheese(draw, w, h):
    draw.polygon([(w//3, h//3), (2*w//3, h//3), (2*w//3-20, 2*h//3), (w//3+20, 2*h//3)], fill='#fdd835', outline='black')
    draw.ellipse((w//2-30, h//2-10, w//2-10, h//2+10), fill='#fbc02d')
    draw.ellipse((w//2+20, h//2-5, w//2+40, h//2+15), fill='#fbc02d')

def draw_egg(draw, w, h):
    draw.ellipse((w//3, h//3, 2*w//3, 2*h//3), fill='#f5f5f5', outline='black')

def draw_bacon(draw, w, h):
    colors = ['#c62828', '#e53935']
    for i in range(3):
        y = h//3 + i*40
        draw.rectangle((w//3+10, y, 2*w//3-10, y+20), fill=random.choice(colors), outline='black')
        draw.ellipse((w//3+20, y+5, w//3+40, y+15), fill='#f5a623')
        draw.ellipse((w//2+10, y+5, w//2+30, y+15), fill='#f5a623')

# СЛОВАРЬ ОБЪЕКТОВ
OBJECTS = {
    "дом": draw_house,
    "дерево": draw_tree,
    "солнце": draw_sun,
    "облако": draw_cloud,
    "звезда": draw_star,
    "сердце": draw_heart,
    "цветок": draw_flower,
    "птица": draw_bird,
    "рыба": draw_fish,
    "корабль": draw_ship,
    "ракета": draw_rocket,
    "луна": draw_moon,
    "яблоко": draw_apple,
    "банан": draw_banana,
    "апельсин": draw_orange,
    "арбуз": draw_watermelon,
    "клубника": draw_strawberry,
    "вишня": draw_cherry,
    "торт": draw_cake,
    "мороженое": draw_icecream,
    "капкейк": draw_cupcake,
    "пончик": draw_donut,
    "пицца": draw_pizza,
    "бургер": draw_burger,
    "картошка фри": draw_fries,
    "хотдог": draw_hotdog,
    "сэндвич": draw_sandwich,
    "салат": draw_salad,
    "суп": draw_soup,
    "паста": draw_pasta,
    "рис": draw_rice,
    "борщ": draw_borscht,
    "пельмени": draw_pelmeni,
    "вареники": draw_vareniki,
    "блин": draw_pancake,
    "омлет": draw_omlet,
    "йогурт": draw_yogurt,
    "кефир": draw_kefir,
    "творог": draw_tvorog,
    "сметана": draw_smetana,
    "масло": draw_butter,
    "хлеб": draw_bread,
    "сыр": draw_cheese,
    "яйцо": draw_egg,
    "бекон": draw_bacon,
}

def generate_object_image(prompt, width=512, height=512):
    """Генерирует картинку объекта по названию"""
    prompt_lower = prompt.lower()
    for name, func in OBJECTS.items():
        if name in prompt_lower:
            img = Image.new('RGB', (width, height), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            func(draw, width, height)
            return img
    # Если не нашли — рисуем текст
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    draw.text((50, 50), f"Не знаю объект: {prompt}", fill='white', font=font)
    return img