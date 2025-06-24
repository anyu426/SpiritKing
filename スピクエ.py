# ストリームリット用スキルCT比較アプリ
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import hsv_to_rgb
from matplotlib.font_manager import FontProperties
import numpy as np
import os
import subprocess

# フォントのダウンロードと設定
FONT_URL = "https://moji.or.jp/wp-content/ipafont/IPAexfont/ipaexg00301.zip"
FONT_ZIP = "/tmp/ipaexg00301.zip"
FONT_PATH = "/tmp/ipaexg00301/ipaexg.ttf"

if not os.path.exists(FONT_PATH):
    subprocess.run(["wget", "-q", "-O", FONT_ZIP, FONT_URL])
    subprocess.run(["unzip", "-o", FONT_ZIP, "-d", "/tmp/"])
font_prop = FontProperties(fname=FONT_PATH)

# スキル定義
skills = [
    {"Name": "ワンワンボンバー", "CT": 3.45, "Effect Time": 2.0},
    {"Name": "ブリザード", "CT": 4.5, "Effect Time": None},
    {"Name": "プロテクション", "CT": 3.9, "Effect Time": 1.5},
    {"Name": "ラグナロク", "CT": 3.0, "Effect Time": None},
    {"Name": "マンドレイク爆弾", "CT": 4.85, "Effect Time": 2.5},
    {"Name": "ピアシングソード", "CT": 3.25, "Effect Time": None},
    {"Name": "自然の力", "CT": 3.75, "Effect Time": 2},
    {"Name": "ポイズンフィールド", "CT": 4.95, "Effect Time": 2.5},
    {"Name": "地獄火", "CT": 4.5, "Effect Time": None},
    {"Name": "精霊地震", "CT": 3.5, "Effect Time": None},
    {"Name": "炎の鞭", "CT": 3.95, "Effect Time": 2.0},
    {"Name": "亡者の堕落", "CT": 3.0, "Effect Time": None},
    {"Name": "キングスライム召喚", "CT": 3.35, "Effect Time": None},
    {"Name": "ドラゴンスレイヤーランス", "CT": 3.75, "Effect Time": 2},
    {"Name": "猫の足跡", "CT": 5, "Effect Time": None},
    {"Name": "月光斬り", "CT": 4.0, "Effect Time": None},
    {"Name": "ゴッドフィスト", "CT": 4.5, "Effect Time": None},
    {"Name": "火山爆発", "CT": 4.45, "Effect Time": 2.5},
    {"Name": "デスサイズ", "CT": 4.7, "Effect Time": 2.5},
    {"Name": "ベヒモス召喚", "CT": 3.9, "Effect Time": None},
    {"Name": "ドラゴンブレス", "CT": 3.85, "Effect Time": None},
    {"Name": "フェニックス召喚", "CT": 4.3, "Effect Time": 2.0},
    {"Name": "アルマゲドン", "CT": 4.75, "Effect Time": None}
]

# 色と重複判定
def generate_distinct_colors(n):
    hues = np.linspace(0, 1, n + 1)[:-1]
    return [hsv_to_rgb((h, 0.6, 0.9)) for h in hues]

def time_overlap(start1, end1, start2, end2):
    return max(0, min(end1, end2) - max(start1, start2))

# 描画関数
def plot_skills(skills, total_time=30, mode="ranking event"):
    fig, ax = plt.subplots(figsize=(12, 6))
    y_labels = [s["Name"] for s in skills]
    colors = generate_distinct_colors(len(skills))
    effect_ranges = [[] for _ in skills]
    instant_times = {}
    bar_height = 0.3

    for i, skill in enumerate(skills):
        ct = float(skill['CT'])
        effect_time = float(skill.get('Effect Time') or 0)
        color = colors[i]
        current_time = 0

        while current_time <= total_time:
            start = current_time + ct if mode == "ranking event" else current_time
            end = start + effect_time
            if start > total_time:
                break

            if effect_time > 0:
                ax.add_patch(patches.Rectangle((start, i - bar_height / 2), end - start, bar_height, color=color, alpha=0.6))
                effect_ranges[i].append((start, end))
            else:
                key = round(start, 2)
                instant_times.setdefault(key, []).append(i)

            current_time += ct

    for i in range(len(skills)):
        for j in range(i + 1, len(skills)):
            for si, ei in effect_ranges[i]:
                for sj, ej in effect_ranges[j]:
                    if time_overlap(si, ei, sj, ej):
                        ov_start = max(si, sj)
                        ov_end = min(ei, ej)
                        for y in [i, j]:
                            ax.add_patch(patches.Rectangle((ov_start, y - bar_height / 2), ov_end - ov_start, bar_height, color='red', alpha=0.8))

    for t, indices in instant_times.items():
        for i in indices:
            overlaps_effect = any(start <= t <= end for j, r in enumerate(effect_ranges) if j != i for start, end in r)
            color = 'red' if len(indices) > 1 else 'blue'
            linestyle = ':' if overlaps_effect else '-'
            ax.plot([t, t], [i - bar_height / 2, i + bar_height / 2], color=color, linestyle=linestyle, linewidth=1.8, alpha=0.9)

    ax.set_ylim(-1, len(skills))
    ax.set_xlim(0, total_time)
    ax.set_yticks(range(len(skills)))
    ax.set_yticklabels(y_labels, fontproperties=font_prop)
    ax.set_xlabel("時間（秒）", fontproperties=font_prop)
    ax.set_title(f"スキルCTタイムライン（{mode}）", fontproperties=font_prop)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    st.pyplot(fig)

# Streamlit UI
st.title("スキルクールタイム比較ツール")
mode = st.radio("モードを選択:", ["ranking event", "normal stage"])
total_time = st.selectbox("比較時間:", [30, 40])
selected_names = st.multiselect("表示するスキルを選択:", [s["Name"] for s in skills])
selected_skills = [s for s in skills if s["Name"] in selected_names]

if selected_skills:
    plot_skills(selected_skills, total_time, mode)
else:
    st.info("スキルを選択してください。")