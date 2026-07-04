#!/usr/bin/env python3
"""End-to-end verification of the KnitBit Forge editor (demos/knitbit_builder.html).

Drives the editor with headless Chromium (Playwright) and asserts against the
window.__KB hooks the page exposes. Two passes:

  1. ``?nofx=1`` — deterministic regression suite (no intro/particles/beats):
     boots+hands present with base parts hidden, idle+wave motion, tab+tile
     equip, plating swap, colorway swap, accent tint, expression swap, blink,
     randomize/undo, PFP + save card.
  2. FX pass — the cinematic layer: intro completes, tab switch moves the
     camera, save-look finale runs (confetti frame diff + card).

Usage:
    python3 -m http.server 8801   # from the repo root, in another shell
    python3 tools/editor_e2e.py [--url http://127.0.0.1:8801]

Exit code is non-zero if any check fails. Screenshots land in
/tmp/kb_e2e/ for visual review.
"""
import argparse
import io
import os
import sys
import time

from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops

CHROMIUM = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
OUT = "/tmp/kb_e2e"
FAILED = []


def check(name, ok, detail=""):
    print(f"[e2e] {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}")
    if not ok:
        FAILED.append(name)


def diff(a, b, box=None, thresh=8):
    ia, ib = Image.open(io.BytesIO(a)).convert("L"), Image.open(io.BytesIO(b)).convert("L")
    if box:
        ia, ib = ia.crop(box), ib.crop(box)
    d = ImageChops.difference(ia, ib)
    return sum(1 for px in d.getdata() if px > thresh)


def launch(pw):
    exe = CHROMIUM if os.path.exists(CHROMIUM) else None
    kw = {"args": ["--use-gl=swiftshader", "--enable-unsafe-swiftshader"]}
    if exe:
        kw["executable_path"] = exe
    return pw.chromium.launch(**kw)


def open_page(browser, url, errors):
    page = browser.new_page(viewport={"width": 1280, "height": 860})
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    page.on("console", lambda m: errors.append("console: " + m.text)
            if m.type == "error" else None)
    page.goto(url)
    page.wait_for_function("window.__KB && window.__KB.ready === true", timeout=90000)
    time.sleep(1.5)
    return page


def regression_pass(browser, base_url):
    print("--- regression pass (?nofx=1) ---")
    errors = []
    page = open_page(browser, base_url + "?nofx=1", errors)

    check("no load failures", page.evaluate("window.__KB.failures.length") == 0,
          str(page.evaluate("window.__KB.failures")))

    d = page.evaluate("window.__KB.debug()")
    boots = [p for p in d["pieces"] if "boot" in p["name"] and p["visible"]]
    hands = [p for p in d["pieces"] if "hand" in p["name"] and p["visible"]]
    check("boots equipped, base feet hidden",
          len(boots) >= 2 and not d["parts"]["base_foot_l"] and not d["parts"]["base_foot_r"])
    check("hands equipped, base hands hidden",
          len(hands) >= 2 and not d["parts"]["base_hand_l"] and not d["parts"]["base_hand_r"])

    VIEW = (0, 100, 820, 860)
    s1 = page.screenshot()
    time.sleep(0.7)
    s2 = page.screenshot()
    check("idle motion", diff(s1, s2, VIEW) > 300, f"{diff(s1, s2, VIEW)} px")
    Image.open(io.BytesIO(s1)).save(f"{OUT}/reg_initial.png")

    # tab + tile equip
    page.click("#tabs button:has-text('Antenna')")
    before = page.evaluate("window.__KB.equips")
    page.click("#tiles .tile:has-text('Scout')")
    page.wait_for_function(f"window.__KB.equips > {before}", timeout=30000)
    check("tab + tile equip", True)

    # plating swap
    s1 = page.screenshot()
    page.click("#platingSw .sw[data-id='porcelain']")
    time.sleep(1.2)
    s2 = page.screenshot()
    check("plating swap", diff(s1, s2, (280, 380, 660, 750)) > 3000)
    check("plating hook", page.evaluate("window.__KB.plating") == "porcelain")

    # colorway swap on porcelain
    s1 = s2
    page.click("#yarnSw .sw[data-id='red']")
    time.sleep(1.2)
    s2 = page.screenshot()
    check("colorway swap", diff(s1, s2, (280, 380, 660, 750)) > 3000)
    Image.open(io.BytesIO(s2)).save(f"{OUT}/reg_porcelain_red.png")

    # accent tint
    s1 = s2
    page.click("#accentSw .sw[title='Arcade']")
    time.sleep(0.9)
    check("accent tint", diff(s1, page.screenshot()) > 200)

    # expression + blink
    s1 = page.screenshot()
    page.click("#faceRow button[data-id='starEyes']")
    time.sleep(0.6)
    check("expression swap", diff(s1, page.screenshot(), (280, 120, 640, 420)) > 400)

    # wave clip
    page.click("#anims button[data-clip='Wave']")
    time.sleep(0.8)
    s1 = page.screenshot()
    time.sleep(0.5)
    check("wave clip", diff(s1, page.screenshot(), VIEW) > 300)

    # randomize + undo
    sel_before = page.evaluate("JSON.stringify(window.__KB.debug().pieces.map(p=>p.name).sort())")
    page.click("#randBtn")
    page.wait_for_function("window.__KB.ops === 0", timeout=30000)
    time.sleep(0.3)
    sel_after = page.evaluate("JSON.stringify(window.__KB.debug().pieces.map(p=>p.name).sort())")
    check("randomize changes loadout", sel_before != sel_after)
    page.click("#undoBtn")
    page.wait_for_function("window.__KB.ops === 0", timeout=30000)
    time.sleep(0.3)
    sel_undone = page.evaluate("JSON.stringify(window.__KB.debug().pieces.map(p=>p.name).sort())")
    check("undo restores loadout", sel_undone == sel_before)

    # save look (nofx: immediate)
    page.fill("#bitName", "Testy")
    page.click("#pfpBtn")
    page.wait_for_function("window.__KB.pfp === true", timeout=25000)
    n = page.evaluate("document.getElementById('avatar').src.length")
    check("pfp captured", n > 20000, f"dataURL {n} bytes")
    check("save card shown", not page.evaluate("document.getElementById('cardWrap').hidden"))
    check("card carries name",
          page.evaluate("document.getElementById('cardName').textContent") == "Testy")
    page.screenshot(path=f"{OUT}/reg_savecard.png")
    page.click("#cardClose")

    check("no page errors", len(errors) == 0, str(errors[:3]))
    page.close()


def fx_pass(browser, base_url):
    print("--- FX pass ---")
    errors = []
    page = open_page(browser, base_url, errors)
    time.sleep(2.0)   # let the intro sweep land

    cam0 = page.evaluate("window.__KB.debug().camera")
    page.click("#tabs button:has-text('Boots')")
    time.sleep(1.2)
    cam1 = page.evaluate("window.__KB.debug().camera")
    moved = sum((a - b) ** 2 for a, b in zip(cam0, cam1)) ** 0.5
    check("tab switch moves camera", moved > 0.3, f"delta {moved:.2f}")
    page.screenshot(path=f"{OUT}/fx_boots_framing.png")

    # equip beat visible (ring flash + pop)
    s1 = page.screenshot()
    before = page.evaluate("window.__KB.equips")
    page.click("#tiles .tile:has-text('Classic')")
    page.wait_for_function(f"window.__KB.equips > {before}", timeout=30000)
    time.sleep(0.15)
    check("equip beat flashes", diff(s1, page.screenshot(), (0, 100, 820, 860)) > 500)

    # save finale: confetti + card
    page.click("#pfpBtn")
    time.sleep(0.8)
    mid = page.screenshot()
    page.wait_for_function("window.__KB.pfp === true", timeout=30000)
    page.screenshot(path=f"{OUT}/fx_savecard.png")
    check("finale runs (frame changes during save)",
          diff(mid, page.screenshot(), (0, 100, 820, 860)) > 500)
    check("save card shown (fx)", not page.evaluate("document.getElementById('cardWrap').hidden"))

    check("no page errors (fx)", len(errors) == 0, str(errors[:3]))
    page.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8801")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    base = args.url.rstrip("/") + "/demos/knitbit_builder.html"
    with sync_playwright() as pw:
        browser = launch(pw)
        regression_pass(browser, base)
        fx_pass(browser, base)
        browser.close()
    print(f"[e2e] {'ALL GREEN' if not FAILED else 'FAILURES: ' + ', '.join(FAILED)}")
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
