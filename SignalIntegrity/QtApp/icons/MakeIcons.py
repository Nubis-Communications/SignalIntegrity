"""renders the SignalIntegrity Qt and Tauri app icons: a glowing eye diagram on a rounded gradient tile"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
# usage: python MakeIcons.py <output folder> qt|tauri  (needs Pillow and numpy)
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

S = 1024          # final size
SS = 2            # supersampling
N = S * SS

def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))

def gradient_tile(top, bottom, glow):
    y = np.linspace(0, 1, N)[:, None]
    x = np.linspace(0, 1, N)[None, :]
    t = np.clip(0.75 * y + 0.25 * x, 0, 1)
    img = np.zeros((N, N, 3))
    for c in range(3):
        img[..., c] = top[c] + (bottom[c] - top[c]) * t
    # soft radial light behind the eye
    r = np.sqrt((x - 0.5) ** 2 + (y - 0.47) ** 2)
    light = np.clip(1 - r / 0.55, 0, 1) ** 2
    for c in range(3):
        img[..., c] = img[..., c] * (1 - 0.55 * light) + glow[c] * 0.55 * light
    return Image.fromarray(img.astype(np.uint8), 'RGB')

def rounded_mask(radius_fraction=0.225, inset=0.035):
    m = Image.new('L', (N, N), 0)
    d = ImageDraw.Draw(m)
    i = int(N * inset)
    d.rounded_rectangle([i, i, N - i - 1, N - i - 1], radius=int(N * radius_fraction), fill=255)
    return m

def eye_density(levels=2, traces=900, seed=3):
    """accumulates many random bit sequences, two unit intervals wide, into a density map"""
    rng = np.random.default_rng(seed)
    x0, x1 = 0.12 * N, 0.88 * N
    yc, amp = 0.50 * N, 0.205 * N
    lv = np.linspace(-1, 1, levels)
    ui = (x1 - x0) / 2
    acc = Image.new('L', (N, N), 0)
    layer = Image.new('L', (N, N), 0)
    for _ in range(traces):
        bits = rng.integers(0, levels, 6)
        # inter-symbol interference: each settled level remembers the previous symbol
        settled = [lv[bits[i]] - 0.16 * (lv[bits[i]] - lv[bits[i - 1]]) * (rng.random() ** 0.5) for i in range(1, 6)]
        shifts = rng.normal(0, 0.045, 6)
        pts = []
        for k in range(241):
            u = k / 240 * 2 - 0.5            # from -0.5 UI to 1.5 UI
            seg = int(np.floor(u + 0.5 - shifts[int(np.floor(u + 0.5)) + 1]))
            seg = min(max(seg, 0), 2)
            frac = u + 0.5 - seg - shifts[seg + 1]
            a, b = settled[seg], settled[seg + 1]
            s = 0.5 - 0.5 * math.cos(math.pi * min(max((frac - 0.5) * 1.45 + 0.5, 0), 1))
            v = a + (b - a) * s + rng.normal(0, 0.012)
            pts.append((x0 + (u + 0.5) * ui, yc - v * amp))
        layer.paste(0, [0, 0, N, N])
        ImageDraw.Draw(layer).line(pts, fill=6, width=int(4 * SS), joint='curve')
        acc = ImageChops.add(acc, layer)
    return acc

def colorize(density, stops):
    d = np.asarray(density, dtype=float) / 255.
    d = np.clip(d * 1.6, 0, 1) ** 0.65
    out = np.zeros(d.shape + (3,))
    xs = [s[0] for s in stops]
    for c in range(3):
        out[..., c] = np.interp(d, xs, [s[1][c] for s in stops])
    alpha = np.clip(d * 2.5, 0, 1)
    return Image.fromarray(out.astype(np.uint8), 'RGB'), Image.fromarray((alpha * 255).astype(np.uint8), 'L')

def make_icon(path_png, path_ico, top, bottom, glow, stops, levels, accent):
    tile = gradient_tile(top, bottom, glow).convert('RGBA')
    # faint oscilloscope graticule
    grid = Image.new('L', (N, N), 0)
    g = ImageDraw.Draw(grid)
    for k in range(1, 10):
        p = int(N * (0.1 + 0.08 * k))
        g.line([(p, int(N * .14)), (p, int(N * .86))], fill=26, width=SS * 2)
        g.line([(int(N * .14), p), (int(N * .86), p)], fill=26, width=SS * 2)
    tile = Image.composite(Image.new('RGBA', (N, N), (255, 255, 255, 255)), tile, grid)
    density = eye_density(levels)
    rgb, alpha = colorize(density, stops)
    glowlayer = rgb.filter(ImageFilter.GaussianBlur(N * 0.018))
    glowalpha = alpha.filter(ImageFilter.GaussianBlur(N * 0.018)).point(lambda v: int(v * 0.9))
    tile = Image.composite(glowlayer.convert('RGBA'), tile, glowalpha)
    tile = Image.composite(rgb.convert('RGBA'), tile, alpha)
    # glossy highlight on the upper half
    gloss = Image.new('L', (N, N), 0)
    ImageDraw.Draw(gloss).ellipse([-N * .35, -N * 1.05, N * 1.35, N * .30], fill=26)
    gloss = gloss.filter(ImageFilter.GaussianBlur(N * 0.08))
    tile = Image.composite(Image.new('RGBA', (N, N), (255, 255, 255, 255)), tile, gloss)
    # accent rim
    rim = Image.new('L', (N, N), 0)
    i = int(N * 0.035)
    ImageDraw.Draw(rim).rounded_rectangle([i, i, N - i - 1, N - i - 1], radius=int(N * .225), outline=200, width=int(N * .010))
    tile = Image.composite(Image.new('RGBA', (N, N), accent + (255,)), tile, rim.filter(ImageFilter.GaussianBlur(SS)))
    mask = rounded_mask()
    out = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    out.paste(tile, (0, 0), mask)
    # drop shadow
    shadow = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    sh = mask.filter(ImageFilter.GaussianBlur(N * 0.015)).point(lambda v: int(v * 0.45))
    shadow.paste((0, 0, 0, 255), (0, int(N * 0.01)), sh)
    final = Image.alpha_composite(shadow, out).resize((S, S), Image.LANCZOS)
    os.makedirs(os.path.dirname(path_png), exist_ok=True)
    final.save(path_png)
    if path_ico:
        final.save(path_ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    return final

if __name__ == '__main__':
    target = sys.argv[1]
    which = sys.argv[2]
    if which == 'qt':
        # emerald/teal tile with a cyan-to-white hot eye
        make_icon(os.path.join(target, 'SignalIntegrityQt.png'), os.path.join(target, 'SignalIntegrityQt.ico'),
                  top=(4, 38, 46), bottom=(6, 112, 96), glow=(20, 190, 170),
                  stops=[(0, (0, 140, 160)), (0.35, (40, 230, 220)), (0.7, (180, 255, 240)), (1, (255, 255, 255))],
                  levels=2, accent=(120, 255, 220))
    else:
        # indigo/violet tile with an amber-to-white hot eye
        make_icon(os.path.join(target, 'app-icon.png'), None,
                  top=(20, 14, 58), bottom=(92, 30, 150), glow=(170, 70, 230),
                  stops=[(0, (180, 60, 20)), (0.35, (255, 150, 40)), (0.7, (255, 225, 150)), (1, (255, 255, 255))],
                  levels=2, accent=(255, 190, 90))
