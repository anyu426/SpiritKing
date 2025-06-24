# ストリームリット用スキルCT比較アプリ
import streamlit as st
import pandas as pd
import altair as alt
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

# ユーザー選択UI
mode = st.radio("Mode:", ["ranking event", "normal stage"])
total_time = st.selectbox("Total Time:", [30, 40])
names = [s["Name"] for s in skills]
selected = st.multiselect("Select skills:", names, default=names[:2])
skills = [s for s in skills if s["Name"] in selected]

if not skills:
    st.info("Please select at least one skill.")
    st.stop()

# データ準備
rows = []
for idx, s in enumerate(skills):
    alias = f"Skill {idx+1}"
    ct, et = s["CT"], s.get("Effect Time") or 0
    t = 0
    while t <= total_time:
        start = t + ct if mode=="ranking event" else t
        end = start + et
        if start > total_time:
            break
        rows.append({"alias": alias, "start": start, "end": end, "et": et})
        t += ct

df = pd.DataFrame(rows)

# 重複判定
def overlap_flag(r, df):
    if r["et"]>0:
        flag = ((df["alias"]!=r["alias"]) &
                (df["start"]<r["end"]) & (df["end"]>r["start"])).any()
        return flag
    return False

df["dup"] = df.apply(lambda r: overlap_flag(r, df), axis=1)

# 即時スキルのデータ（エフェクト無）
inst = []
for r in rows:
    if r["et"]==0:
        inst.append({
            "alias": r["alias"], "t": round(r["start"],2),
            "dup": overlap_flag(r, df)
        })
df_inst = pd.DataFrame(inst)

# Altair プロット
base = alt.Chart(df).encode(
    y=alt.Y('alias:N', sort=list(df['alias'].unique())),
)

bars = base.mark_bar(opacity=0.6).encode(
    x='start:Q',
    x2='end:Q',
    color=alt.condition("datum.dup", alt.value('red'), alt.value('steelblue'))
)

inst_plots = alt.Chart(df_inst).mark_rule().encode(
    x='t:Q',
    y=alt.Y('alias:N', sort=list(df_inst['alias'].unique())),
    color=alt.condition("datum.dup", alt.value('red'), alt.value('steelblue')),
    size=alt.value(2)
)

chart = (bars + inst_plots).properties(width=700, height=50*len(skills))
st.altair_chart(chart)

# Mapping確認
st.markdown("**Legend mapping:**")
for i, s in enumerate(skills):
    st.markdown(f"- **Skill {i+1}** = {s['Name']}")