import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from datetime import datetime

# ==================== 页面配置 ====================
st.set_page_config(page_title="Malaysian Food Quiz", layout="wide")
st.title("🍜 Malaysia Food Quiz")
st.header("Test your knowledge about Malaysian Cuisine!")

# ==================== 初始化Session State ====================
# 存储所有参与者的答题记录
if "all_participants" not in st.session_state:
    st.session_state.all_participants = []  # 格式: [name, total_score, answers_list, timestamp]

# 当前答题状态
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "current_participant" not in st.session_state:
    st.session_state.current_participant = ""
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = [None] * 4  # 4道题
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False

# ==================== 题库定义 ====================
# 题目格式: [问题文本, 选项列表, 正确答案, 图片路径(可选)]
questions = [
    {
        "text": "Which of the following dishes is considered Malaysia's national dish?",
        "options": ["A. Nasi Lemak", "B. Laksa", "C. Satay", "D. Roti Canai"],
        "correct": "A. Nasi Lemak",
        "image": None
    },
    {
        "text": "What is the main protein usually used in a traditional Malaysian Satay?",
        "options": ["A. Beef", "B. Chicken", "C. Fish", "D. Lamb"],
        "correct": "B. Chicken",
        "image": None
    },
    {
        "text": "This dish is known as Laksa Penang. Where did it originate?",
        "options": ["A. Kuala Lumpur", "B. Melaka", "C. Penang", "D. Terengganu"],
        "correct": "C. Penang",
        "image": "Q3.png"
    },
    {
        "text": "Satay is a popular grilled meat dish. Its origin is:",
        "options": ["A. Kedah", "B. Johor", "C. Selangor", "D. Perlis"],
        "correct": "B. Johor",
        "image": "Q4.png"
    }
]

# ==================== 侧边栏 - 显示统计进度 ====================
with st.sidebar:
    st.subheader("📊 Quiz Progress")
    st.write(f"**Participants completed:** {len(st.session_state.all_participants)}/5")
    st.markdown("---")

    if len(st.session_state.all_participants) > 0:
        st.subheader("📝 Completed Participants")
        for idx, p in enumerate(st.session_state.all_participants):
            st.write(f"{idx + 1}. {p[0]}: **{p[1]}/4**")

    st.markdown("---")
    if st.button("🔄 Reset All Data (Admin)"):
        for key in ["all_participants", "quiz_active", "current_participant",
                    "current_q_index", "user_answers", "quiz_completed"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ==================== 主界面 - 输入姓名 ====================
if not st.session_state.quiz_active and not st.session_state.quiz_completed:
    st.subheader("👤 Participant Registration")

    # 检查是否已经达到5人上限
    if len(st.session_state.all_participants) >= 5:
        st.warning("⚠️ Maximum 5 participants have already completed the quiz! Please view statistics below.")
        st.session_state.quiz_completed = True
        st.rerun()

    participant_name = st.text_input("Enter your name:", value="", key="name_input")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 Start Quiz", use_container_width=True):
            if participant_name.strip():
                st.session_state.current_participant = participant_name
                st.session_state.quiz_active = True
                st.session_state.current_q_index = 0
                st.session_state.user_answers = [None] * 4
                st.rerun()
            else:
                st.error("❌ Please enter your name!")

    with col2:
        if len(st.session_state.all_participants) > 0 and st.button("📊 View Statistics", use_container_width=True):
            st.session_state.quiz_completed = True
            st.rerun()

# ==================== 答题界面 ====================
if st.session_state.quiz_active and not st.session_state.quiz_completed:
    # 显示当前参与者信息
    st.info(f"👋 **Current Participant:** {st.session_state.current_participant}")

    # 获取当前题目
    q = questions[st.session_state.current_q_index]
    q_num = st.session_state.current_q_index + 1

    st.subheader(f"📌 Question {q_num} of {len(questions)}")
    st.markdown(f"### {q['text']}")

    # 显示图片（如果是Type B题目）
    if q['image']:
        try:
            img = Image.open(q['image'])
            st.image(img, width=300, caption="Food Image")
        except FileNotFoundError:
            st.warning(f"⚠️ Image file '{q['image']}' not found, but you can still answer the question.")

    # 显示单选选项
    st.write("**Choose your answer:**")
    default_index = None
    if st.session_state.user_answers[st.session_state.current_q_index]:
        saved = st.session_state.user_answers[st.session_state.current_q_index]
        for i, opt in enumerate(q['options']):
            if opt == saved:
                default_index = i
                break

    selected_answer = st.radio(
        "Options:",
        q['options'],
        index=default_index,
        key=f"q_{st.session_state.current_q_index}",
        label_visibility="collapsed"
    )

    st.divider()

    # 按钮布局
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # 上一题按钮
        if st.session_state.current_q_index > 0:
            if st.button("⬅ Previous Question", use_container_width=True):
                st.session_state.user_answers[st.session_state.current_q_index] = selected_answer
                st.session_state.current_q_index -= 1
                st.rerun()

    with col2:
        # 下一题按钮（不是最后一题时）
        if st.session_state.current_q_index < len(questions) - 1:
            if st.button("Next Question ➡", use_container_width=True):
                st.session_state.user_answers[st.session_state.current_q_index] = selected_answer
                st.session_state.current_q_index += 1
                st.rerun()

    with col3:
        # 提交按钮（最后一题时）
        if st.session_state.current_q_index == len(questions) - 1:
            if st.button("✅ Submit Quiz", use_container_width=True, type="primary"):
                # 保存最后一题的答案
                st.session_state.user_answers[st.session_state.current_q_index] = selected_answer
                st.session_state.quiz_active = False
                st.session_state.quiz_completed = True
                st.rerun()

    # 显示进度条
    progress = (st.session_state.current_q_index + 1) / len(questions)
    st.progress(progress, text=f"Progress: {int(progress * 100)}%")

# ==================== 结果页面（显示答案和总分） ====================
if st.session_state.quiz_completed:
    # 计算当前参与者的分数
    total_score = 0
    results_data = []

    for i, q in enumerate(questions):
        user_ans = st.session_state.user_answers[i]
        correct_ans = q['correct']
        is_correct = (user_ans == correct_ans)

        if is_correct:
            total_score += 1

        results_data.append({
            "Question": q['text'][:60] + "..." if len(q['text']) > 60 else q['text'],
            "Your Answer": user_ans if user_ans else "Not answered",
            "Correct Answer": correct_ans,
            "Result": "✅ Correct" if is_correct else "❌ Wrong"
        })

    # 检查是否已经保存过这个参与者的记录
    already_saved = False
    for p in st.session_state.all_participants:
        if p[0] == st.session_state.current_participant:
            already_saved = True
            break

    # 保存当前参与者的记录
    if not already_saved and len(st.session_state.all_participants) < 5:
        st.session_state.all_participants.append([
            st.session_state.current_participant,
            total_score,
            st.session_state.user_answers.copy(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])

    # ========== 显示答题结果页面 ==========
    st.success(f"🎉 Thank you, {st.session_state.current_participant}!")

    # 显示总分卡片
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; background-color: #f0f2f6; padding: 20px; border-radius: 10px;">
            <h2>📊 Your Total Score</h2>
            <h1 style="color: #4CAF50; font-size: 60px;">{total_score} / {len(questions)}</h1>
        </div>
        """, unsafe_allow_html=True)

    # 显示详细结果表格
    st.subheader("📋 Detailed Results")
    df_results = pd.DataFrame(results_data)
    st.dataframe(df_results, use_container_width=True, hide_index=True)

    # 按钮区域
    col1, col2, col3 = st.columns(3)

    with col1:
        if len(st.session_state.all_participants) < 5:
            if st.button("👥 Next Participant", use_container_width=True, type="primary"):
                # 重置答题状态，让下一个人答题
                st.session_state.quiz_active = False
                st.session_state.quiz_completed = False
                st.session_state.current_participant = ""
                st.session_state.user_answers = [None] * 4
                st.session_state.current_q_index = 0
                st.rerun()

    with col2:
        if st.button("🏠 Back to Start", use_container_width=True):
            st.session_state.quiz_active = False
            st.session_state.quiz_completed = False
            st.session_state.current_participant = ""
            st.session_state.user_answers = [None] * 4
            st.session_state.current_q_index = 0
            st.rerun()

    with col3:
        if st.button("❌ Quit", use_container_width=True):
            st.stop()

    st.markdown("---")

    # ==================== 统计分析（达到5人后显示） ====================
    if len(st.session_state.all_participants) >= 5:
        st.header("📊 Statistical Analysis Report")

        # 提取数据
        participant_names = [p[0] for p in st.session_state.all_participants]
        participant_scores = [p[1] for p in st.session_state.all_participants]

        # 计算统计指标
        average_score = np.mean(participant_scores)
        median_score = np.median(participant_scores)
        mean_score = np.mean(participant_scores)
        highest_score = max(participant_scores)
        lowest_score = min(participant_scores)

        # 显示统计卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📈 Average", f"{average_score:.2f} / 4")
        with col2:
            st.metric("📊 Median", f"{median_score:.1f} / 4")
        with col3:
            st.metric("🎯 Mean", f"{mean_score:.2f} / 4")
        with col4:
            st.metric("🏆 Range", f"{lowest_score} - {highest_score}")

        # 显示所有参与者的成绩矩阵
        st.subheader("👥 Participant Results Matrix")

        # 计算每道题所有参与者的正确率
        question_stats = []
        for q_idx in range(len(questions)):
            correct_count = 0
            for p in st.session_state.all_participants:
                if p[2][q_idx] == questions[q_idx]['correct']:
                    correct_count += 1
            question_stats.append({
                "Question": f"Q{q_idx + 1}: {questions[q_idx]['text'][:40]}...",
                "Correct Count": correct_count,
                "Total Participants": len(st.session_state.all_participants),
                "Accuracy": f"{correct_count / len(st.session_state.all_participants) * 100:.1f}%"
            })

        # 创建成绩矩阵表格
        matrix_data = []
        for p in st.session_state.all_participants:
            row = {
                "Participant": p[0],
                "Total Score": f"{p[1]}/4"
            }
            for q_idx in range(len(questions)):
                is_correct = (p[2][q_idx] == questions[q_idx]['correct'])
                row[f"Q{q_idx + 1}"] = "✅" if is_correct else "❌"
            matrix_data.append(row)

        df_matrix = pd.DataFrame(matrix_data)
        st.dataframe(df_matrix, use_container_width=True, hide_index=True)

        # 显示题目统计
        st.subheader("📈 Per-Question Statistics")
        df_q_stats = pd.DataFrame(question_stats)
        st.dataframe(df_q_stats, use_container_width=True, hide_index=True)

        # 计算所有参与者总分数
        total_all_scores = sum(participant_scores)
        st.info(
            f"📊 **Total marks obtained by all participants for the whole quiz:** {total_all_scores} / {len(participants) * len(questions)}")

        # 绘制柱状图
        st.subheader("📊 Score Visualization Chart")
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(participant_names, participant_scores, color='skyblue', edgecolor='navy', linewidth=1.5)
        ax.axhline(average_score, color='red', linestyle='--', linewidth=2, label=f'Average = {average_score:.2f}')
        ax.set_xlabel("Participant Name", fontsize=12)
        ax.set_ylabel("Score (out of 4)", fontsize=12)
        ax.set_title("Quiz Scores by Participant", fontsize=14)
        ax.set_ylim(0, 4.5)
        ax.legend(loc='upper right')

        # 在柱子上显示数值
        for bar, score in zip(bars, participant_scores):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    str(score), ha='center', va='bottom', fontsize=11, fontweight='bold')

        st.pyplot(fig)

        # 导出数据按钮
        col1, col2 = st.columns(2)
        with col1:
            csv_data = pd.DataFrame(participant_names, columns=["Name"])
            csv_data["Score"] = participant_scores
            csv = csv_data.to_csv(index=False)
            st.download_button(
                label="💾 Download Results as CSV",
                data=csv,
                file_name="quiz_results.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            if st.button("🔄 Reset & Start Over", use_container_width=True):
                for key in ["all_participants", "quiz_active", "current_participant",
                            "current_q_index", "user_answers", "quiz_completed"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    else:
        # 未满5人时的提示
        remaining = 5 - len(st.session_state.all_participants)
        st.info(
            f"📌 **{remaining} more participant(s) needed to show statistical analysis.** Please have more people take the quiz.")

        # 显示当前已收集的数据
        if len(st.session_state.all_participants) > 0:
            st.subheader("Current Participants")
            current_df = pd.DataFrame([[p[0], f"{p[1]}/4"] for p in st.session_state.all_participants],
                                      columns=["Name", "Score"])
            st.dataframe(current_df, use_container_width=True, hide_index=True)