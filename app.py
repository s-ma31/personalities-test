import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import datetime
import math
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

# ==========================================
# 0. 設定とCSSスタイル定義
# ==========================================
st.set_page_config(page_title="性格タイプ診断", layout="wide")

# CSSによるデザイン調整
st.markdown("""
<style>
    /* ページ全体を強制的にトップにスクロール */
    .main { scroll-behavior: auto !important; }
    
    /* 質問文のスタイル */
    .question-text {
        font-size: 1.4rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 30px;
        margin-top: 40px;
        color: #333;
    }
    @media (prefers-color-scheme: dark) { .question-text { color: #eee; } }

    /* 診断用ラジオボタン（7選択肢）全体のコンテナ */
    div[role="radiogroup"]:has(label:nth-of-type(7)) {
        display: flex;
        justify-content: center !important;
        align-items: center;
        gap: 8px;
        width: 100%;
        margin-bottom: 20px;
        flex-wrap: nowrap !important;
    }

    /* 診断用ラジオボタンのラベルテキストを非表示 */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label > div[data-testid="stMarkdownContainer"] {
        display: none !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label p { display: none !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label span { display: none !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label div p { display: none !important; }

    /* 診断用ラベル全体 */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label {
        cursor: pointer !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 診断用ラジオボタンの丸部分のコンテナ */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label > div:first-child {
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
    div[role="radiogroup"]:has(label:nth-of-type(7)) label > div:first-child > div {
        display: none !important;
    }

    /* --- サイズ設定（外側ほど大きく） --- */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(1) > div:first-child {
        width: 42px !important; height: 42px !important; min-width: 42px !important; min-height: 42px !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(2) > div:first-child {
        width: 32px !important; height: 32px !important; min-width: 32px !important; min-height: 32px !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(3) > div:first-child {
        width: 24px !important; height: 24px !important; min-width: 24px !important; min-height: 24px !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(4) > div:first-child {
        width: 18px !important; height: 18px !important; min-width: 18px !important; min-height: 18px !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(5) > div:first-child {
        width: 24px !important; height: 24px !important; min-width: 24px !important; min-height: 24px !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(6) > div:first-child {
        width: 32px !important; height: 32px !important; min-width: 32px !important; min-height: 32px !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(7) > div:first-child {
        width: 42px !important; height: 42px !important; min-width: 42px !important; min-height: 42px !important;
    }

    /* --- 色設定（左：紫 / 右：緑） --- */

    /* デフォルト枠線色 */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(1) > div:first-child { border-color: #E1BEE7 !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(2) > div:first-child { border-color: #CE93D8 !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(3) > div:first-child { border-color: #BA68C8 !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(5) > div:first-child { border-color: #C8E6C9 !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(6) > div:first-child { border-color: #A5D6A7 !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(7) > div:first-child { border-color: #81C784 !important; }

    /* ホバー時 */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(1):hover > div:first-child,
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(2):hover > div:first-child,
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(3):hover > div:first-child {
        border-color: #9C27B0 !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(5):hover > div:first-child,
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(6):hover > div:first-child,
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(7):hover > div:first-child {
        border-color: #81C784 !important;
    }

    /* 選択時（塗りつぶし） */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:has(input:checked):nth-of-type(1) > div:first-child {
        background-color: #4A148C !important; border-color: #4A148C !important; transform: scale(1.14) !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:has(input:checked):nth-of-type(2) > div:first-child {
        background-color: #7B1FA2 !important; border-color: #7B1FA2 !important; transform: scale(1.12) !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:has(input:checked):nth-of-type(3) > div:first-child {
        background-color: #BA68C8 !important; border-color: #BA68C8 !important; transform: scale(1.1) !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:has(input:checked):nth-of-type(4) > div:first-child {
        background-color: #9E9E9E !important; border-color: #9E9E9E !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:has(input:checked):nth-of-type(5) > div:first-child {
        background-color: #66BB6A !important; border-color: #66BB6A !important; transform: scale(1.1) !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:has(input:checked):nth-of-type(6) > div:first-child {
        background-color: #43A047 !important; border-color: #43A047 !important; transform: scale(1.12) !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:has(input:checked):nth-of-type(7) > div:first-child {
        background-color: #2E7D32 !important; border-color: #2E7D32 !important; transform: scale(1.14) !important;
    }

    /* ヘッダー隠し */
    header {visibility: hidden;}
    
    /* ボタン調整・中央寄せ */
    .stButton { display: flex; justify-content: center; }
    .stButton button {
        width: 100%; max-width: 320px; font-weight: bold;
        padding: 10px 0; border-radius: 20px; margin: 0 auto;
    }
    
    /* テキストラベルの色 */
    .agree-label { 
        text-align: left; color: #4CAF50; font-weight: bold; font-size: 1.15rem; padding-top: 5px; 
    }
    .disagree-label { 
        text-align: right; color: #8E24AA; font-weight: bold; font-size: 1.15rem; padding-top: 5px; 
    }

    /* 性別選択セクション */
    .gender-section { background-color: rgba(128, 128, 128, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    
    /* 画像用 */
    img.pixelated { image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges; }
    
    @media (max-width: 640px) { div[data-testid="stForm"] div[role="radiogroup"] { gap: 8px; } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 質問データベース（バランス調整済み: 60問）
# ==========================================
questions_data = [
    # --- Mind: 意識 (E:外向 vs I:内向) ---
    {"text": "定期的に新しい交友関係を築いている", "axis": "Mind", "weight": 1},
    {"text": "事前の約束がなくても、興味を持った相手に自分から声をかけられる", "axis": "Mind", "weight": 1},
    {"text": "チームで取り組む作業が好きだ", "axis": "Mind", "weight": 1},
    {"text": "一人で過ごすより、誰かと一緒にいるほうが心地よい", "axis": "Mind", "weight": 1},
    {"text": "周囲の友人は、自分を活発で社交的だと評価するだろう", "axis": "Mind", "weight": 1},
    {"text": "初対面でも、比較的すぐに相手と意思疎通ができる", "axis": "Mind", "weight": 1},
    {"text": "人脈づくりや初対面の人への自己アピールは、かなり負担に感じる", "axis": "Mind", "weight": -1},
    {"text": "集団で行う活動より、単独での趣味のほうが性に合っている", "axis": "Mind", "weight": -1},
    {"text": "社交の場では、自分から名乗るより相手の出方を待つことが多い", "axis": "Mind", "weight": -1},
    {"text": "電話でのやり取りは避けがちだ", "axis": "Mind", "weight": -1},
    {"text": "ほぼ一人で進める仕事に魅力を感じる", "axis": "Mind", "weight": -1},
    {"text": "人が多く活気のある場所に長時間いると、疲れを感じやすい", "axis": "Mind", "weight": -1},

    # --- Energy: エネルギー (N:直感 vs S:現実) ---
    {"text": "単純で分かりやすい発想より、複雑で新規性のある発想に魅力を感じる", "axis": "Energy", "weight": 1},
    {"text": "未経験のやり方や新しい手法に挑戦するのは楽しい", "axis": "Energy", "weight": 1},
    {"text": "倫理的な問題について考え、議論するのが好きだ", "axis": "Energy", "weight": 1},
    {"text": "文章を書くなどの創造的な表現活動に惹かれる", "axis": "Energy", "weight": 1},
    {"text": "馴染みのない発想や視点を探るのは楽しい", "axis": "Energy", "weight": 1},
    {"text": "決められた手順の作業より、創造的な解決を考える仕事が好きだ", "axis": "Energy", "weight": 1},
    {"text": "創作物の多様な解釈について議論することには関心がない", "axis": "Energy", "weight": -1},
    {"text": "創作として架空の物語を書く仕事は想像しにくい", "axis": "Energy", "weight": -1},
    {"text": "議論が理論一辺倒になると、興味を失いやすい", "axis": "Energy", "weight": -1},
    {"text": "将来世界についての理論的な議論には関心が薄い", "axis": "Energy", "weight": -1},
    {"text": "抽象的・哲学的な問題を深く考えるのは無駄だと思う", "axis": "Energy", "weight": -1},
    {"text": "新しい刺激よりも、慣れ親しんだルーチンの方が落ち着く", "axis": "Energy", "weight": -1},

    # --- Nature: 気質 (F:道理 vs T:論理) ---
    {"text": "事実を積み上げた議論より、感情に訴える内容のほうが心を動かされる", "axis": "Nature", "weight": 1},
    {"text": "数値やデータより、人の体験談や感情のほうが強く印象に残る", "axis": "Nature", "weight": 1},
    {"text": "率直さよりも、相手への配慮を優先する", "axis": "Nature", "weight": 1},
    {"text": "事実と感情が食い違う場合、多くは感情を優先する", "axis": "Nature", "weight": 1},
    {"text": "判断の際、最も合理的な方法よりも関係者の気持ちを重んじる", "axis": "Nature", "weight": 1},
    {"text": "意思決定では、論理より感情的な直感に頼りやすい", "axis": "Nature", "weight": 1},
    {"text": "方針を決める際、他人の気持ちよりも事実を重視する", "axis": "Nature", "weight": -1},
    {"text": "多少感情を犠牲にしてでも、効率的な判断を好む", "axis": "Nature", "weight": -1},
    {"text": "意見が対立したとき、相手の感情より自分の正当性を示すことを優先する", "axis": "Nature", "weight": -1},
    {"text": "感情的な議論には流されにくい", "axis": "Nature", "weight": -1},
    {"text": "感覚的な印象より、客観的な事実を基準に判断することが多い", "axis": "Nature", "weight": -1},
    {"text": "友人が悲しんでいる時、情緒的サポートより問題解決策を提案したくなる", "axis": "Nature", "weight": -1},

    # --- Tactics: 戦術 (J:計画 vs P:探索) ---
    {"text": "生活空間や仕事環境は、整っていて清潔に保たれている", "axis": "Tactics", "weight": 1},
    {"text": "仕事には優先順位をつけ、効率よく計画し、締め切りより早く終えることが多い", "axis": "Tactics", "weight": 1},
    {"text": "スケジュール帳やリストなどの管理ツールを使うのが好きだ", "axis": "Tactics", "weight": 1},
    {"text": "やるべきことを済ませてから休むほうが落ち着く", "axis": "Tactics", "weight": 1},
    {"text": "手順を省かず、順番通り丁寧に進めたい", "axis": "Tactics", "weight": 1},
    {"text": "計画が崩れた場合、できるだけ早く立て直すことを最優先にする", "axis": "Tactics", "weight": 1},
    {"text": "特に計画を立てずに一日を過ごすことがよくある", "axis": "Tactics", "weight": -1},
    {"text": "締め切り直前になってようやく動くことが多い", "axis": "Tactics", "weight": -1},
    {"text": "一定のスケジュールを維持するのは難しいと感じる", "axis": "Tactics", "weight": -1},
    {"text": "自分の働き方は、継続的努力より突発的な集中力の波に近い", "axis": "Tactics", "weight": -1},
    {"text": "締め切りを守るのが得意ではない", "axis": "Tactics", "weight": -1},
    {"text": "タスクリストを作るより、その場の流れで動くのが好きだ", "axis": "Tactics", "weight": -1},

    # --- Identity: アイデンティティ (A:自己主張 vs T:慎重) ---
    {"text": "強い重圧がかかっても、たいてい冷静さを保てる", "axis": "Identity", "weight": 1},
    {"text": "他人にどう思われるかは、ほとんど意識しない", "axis": "Identity", "weight": 1},
    {"text": "不安を感じることはほとんどない", "axis": "Identity", "weight": 1},
    {"text": "一度決断すると、それを疑うことはほとんどない", "axis": "Identity", "weight": 1},
    {"text": "正しいと感じた決断なら、追加の根拠がなくても行動に移す", "axis": "Identity", "weight": 1},
    {"text": "自分に関わることは、うまく進むはずだと感じている", "axis": "Identity", "weight": 1},
    {"text": "些細なミスでも、自分の能力全体に疑問を抱いてしまう", "axis": "Identity", "weight": -1},
    {"text": "物事が悪い結果になるのではと考えがちだ", "axis": "Identity", "weight": -1},
    {"text": "急に感情が変化することがある", "axis": "Identity", "weight": -1},
    {"text": "過去の失敗を、今でも引きずっていることがある", "axis": "Identity", "weight": -1},
    {"text": "感情を制御するというより、感情に左右されていると感じる", "axis": "Identity", "weight": -1},
    {"text": "高く評価されると、いつ相手を失望させるか考えてしまう", "axis": "Identity", "weight": -1},
]

# IDを付与
for i, q in enumerate(questions_data):
    q['id'] = i

# ==========================================
# 2. セッション管理とロジック
# ==========================================

if 'finished' not in st.session_state:
    st.session_state.finished = False
# 7段階の数値選択肢（intで保持）
OPTIONS = [-3, -2, -1, 0, 1, 2, 3]

if 'answers' not in st.session_state:
    st.session_state.answers = {i: 0 for i in range(len(questions_data))}
if 'gender_input' not in st.session_state:
    st.session_state.gender_input = "回答しない"
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'scroll_to_top' not in st.session_state:
    st.session_state.scroll_to_top = False

# 初期化フラグを使い、セッション開始時に強制的に全問0でリセット
if 'initialized_once' not in st.session_state:
    st.session_state.initialized_once = True
    st.session_state.finished = False
    st.session_state.answers = {i: 0 for i in range(len(questions_data))}

def calculate_result():
    # answersを正規化（不正値は0）
    for q in questions_data:
        qid = q['id']
        val = st.session_state.answers.get(qid, 0)
        if val not in OPTIONS:
            val = 0
        st.session_state.answers[qid] = int(val)

    scores = {"Mind": 0, "Energy": 0, "Nature": 0, "Tactics": 0, "Identity": 0}
    max_scores = {"Mind": 0, "Energy": 0, "Nature": 0, "Tactics": 0, "Identity": 0}

    for q in questions_data:
        qid = q['id']
        val = st.session_state.answers.get(qid, 0)
        axis = q.get("axis")
        if axis not in scores: continue
        scores[axis] += val * q["weight"]
        max_scores[axis] += 3 * abs(q["weight"])

    result_type = ""
    details = {}

    def axis_letter_and_pct(score, max_score, pos_letter, neg_letter):
        if max_score == 0: return pos_letter, 0
        left_pct = ((score + max_score) / (2 * max_score)) * 100
        left_pct = min(100, max(0, left_pct))
        if left_pct > (100 - left_pct):
            letter = pos_letter
            pct = int(round(left_pct))
        elif (100 - left_pct) > left_pct:
            letter = neg_letter
            pct = int(round(100 - left_pct))
        else:
            letter = pos_letter if score >= 0 else neg_letter
            pct = int(round(left_pct))
        return letter, pct

    letter, pct = axis_letter_and_pct(scores["Mind"], max_scores["Mind"], "E", "I")
    result_type += letter
    details["Mind"] = {"trait": "外向型" if letter == "E" else "内向型", "pct": pct, "letter": letter}

    letter, pct = axis_letter_and_pct(scores["Energy"], max_scores["Energy"], "N", "S")
    result_type += letter
    details["Energy"] = {"trait": "直感型" if letter == "N" else "現実型", "pct": pct, "letter": letter}

    letter, pct = axis_letter_and_pct(scores["Nature"], max_scores["Nature"], "F", "T")
    result_type += letter
    details["Nature"] = {"trait": "道理型" if letter == "F" else "論理型", "pct": pct, "letter": letter}

    letter, pct = axis_letter_and_pct(scores["Tactics"], max_scores["Tactics"], "J", "P")
    result_type += letter
    details["Tactics"] = {"trait": "計画型" if letter == "J" else "探索型", "pct": pct, "letter": letter}

    letter, pct = axis_letter_and_pct(scores["Identity"], max_scores["Identity"], "A", "T")
    result_type += "-" + letter
    details["Identity"] = {"trait": "自己主張型" if letter == "A" else "慎重型", "pct": pct, "letter": letter}

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
# メール送信機能
# ==========================================
def send_result_email(to_email, result_type, details, gender, user_name, csv_data):
    """
    診断結果をメールで送信する
    Gmail SMTP設定を使用
    """
    # SMTP設定（Gmail）
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    
    # 送信元メールアドレスとパスワード
    # 優先順位: 1. Streamlit secrets  2. 環境変数
    def get_secret(key):
        # Streamlit secretsから取得を試行
        try:
            if key in st.secrets:
                return st.secrets[key]
        except:
            pass
        # 環境変数から取得
        return os.environ.get(key)
    
    SENDER_EMAIL = get_secret("SENDER_EMAIL")
    SENDER_PASSWORD = get_secret("SENDER_PASSWORD")
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return False, "メール設定が見つかりません。環境変数 SENDER_EMAIL / SENDER_PASSWORD を設定してください"
    
    # ユーザー名の表示処理
    display_name = user_name if user_name else "未入力"
    
    # メール本文を作成
    traits_text = ""
    trait_labels = {
        "Mind": "意識",
        "Energy": "エネルギー",
        "Nature": "気質",
        "Tactics": "戦術",
        "Identity": "アイデンティティ"
    }
    for key, val in details.items():
        label = trait_labels.get(key, key)
        traits_text += f"  {label}: {val['trait']} ({val['pct']}%)\n"
    
    body = f"""
性格タイプ診断の結果をお知らせします。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【診断結果】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

■ 回答者: {display_name}
■ 性格タイプ: {result_type}
■ 性別: {gender}

■ 詳細スコア:
{traits_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

詳細データはCSVファイルをご確認ください。
このメールは性格タイプ診断アプリから自動送信されました。
"""
    
    # MIMEメッセージを作成
    msg = MIMEMultipart()
    msg['Subject'] = f'【性格タイプ診断結果】{display_name}さん: {result_type}'
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # CSVを添付ファイルとして追加
    csv_attachment = MIMEBase('application', 'octet-stream')
    csv_attachment.set_payload(csv_data)
    encoders.encode_base64(csv_attachment)
    # 日本語ファイル名をRFC 2231形式でエンコード
    from urllib.parse import quote
    csv_filename = f'personality_{user_name}_{result_type}.csv' if user_name else f'personality_user_{result_type}.csv'
    encoded_filename = quote(csv_filename, safe='')
    csv_attachment.add_header(
        'Content-Disposition',
        'attachment',
        filename=('utf-8', '', csv_filename)
    )
    msg.attach(csv_attachment)
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True, "メールを送信しました！"
    except smtplib.SMTPAuthenticationError:
        return False, "認証エラー: メールアドレスまたはパスワードを確認してください"
    except smtplib.SMTPException as e:
        return False, f"送信エラー: {str(e)}"
    except Exception as e:
        return False, f"エラーが発生しました: {str(e)}"

# --- 16タイプ分類（名称のみ） ---
def get_type_info(result_type):
    base_type = result_type.split("-")[0]
    base_dir = Path(__file__).parent
    
    color_nt = "#8867c0" # 紫
    color_nf = "#41c46c" # 緑
    color_sj = "#4298b4" # 青
    color_sp = "#e4ae3a" # 黄

    type_map = {
        "INTJ": {"group": "建築家", "color": color_nt},
        "INTP": {"group": "論理学者", "color": color_nt},
        "ENTJ": {"group": "指揮官", "color": color_nt},
        "ENTP": {"group": "討論者", "color": color_nt},
        "INFJ": {"group": "提唱者", "color": color_nf},
        "INFP": {"group": "仲介者", "color": color_nf},
        "ENFJ": {"group": "主人公", "color": color_nf},
        "ENFP": {"group": "広報運動家", "color": color_nf},
        "ISTJ": {"group": "管理者", "color": color_sj},
        "ISFJ": {"group": "擁護者", "color": color_sj},
        "ESTJ": {"group": "幹部", "color": color_sj},
        "ESFJ": {"group": "領事官", "color": color_sj},
        "ISTP": {"group": "巨匠", "color": color_sp},
        "ISFP": {"group": "冒険家", "color": color_sp},
        "ESTP": {"group": "起業家", "color": color_sp},
        "ESFP": {"group": "エンターテイナー", "color": color_sp},
    }
    info = type_map.get(base_type, {"group": "診断結果", "color": "#333"})
    # スクリプトディレクトリ基準で images/TYPE.png を指す
    info["image"] = str((base_dir / "images" / f"{base_type.lower()}.png").as_posix())
    return info

# ==========================================
# 3. UI表示（色と％表示を復活させたバージョン）
# ==========================================

def display_progress_bar(label, left_text, right_text, percentage, is_left_dominant, color="#00ACC1"):
    pct = max(0, min(100, int(percentage)))
    dominant_text = left_text if is_left_dominant else right_text
    
    # ラベルと％表示
    st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'><strong>{label}</strong><div style='font-weight:bold;'>{dominant_text} {pct}%</div></div>", unsafe_allow_html=True)
    
    col_l, col_bar, col_r = st.columns([2, 6, 2])
    with col_l:
        left_color = color if is_left_dominant else "#888"
        st.markdown(f"<div style='text-align:right; color:{left_color}; font-weight:bold;'>{left_text}</div>", unsafe_allow_html=True)
    with col_bar:
        fill_color = color
        fill_dir = 'to right' if is_left_dominant else 'to left'
        if is_left_dominant:
            marker_left = f"calc({pct}% - 8px)"
            fill_style = f"left:0; width:{pct}%;"
        else:
            marker_left = f"calc({100 - pct}% - 8px)"
            fill_style = f"right:0; width:{pct}%;"

        # HTMLによるカスタムバー描画
        bar_html = f"""
        <div style='position:relative; width:100%; height:18px; background:#eee; border-radius:10px; overflow:visible;'>
            <div style='position:absolute; top:0; bottom:0; {fill_style} background:linear-gradient({fill_dir}, {fill_color}, {fill_color}); border-radius:10px 10px 10px 10px;'></div>
            <div style='position:absolute; top:50%; left:{marker_left}; transform:translateY(-50%); width:16px; height:16px; border-radius:50%; background:#fff; border:3px solid #444; box-shadow:0 2px 4px rgba(0,0,0,0.2);'></div>
        </div>
        """
        st.markdown(bar_html, unsafe_allow_html=True)
    with col_r:
        right_color = color if not is_left_dominant else "#888"
        st.markdown(f"<div style='text-align:left; color:{right_color}; font-weight:bold;'>{right_text}</div>", unsafe_allow_html=True)

def render_result():
    st.balloons()
    result_type, details = calculate_result()
    gender = st.session_state.get("gender_input", "回答しない")
    ai_context = generate_ai_context(result_type, details, gender)

    type_info = get_type_info(result_type)
    theme_color = type_info["color"]
    group_name = type_info["group"]
    image_filename = type_info["image"]

    st.markdown("<h1 style='text-align: center;'>あなたの性格タイプ</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: {theme_color}; margin-bottom: 0;'>{group_name}</h3>", unsafe_allow_html=True)

    st.markdown(f"<h2 style='text-align: center; color: {theme_color}; font-size: 4em; margin-top: 0;'>{result_type}</h2>", unsafe_allow_html=True)

    img_col = st.columns([1, 1, 1])[1]
    with img_col:
        if image_filename:
            try:
                st.image(image_filename, width=220)
            except:
                st.write("No Image")
        else:
            st.write("No Image")
    
    st.markdown("---")
    
    colors = {
        "Mind": "#00ACC1",      # teal
        "Energy": "#FFA726",    # orange
        "Nature": "#66BB6A",    # green
        "Tactics": "#7E57C2",   # purple
        "Identity": "#EF5350"   # red
    }
    
    display_progress_bar("意識 (Mind)", "外向型 (E)", "内向型 (I)", details["Mind"]["pct"], details["Mind"]["letter"] == "E", color=colors["Mind"])
    display_progress_bar("エネルギー (Energy)", "直感型 (N)", "現実型 (S)", details["Energy"]["pct"], details["Energy"]["letter"] == "N", color=colors["Energy"])
    display_progress_bar("気質 (Nature)", "道理型 (F)", "論理型 (T)", details["Nature"]["pct"], details["Nature"]["letter"] == "F", color=colors["Nature"])
    display_progress_bar("戦術 (Tactics)", "計画型 (J)", "探索型 (P)", details["Tactics"]["pct"], details["Tactics"]["letter"] == "J", color=colors["Tactics"])
    display_progress_bar("アイデンティティ (Identity)", "自己主張型 (A)", "慎重型 (T)", details["Identity"]["pct"], details["Identity"]["letter"] == "A", color=colors["Identity"])

    st.markdown("---")
    
    # メール送信セクション
    st.markdown("### 📧 結果をメールで送信")
    recipient_email = "soma_yamashita@jp.honda"
    st.info(f"送信先: {recipient_email}")
    
    # 回答者名入力（結果ページでも入力・編集可能）
    user_name = st.text_input(
        "回答者名（必須）",
        value=st.session_state.get("user_name", ""),
        placeholder="例: 本田宗一郎",
        key="user_name_result"
    )
    # 入力値をsession_stateに反映
    st.session_state.user_name = user_name
    
    # CSVデータ生成（入力された名前を使用）
    csv_data = {
        "User_Name": [user_name if user_name else "未入力"],
        "Result_Type": [result_type],
        "Gender": [gender],
        "AI_Prompt_JSON": [ai_context]
    }
    for key, val in details.items():
        csv_data[f"{key}_Trait"] = [val["trait"]]
        csv_data[f"{key}_Pct"] = [val["pct"]]
    for q in questions_data:
        qid = q["id"]
        val = st.session_state.answers.get(qid, 0)
        csv_data[f"Q{qid+1}"] = [val]
    df = pd.DataFrame(csv_data)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    
    if st.button("📧 診断結果をメールで送信", type="primary", use_container_width=True):
        if not user_name:
            st.error("お名前を入力してください。")
        else:
            with st.spinner("送信中..."):
                success, message = send_result_email(recipient_email, result_type, details, gender, user_name, csv)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    st.markdown("### 📥 データのダウンロード")
    safe_name = user_name.replace(' ', '_') if user_name else 'user'
    st.download_button("診断結果CSVをダウンロード", data=csv, file_name=f'personality_{safe_name}_{result_type}.csv', mime='text/csv')
    
    st.markdown("---")
    
    if st.button("最初からやり直す", use_container_width=True):
        st.session_state.answers = {i: 0 for i in range(len(questions_data))}
        st.session_state.finished = False
        st.session_state.current_page = 0
        st.rerun()


def main():
    # ページトップスクロール処理
    if st.session_state.get('scroll_to_top', False):
        components.html(
            """
            <script>
                window.parent.document.querySelector('section.main').scrollTo(0, 0);
            </script>
            """,
            height=0
        )
        st.session_state.scroll_to_top = False
    
    # 完了フラグが立っていたら結果を表示して終了
    if st.session_state.finished:
        render_result()
        return

    # --- 診断画面（全問1ページ表示） ---
    st.title("🧩 性格タイプ診断")
    
    st.info("以下の60問の質問に対し、あなたの感覚に最も近いものを選択してください。")
    
    # 基本情報入力
    st.markdown("<div class='gender-section'>", unsafe_allow_html=True)
    st.markdown("### 👤 基本情報")
    
    # ユーザー名入力
    st.session_state.user_name = st.text_input(
        "お名前（必須）",
        value=st.session_state.user_name,
        placeholder="例: 本田宗一郎",
        key="user_name_input"
    )
    
    # 性別選択
    st.session_state.gender_input = st.radio(
        "性別（任意）", 
        ["男性", "女性", "その他", "回答しない"], 
        horizontal=True,
        key="gender_radio_main"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

    # --- ページング設定 ---
    questions_per_page = 6
    total_pages = math.ceil(len(questions_data) / questions_per_page)
    current_page = st.session_state.current_page
    current_page = max(0, min(total_pages - 1, current_page))
    st.session_state.current_page = current_page

    start_idx = current_page * questions_per_page
    end_idx = min(start_idx + questions_per_page, len(questions_data))
    st.markdown(f"#### 質問ページ {current_page + 1} / {total_pages}")
    st.progress((current_page + 1) / total_pages)

    # --- 質問一覧（スライダーで7段階選択） ---
    for q in questions_data[start_idx:end_idx]:
        st.markdown(f"<div class='question-text'>{q['text']}</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1.5, 7, 1.5])

        with c1:
            st.markdown("<div class='disagree-label'>同意しない</div>", unsafe_allow_html=True)
        with c2:
            key = f"slider_{q['id']}"
            qid = q['id']

            current_val = st.session_state.answers.get(qid, 0)
            if current_val not in OPTIONS:
                current_val = 0

            selected = st.select_slider(
                f"q_{qid}",
                options=OPTIONS,
                value=current_val,
                label_visibility="collapsed",
                key=key
            )

            st.session_state.answers[qid] = int(selected)

        with c3:
            st.markdown("<div class='agree-label'>同意する</div>", unsafe_allow_html=True)

        # 区切り線を廃止し、余白のみ付与
        st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ナビゲーションと送信ボタン
    nav_left, nav_mid, nav_right = st.columns([1, 2, 1])
    with nav_left:
        if st.button("＜ 前へ", disabled=current_page == 0, use_container_width=True):
            st.session_state.current_page = max(0, current_page - 1)
            st.rerun()
    with nav_right:
        if st.button("次へ ＞", disabled=current_page >= total_pages - 1, use_container_width=True):
            st.session_state.current_page = min(total_pages - 1, current_page + 1)
            st.session_state.scroll_to_top = True
            st.rerun()

    if current_page == total_pages - 1:
        _, submit_col, _ = st.columns([1, 2, 1])
        with submit_col:
            if st.button("診断結果を見る ＞", type="primary", use_container_width=True):
                for q in questions_data:
                    qid = q["id"]
                    val = st.session_state.answers.get(qid, 0)
                    if val not in OPTIONS:
                        val = 0
                    st.session_state.answers[qid] = int(val)
                st.session_state.finished = True
                st.rerun()

if __name__ == "__main__":
    main()
