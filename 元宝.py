import streamlit as st
from PIL import Image

# --- 页面配置 ---
st.set_page_config(page_title="Malaysia Food Quiz", layout="centered")

# --- 1. 标题和姓名输入 ---
st.title("🇲🇾 Malaysia Food Quiz")
st.header("Test your knowledge about Malaysian Cuisine!")

# 检查是否已经输入姓名，如果没有，阻止答题
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""

student_name = st.text_input("Enter your name:", value=st.session_state.student_name, key="name_input")

# 如果姓名为空，显示警告并停止后续操作
if student_name == "":
    st.warning("Please enter your name to start the quiz.")
    st.stop()

# --- 2. 初始化 Session State ---
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}  # 用于存储每道题的答案

# --- 3. 定义题目数据 (方便管理和分页) ---
questions = [
    {
        "id": 1,
        "type": "A",
        "title": "Which of the following dishes is considered Malaysia’s national dish?",
        "options": ["A. Nasi Lemak", "B. Laksa", "C. Satay", "D. Roti Canai"],
        "answer": "A. Nasi Lemak"
    },
    {
        "id": 2,
        "type": "A",
        "title": "What is the main protein usually used in a traditional Malaysian Satay?",
        "options": ["A. Beef", "B. Chicken", "C. Fish", "D. Lamb"],
        "answer": "B. Chicken"
    },
    {
        "id": 3,
        "type": "B",
        "title": "This dish is known as Laksa Penang. Where did it originate?",
        "image": "Q3.png",  # 确保图片在同目录下
        "options": ["A. Kuala Lumpur", "B. Melaka", "C. Penang", "D. Terengganu"],
        "answer": "C. Penang"
    },
    {
        "id": 4,
        "type": "B",
        "title": "Satay is a popular grilled meat dish. Its origin is:",
        "image": "Q4.png",  # 确保图片在同目录下
        "options": ["A. Kedah", "B. Johor", "C. Selangor", "D. Perlis"],
        "answer": "B. Johor"
    }
]

# --- 4. 题目导航逻辑 ---
total_questions = len(questions)

# 如果所有题目都答完了，显示结果页
if st.session_state.current_question >= total_questions:
    st.balloons()
    st.header(f"🎉 Thank you for completing the quiz, {student_name}!")

    st.subheader(f"Your Total Score: {st.session_state.score}/{total_questions}")

    # 显示答题详情
    st.subheader("Review your answers:")
    for i, q in enumerate(questions):
        user_answer = st.session_state.answers.get(i, "Not answered")
        correct_answer = q["answer"]
        status = "✅ Correct" if user_answer == correct_answer else f"❌ Wrong (Correct: {correct_answer})"
        st.write(f"**Q{i + 1}: {q['title']}**")
        st.write(f"Your answer: {user_answer} - {status}")
        st.divider()

    # 退出按钮 (使用 st.button 或 st.link_button)
    if st.button("Quit"):
        st.session_state.current_question = 0  # 重置
        st.session_state.score = 0
        st.experimental_rerun()  # 刷新页面

else:
    # 显示当前题目
    current_q = questions[st.session_state.current_question]

    st.subheader(f"Question {current_q['id']} of {total_questions} ({current_q['type']} Type)")
    st.write(current_q["title"])

    # 如果是 Type B，显示图片
    if current_q["type"] == "B":
        try:
            image = Image.open(current_q["image"])
            st.image(image, width=300, caption="Image of the dish")
        except FileNotFoundError:
            st.error(f"Image file '{current_q['image']}' not found.")

    # 单选按钮
    # 使用 key 参数确保 Streamlit 记住选择
    selected_option = st.radio(
        "Choose your answer:",
        current_q["options"],
        key=f"q_{st.session_state.current_question}"
    )

    # 存储答案
    st.session_state.answers[st.session_state.current_question] = selected_option

    st.divider()

    # --- 5. 导航按钮 (Previous / Next / Submit) ---
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.session_state.current_question > 0:
            if st.button("⬅️ Previous"):
                st.session_state.current_question -= 1
                st.experimental_rerun()

    with col2:
        if st.session_state.current_question < total_questions - 1:
            if st.button("➡️ Next"):
                st.session_state.current_question += 1
                st.experimental_rerun()

    with col3:
        if st.session_state.current_question == total_questions - 1:  # 最后一题
            if st.button("✅ Submit Answers"):
                # 计算最终分数
                score = 0
                for i, q in enumerate(questions):
                    if st.session_state.answers.get(i) == q["answer"]:
                        score += 1
                st.session_state.score = score
                st.session_state.current_question = total_questions  # 跳转到结果页
                st.experimental_rerun()

# --- 6. 侧边栏显示当前进度 (可选，增加专业感) ---
st.sidebar.header("Quiz Progress")
st.sidebar.write(f"Student: {student_name}")
st.sidebar.write(f"Current Question: {st.session_state.current_question + 1}/{total_questions}")
st.sidebar.progress((st.session_state.current_question + 1) / total_questions)