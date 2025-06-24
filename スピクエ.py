# ストリームリット用スキルCT比較アプリ
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import hsv_to_rgb
from matplotlib.font_manager import FontProperties
import numpy as np


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

# 色と重複処理用
def generate_distinct_colors(n):
    hues = np.linspace(0, 1, n + 1)[:-1]
    return [hsv_to_rgb((h, 0.6, 0.9)) for h in hues]

def time_overlap(a1, b1, a2, b2):
    return max(0, min(b1, b2) - max(a1, a2))

# プロット関数（英語エイリアス）
def plot_skills_alias(skills, total_time=30, mode="ranking event"):
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = generate_distinct_colors(len(skills))
    effect_ranges = [[] for _ in skills]
    instant_times = {}
    bar_height = 0.3

    aliases = [f"Skill {i+1}" for i in range(len(skills))]

    for i, skill in enumerate(skills):
        ct = float(skill["CT"])
        et = float(skill.get("Effect Time") or 0)
        color = colors[i]
        t = 0
        while t <= total_time:
            start = t + ct if mode == "ranking event" else t
            end = start + et
            if start > total_time:
                break
            if et > 0:
                ax.add_patch(patches.Rectangle((start, i - bar_height/2), end - start, bar_height,
                                               color=color, alpha=0.6))
                effect_ranges[i].append((start, end))
            else:
                key = round(start, 2)
                instant_times.setdefault(key, []).append(i)
            t += ct

    # overlap bars
    for i in range(len(skills)):
        for j in range(i+1, len(skills)):
            for s1, e1 in effect_ranges[i]:
                for s2, e2 in effect_ranges[j]:
                    if time_overlap(s1, e1, s2, e2):
                        o_s = max(s1, s2)
                        o_e = min(e1, e2)
                        for y in [i, j]:
                            ax.add_patch(patches.Rectangle((o_s, y-bar_height/2), o_e-o_s, bar_height,
                                                           color='red', alpha=0.8))

    # instant skill lines
    for key, idxs in instant_times.items():
        for i in idxs:
            overlaps = any(s <= key <= e for j, rng in enumerate(effect_ranges) if j != i for s, e in rng)
            color = 'red' if len(idxs) > 1 else 'blue'
            linestyle = ':' if overlaps else '-'
            ax.plot([key, key], [i-bar_height/2, i+bar_height/2],
                    color=color, linestyle=linestyle, linewidth=1.8, alpha=0.9)

    ax.set_ylim(-1, len(skills))
    ax.set_xlim(0, total_time)
    ax.set_yticks(range(len(skills)))
    ax.set_yticklabels(aliases)
    ax.set_xlabel("Time (sec)")
    ax.set_title(f"Skill CT Timeline ({mode})")
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    st.pyplot(fig)

    st.markdown("**Legend mapping:**")
    for i, skill in enumerate(skills):
        st.markdown(f"- **Skill {i+1}** = {skill['Name']}")

# Streamlit UI
st.title("Skill CT Timeline Comparison")
mode = st.radio("Mode:", ["ranking event", "normal stage"])
total_time = st.selectbox("Total Time:", [30, 40], index=0)

names = [s["Name"] for s in skills]
selected = st.multiselect("Select skills:", names, default=names[:2])
sel = [s for s in skills if s["Name"] in selected]

if sel:
    plot_skills_alias(sel, total_time, mode)
else:
    st.info("Please select at least one skill.")