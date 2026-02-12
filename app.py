import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os
import signal
import json
import datetime

# ==========================================
# 0. 設定とCSSスタイル定義
# ==========================================
# Streamlit layout options: "centered" (default) or "wide".
# - "centered": コンテンツ幅が中央に固定されます（デフォルト）。
# - "wide": ページ幅いっぱいに広がります。
st.set_page_config(page_title="性格タイプ診断", layout="wide")

# CSSによるデザイン調整
st.markdown("""
<style>
    /* ページ全体を強制的にトップにスクロール */
    .main {
        scroll-behavior: auto !important;
    }
    
    /* 質問文のスタイル */
    .question-text {
        font-size: 1.4rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 30px;
        margin-top: 40px;
        color: #333;
    }
    @media (prefers-color-scheme: dark) {
        .question-text { color: #eee; }
    }

    /* ラジオボタン全体のコンテナ */
    div[data-testid="stForm"] div[role="radiogroup"] {
        display: flex;
        justify-content: center !important;
        align-items: center;
        gap: 8px;
        width: 100%;
        margin-bottom: 20px;
        flex-wrap: nowrap !important;
    }

    /* ラベルのテキストを完全に非表示 */
    div[data-testid="stForm"] div[role="radiogroup"] label > div[data-testid="stMarkdownContainer"] {
        display: none !important;
    }
    
    /* ラジオボタンのラベルテキスト（質問1、-3など）を非表示 */
    div[data-testid="stForm"] div[role="radiogroup"] label p {
        display: none !important;
    }
    
    div[data-testid="stForm"] div[role="radiogroup"] label span {
        display: none !important;
    }
    
    div[data-testid="stForm"] div[role="radiogroup"] label div p {
        display: none !important;
    }

    /* ラベル全体 */
    div[data-testid="stForm"] div[role="radiogroup"] label {
        cursor: pointer !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ラジオボタンの丸部分のコンテナ */
    div[data-testid="stForm"] div[role="radiogroup"] label > div:first-child {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 50% !important;
        border: 2px solid #BDBDBD !important;
        background-color: transparent !important;
        transition: all 0.2s ease-in-out !important;
        cursor: pointer !important;
    }

    /* 内側の点を非表示 */
    div[data-testid="stForm"] div[role="radiogroup"] label > div:first-child > div {
        display: none !important;
    }

    /* サイズ設定（少し大きめ） */
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(1) > div:first-child {
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        min-height: 42px !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(2) > div:first-child {
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        min-height: 32px !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(3) > div:first-child {
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
        min-height: 24px !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(4) > div:first-child {
        width: 18px !important;
        height: 18px !important;
        min-width: 18px !important;
        min-height: 18px !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(5) > div:first-child {
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
        min-height: 24px !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(6) > div:first-child {
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        min-height: 32px !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(7) > div:first-child {
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        min-height: 42px !important;
    }

    /* ホバー時 - 左側（水色） */
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(1):hover > div:first-child,
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(2):hover > div:first-child,
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(3):hover > div:first-child {
        border-color: #4DD0E1 !important;
    }

    /* ホバー時 - 右側（緑） */
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(5):hover > div:first-child,
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(6):hover > div:first-child,
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(7):hover > div:first-child {
        border-color: #81C784 !important;
    }

    /* 選択時 - 左側3つ（水色で塗りつぶし） */
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(1) > div:first-child,
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(2) > div:first-child,
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(3) > div:first-child {
        background-color: #00BCD4 !important;
        border-color: #00BCD4 !important;
        transform: scale(1.1);
    }

    /* 選択時 - 中央（グレー） */
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(4) > div:first-child {
        background-color: #9E9E9E !important;
        border-color: #9E9E9E !important;
    }

    /* 選択時 - 右側3つ（緑で塗りつぶし） */
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(5) > div:first-child,
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(6) > div:first-child,
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(7) > div:first-child {
        background-color: #4CAF50 !important;
        border-color: #4CAF50 !important;
        transform: scale(1.1);
    }

    /* ヘッダー隠し */
    header {visibility: hidden;}
    
    /* ボタン調整 */
    .stButton button {
        width: 100%;
        font-weight: bold;
        padding: 10px 0;
        border-radius: 20px;
    }
    
    /* テキストラベルの色 */
    .agree-label {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin: 0;
        padding: 0 2px;
        color: #4CAF50;
        font-weight: 700;
        font-size: 1.15rem;
        line-height: 1;
    }
    .disagree-label {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        margin: 0;
        padding: 0 2px;
        color: #00BCD4;
        font-weight: 700;
        font-size: 1.15rem;
        line-height: 1;
    }

    /* 性別選択セクション */
    .gender-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    @media (prefers-color-scheme: dark) {
        .gender-section { background-color: #2d2d2d; }
    }

    /* モバイル対応 */
    @media (max-width: 640px) {
        div[data-testid="stForm"] div[role="radiogroup"] { gap: 8px; }
    }
    /* 未選択時は薄い色に、選択時に濃い色になるように調整 */
    /* デフォルト（未選択）の境界色と淡い背景 */
    div[data-testid="stForm"] div[role="radiogroup"] label > div:first-child {
        background-color: transparent !important;
        border-color: #E0E0E0 !important;
    }
    /* 左側（否定寄り）薄色トーン */
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(1) > div:first-child { border-color: #B2DFDB !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(2) > div:first-child { border-color: #80CBC4 !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(3) > div:first-child { border-color: #4DD0E1 !important; }
    /* 右側（肯定寄り）薄色トーン */
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(5) > div:first-child { border-color: #C8E6C9 !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(6) > div:first-child { border-color: #A5D6A7 !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(7) > div:first-child { border-color: #81C784 !important; }

    /* ホバー時は少し色味を強める（未選択でも反応） */
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(1):hover > div:first-child { border-color: #00ACC1 !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(2):hover > div:first-child { border-color: #00BCD4 !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(3):hover > div:first-child { border-color: #00BCD4 !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(5):hover > div:first-child { border-color: #66BB6A !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(6):hover > div:first-child { border-color: #43A047 !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(7):hover > div:first-child { border-color: #2E7D32 !important; }

    /* 選択時は濃い色で塗りつぶす（既存の色より濃く） */
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(1) > div:first-child { background-color: #00695C !important; border-color: #00695C !important; transform: scale(1.14); }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(2) > div:first-child { background-color: #00796B !important; border-color: #00796B !important; transform: scale(1.12); }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(3) > div:first-child { background-color: #00897B !important; border-color: #00897B !important; transform: scale(1.1); }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(5) > div:first-child { background-color: #4CAF50 !important; border-color: #4CAF50 !important; transform: scale(1.1); }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(6) > div:first-child { background-color: #388E3C !important; border-color: #388E3C !important; transform: scale(1.12); }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(7) > div:first-child { background-color: #2E7D32 !important; border-color: #2E7D32 !important; transform: scale(1.14); }
    /* サイズごとに色の濃さを段階付け（選択時） */
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(1) > div:first-child {
        background-color: #00796B !important;
        border-color: #00796B !important;
        transform: scale(1.14) !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(2) > div:first-child {
        background-color: #00897B !important;
        border-color: #00897B !important;
        transform: scale(1.12) !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(3) > div:first-child {
        background-color: #00ACC1 !important;
        border-color: #00ACC1 !important;
        transform: scale(1.1) !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(4) > div:first-child {
        background-color: #9E9E9E !important;
        border-color: #9E9E9E !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(5) > div:first-child {
        background-color: #66BB6A !important;
        border-color: #66BB6A !important;
        transform: scale(1.1) !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(6) > div:first-child {
        background-color: #43A047 !important;
        border-color: #43A047 !important;
        transform: scale(1.12) !important;
    }
    div[data-testid="stForm"] div[role="radiogroup"] label:has(input:checked):nth-of-type(7) > div:first-child {
        background-color: #2E7D32 !important;
        border-color: #2E7D32 !important;
        transform: scale(1.14) !important;
    }

    /* ホバー時の色も段階付け */
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(1):hover > div:first-child { border-color: #00796B !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(2):hover > div:first-child { border-color: #00897B !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(3):hover > div:first-child { border-color: #00ACC1 !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(5):hover > div:first-child { border-color: #66BB6A !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(6):hover > div:first-child { border-color: #43A047 !important; }
    div[data-testid="stForm"] div[role="radiogroup"] label:nth-of-type(7):hover > div:first-child { border-color: #2E7D32 !important; }
</style>

<script>
    // ページ読み込み時に強制的にトップへスクロール
    window.addEventListener('load', function() {
        window.scrollTo(0, 0);
        const main = window.parent.document.querySelector('.main');
        if (main) main.scrollTop = 0;
    });
</script>
""", unsafe_allow_html=True)

# ==========================================
# 1. 質問データベース
# ==========================================

questions_data = [
    # --- Page 1 ---
    {"text": "定期的に新しい交友関係を築いている", "axis": "Mind", "weight": 1},
    {"text": "単純で分かりやすい発想より、複雑で新規性のある発想に魅力を感じる", "axis": "Energy", "weight": 1},
    {"text": "事実を積み上げた議論より、感情に訴える内容のほうが心を動かされる", "axis": "Nature", "weight": 1},
    {"text": "生活空間や仕事環境は、整っていて清潔に保たれている", "axis": "Tactics", "weight": 1},
    {"text": "強い重圧がかかっても、たいてい冷静さを保てる", "axis": "Identity", "weight": 1},
    {"text": "人脈づくりや初対面の人への自己アピールは、かなり負担に感じる", "axis": "Mind", "weight": -1},
    # --- Page 2 ---
    {"text": "仕事には優先順位をつけ、効率よく計画し、締め切りより早く終えることが多い", "axis": "Tactics", "weight": 1},
    {"text": "数値やデータより、人の体験談や感情のほうが強く印象に残る", "axis": "Nature", "weight": 1},
    {"text": "スケジュール帳やリストなどの管理ツールを使うのが好きだ", "axis": "Tactics", "weight": 1},
    {"text": "些細なミスでも、自分の能力全体に疑問を抱いてしまう", "axis": "Identity", "weight": -1},
    {"text": "事前の約束がなくても、興味を持った相手に自分から声をかけられる", "axis": "Mind", "weight": 1},
    {"text": "創作物の多様な解釈について議論することには関心がない", "axis": "Energy", "weight": -1},
    # --- Page 3 ---
    {"text": "方針を決める際、他人の気持ちよりも事実を重視する", "axis": "Nature", "weight": -1},
    {"text": "特に計画を立てずに一日を過ごすことがよくある", "axis": "Tactics", "weight": -1},
    {"text": "他人にどう思われるかは、ほとんど意識しない", "axis": "Identity", "weight": 1},
    {"text": "チームで取り組む作業が好きだ", "axis": "Mind", "weight": 1},
    {"text": "未経験のやり方や新しい手法に挑戦するのは楽しい", "axis": "Energy", "weight": 1},
    {"text": "率直さよりも、相手への配慮を優先する", "axis": "Nature", "weight": 1},
    # --- Page 4 ---
    {"text": "新しい体験や知識を積極的に求めている", "axis": "Energy", "weight": 1},
    {"text": "物事が悪い結果になるのではと考えがちだ", "axis": "Identity", "weight": -1},
    {"text": "集団で行う活動より、単独での趣味のほうが性に合っている", "axis": "Mind", "weight": -1},
    {"text": "創作として架空の物語を書く仕事は想像しにくい", "axis": "Energy", "weight": -1},
    {"text": "多少感情を犠牲にしてでも、効率的な判断を好む", "axis": "Nature", "weight": -1},
    {"text": "やるべきことを済ませてから休むほうが落ち着く", "axis": "Tactics", "weight": 1},
    # --- Page 5 ---
    {"text": "意見が対立したとき、相手の感情より自分の正当性を示すことを優先する", "axis": "Nature", "weight": -1},
    {"text": "社交の場では、自分から名乗るより相手の出方を待つことが多い", "axis": "Mind", "weight": -1},
    {"text": "急に感情が変化することがある", "axis": "Identity", "weight": -1},
    {"text": "感情的な議論には流されにくい", "axis": "Nature", "weight": -1},
    {"text": "締め切り直前になってようやく動くことが多い", "axis": "Tactics", "weight": -1},
    {"text": "倫理的な問題について考え、議論するのが好きだ", "axis": "Energy", "weight": 1},
    # --- Page 6 ---
    {"text": "一人で過ごすより、誰かと一緒にいるほうが心地よい", "axis": "Mind", "weight": 1},
    {"text": "議論が理論一辺倒になると、興味を失いやすい", "axis": "Energy", "weight": -1},
    {"text": "事実と感情が食い違う場合、多くは感情を優先する", "axis": "Nature", "weight": 1},
    {"text": "一定のスケジュールを維持するのは難しいと感じる", "axis": "Tactics", "weight": -1},
    {"text": "一度決断すると、それを疑うことはほとんどない", "axis": "Identity", "weight": 1},
    {"text": "周囲の友人は、自分を活発で社交的だと評価するだろう", "axis": "Mind", "weight": 1},
    # --- Page 7 ---
    {"text": "文章を書くなどの創造的な表現活動に惹かれる", "axis": "Energy", "weight": 1},
    {"text": "感覚的な印象より、客観的な事実を基準に判断することが多い", "axis": "Nature", "weight": -1},
    {"text": "毎日のタスクを書き出すのが好きだ", "axis": "Tactics", "weight": 1},
    {"text": "不安を感じることはほとんどない", "axis": "Identity", "weight": 1},
    {"text": "電話でのやり取りは避けがちだ", "axis": "Mind", "weight": -1},
    {"text": "馴染みのない発想や視点を探るのは楽しい", "axis": "Energy", "weight": 1},
    # --- Page 8 ---
    {"text": "初対面でも、比較的すぐに相手と意思疎通ができる", "axis": "Mind", "weight": 1},
    {"text": "計画が崩れた場合、できるだけ早く立て直すことを最優先にする", "axis": "Tactics", "weight": 1},
    {"text": "過去の失敗を、今でも引きずっていることがある", "axis": "Identity", "weight": -1},
    {"text": "将来世界についての理論的な議論には関心が薄い", "axis": "Energy", "weight": -1},
    {"text": "感情を制御するというより、感情に左右されていると感じる", "axis": "Identity", "weight": -1},
    {"text": "判断の際、最も合理的な方法よりも関係者の気持ちを重んじる", "axis": "Nature", "weight": 1},
    # --- Page 9 ---
    {"text": "自分の働き方は、継続的努力より突発的な集中力の波に近い", "axis": "Tactics", "weight": -1},
    {"text": "高く評価されると、いつ相手を失望させるか考えてしまう", "axis": "Identity", "weight": -1},
    {"text": "ほぼ一人で進める仕事に魅力を感じる", "axis": "Mind", "weight": -1},
    {"text": "抽象的・哲学的な問題を深く考えるのは無駄だと思う", "axis": "Energy", "weight": -1},
    {"text": "静かな場所より、人が多く活気のある環境を好む", "axis": "Mind", "weight": 1},
    {"text": "正しいと感じた決断なら、追加の根拠がなくても行動に移す", "axis": "Identity", "weight": 1},
    # --- Page 10 ---
    {"text": "精神的に余裕がないと感じることが多い", "axis": "Identity", "weight": -1},
    {"text": "手順を省かず、順番通り丁寧に進めたい", "axis": "Tactics", "weight": 1},
    {"text": "決められた手順の作業より、創造的な解決を考える仕事が好きだ", "axis": "Energy", "weight": 1},
    {"text": "意思決定では、論理より感情的な直感に頼りやすい", "axis": "Nature", "weight": 1},
    {"text": "締め切りを守るのが得意ではない", "axis": "Tactics", "weight": -1},
    {"text": "自分に関わることは、うまく進むはずだと感じている", "axis": "Identity", "weight": 1},
]

# IDを付与
for i, q in enumerate(questions_data):
    q['id'] = i

# ==========================================
# 2. セッション管理とロジック
# ==========================================

if 'page' not in st.session_state:
    st.session_state.page = 0
if 'finished' not in st.session_state:
    st.session_state.finished = False
if 'answers' not in st.session_state:
    st.session_state.answers = {}
    # 全質問の初期値を0（中立）に設定
    for i in range(len(questions_data)):
        st.session_state.answers[i] = 0


def log_session_state(event: str):
    try:
        data = {
            "time": datetime.datetime.now().isoformat(),
            "event": event,
            "page": st.session_state.get("page"),
            "finished": st.session_state.get("finished"),
            "gender": st.session_state.get("gender_input"),
            "answers": st.session_state.get("answers")
        }
        with open("session_state_log.txt", "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception:
        pass

QUESTIONS_PER_PAGE = 6
TOTAL_PAGES = len(questions_data) // QUESTIONS_PER_PAGE

def calculate_result():
    # questions_data uses English axis keys: Mind, Energy, Nature, Tactics, Identity
    scores = {"Energy": 0, "Mind": 0, "Nature": 0, "Tactics": 0, "Identity": 0}
    max_scores = {"Energy": 0, "Mind": 0, "Nature": 0, "Tactics": 0, "Identity": 0}

    for q in questions_data:
        qid = q['id']
        val = st.session_state.answers.get(qid, 0)
        axis = q.get("axis")
        if axis not in scores:
            # skip unknown axis
            continue
        scores[axis] += val * q["weight"]
        max_scores[axis] += 3 * abs(q["weight"])

    result_type = ""
    details = {}

    # helper to compute letter and percentage
    def axis_letter_and_pct(score, max_score, pos_letter, neg_letter):
        pct = (abs(score) / max_score) * 100 if max_score != 0 else 0
        pct = min(100, max(0, pct))
        letter = pos_letter if score >= 0 else neg_letter
        return letter, int(pct)

    # Mind -> 意識 (E/I)
    letter, pct = axis_letter_and_pct(scores["Mind"], max_scores["Mind"], "E", "I")
    result_type += letter
    details["意識"] = {"trait": "外向型" if letter == "E" else "内向型", "pct": pct, "letter": letter}

    # Energy -> エネルギー (N/S)
    letter, pct = axis_letter_and_pct(scores["Energy"], max_scores["Energy"], "N", "S")
    result_type += letter
    details["エネルギー"] = {"trait": "直感型" if letter == "N" else "現実型", "pct": pct, "letter": letter}

    # Nature -> 性質 (F/T)
    letter, pct = axis_letter_and_pct(scores["Nature"], max_scores["Nature"], "F", "T")
    result_type += letter
    details["性質"] = {"trait": "感情型" if letter == "F" else "思考型", "pct": pct, "letter": letter}

    # Tactics -> 戦術 (J/P)
    letter, pct = axis_letter_and_pct(scores["Tactics"], max_scores["Tactics"], "J", "P")
    result_type += letter
    details["戦術"] = {"trait": "計画型" if letter == "J" else "探索型", "pct": pct, "letter": letter}

    # Identity -> アイデンティティ (A/T) - append with hyphen
    letter, pct = axis_letter_and_pct(scores["Identity"], max_scores["Identity"], "A", "T")
    result_type += "-" + letter
    details["アイデンティティ"] = {"trait": "自己主張型" if letter == "A" else "慎重型", "pct": pct, "letter": letter}

    return result_type, details

def generate_ai_context(result_type, details, gender):
    prompt_data = {
        "target_persona": {
            "mbti_type": result_type,
            "gender": gender,
            "traits": details
        }
    }
    return json.dumps(prompt_data, ensure_ascii=False)

# ==========================================
# 3. UI表示
# ==========================================

def display_progress_bar(label, left_text, right_text, percentage, is_left_dominant):
    st.markdown(f"**{label}**")
    col_l, col_bar, col_r = st.columns([2, 6, 2])
    with col_l:
        color = "#009688" if is_left_dominant else "#aaa"
        st.markdown(f"<div style='text-align:right; color:{color}; font-weight:bold;'>{left_text}</div>", unsafe_allow_html=True)
    with col_bar:
        # プログレスバー表示（Streamlit は 0.0-1.0 を想定）
        st.progress(percentage / 100)
        # 数値のパーセンテージをプログレスバー下に表示
        st.markdown(f"<div style='text-align:center; font-weight:bold; margin-top:6px;'>{int(percentage)}%</div>", unsafe_allow_html=True)
    with col_r:
        color = "#884444" if not is_left_dominant else "#aaa"
        st.markdown(f"<div style='text-align:left; color:{color}; font-weight:bold;'>{right_text}</div>", unsafe_allow_html=True)

def main():
    # ページ読み込み時のスクロール処理などはそのまま維持
    st.markdown("""
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() { window.scrollTo(0, 0); }, 100);
        });
    </script>
    """, unsafe_allow_html=True)

    # ページ遷移時にトップへスクロールするためのフラグ検出
    if st.session_state.get('scroll_to_top', False):
        st.markdown("""
        <script>
            const main = window.parent.document.querySelector('.main');
            if (main) { main.scrollTop = 0; }
            window.scrollTo(0, 0);
        </script>
        """, unsafe_allow_html=True)
        st.session_state['scroll_to_top'] = False

    # 完了画面の処理
    if st.session_state.finished:
        st.balloons()
        result_type, details = calculate_result()
        gender = st.session_state.get("gender_input", "回答しない")
        ai_context = generate_ai_context(result_type, details, gender)

        st.markdown("<h1 style='text-align: center;'>あなたの性格タイプ</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #4CAF50; font-size: 4em;'>{result_type}</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        display_progress_bar("意識 (Mind)", "外向型 (E)", "内向型 (I)", details["意識"]["pct"], details["意識"]["letter"] == "E")
        display_progress_bar("エネルギー (Energy)", "直感型 (N)", "現実型 (S)", details["エネルギー"]["pct"], details["エネルギー"]["letter"] == "N")
        display_progress_bar("性質 (Nature)", "感情型 (F)", "思考型 (T)", details["性質"]["pct"], details["性質"]["letter"] == "F")
        display_progress_bar("戦術 (Tactics)", "計画型 (J)", "探索型 (P)", details["戦術"]["pct"], details["戦術"]["letter"] == "J")
        display_progress_bar("アイデンティティ (Identity)", "自己主張型 (A)", "慎重型 (T)", details["アイデンティティ"]["pct"], details["アイデンティティ"]["letter"] == "A")

        st.markdown("---")
        
        csv_data = {
            "User_ID": ["User_001"],
            "Result_Type": [result_type],
            "Gender": [gender],
            "AI_Prompt_JSON": [ai_context]
        }
        for key, val in details.items():
            csv_data[f"{key}_Trait"] = [val["trait"]]
            csv_data[f"{key}_Pct"] = [val["pct"]]
        for qid, val in st.session_state.answers.items():
            csv_data[f"Q{qid+1}"] = [val]
        df = pd.DataFrame(csv_data)
        csv = df.to_csv(index=False).encode('utf-8-sig')

        st.markdown("### 📥 データのダウンロード")
        st.download_button("診断結果CSVをダウンロード", data=csv, file_name=f'personality_{result_type}.csv', mime='text/csv')
        
        if st.button("最初からやり直す"):
            # 全リセット
            st.session_state.page = 0
            st.session_state.answers = {i: 0 for i in range(len(questions_data))}
            st.session_state.finished = False
            log_session_state("reset")
            st.rerun()
        return

    # --- 診断画面 ---
    st.title("🧩 性格タイプ診断")
    
    # ページ0のみ性別などを表示
    if st.session_state.page == 0:
        st.info("以下の質問に対し、あなたの感覚に最も近いものを選択してください。")
        st.markdown("<div class='gender-section'>", unsafe_allow_html=True)
        st.markdown("### 👤 基本情報")
        st.session_state.gender_input = st.radio(
            "性別（任意）", 
            ["男性", "女性", "その他", "回答しない"], 
            horizontal=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
    
    # ページ計算
    start_idx = st.session_state.page * QUESTIONS_PER_PAGE
    end_idx = start_idx + QUESTIONS_PER_PAGE
    current_questions = questions_data[start_idx:end_idx]

    # 進捗バー
    progress = (st.session_state.page) / TOTAL_PAGES
    st.progress(progress)
    st.caption(f"Page {st.session_state.page + 1} / {TOTAL_PAGES}")

    # --- フォーム開始 ---
    with st.form(key=f"form_page_{st.session_state.page}"):
        options = [-3, -2, -1, 0, 1, 2, 3]
        
        for q in current_questions:
            st.markdown(f"<div class='question-text'>{q['text']}</div>", unsafe_allow_html=True)
            # カラム比を調整してラベルをラジオボタンに近づける
            c1, c2, c3 = st.columns([1, 7, 1])
            
            with c1:
                st.markdown("<div class='disagree-label'>同意しない</div>", unsafe_allow_html=True)
            with c2:
                # 【重要】session_state.answers から保存済みの値を取得（なければ0）
                current_val = st.session_state.answers.get(q['id'], 0)
                
                # key を radio_{id} に設定することで、自動的に session_state に入る
                key_radio = f"radio_{q['id']}"
                st.radio(
                    f"質問 {q['id']}",
                    options,
                    index=options.index(current_val) if current_val in options else 0,
                    horizontal=True,
                    format_func=lambda x: "",
                    label_visibility="collapsed",
                    key=key_radio
                )
                # 常に最新のラジオ値を `st.session_state.answers` に反映
                st.session_state.answers[q['id']] = st.session_state.get(key_radio, 0)
            with c3:
                st.markdown("<div class='agree-label'>同意する</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

        # --- ボタン配置エリア (中央寄せ) ---
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3カラム作成： [空白(1)] [ボタンエリア(2)] [空白(1)] で中央に寄せる
        b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
        
        # ページ移動のロジック
        is_first_page = (st.session_state.page == 0)
        is_last_page = (st.session_state.page == TOTAL_PAGES - 1)
        
        # ボタンエリア(中央)の中にさらに2カラム作って「戻る」「次へ」を並べる
        with b_col2:
            # ページごとにボタンの出し分け
            if is_first_page:
                # 最初のページは「次へ」のみ
                if st.form_submit_button("次へ ＞", type="primary", use_container_width=True):
                    # 【重要】現在のページの回答を保存
                    for q in current_questions:
                        st.session_state.answers[q['id']] = st.session_state[f"radio_{q['id']}"]
                    st.session_state['scroll_to_top'] = True
                    st.session_state.page += 1
                    log_session_state("next_page")
                    st.rerun()

            elif is_last_page:
                # 最後のページは「戻る」と「結果を見る」
                btns = st.columns(2)
                with btns[0]:
                    if st.form_submit_button("＜ 前へ", use_container_width=True):
                        # 戻る時も一応保存しておく
                        for q in current_questions:
                            st.session_state.answers[q['id']] = st.session_state[f"radio_{q['id']}"]
                        st.session_state['scroll_to_top'] = True
                        st.session_state.page -= 1
                        log_session_state("prev_page")
                        st.rerun()
                with btns[1]:
                    if st.form_submit_button("診断結果を見る ＞", type="primary", use_container_width=True):
                        # 回答を保存
                        for q in current_questions:
                            st.session_state.answers[q['id']] = st.session_state[f"radio_{q['id']}"]
                        st.session_state.finished = True
                        st.session_state['scroll_to_top'] = True
                        log_session_state("finished")
                        st.rerun()
            
            else:
                # 中間のページは「戻る」と「次へ」
                btns = st.columns(2)
                with btns[0]:
                    if st.form_submit_button("＜ 前へ", use_container_width=True):
                        for q in current_questions:
                            st.session_state.answers[q['id']] = st.session_state[f"radio_{q['id']}"]
                        st.session_state['scroll_to_top'] = True
                        st.session_state.page -= 1
                        log_session_state("prev_page")
                        st.rerun()
                with btns[1]:
                    if st.form_submit_button("次へ ＞", type="primary", use_container_width=True):
                        for q in current_questions:
                            st.session_state.answers[q['id']] = st.session_state[f"radio_{q['id']}"]
                        st.session_state['scroll_to_top'] = True
                        st.session_state.page += 1
                        log_session_state("next_page")
                        st.rerun()

    # 開発用：ローカル実行時にサーバを停止するボタン（Ctrl+C の代替）
    st.markdown("---")
    st.markdown("<div style='text-align:center;'><small>開発用：ローカルで実行中の Streamlit サーバを停止します。</small></div>", unsafe_allow_html=True)
    if st.button("サーバーを終了する（ローカルのみ）"):
        st.warning("サーバーを停止しています...")
        try:
            log_session_state("server_stop")
            os.kill(os.getpid(), signal.SIGTERM)
        except Exception:
            log_session_state("server_stop")
            os._exit(0)

if __name__ == "__main__":
    main()