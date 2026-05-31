
import streamlit as st  # 用于创建网页界面
import pandas as pd  # 用于数据处理和表格显示
from PIL import Image  # 用于处理图片文件
import os  # 用于文件操作

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="Malaysian Food Quiz",
    page_icon="🍜",
    layout="wide"
)

# ==================== 应用标题 ====================
st.title("🍜 Malaysian Food Quiz")
st.header("Test your knowledge about Malaysian Cuisine!")

# ==================== 常量 ====================
QUESTIONS_FILE = "Questions.txt"  # 外部题目输入文件
ANSWERS_FILE = "Answers.txt"  # 外部用户答案输出文件
REQUIRED_PARTICIPANTS = 5  # 所需的最少参与者人数


# ==================== 从外部文件加载题目的函数 ====================
def load_questions_from_file(file_path):
    """
    Read questions from external input file.

    File format:
    number:type:question:correct_position:option1:option2:option3:option4
    For Type B: number:type:question:correct_position:option1:option2:option3:option4|image_name

    Example: 1:A:Malaysia national dish?:1:Nasi Lemak:Laksa:Satay:Roti Canai
    """
    questions_list = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                # Handle Type B with image
                image_name = None
                if '|' in line:
                    question_part, image_name = line.split('|')
                    parts = question_part.split(':')
                else:
                    parts = line.split(':')

                if len(parts) >= 8:  # 现在需要至少8个部分（增加了正确选项位置）
                    question_number = parts[0]
                    question_type = parts[1]
                    question_text = parts[2]
                    correct_position = int(parts[3])  # 正确选项的位置（1-4）
                    raw_options = parts[4:8]  # 4个选项，不带前缀

                    # Add letter prefixes (A., B., C., D.)
                    letter_prefixes = ['A', 'B', 'C', 'D']
                    formatted_options = [f"{letter_prefixes[i]}. {opt}" for i, opt in enumerate(raw_options)]

                    # 根据正确位置获取正确答案
                    # correct_position 是 1, 2, 3, 4，对应索引 0, 1, 2, 3
                    correct_answer = formatted_options[correct_position - 1]

                    questions_list.append({
                        "question_number": int(question_number),
                        "question_text": question_text,
                        "options": formatted_options,
                        "correct_answer": correct_answer,
                        "question_type": question_type,
                        "image_path": image_name if image_name else None
                    })

    except FileNotFoundError:
        st.error(f"❌ Questions file '{file_path}' not found!")
        return []
    except Exception as e:
        st.error(f"❌ Error parsing questions: {e}")
        return []

    return questions_list


# ==================== 将答案保存到外部文件的函数 ====================
def save_answers_to_file(participant_name, answers_list, score, questions_data):
    """
    Save user answers to external output file.

    Parameters:
        participant_name (str): Name of the participant
        answers_list (list): List of answers selected by the participant
        score (int): Participant's total score
        questions_data (list): List of question dictionaries
    """
    try:
        # 检查文件是否存在，以确定是否需要写入表头
        file_exists = os.path.isfile(ANSWERS_FILE)

        with open(ANSWERS_FILE, 'a', encoding='utf-8') as file:
            # 如果是新文件，写入表头
            if not file_exists:
                file.write("=" * 80 + "\n")
                file.write("MALAYSIAN FOOD KNOWLEDGE QUIZ - PARTICIPANT ANSWERS\n")
                file.write("=" * 80 + "\n\n")

            # 写入参与者信息
            file.write(f"Participant: {participant_name}\n")
            file.write(f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Total Score: {score}/{len(questions_data)}\n")
            file.write("-" * 50 + "\n")

            # 写入每道题及其答案
            for i, q in enumerate(questions_data):
                file.write(f"Q{i + 1}: {q['question_text']}\n")
                file.write(f"   Answer: {answers_list[i] if answers_list[i] else 'Not answered'}\n")
                file.write(f"   Correct: {q['correct_answer']}\n")
                file.write(f"   Result: {'✓ Correct' if answers_list[i] == q['correct_answer'] else '✗ Wrong'}\n\n")

            file.write("=" * 80 + "\n\n")

        return True

    except Exception as e:
        st.error(f"❌ Error saving answers to file: {e}")
        return False


# ==================== 显示图片的函数 ====================
def display_question_image(image_path):
    """
    Display image for Type B questions.

    Parameters:
        image_path (str): Path to the image file
    """
    if image_path and os.path.exists(image_path):
        try:
            img = Image.open(image_path)
            st.image(img, width=300, caption="Food Image")
        except Exception as e:
            st.warning(f"⚠️ Could not load image: {image_path}")
    elif image_path:
        st.warning(f"⚠️ Image file '{image_path}' not found")


# ==================== 加载题目 ====================
questions = load_questions_from_file(QUESTIONS_FILE)

if not questions:
    st.stop()

# 按题号排序
questions.sort(key=lambda x: x['question_number'])

# 常量
TOTAL_QUESTIONS = len(questions)

# ==================== 会话状态初始化 ====================
# 存储所有参与者的结果：[姓名, 总分, 答案列表]
if "all_participants_results" not in st.session_state:
    st.session_state.all_participants_results = []  # 列表类型

# 控制测验流程状态
if "is_quiz_active" not in st.session_state:
    st.session_state.is_quiz_active = False  # 布尔类型

# 存储当前参与者的姓名
if "current_participant_name" not in st.session_state:
    st.session_state.current_participant_name = ""  # 字符串类型

# 跟踪当前题号索引
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0  # 整数类型

# 存储当前参与者的答案
if "current_participant_answers" not in st.session_state:
    st.session_state.current_participant_answers = [None] * TOTAL_QUESTIONS  # 列表类型

# 检查当前参与者是否已完成测验
if "has_quiz_completed" not in st.session_state:
    st.session_state.has_quiz_completed = False  # 布尔类型


# ==================== 辅助函数 ====================

def reset_quiz_state():
    """
    Reset all quiz-related session state variables.
    No parameters. No return value.
    """
    st.session_state.is_quiz_active = False
    st.session_state.has_quiz_completed = False
    st.session_state.current_participant_name = ""
    st.session_state.current_participant_answers = [None] * TOTAL_QUESTIONS
    st.session_state.current_question_index = 0


def calculate_participant_score(answers_list):
    """
    Calculate total score for a single participant.

    Parameters:
        answers_list (list): List of answers selected by the participant
    Returns:
        int: Total score (number of correct answers)
    """
    score = 0  # 整数类型，初始化为 0

    for i in range(TOTAL_QUESTIONS):  # 遍历每一道题
        if answers_list[i] == questions[i]["correct_answer"]:  # 检查答案是否正确
            score += 1  # 答对一题加 1 分

    return score


def calculate_per_question_total():
    """
    Calculate total marks obtained by all participants for each question.

    Returns:
        list: List of correct counts per question
    """
    per_question_total = [0] * TOTAL_QUESTIONS  # 初始化每道题的正确人数

    for participant in st.session_state.all_participants_results:  # 遍历每位参与者
        answers_list = participant[2]  # 获取参与者的答案
        for i in range(TOTAL_QUESTIONS):  # 遍历每道题
            if answers_list[i] == questions[i]["correct_answer"]:  # 检查是否正确
                per_question_total[i] += 1  # 正确人数加 1

    return per_question_total


def calculate_overall_total():
    """
    Calculate total marks obtained by all participants for the whole quiz.

    Returns:
        int: Sum of all participants' scores
    """
    overall_total = 0  # 整数类型，初始化为 0

    for participant in st.session_state.all_participants_results:  # 遍历每位参与者
        overall_total += participant[1]  # 将参与者的得分加入总分

    return overall_total


# ==================== 侧边栏 ====================
with st.sidebar:
    st.subheader("📊 Quiz Progress")
    st.write(f"**Participants completed:** {len(st.session_state.all_participants_results)}/{REQUIRED_PARTICIPANTS}")
    st.markdown("---")

    # 显示已完成参与者名单
    if len(st.session_state.all_participants_results) > 0:
        st.subheader("📝 Completed Participants")
        for index, record in enumerate(st.session_state.all_participants_results):
            st.write(f"{index + 1}. {record[0]}: **{record[1]}/{TOTAL_QUESTIONS}**")

    st.markdown("---")

    # 管理员重置按钮
    if st.button("🔄 Reset All Data"):
        for key in ["all_participants_results", "is_quiz_active", "current_participant_name",
                    "current_question_index", "current_participant_answers", "has_quiz_completed"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ==================== 主界面：姓名输入 ====================
if not st.session_state.is_quiz_active and not st.session_state.has_quiz_completed:
    st.subheader("👤 Participant Registration")

    # 检查是否已达到最大参与者人数
    if len(st.session_state.all_participants_results) >= REQUIRED_PARTICIPANTS:
        st.warning(f"⚠️ {REQUIRED_PARTICIPANTS} participants have already completed the quiz!")
        st.session_state.has_quiz_completed = True
        st.rerun()

    # 询问用户输入姓名
    name = st.text_input("Please enter your name:", value="")

    if st.button("🎯 Start Quiz", use_container_width=True):
        if name.strip():
            st.session_state.current_participant_name = name
            st.session_state.is_quiz_active = True
            st.rerun()
        else:
            st.error("❌ Please enter your name!")

# ==================== 题目页面 ====================
if st.session_state.is_quiz_active and not st.session_state.has_quiz_completed:

    # 显示参与者姓名
    st.info(f"👋 **Current Participant:** {st.session_state.current_participant_name}")

    # 获取当前题目数据
    current_index = st.session_state.current_question_index
    current_question = questions[current_index]

    # 显示题号和题目
    st.subheader(f"📌 Question {current_index + 1} of {TOTAL_QUESTIONS}")
    st.markdown(f"### {current_question['question_text']}")

    # 为 B 类型题目显示图片
    if current_question["question_type"] == "B":
        display_question_image(current_question["image_path"])

    # 显示可点击的答案选项
    st.write("**Please select your answer:**")

    # 恢复之前已选择的答案（如果有）
    default_index = None
    saved_answer = st.session_state.current_participant_answers[current_index]
    if saved_answer:
        for i, option in enumerate(current_question["options"]):
            if option == saved_answer:
                default_index = i
                break

    # 可点击的答案选项（单选按钮）
    selected_answer = st.radio(
        label="Answer Options",
        options=current_question["options"],
        index=default_index,
        key=f"q_{current_index}",
        label_visibility="collapsed"
    )

    st.divider()

    # 导航按钮：上一题、下一题、提交
    col1, col2, col3 = st.columns([1, 1, 1])

    # 上一题按钮
    with col1:
        if current_index > 0:
            if st.button("⬅ Previous", use_container_width=True):
                st.session_state.current_participant_answers[current_index] = selected_answer
                st.session_state.current_question_index -= 1
                st.rerun()

    # 下一题按钮
    with col2:
        if current_index < TOTAL_QUESTIONS - 1:
            if st.button("Next ➡", use_container_width=True):
                st.session_state.current_participant_answers[current_index] = selected_answer
                st.session_state.current_question_index += 1
                st.rerun()

    # 提交按钮（仅在最后一题显示）
    with col3:
        if current_index == TOTAL_QUESTIONS - 1:
            if st.button("✅ Submit Quiz", use_container_width=True, type="primary"):
                st.session_state.current_participant_answers[current_index] = selected_answer
                st.session_state.is_quiz_active = False
                st.session_state.has_quiz_completed = True
                st.rerun()

    # 显示进度条
    st.progress((current_index + 1) / TOTAL_QUESTIONS,
                text=f"Progress: {int((current_index + 1) / TOTAL_QUESTIONS * 100)}%")

    # 提示结束测验并查看结果
    if current_index == TOTAL_QUESTIONS - 1:
        st.info("💡 **Tip:** Click 'Submit Quiz' to view your results!")

# ==================== 答案页面 ====================
if st.session_state.has_quiz_completed:

    # 计算当前参与者的总分
    total_score = calculate_participant_score(st.session_state.current_participant_answers)

    # 将答案保存到外部文件（Answers.txt）
    save_answers_to_file(
        st.session_state.current_participant_name,
        st.session_state.current_participant_answers,
        total_score,
        questions
    )

    # 构建结果汇总表
    results_list = []
    for i in range(TOTAL_QUESTIONS):
        is_correct = (st.session_state.current_participant_answers[i] == questions[i]["correct_answer"])
        question_text = questions[i]["question_text"]
        if len(question_text) > 50:
            question_text = question_text[:50] + "..."

        results_list.append({
            "Question": question_text,
            "Your Answer": st.session_state.current_participant_answers[i] if
            st.session_state.current_participant_answers[i] else "Not answered",
            "Correct Answer": questions[i]["correct_answer"],
            "Result": "✅ Correct" if is_correct else "❌ Wrong"
        })

    # 检查参与者是否已保存（防止重复）
    already_exists = False
    for record in st.session_state.all_participants_results:
        if record[0] == st.session_state.current_participant_name:
            already_exists = True
            break

    # 保存当前参与者记录（如果尚未保存且参与者少于 5 人）
    if not already_exists and len(st.session_state.all_participants_results) < REQUIRED_PARTICIPANTS:
        st.session_state.all_participants_results.append([
            st.session_state.current_participant_name,
            total_score,
            st.session_state.current_participant_answers.copy()
        ])

    # ========== 显示答案页面内容 ==========
    st.success(f"🎉 Thank you, {st.session_state.current_participant_name}!")

    # 显示参与者姓名
    st.markdown(f"### 👤 Participant: {st.session_state.current_participant_name}")

    # 显示总分
    st.markdown(f"### 📊 Total Score: **{total_score} / {TOTAL_QUESTIONS}**")

    # 显示结果汇总表
    st.subheader("📋 Results Summary Table")
    st.dataframe(pd.DataFrame(results_list), use_container_width=True, hide_index=True)

    # 显示答案已保存到文件的提示
    st.success(f"💾 Your answers have been saved to '{ANSWERS_FILE}'")

    # 退出按钮
    col1, col2, col3 = st.columns(3)

    with col1:
        if len(st.session_state.all_participants_results) < REQUIRED_PARTICIPANTS:
            if st.button("👥 Next Participant", use_container_width=True, type="primary"):
                reset_quiz_state()
                st.rerun()

    with col2:
        if st.button("🏠 Back to Start", use_container_width=True):
            reset_quiz_state()
            st.rerun()

    with col3:
        if st.button("❌ Quit", use_container_width=True):
            st.stop()

    st.markdown("---")

    # ==================== 五位参与者完成后显示统计信息 ====================
    if len(st.session_state.all_participants_results) >= REQUIRED_PARTICIPANTS:
        st.header("📊 All Participants Results")

        # 提取数据
        name_list = [p[0] for p in st.session_state.all_participants_results]
        score_list = [p[1] for p in st.session_state.all_participants_results]

        # 1. 计算并显示所有参与者每道题的总得分
        st.subheader("📊 Total Marks Obtained by All Participants Per Question")
        per_question_total = calculate_per_question_total()
        per_question_stats = []
        for i in range(TOTAL_QUESTIONS):
            question_preview = questions[i]["question_text"]
            if len(question_preview) > 40:
                question_preview = question_preview[:40] + "..."
            per_question_stats.append({
                "Question": f"Q{i + 1}: {question_preview}",
                "Correct Count": per_question_total[i],
                "Total Participants": len(st.session_state.all_participants_results)
            })
        st.dataframe(pd.DataFrame(per_question_stats), use_container_width=True, hide_index=True)

        # 2. 计算并显示所有参与者在整个测验中的总得分
        st.subheader("📊 Total Marks Obtained by All Participants for the Whole Quiz")
        overall_total = calculate_overall_total()
        max_possible_total = len(st.session_state.all_participants_results) * TOTAL_QUESTIONS
        st.info(f"**Overall Total: {overall_total} / {max_possible_total}**")

        # 3. 显示参与者结果矩阵（显示每道题的答题情况）
        st.subheader("👥 Participant Results Matrix")
        matrix = []
        for record in st.session_state.all_participants_results:
            row = {"Participant": record[0], "Total Score": f"{record[1]}/{TOTAL_QUESTIONS}"}
            for i in range(TOTAL_QUESTIONS):
                is_correct = (record[2][i] == questions[i]["correct_answer"])
                row[f"Q{i + 1}"] = "✅" if is_correct else "❌"
            matrix.append(row)
        st.dataframe(pd.DataFrame(matrix), use_container_width=True, hide_index=True)

        # 分数汇总表
        st.subheader("📋 Score Summary")
        summary = pd.DataFrame({"Participant": name_list, "Score": score_list})
        st.dataframe(summary, use_container_width=True, hide_index=True)

        # 重置按钮
        if st.button("🔄 Reset & Start Over", use_container_width=True):
            for key in ["all_participants_results", "is_quiz_active", "current_participant_name",
                        "current_question_index", "current_participant_answers", "has_quiz_completed"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    else:
        remaining = REQUIRED_PARTICIPANTS - len(st.session_state.all_participants_results)
        st.info(f"📌 **Need {remaining} more participant(s) to display all results.**")