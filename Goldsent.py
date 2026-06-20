"""
老斯密碼 - 老師語言翻譯系統 (Streamlit 版)
------------------------------------------------
這個檔案是原本 gui_app.py (Tkinter 介面) 的 Streamlit 改寫版本。
商業邏輯完全沒有更動，仍由 teacher_translator.py 的 LaoSiMiDaSystem 負責，
這裡只負責「畫面」與「狀態管理」。
"""

import streamlit as st
from teacher_translator import LaoSiMiDaSystem

# ------------------------------------------------------------------
# 基本設定
# ------------------------------------------------------------------
st.set_page_config(
    page_title="老斯密碼 - 老師語言翻譯系統",
    page_icon="🧑‍🏫",
    layout="centered",
    initial_sidebar_state="expanded",
)

ADMIN_NAME = "歐陽建泓隊"
ADMIN_PASSWORD = "歐陽建泓隊"  # 與原程式一致

# ------------------------------------------------------------------
# 簡單的視覺樣式（呼應原本 Tkinter 版的配色）
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    .lsmd-banner {
        background:#EBF4F0;border:1px solid #D3E4DB;border-radius:8px;
        padding:14px 18px;margin-bottom:18px;color:#3A4A41;
    }
    .lsmd-board {
        background:#334539;border-radius:10px;padding:24px;margin-bottom:24px;
    }
    .lsmd-board .hello{color:white;font-size:14px;}
    .lsmd-board .name{color:#F27A60;font-size:28px;font-weight:bold;margin:4px 0 16px 0;}
    .lsmd-stat-num{color:#F2CA5C;font-size:24px;font-weight:bold;font-style:italic;}
    .lsmd-stat-label{color:#A3B1A9;font-size:12px;}
    .lsmd-quote-box{
        background:white;border:1px solid #BFC9C4;border-radius:8px;
        padding:30px;text-align:center;font-style:italic;font-size:18px;color:#2C3E50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# 商業邏輯 (沿用原本的 LaoSiMiDaSystem，整個 App 共用一個實例)
# ------------------------------------------------------------------
@st.cache_resource
def get_app_logic():
    return LaoSiMiDaSystem()


app_logic = get_app_logic()


def get_sentence_by_id(sentence_id):
    """補一個小工具：依 id 重新讀取最新票數（vote 之後要刷新畫面用）"""
    conn = app_logic.get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT sentence_id, teacher_sentence, translation, agree_votes, disagree_votes "
        "FROM sentences WHERE sentence_id = ?",
        (sentence_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


# ------------------------------------------------------------------
# Session State 初始化
# ------------------------------------------------------------------
_defaults = {
    "current_user": None,
    "view": "home",
    "translate_mode": "teacher_to_subtext",
    "admin_authed": False,
    "prefill_teacher": "",
    "prefill_subtext": "",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def goto(view):
    st.session_state.view = view


# ------------------------------------------------------------------
# 登入頁
# ------------------------------------------------------------------
def render_login():
    st.markdown(
        "<h2 style='text-align:center;margin-top:60px;'>✨ 歡迎使用「老」斯密碼 ✨</h2>",
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("login_form"):
            user_id = st.text_input("請輸入 User ID", placeholder="Student_A")
            submitted = st.form_submit_button("🚀 登入系統", use_container_width=True, type="primary")
            if submitted:
                uid = user_id.strip() or "Student_A"
                st.session_state.current_user = uid
                st.session_state.view = "home"
                st.rerun()


# ------------------------------------------------------------------
# 側邊導覽
# ------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("### 老師<span style='color:#F27A60'>密碼</span>", unsafe_allow_html=True)
        st.caption(f"使用者：**{st.session_state.current_user}**")
        st.divider()

        nav_items = [
            ("🏠 首頁", "home", None),
            ("🔍 老師➔潛台詞", "translate", "teacher_to_subtext"),
            ("🔄 潛台詞➔老師", "translate", "subtext_to_teacher"),
            ("✏️ 投稿新語錄", "add_idea", None),
            ("🏅 我的徽章", "badges", None),
            ("📉 低認同度語句", "low_agreement", None),
            ("🔮 大師金句", "gold_quote", None),
            ("🔒 管理員審核", "admin", None),
        ]
        for label, view, mode in nav_items:
            if st.button(label, use_container_width=True, key=f"nav_{label}"):
                if mode:
                    st.session_state.translate_mode = mode
                goto(view)
                st.rerun()

        st.divider()
        if st.button("登出", use_container_width=True):
            st.session_state.current_user = None
            st.session_state.view = "home"
            st.session_state.admin_authed = False
            st.rerun()


# ------------------------------------------------------------------
# 首頁
# ------------------------------------------------------------------
def render_home():
    user = st.session_state.current_user
    st.markdown(f"<div class='lsmd-banner'>歡迎回來，<b>{user}</b>！</div>", unsafe_allow_html=True)

    p_count = app_logic.get_user_translation_count(user)
    t_count = app_logic.get_total_translation_count()

    st.markdown(
        f"""
        <div class='lsmd-board'>
            <div class='hello'>👋 你好，</div>
            <div class='name'>{user}</div>
            <div style='display:flex;gap:50px;'>
                <div>
                    <div class='lsmd-stat-num'>{p_count}</div>
                    <div class='lsmd-stat-label'>我的翻譯次數</div>
                </div>
                <div>
                    <div class='lsmd-stat-num'>{t_count}</div>
                    <div class='lsmd-stat-label'>全站總翻譯</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cards = [
        ("🔍", "老師➔潛台詞", "輸入老師的話，解碼背後的真實意圖", "translate", "teacher_to_subtext"),
        ("🔄", "潛台詞➔老師", "輸入你以為的意思，找出老師是怎麼說的", "translate", "subtext_to_teacher"),
        ("✏️", "投稿新語錄", "你有更好的翻譯嗎？投稿讓大家一起評鑑", "add_idea", None),
        ("🏅", "我的徽章", "查看你累積的成就與翻譯紀錄", "badges", None),
        ("📉", "低認同度語句", "協助優化翻譯，提升系統準確度", "low_agreement", None),
        ("🔮", "大師金句", "大師開示，每日更新你的教育哲學", "gold_quote", None),
    ]
    cols = st.columns(2)
    for i, (icon, title, desc, view, mode) in enumerate(cards):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{icon} {title} ➔**")
                st.caption(desc)
                if st.button("前往", key=f"card_{view}_{mode}", use_container_width=True):
                    if mode:
                        st.session_state.translate_mode = mode
                    goto(view)
                    st.rerun()

    with st.container(border=True):
        st.markdown("**🔒 管理員審核 ➔**")
        st.caption("盤點與審核全站的新投稿語錄")
        if st.button("前往管理員審核", use_container_width=True, key="card_admin"):
            goto("admin")
            st.rerun()


# ------------------------------------------------------------------
# 翻譯頁 (老師➔潛台詞 / 潛台詞➔老師 共用)
# ------------------------------------------------------------------
def render_translate():
    mode = st.session_state.translate_mode
    title = "老師的話 ➔ 潛台詞" if mode == "teacher_to_subtext" else "潛台詞 ➔ 老師的話"
    st.subheader(title)

    input_label = "請輸入老師說的話:" if mode == "teacher_to_subtext" else "請輸入潛台詞:"
    input_key = f"text_{mode}"
    no_data_key = f"no_data_{mode}"
    if input_key not in st.session_state:
        st.session_state[input_key] = ""

    def _recommend(mode=mode, input_key=input_key, no_data_key=no_data_key):
        # 用 on_click callback 設定 session_state，必須在 widget 畫出來「之前」執行，
        # 否則 Streamlit 會丟出 StreamlitAPIException（這就是原本崩潰的原因）。
        res = app_logic.get_random_recommendation()
        if res:
            teacher_s, trans = res
            chosen = teacher_s if mode == "teacher_to_subtext" else trans
            st.session_state[input_key] = chosen
            st.session_state[no_data_key] = False
        else:
            st.session_state[no_data_key] = True

    col1, col2 = st.columns([1, 2])
    with col1:
        search_clicked = st.button("🔍 開始翻譯", type="primary", key=f"go_{mode}")
    with col2:
        st.button("💡 不知道翻譯什麼？為你推薦", key=f"rec_{mode}", on_click=_recommend)

    if st.session_state.get(no_data_key):
        st.info("目前資料庫為空，無法提供推薦喔！")

    text_value = st.text_input(input_label, key=input_key)

    results_key = f"results_{mode}"
    confirmed_key = f"confirmed_id_{mode}"
    search_text_key = f"search_text_{mode}"

    if search_clicked:
        text = text_value.strip()
        if not text:
            st.warning("請先輸入文字！")
        else:
            st.session_state[results_key] = app_logic.search_sentences(text, mode=mode)
            st.session_state[confirmed_key] = None
            st.session_state[search_text_key] = text

    results = st.session_state.get(results_key)
    confirmed_id = st.session_state.get(confirmed_key)

    if results is not None and not confirmed_id:
        if not results:
            searched = st.session_state.get(search_text_key, "")
            st.warning(f"找不到關於「{searched}」的翻譯。")
            st.write("是否要現在投稿，造福大眾？")
            if st.button("✏️ 投稿這句翻譯", key=f"toadd_{mode}"):
                if mode == "teacher_to_subtext":
                    st.session_state.prefill_teacher = searched
                    st.session_state.prefill_subtext = ""
                else:
                    st.session_state.prefill_teacher = ""
                    st.session_state.prefill_subtext = searched
                goto("add_idea")
                st.rerun()

        elif len(results) == 1:
            sentence_data = results[0]
            matched = sentence_data[1] if mode == "teacher_to_subtext" else sentence_data[2]
            st.info(f"系統找到最相似的句子是：「{matched}」，請問您要查詢的是這句嗎？")
            c1, c2 = st.columns(2)
            if c1.button("✅ 是，就是這句", key=f"yes_{mode}"):
                app_logic.record_translation_event(st.session_state.current_user)
                st.session_state[confirmed_key] = sentence_data[0]
                st.rerun()
            if c2.button("❌ 不是", key=f"no_{mode}"):
                st.session_state[results_key] = []
                st.rerun()

        else:
            options = {}
            for i, data in enumerate(results):
                disp = data[1] if mode == "teacher_to_subtext" else data[2]
                options[f"{i + 1}. {disp}"] = data[0]
            choice = st.radio(
                "系統找到了多筆相關結果，請選擇最相符的項目：",
                list(options.keys()),
                key=f"radio_{mode}",
            )
            if st.button("✅ 確認選擇", key=f"confirm_multi_{mode}"):
                app_logic.record_translation_event(st.session_state.current_user)
                st.session_state[confirmed_key] = options[choice]
                st.rerun()

    if confirmed_id:
        row = get_sentence_by_id(confirmed_id)
        if row:
            s_id, teacher_sentence, translation, agree_v, disagree_v = row
            if mode == "teacher_to_subtext":
                original_text, translated_text = teacher_sentence, translation
            else:
                original_text, translated_text = translation, teacher_sentence

            st.divider()
            st.markdown(f"📝 **原文：** {original_text}")
            st.markdown("✅ **翻譯結果：**")
            st.markdown(f"#### {translated_text}")

            if st.session_state.current_user == "iamadmin":
                st.caption(f"【管理者數據】 認同票: {agree_v} | 不認同票: {disagree_v}")

            st.write("您認同這句翻譯嗎？")
            v1, v2 = st.columns(2)
            if v1.button("👍 認同", key=f"agree_{mode}_{s_id}"):
                app_logic.vote(s_id, True)
                st.toast("感謝您的反饋！您的意見將讓系統更準確。")
                st.rerun()
            if v2.button("👎 不認同", key=f"disagree_{mode}_{s_id}"):
                app_logic.vote(s_id, False)
                st.toast("感謝您的反饋！您的意見將讓系統更準確。")
                st.rerun()

            st.divider()
            st.markdown("**🏫 誰常說這句話？**")
            teachers = app_logic.get_associated_teachers(s_id)
            if not teachers:
                st.caption("(目前還沒有人標記老師)")
            else:
                for t in teachers:
                    tc1, tc2 = st.columns([4, 1])
                    tc1.write(f"{t[1]} ({t[2]} 票)")
                    if tc2.button("+1", key=f"voteT_{t[0]}"):
                        app_logic.vote_associated_teacher(t[0])
                        st.rerun()

            with st.form(f"add_teacher_form_{s_id}", clear_on_submit=True):
                new_teacher = st.text_input("➕ 我老師也說過！(請輸入稱呼，如：王老師)")
                if st.form_submit_button("新增"):
                    if new_teacher.strip():
                        msg = app_logic.add_teacher_association(s_id, new_teacher.strip())
                        st.success(msg)
                        st.rerun()


# ------------------------------------------------------------------
# 投稿新語錄
# ------------------------------------------------------------------
def render_add_idea():
    st.subheader("✨ 貢獻您的智慧 ✨")
    with st.form("add_idea_form", clear_on_submit=True):
        t = st.text_input("老師語錄 (Ex: 這是送分題):", value=st.session_state.prefill_teacher)
        s = st.text_input("對應潛台詞 (Ex: 這題很難):", value=st.session_state.prefill_subtext)
        if st.form_submit_button("🚀 提交審核", type="primary"):
            if t.strip() and s.strip():
                msg = app_logic.add_idea(st.session_state.current_user, t.strip(), s.strip())
                st.success(msg)
                st.session_state.prefill_teacher = ""
                st.session_state.prefill_subtext = ""
            else:
                st.warning("請完整填寫老師的話與潛台詞喔！")


# ------------------------------------------------------------------
# 我的徽章
# ------------------------------------------------------------------
def render_badges():
    st.subheader(f"🏆 {st.session_state.current_user} 的成就")
    badges = app_logic.check_badges(st.session_state.current_user)
    for b in badges:
        st.markdown(f"- 🔸 {b}")


# ------------------------------------------------------------------
# 低認同度語句
# ------------------------------------------------------------------
def render_low_agreement():
    st.subheader("📉 這些翻譯需要您的建議")
    rows = app_logic.get_low_agreement_sentences()
    if not rows:
        st.info("目前沒有低認同度的語句，大家的翻譯都很棒！")
        return
    for i, data in enumerate(rows):
        s_id, teacher_s, trans, agree, disagree = data
        total = agree + disagree
        rate = (agree / total) * 100 if total else 0
        st.write(f"**[{i + 1}]** 老師：{teacher_s} → 潛台詞：{trans}　(認同率: {rate:.1f}%)")


# ------------------------------------------------------------------
# 大師金句
# ------------------------------------------------------------------
def render_gold_quote():
    st.subheader("✨ 課堂與人生開示 ✨")
    if "gold_quote_text" not in st.session_state:
        st.session_state.gold_quote_text = app_logic.get_master_gold_sentence()

    st.markdown(f"<div class='lsmd-quote-box'>{st.session_state.gold_quote_text}</div>", unsafe_allow_html=True)
    st.write("")

    c1, c2 = st.columns(2)
    if c1.button("🔄 再聽一句開示", use_container_width=True):
        st.session_state.gold_quote_text = app_logic.get_master_gold_sentence()
        st.rerun()
    if c2.button("❌ 弟子告退", use_container_width=True):
        goto("home")
        st.rerun()


# ------------------------------------------------------------------
# 管理員審核
# ------------------------------------------------------------------
def render_admin():
    if not st.session_state.admin_authed:
        st.subheader("🔒 管理員驗證")
        with st.form("admin_login_form"):
            pwd = st.text_input("請輸入管理員密碼：", type="password")
            if st.form_submit_button("驗證"):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.admin_authed = True
                    st.rerun()
                else:
                    st.error("密碼錯誤，拒絕存取！")
        return

    st.subheader("盤點待審核的創意投稿")
    ideas = app_logic.get_pending_ideas()
    if not ideas:
        st.info("目前沒有待審核的投稿。")
    for idea in ideas:
        idea_id, user_id, t_sentence, trans = idea[0], idea[1], idea[2], idea[3]
        with st.container(border=True):
            st.write(f"**ID {idea_id}** | 來自 {user_id}：「{t_sentence}」→「{trans}」")
            c1, c2 = st.columns(2)
            if c1.button("✅ 採納通過", key=f"approve_{idea_id}"):
                msg = app_logic.review_idea(ADMIN_NAME, idea_id, "approve")
                st.success(msg)
                st.rerun()
            if c2.button("❌ 駁回拒絕", key=f"reject_{idea_id}"):
                msg = app_logic.review_idea(ADMIN_NAME, idea_id, "reject")
                st.warning(msg)
                st.rerun()


# ------------------------------------------------------------------
# 主流程
# ------------------------------------------------------------------
if not st.session_state.current_user:
    render_login()
else:
    render_sidebar()
    view = st.session_state.view
    if view == "home":
        render_home()
    elif view == "translate":
        render_translate()
    elif view == "add_idea":
        render_add_idea()
    elif view == "badges":
        render_badges()
    elif view == "low_agreement":
        render_low_agreement()
    elif view == "gold_quote":
        render_gold_quote()
    elif view == "admin":
        render_admin()
