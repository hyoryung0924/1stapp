import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import random

# 페이지 설정
st.set_page_config(
    page_title="인터랙티브 삼각함수 마스터",
    page_layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화 (퀴즈 상태 및 오답노트 관리)
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = {"correct": 0, "total": 0}
if "wrong_answers" not in st.session_state:
    st.session_state.wrong_answers = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "show_hint" not in st.session_state:
    st.session_state.show_hint = False

# 앱 타이틀
st.title("📐 30년차 개발자의 삼각함수 마스터 LAB")
st.markdown("시각적 그래프와 인터랙티브 퀴즈를 통해 삼각함수의 직관과 개념을 다져보세요!")

# 사이드바 메뉴
menu = st.sidebar.radio(
    "학습 메뉴 선택",
    ["1. 삼각함수 개념 & 시각화", "2. 단원별 퀴즈 풀기", "3. 오답노트 & 성적 확인"]
)

# ==========================================
# 1. 삼각함수 개념 & 시각화
# ==========================================
if menu == "1. 삼각함수 개념 & 시각화":
    st.header("1. 단위원과 삼각함수 그래프 연동")
    st.write("슬라이더를 움직여 각도( $\\theta$ )에 따른 $\\sin, \\cos, \\tan$의 변화를 확인하세요.")

    col1, col2 = st.columns([1, 2])

    with col1:
        degree = st.slider("각도 (도, °)", 0, 360, 45, step=5)
        rad = np.radians(degree)

        sin_val = np.sin(rad)
        cos_val = np.cos(rad)
        tan_val = np.tan(rad) if degree % 180 != 90 else None

        st.latex(rf"\theta = {degree}^\circ = \frac{{{degree}}}{{180}}\pi \text{{ rad}}")
        st.metric("Sin(θ) [y좌표]", f"{sin_val:.4f}")
        st.metric("Cos(θ) [x좌표]", f"{cos_val:.4f}")
        if tan_val is not None:
            st.metric("Tan(θ) [기울기]", f"{tan_val:.4f}")
        else:
            st.metric("Tan(θ) [기울기]", "정의되지 않음 (무한대)")

    with col2:
        # Plotly 그래프 생성
        fig = go.Figure()

        # 단위원 그리기
        circle_theta = np.linspace(0, 2*np.pi, 200)
        fig.add_trace(go.Scatter(
            x=np.cos(circle_theta), y=np.sin(circle_theta),
            mode='lines', name='단위원', line=dict(color='gray', dash='dash')
        ))

        # 동경 및 삼각비 표시
        fig.add_trace(go.Scatter(
            x=[0, cos_val], y=[0, sin_val],
            mode='lines+markers', name='동경 (r=1)', line=dict(color='red', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=[cos_val, cos_val], y=[0, sin_val],
            mode='lines', name='Sin (높이)', line=dict(color='blue', width=2, dash='dot')
        ))
        fig.add_trace(go.Scatter(
            x=[0, cos_val], y=[0, 0],
            mode='lines', name='Cos (밑변)', line=dict(color='green', width=2, dash='dot')
        ))

        fig.update_layout(
            title=f"단위원 상의 각도: {degree}°",
            xaxis=dict(range=[-1.5, 1.5], zeroline=True, scaleratio=1),
            yaxis=dict(range=[-1.5, 1.5], zeroline=True, scaleanchor="x"),
            width=500, height=500,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 0° ~ 360° 전체 삼각함수 파형")
    
    x_deg = np.linspace(0, 360, 361)
    x_rad = np.radians(x_deg)
    
    fig_wave = go.Figure()
    fig_wave.add_trace(go.Scatter(x=x_deg, y=np.sin(x_rad), mode='lines', name='sin(θ)', line=dict(color='blue')))
    fig_wave.add_trace(go.Scatter(x=x_deg, y=np.cos(x_rad), mode='lines', name='cos(θ)', line=dict(color='green')))
    
    # 현재 선택된 각도 점 찍기
    fig_wave.add_trace(go.Scatter(x=[degree], y=[sin_val], mode='markers', name='현재 sin', marker=dict(size=10, color='blue')))
    fig_wave.add_trace(go.Scatter(x=[degree], y=[cos_val], mode='markers', name='현재 cos', marker=dict(size=10, color='green')))

    fig_wave.update_layout(
        title="삼각함수 주기 그래프",
        xaxis_title="각도 (°)",
        yaxis_title="값",
        yaxis=dict(range=[-1.2, 1.2]),
        height=350
    )
    st.plotly_chart(fig_wave, use_container_width=True)

# ==========================================
# 2. 단원별 퀴즈 풀기
# ==========================================
elif menu == "2. 단원별 퀴즈 풀기":
    st.header("🎯 단원별 삼각함수 연습 퀴즈")

    stage = st.selectbox(
        "연습할 단원을 선택하세요:",
        ["1단원: 특수각의 삼각비 (0°, 30°, 45°, 60°, 90°)",
         "2단원: 사분면과 부호 (All-S-T-C)",
         "3단원: 호도법과 삼각함수 변환"]
    )

    # 문제 은행 생성 함수
    def generate_question(stage_name):
        if "1단원" in stage_name:
            angles = [0, 30, 45, 60, 90]
            angle = random.choice(angles)
            func = random.choice(["sin", "cos", "tan"])
            
            # tan 90도는 제외
            if func == "tan" and angle == 90:
                angle = 45

            if func == "sin":
                ans_map = {0: "0", 30: "1/2", 45: "√2/2", 60: "√3/2", 90: "1"}
            elif func == "cos":
                ans_map = {0: "1", 30: "√3/2", 45: "√2/2", 60: "1/2", 90: "0"}
            else:
                ans_map = {0: "0", 30: "1/√3", 45: "1", 60: "√3"}

            return {
                "question": f"$\\{func}({angle}^\circ)$의 값은 무엇일까요?",
                "options": ["0", "1/2", "√2/2", "√3/2", "1", "1/√3", "√3"],
                "answer": ans_map[angle],
                "hint": f"단위원에서 {angle}°일 때의 { 'y좌표' if func=='sin' else 'x좌표' if func=='cos' else 'y/x (기울기)' }를 생각해보세요!",
                "stage": stage_name
            }

        elif "2단원" in stage_name:
            quadrant = random.choice([1, 2, 3, 4])
            func = random.choice(["sin", "cos", "tan"])
            
            if quadrant == 1:
                ans = "양수 (+)"
            elif quadrant == 2:
                ans = "양수 (+)" if func == "sin" else "음수 (-)"
            elif quadrant == 3:
                ans = "양수 (+)" if func == "tan" else "음수 (-)"
            else:
                ans = "양수 (+)" if func == "cos" else "음수 (-)"

            return {
                "question": f"제 {quadrant}사분면에서 $\\{func}(\\theta)$의 부호는 무엇일까요?",
                "options": ["양수 (+)", "음수 (-)"],
                "answer": ans,
                "hint": "사분면 부호 공식 '올-싸-탄-코 (All-Sin-Tan-Cos)'를 떠올려보세요!",
                "stage": stage_name
            }

        else: # 3단원
            deg_rad_list = [
                (180, "π"), (90, "π/2"), (60, "π/3"), (45, "π/4"), (30, "π/6"), (360, "2π")
            ]
            item = random.choice(deg_rad_list)
            return {
                "question": f"각도 ${item[0]}^\circ$를 라디안(호도법)으로 올바르게 나타낸 것은?",
                "options": ["π/6", "π/4", "π/3", "π/2", "π", "2π"],
                "answer": item[1],
                "hint": "180° = π 라디안 임을 이용해 비례식을 세워보세요.",
                "stage": stage_name
            }

    # 새 문제 불러오기 버튼 또는 문제 초기화
    if st.button("🎲 새 문제 불러오기") or st.session_state.current_question is None:
        st.session_state.current_question = generate_question(stage)
        st.session_state.show_hint = False

    q = st.session_state.current_question

    st.subheader(f"[{q['stage']}]")
    st.markdown(f"### 문제: {q['question']}")

    user_ans = st.radio("정답을 선택하세요:", q["options"], key="quiz_choice")

    if st.button("정답 제출"):
        st.session_state.quiz_score["total"] += 1
        if user_ans == q["answer"]:
            st.success("🎉 정답입니다! 삼각함수 감각이 훌륭하시네요.")
            st.session_state.quiz_score["correct"] += 1
            st.session_state.show_hint = False
        else:
            st.error("❌ 틀렸습니다. 다시 고민해보세요!")
            st.session_state.show_hint = True
            
            # 오답노트에 추가 (중복 방지)
            wrong_entry = {
                "question": q["question"],
                "user_ans": user_ans,
                "correct_ans": q["answer"],
                "stage": q["stage"]
            }
            if wrong_entry not in st.session_state.wrong_answers:
                st.session_state.wrong_answers.append(wrong_entry)

    # 힌트 표시 영역 (틀렸을 때 보여줌)
    if st.session_state.show_hint:
        st.info(f"💡 **힌트**: {q['hint']}")

# ==========================================
# 3. 오답노트 & 성적 확인
# ==========================================
elif menu == "3. 오답노트 & 성적 확인":
    st.header("📝 오답노트 및 학습 통계")

    # 성적 통계
    score = st.session_state.quiz_score
    if score["total"] > 0:
        acc = (score["correct"] / score["total"]) * 100
        st.write(f"**현재 정답률:** {score['correct']} / {score['total']} ({acc:.1f}%)")
    else:
        st.write("아직 풀이한 퀴즈가 없습니다. 퀴즈 메뉴에서 문제를 풀어보세요!")

    st.markdown("---")
    st.subheader("📌 나의 오답노트")

    if st.session_state.wrong_answers:
        df_wrong = pd.DataFrame(st.session_state.wrong_answers)
        df_wrong.columns = ["문제", "내가 제출한 답", "실제 정답", "단원"]
        st.dataframe(df_wrong, use_container_width=True)

        if st.button("🗑️ 오답노트 초기화"):
            st.session_state.wrong_answers = []
            st.rerun()
    else:
        st.success("오답이 없습니다. 완벽합니다! 👏")
