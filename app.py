import streamlit as st
import pandas as pd
from collections import Counter
from itertools import combinations

st.title("AI 로또 전략 추천 시스템")

uploaded_file = st.file_uploader("로또 당첨번호 엑셀(.xlsx) 업로드", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["번호 리스트"] = df["당첨번호_y"].apply(lambda x: list(map(int, str(x).split(", "))))
    df = df.sort_values("회차")

    def run_final_pick(df):
        all_nums = [n for row in df["번호 리스트"] for n in row]
        return [n for n, _ in Counter(all_nums).most_common(30)]

    def run_strategy_3(df):
        all_nums = [n for row in df["번호 리스트"] for n in row]
        freq = Counter(all_nums)
        return list(set([n for n, _ in freq.most_common(2)] + [n for n, _ in freq.most_common()[-2:]]))

    def run_strategy_C_enhanced(df):
        all_nums = [n for row in df["번호 리스트"] for n in row]
        top5 = [n for n, _ in Counter(all_nums).most_common(5)]
        bonus = [row[-1] for row in df.tail(20)["번호 리스트"]]
        return list(set(top5 + bonus))

    def run_strategy_A(df):
        all_nums = [n for row in df["번호 리스트"] for n in row]
        freq = Counter(all_nums)
        return list(set([n for n, _ in freq.most_common(10)] + [n for n, _ in freq.most_common()[-10:]]))

    def run_super_strong(df):
        base = set(run_final_pick(df))
        s3 = set(run_strategy_3(df))
        sc = set(run_strategy_C_enhanced(df))
        sa = set(run_strategy_A(df))
        enhanced = base & (s3 | sc | sa)
        last_nums = [r[-1] for r in df.tail(30)["번호 리스트"]]
        repeated = {n for n, c in Counter(last_nums).items() if c >= 2}
        return sorted(enhanced.union(repeated))

    round_input = st.number_input("예측할 회차 입력", min_value=2, max_value=int(df["회차"].max() + 1), value=int(df["회차"].max() + 1), step=1)

    if st.button("예측 실행"):
        past_df = df[df["회차"] < round_input]
        predicted = run_super_strong(past_df)
        st.markdown(f"### [기훈픽-최종픽-슈퍼강화형] 예측 번호 ({len(predicted)}개)")
        st.write(predicted)

        combis = list(combinations(predicted, 6))
        sample = combis[:20]
        st.markdown("### 추천 조합 (20개 예시)")
        for i, c in enumerate(sample, 1):
            st.write(f"조합 {i}: {sorted(c)}")

        if round_input <= df["회차"].max():
            actual = set(df[df["회차"] == round_input]["번호 리스트"].values[0])
            matched = actual & set(predicted)
            st.markdown("### 실제 당첨번호와 비교")
            st.write(f"실제 번호: {sorted(actual)}")
            st.write(f"적중 번호: {sorted(matched)}")
            st.write(f"적중 수: {len(matched)}")