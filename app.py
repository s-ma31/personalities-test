"""
================================================================================
性格タイプ診断アプリケーション (16タイプ診断)
================================================================================

このアプリケーションは、Streamlitを使用した性格タイプ診断Webアプリです。
60問の質問に回答することで、16種類の性格タイプを診断します。

【機能概要】
- 60問の質問による性格診断
- 5つの軸（Mind, Energy, Nature, Tactics, Identity）での分析
- 結果のCSVダウンロード
- 診断結果のメール送信

================================================================================
"""

# ==========================================
# 必要なライブラリのインポート
# ==========================================
import streamlit as st          # Webアプリケーションフレームワーク
import pandas as pd             # データ処理・CSV出力用
import json                     # JSON形式でのデータ変換
import datetime                 # 日時処理（現在未使用だが将来の拡張用）
import math                     # ページング計算用（ceil関数）
import os                       # 環境変数の取得
import smtplib                  # SMTPメール送信
from email.mime.text import MIMEText           # メール本文作成
from email.mime.multipart import MIMEMultipart # マルチパートメール作成
from email.mime.base import MIMEBase           # 添付ファイル用
from email import encoders                     # Base64エンコーディング
from pathlib import Path                       # ファイルパス操作

# ==========================================
# 0. ページ設定とCSSスタイル定義
# ==========================================
# Streamlitのページ設定（タイトルとレイアウト）
st.set_page_config(page_title="性格タイプ診断", layout="wide")

# カスタムCSSによるデザイン調整
# - 7段階スライダーのカスタムスタイル（視覚的な円形ボタン表現）
# - レスポンシブデザイン対応
# - ダークモード対応
st.markdown("""
<style>
    /* ============================================
       ページ全体のスクロール挙動設定
       - スムーズスクロールを無効化し、即座に移動
       ============================================ */
    .main { scroll-behavior: auto !important; }
    
    /* ============================================
       質問文のスタイル
       - フォントサイズ: 1.4rem（見やすい大きさ）
       - 中央揃え、太字
       - 上下にマージンを設定
       ============================================ */
    .question-text {
        font-size: 1.4rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 30px;
        margin-top: 40px;
        color: #333;
    }
    /* ダークモード時の質問文の色を明るく調整 */
    @media (prefers-color-scheme: dark) { .question-text { color: #eee; } }

    /* ============================================
       診断用7段階スライダーのスタイル
       Streamlitのselect_sliderは内部的にラジオボタンUIを使用しているため、
       CSSでカスタマイズして円形ボタンとして表示
       - 7つの選択肢を横並びに表示
       - 中央から外側に向かってボタンサイズが大きくなる
       - 左側（紫系）: 同意しない方向
       - 右側（緑系）: 同意する方向
       ============================================ */
    /* 7選択肢のスライダーUIコンテナ */
    div[role="radiogroup"]:has(label:nth-of-type(7)) {
        display: flex;
        justify-content: center !important;
        align-items: center;
        gap: 8px;
        width: 100%;
        margin-bottom: 20px;
        flex-wrap: nowrap !important;
    }

    /* スライダーのラベルテキストを非表示（丸いボタンのみ表示するため） */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label > div[data-testid="stMarkdownContainer"] {
        display: none !important;
    }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label p { display: none !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label span { display: none !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label div p { display: none !important; }

    /* 各選択肢ボタンのクリック可能領域設定 */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label {
        cursor: pointer !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 選択肢の丸いボタン部分のスタイル（円形、ボーダー付き） */
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

    /* デフォルトの選択マーカー（内側の点）を非表示 */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label > div:first-child > div {
        display: none !important;
    }

    /* ============================================
       ボタンサイズ設定（リッカート尺度の視覚表現）
       - 中央（4番目）が最小: 18px（どちらでもない）
       - 外側に向かって大きくなる
       - 両端が最大: 42px（強く同意/強く不同意）
       ============================================ */
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

    /* ============================================
       色設定
       - 左側（1-3番目）: 紫系グラデーション（同意しない）
       - 中央（4番目）: グレー（どちらでもない）
       - 右側（5-7番目）: 緑系グラデーション（同意する）
       ============================================ */

    /* デフォルト状態の枠線色（淡い色） */
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(1) > div:first-child { border-color: #E1BEE7 !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(2) > div:first-child { border-color: #CE93D8 !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(3) > div:first-child { border-color: #BA68C8 !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(5) > div:first-child { border-color: #C8E6C9 !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(6) > div:first-child { border-color: #A5D6A7 !important; }
    div[role="radiogroup"]:has(label:nth-of-type(7)) label:nth-of-type(7) > div:first-child { border-color: #81C784 !important; }

    /* マウスホバー時の枠線色（より濃い色で強調） */
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

    /* 選択時のスタイル（背景色を塗りつぶし、スケールアップでアニメーション効果） */
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

    /* Streamlitデフォルトヘッダーを非表示 */
    header {visibility: hidden;}
    
    /* ボタンの中央寄せとスタイル調整 */
    .stButton { display: flex; justify-content: center; }
    .stButton button {
        width: 100%; max-width: 320px; font-weight: bold;
        padding: 10px 0; border-radius: 20px; margin: 0 auto;
    }
    
    /* 「同意する」ラベル（緑色、左寄せ） */
    .agree-label { 
        text-align: left; color: #4CAF50; font-weight: bold; font-size: 1.15rem; padding-top: 5px; 
    }
    /* 「同意しない」ラベル（紫色、右寄せ） */
    .disagree-label { 
        text-align: right; color: #8E24AA; font-weight: bold; font-size: 1.15rem; padding-top: 5px; 
    }

    /* 性別選択セクションの背景スタイル（薄いグレー背景、角丸） */
    .gender-section { background-color: rgba(128, 128, 128, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    
    /* 画像のレンダリング設定（ピクセルアート用の鮮明な表示） */
    img.pixelated { image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges; }
    
    /* モバイル対応: 画面幅640px以下でスライダーボタンの間隔を調整 */
    @media (max-width: 640px) { div[data-testid="stForm"] div[role="radiogroup"] { gap: 8px; } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 質問データベース（バランス調整済み: 60問）
# ==========================================
"""
質問データの構造:
- text: 質問文（日本語）
- axis: 測定する軸（Mind/Energy/Nature/Tactics/Identity）
- weight: スコアの重み（+1: 肯定的回答が軸の左側、-1: 肯定的回答が軸の右側）

各軸の説明:
- Mind: 意識の向き (E:外向型 vs I:内向型)
- Energy: 情報の取り入れ方 (N:直感型 vs S:現実型)
- Nature: 判断の基準 (F:感情型 vs T:思考型)
- Tactics: 生活スタイル (J:計画型 vs P:探索型)
- Identity: 自己認識 (A:自己主張型 vs T:慎重型)
"""
questions_data = [
    # ============================================
    # Mind軸: 意識 (E:外向型 vs I:内向型)
    # 社会的な相互作用への態度を測定
    # weight=1: 外向的傾向を示す質問
    # weight=-1: 内向的傾向を示す質問
    # ============================================
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

    # ============================================
    # Energy軸: エネルギー (N:直感型 vs S:現実型)
    # 情報の取り入れ方・思考の傾向を測定
    # weight=1: 直感的・抽象的思考の傾向
    # weight=-1: 現実的・具体的思考の傾向
    # ============================================
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

    # ============================================
    # Nature軸: 気質 (F:感情型 vs T:思考型)
    # 意思決定の基準を測定
    # weight=1: 感情・人間関係を重視する傾向
    # weight=-1: 論理・客観性を重視する傾向
    # ============================================
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

    # ============================================
    # Tactics軸: 戦術 (J:計画型 vs P:探索型)
    # 日常生活や仕事のスタイルを測定
    # weight=1: 計画的・組織的な傾向
    # weight=-1: 柔軟・即興的な傾向
    # ============================================
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

    # ============================================
    # Identity軸: アイデンティティ (A:自己主張型 vs T:慎重型)
    # 自信の度合い・ストレス耐性を測定
    # weight=1: 自信がある・楽観的な傾向
    # weight=-1: 慎重・心配しやすい傾向
    # ============================================
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

# 各質問に一意のID（インデックス番号）を付与
# これにより回答の保存・取得が容易になる
for i, q in enumerate(questions_data):
    q['id'] = i

# ==========================================
# 2. セッション状態管理と診断ロジック
# ==========================================
"""
Streamlitのsession_stateを使用して、ユーザーの回答状態を保持
- finished: 診断完了フラグ
- answers: 各質問への回答（-3〜+3の7段階）
- gender_input: 性別の回答
- user_name: ユーザー名
- current_page: 現在表示中のページ番号
"""

# 診断完了フラグの初期化（Falseで診断画面を表示）
if 'finished' not in st.session_state:
    st.session_state.finished = False

# 7段階のリッカート尺度オプション
# -3: 強く同意しない, -2: 同意しない, -1: やや同意しない
#  0: どちらでもない
# +1: やや同意する, +2: 同意する, +3: 強く同意する
OPTIONS = [-3, -2, -1, 0, 1, 2, 3]

# 回答データの初期化（全問0（どちらでもない）で開始）
if 'answers' not in st.session_state:
    st.session_state.answers = {i: 0 for i in range(len(questions_data))}
# 性別の初期値（「回答しない」を選択した状態）
if 'gender_input' not in st.session_state:
    st.session_state.gender_input = "回答しない"
# ユーザー名の初期値（空文字）
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
# 現在のページ番号（0から開始）
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

# 初回アクセス時の初期化処理
# ブラウザのリロード時など、セッション開始時に全ての状態をクリーンにリセット
if 'initialized_once' not in st.session_state:
    st.session_state.initialized_once = True
    st.session_state.finished = False
    st.session_state.answers = {i: 0 for i in range(len(questions_data))}


def calculate_result():
    """
    診断結果を計算する関数
    
    処理の流れ:
    1. 全ての回答を正規化（不正な値は0に修正）
    2. 各軸（Mind/Energy/Nature/Tactics/Identity）のスコアを集計
    3. スコアを百分率に変換
    4. 各軸の優勢な傾向を判定して性格タイプコードを生成
    
    Returns:
        tuple: (result_type, details)
            - result_type: 性格タイプコード（例: "ENFJ-A"）
            - details: 各軸の詳細情報（傾向名、百分率、アルファベット）
    """
    """
    診断結果を計算する関数
    
    処理の流れ:
    1. 全ての回答を正規化（不正な値は0に修正）
    2. 各軸（Mind/Energy/Nature/Tactics/Identity）のスコアを集計
    3. スコアを百分率に変換
    4. 各軸の優勢な傾向を判定して性格タイプコードを生成
    
    Returns:
        tuple: (result_type, details)
            - result_type: 性格タイプコード（例: "ENFJ-A"）
            - details: 各軸の詳細情報（傾向名、百分率、アルファベット）
    """
    # ステップ1: 回答値の正規化（範囲外の値は0にリセット）
    for q in questions_data:
        qid = q['id']
        val = st.session_state.answers.get(qid, 0)
        if val not in OPTIONS:
            val = 0
        st.session_state.answers[qid] = int(val)

    # 各軸のスコアを格納する辞書（初期値0）
    scores = {"Mind": 0, "Energy": 0, "Nature": 0, "Tactics": 0, "Identity": 0}
    # 各軸の最大可能スコア（百分率計算用）
    max_scores = {"Mind": 0, "Energy": 0, "Nature": 0, "Tactics": 0, "Identity": 0}

    # ステップ2: 各質問の回答からスコアを集計
    for q in questions_data:
        qid = q['id']
        val = st.session_state.answers.get(qid, 0)
        axis = q.get("axis")
        if axis not in scores: continue
        # スコア = 回答値 × 重み（重みが-1の質問は反転）
        scores[axis] += val * q["weight"]
        # 最大スコア = 全質問が+3または-3で回答された場合の合計
        max_scores[axis] += 3 * abs(q["weight"])

    # 性格タイプコード（例: ENFJ-A）を構築
    result_type = ""
    # 各軸の詳細情報を格納
    details = {}

    def axis_letter_and_pct(score, max_score, pos_letter, neg_letter):
        """
        軸のスコアから性格タイプの文字と百分率を計算する内部関数
        
        Args:
            score: 該当軸の合計スコア
            max_score: 該当軸の最大可能スコア
            pos_letter: 正方向（左側）の性格タイプ文字（例: E, N, F, J, A）
            neg_letter: 負方向（右側）の性格タイプ文字（例: I, S, T, P, T）
        
        Returns:
            tuple: (letter, pct) - 優勢な傾向の文字と百分率
        """
        """
        軸のスコアから性格タイプの文字と百分率を計算する内部関数
        
        Args:
            score: 該当軸の合計スコア
            max_score: 該当軸の最大可能スコア
            pos_letter: 正方向（左側）の性格タイプ文字（例: E, N, F, J, A）
            neg_letter: 負方向（右側）の性格タイプ文字（例: I, S, T, P, T）
        
        Returns:
            tuple: (letter, pct) - 優勢な傾向の文字と百分率
        """
        # 最大スコアが0の場合（質問がない場合）はデフォルト値を返す
        if max_score == 0: return pos_letter, 0
        
        # スコアを0〜100%の範囲に正規化
        # score = -max_score → 0%, score = 0 → 50%, score = +max_score → 100%
        left_pct = ((score + max_score) / (2 * max_score)) * 100
        left_pct = min(100, max(0, left_pct))  # 0〜100の範囲にクリップ
        
        # 優勢な傾向を判定
        if left_pct > (100 - left_pct):
            # 左側（正方向）が優勢
            letter = pos_letter
            pct = int(round(left_pct))
        elif (100 - left_pct) > left_pct:
            # 右側（負方向）が優勢
            letter = neg_letter
            pct = int(round(100 - left_pct))
        else:
            # 同点の場合、スコアの符号で決定
            letter = pos_letter if score >= 0 else neg_letter
            pct = int(round(left_pct))
        return letter, pct

    # ステップ3: 各軸の結果を計算して性格タイプコードを構築
    
    # Mind軸: E(外向型) vs I(内向型)
    letter, pct = axis_letter_and_pct(scores["Mind"], max_scores["Mind"], "E", "I")
    result_type += letter
    details["Mind"] = {"trait": "外向型" if letter == "E" else "内向型", "pct": pct, "letter": letter}

    # Energy軸: N(直感型) vs S(現実型)
    letter, pct = axis_letter_and_pct(scores["Energy"], max_scores["Energy"], "N", "S")
    result_type += letter
    details["Energy"] = {"trait": "直感型" if letter == "N" else "現実型", "pct": pct, "letter": letter}

    # Nature軸: F(感情型) vs T(思考型)
    letter, pct = axis_letter_and_pct(scores["Nature"], max_scores["Nature"], "F", "T")
    result_type += letter
    details["Nature"] = {"trait": "感情型" if letter == "F" else "思考型", "pct": pct, "letter": letter}

    # Tactics軸: J(計画型) vs P(探索型)
    letter, pct = axis_letter_and_pct(scores["Tactics"], max_scores["Tactics"], "J", "P")
    result_type += letter
    details["Tactics"] = {"trait": "計画型" if letter == "J" else "探索型", "pct": pct, "letter": letter}

    # Identity軸: A(自己主張型) vs T(慎重型)（ハイフン区切りで追加）
    letter, pct = axis_letter_and_pct(scores["Identity"], max_scores["Identity"], "A", "T")
    result_type += "-" + letter  # 例: ENFJ-A のようにハイフンで区切る
    details["Identity"] = {"trait": "自己主張型" if letter == "A" else "慎重型", "pct": pct, "letter": letter}

    return result_type, details


def generate_ai_context(result_type, details, gender):
    """
    AIへのプロンプト用のコンテキストデータを生成する関数
    
    診断結果をJSON形式で構造化し、AI（LLMなど）への入力データとして利用可能な形式に変換
    
    Args:
        result_type: 性格タイプコード（例: "ENFJ-A"）
        details: 各軸の詳細情報
        gender: 性別
    
    Returns:
        str: JSON形式の文字列
    """
    prompt_data = {
        "target_persona": {
            "mbti_type": result_type,   # 性格タイプコード
            "gender": gender,            # 性別
            "traits": details            # 各軸の詳細スコア
        }
    }
    # 日本語を含むため ensure_ascii=False で出力
    return json.dumps(prompt_data, ensure_ascii=False)

# ==========================================
# メール送信機能
# ==========================================
def send_result_email(to_email, result_type, details, gender, user_name, csv_data):
    """
    診断結果をメールで送信する関数
    
    Gmail SMTPサーバーを使用して、診断結果とCSVファイルをメール送信
    
    Args:
        to_email: 送信先メールアドレス
        result_type: 性格タイプコード（例: "ENFJ-A"）
        details: 各軸の詳細情報
        gender: 性別
        user_name: ユーザー名
        csv_data: 添付するCSVデータ（バイナリ）
    
    Returns:
        tuple: (success, message)
            - success: 送信成功ならTrue、失敗ならFalse
            - message: 結果メッセージ
    
    注意:
        環境変数またはStreamlit secretsに以下の設定が必要:
        - SENDER_EMAIL: 送信元メールアドレス
        - SENDER_PASSWORD: アプリパスワード（Gmailの場合）
    """
    # Gmail SMTPサーバー設定
    SMTP_SERVER = "smtp.gmail.com"  # GmailのSMTPサーバー
    SMTP_PORT = 587                  # TLS用ポート番号
    
    def get_secret(key):
        """
        認証情報を安全に取得する内部関数
        
        取得優先順位:
        1. Streamlit secrets（st.secrets）- 本番環境推奨
        2. 環境変数（os.environ）- 開発環境用
        
        Args:
            key: 取得するシークレットのキー名
        
        Returns:
            str: シークレットの値、見つからない場合はNone
        """
        # Streamlit secretsから取得を試行（本番環境）
        try:
            if key in st.secrets:
                return st.secrets[key]
        except:
            pass
        # 環境変数から取得（ローカル開発環境）
        return os.environ.get(key)
    
    # 送信元メールの認証情報を取得
    SENDER_EMAIL = get_secret("SENDER_EMAIL")      # 送信元メールアドレス
    SENDER_PASSWORD = get_secret("SENDER_PASSWORD") # アプリパスワード
    
    # 認証情報が設定されていない場合はエラーを返す
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return False, "メール設定が見つかりません。環境変数 SENDER_EMAIL / SENDER_PASSWORD を設定してください"
    
    # ユーザー名の表示用文字列（空の場合は「未入力」と表示）
    display_name = user_name if user_name else "未入力"
    
    # メール本文に表示する特性情報のテキストを生成
    traits_text = ""
    # 軸名の英語→日本語変換マッピング
    trait_labels = {
        "Mind": "意識",
        "Energy": "エネルギー",
        "Nature": "気質",
        "Tactics": "戦術",
        "Identity": "アイデンティティ"
    }
    # 各軸の結果を日本語でフォーマット
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
    
    # MIMEマルチパートメッセージを作成（本文 + 添付ファイル）
    msg = MIMEMultipart()
    msg['Subject'] = f'【性格タイプ診断結果】{display_name}さん: {result_type}'  # 件名
    msg['From'] = SENDER_EMAIL     # 送信元
    msg['To'] = to_email           # 送信先
    # 本文をUTF-8でエンコードして添付
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # CSVファイルを添付ファイルとして追加
    csv_attachment = MIMEBase('application', 'octet-stream')   # バイナリデータとして設定
    csv_attachment.set_payload(csv_data)                       # CSVデータをペイロードに設定
    encoders.encode_base64(csv_attachment)                     # Base64エンコード
    
    # 日本語ファイル名をRFC 2231形式でエンコード（メールクライアントの互換性確保）
    from urllib.parse import quote
    # ファイル名を生成（ユーザー名と性格タイプを含む）
    csv_filename = f'personality_{user_name}_{result_type}.csv' if user_name else f'personality_user_{result_type}.csv'
    encoded_filename = quote(csv_filename, safe='')  # URLエンコード
    # 添付ファイルのヘッダーを設定
    csv_attachment.add_header(
        'Content-Disposition',
        'attachment',
        filename=('utf-8', '', csv_filename)  # UTF-8エンコードのファイル名
    )
    msg.attach(csv_attachment)  # メッセージに添付
    
    # SMTPサーバーに接続してメールを送信
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()                              # TLS暗号化を開始
            server.login(SENDER_EMAIL, SENDER_PASSWORD)    # 認証
            server.send_message(msg)                       # メール送信
        return True, "メールを送信しました！"
    except smtplib.SMTPAuthenticationError:
        # 認証失敗（メールアドレスまたはパスワードが間違っている）
        return False, "認証エラー: メールアドレスまたはパスワードを確認してください"
    except smtplib.SMTPException as e:
        # その他のSMTP関連エラー
        return False, f"送信エラー: {str(e)}"
    except Exception as e:
        # 予期しないエラー
        return False, f"エラーが発生しました: {str(e)}"

# ==========================================
# 16タイプ分類情報の取得
# ==========================================
def get_type_info(result_type):
    """
    性格タイプコードから詳細情報を取得する関数
    
    16種類の性格タイプそれぞれに対応する：
    - グループ名（日本語の呼称）
    - テーマカラー
    - キャラクター画像パス
    を返す
    
    Args:
        result_type: 性格タイプコード（例: "ENFJ-A"）
    
    Returns:
        dict: タイプ情報 {"group": グループ名, "color": 色コード, "image": 画像パス}
    """
    # ハイフン以前の4文字を基本タイプとして抽出（例: "ENFJ-A" → "ENFJ"）
    base_type = result_type.split("-")[0]
    # スクリプトファイルのディレクトリを基準パスとして取得
    base_dir = Path(__file__).parent
    
    # 16タイプを4つのグループに分け、それぞれテーマカラーを設定
    color_nt = "#8867c0"  # 分析家グループ（紫）: INTJ, INTP, ENTJ, ENTP
    color_nf = "#41c46c"  # 外交官グループ（緑）: INFJ, INFP, ENFJ, ENFP
    color_sj = "#4298b4"  # 番人グループ　（青）: ISTJ, ISFJ, ESTJ, ESFJ
    color_sp = "#e4ae3a"  # 探検家グループ（黄）: ISTP, ISFP, ESTP, ESFP

    # 16タイプの詳細マッピング
    # 各タイプに日本語の呼称とグループカラーを設定
    type_map = {
        # 分析家グループ（NT型）- 紫
        "INTJ": {"group": "建築家", "color": color_nt},      # 戦略的思考の持ち主
        "INTP": {"group": "論理学者", "color": color_nt},    # 論理的な発明家
        "ENTJ": {"group": "指揮官", "color": color_nt},      # 大胆なリーダー
        "ENTP": {"group": "討論者", "color": color_nt},      # 知的な挑戦者
        # 外交官グループ（NF型）- 緑
        "INFJ": {"group": "提唱者", "color": color_nf},      # 静かなる理想主義者
        "INFP": {"group": "仲介者", "color": color_nf},      # 詩的な理想主義者
        "ENFJ": {"group": "主人公", "color": color_nf},      # カリスマ的リーダー
        "ENFP": {"group": "広報運動家", "color": color_nf},  # 熱意あふれる自由人
        # 番人グループ（SJ型）- 青
        "ISTJ": {"group": "管理者", "color": color_sj},      # 責任感の強い現実主義者
        "ISFJ": {"group": "擁護者", "color": color_sj},      # 献身的な保護者
        "ESTJ": {"group": "幹部", "color": color_sj},        # 秩序を重んじる管理者
        "ESFJ": {"group": "領事官", "color": color_sj},      # 思いやりのある社交家
        # 探検家グループ（SP型）- 黄
        "ISTP": {"group": "巨匠", "color": color_sp},        # 大胆な職人
        "ISFP": {"group": "冒険家", "color": color_sp},      # 柔軟な芸術家
        "ESTP": {"group": "起業家", "color": color_sp},      # エネルギッシュな起業家
        "ESFP": {"group": "エンターテイナー", "color": color_sp},  # 自発的なパフォーマー
    }
    # マッピングから情報を取得（見つからない場合はデフォルト値）
    info = type_map.get(base_type, {"group": "診断結果", "color": "#333"})
    # キャラクター画像のパスを設定（images/タイプ名.png）
    info["image"] = str((base_dir / "images" / f"{base_type.lower()}.png").as_posix())
    return info

# ==========================================
# 3. UI表示コンポーネント
# ==========================================

def display_progress_bar(label, left_text, right_text, percentage, is_left_dominant, color="#00ACC1"):
    """
    カスタムプログレスバーを表示する関数
    
    診断結果の各軸を視覚的に表現するプログレスバーを描画
    優勢な傾向の方向に塗りつぶし、マーカーで現在位置を表示
    
    Args:
        label: 軸のラベル（例: "意識 (Mind)"）
        left_text: 左側の傾向名（例: "外向型 (E)"）
        right_text: 右側の傾向名（例: "内向型 (I)"）
        percentage: 優勢な傾向の百分率（0-100）
        is_left_dominant: Trueなら左側が優勢、Falseなら右側が優勢
        color: プログレスバーの色（16進数カラーコード）
    """
    """
    カスタムプログレスバーを表示する関数
    
    診断結果の各軸を視覚的に表現するプログレスバーを描画
    優勢な傾向の方向に塗りつぶし、マーカーで現在位置を表示
    
    Args:
        label: 軸のラベル（例: "意識 (Mind)"）
        left_text: 左側の傾向名（例: "外向型 (E)"）
        right_text: 右側の傾向名（例: "内向型 (I)"）
        percentage: 優勢な傾向の百分率（0-100）
        is_left_dominant: Trueなら左側が優勢、Falseなら右側が優勢
        color: プログレスバーの色（16進数カラーコード）
    """
    # 百分率を0-100の範囲にクリップ
    pct = max(0, min(100, int(percentage)))
    # 優勢な傾向のテキストを選択
    dominant_text = left_text if is_left_dominant else right_text
    
    # ラベルと百分率をヘッダーとして表示
    st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'><strong>{label}</strong><div style='font-weight:bold;'>{dominant_text} {pct}%</div></div>", unsafe_allow_html=True)
    
    # 3カラムレイアウト: 左ラベル | プログレスバー | 右ラベル
    col_l, col_bar, col_r = st.columns([2, 6, 2])
    with col_l:
        # 左側ラベル（優勢ならテーマカラー、そうでなければグレー）
        left_color = color if is_left_dominant else "#888"
        st.markdown(f"<div style='text-align:right; color:{left_color}; font-weight:bold;'>{left_text}</div>", unsafe_allow_html=True)
    with col_bar:
        # プログレスバーの描画設定
        fill_color = color
        fill_dir = 'to right' if is_left_dominant else 'to left'  # 塗りつぶし方向  # 塗りつぶし方向
        
        # マーカー位置と塗りつぶしスタイルを計算
        if is_left_dominant:
            # 左が優勢: 左から右へ塗りつぶし
            marker_left = f"calc({pct}% - 8px)"      # マーカーの左位置
            fill_style = f"left:0; width:{pct}%;"   # 左端から塗りつぶし
        else:
            # 右が優勢: 右から左へ塗りつぶし
            marker_left = f"calc({100 - pct}% - 8px)"  # マーカーの左位置
            fill_style = f"right:0; width:{pct}%;"     # 右端から塗りつぶし

        # HTMLによるカスタムプログレスバーの描画
        bar_html = f"""
        <div style='position:relative; width:100%; height:18px; background:#eee; border-radius:10px; overflow:visible;'>
            <div style='position:absolute; top:0; bottom:0; {fill_style} background:linear-gradient({fill_dir}, {fill_color}, {fill_color}); border-radius:10px 10px 10px 10px;'></div>
            <div style='position:absolute; top:50%; left:{marker_left}; transform:translateY(-50%); width:16px; height:16px; border-radius:50%; background:#fff; border:3px solid #444; box-shadow:0 2px 4px rgba(0,0,0,0.2);'></div>
        </div>
        """
        st.markdown(bar_html, unsafe_allow_html=True)
    with col_r:
        # 右側ラベル（優勢ならテーマカラー、そうでなければグレー）
        right_color = color if not is_left_dominant else "#888"
        st.markdown(f"<div style='text-align:left; color:{right_color}; font-weight:bold;'>{right_text}</div>", unsafe_allow_html=True)


def render_result():
    """
    診断結果画面を表示する関数
    
    以下の要素を表示:
    1. 祝福アニメーション（バルーン）
    2. 性格タイプのタイトルとキャラクター画像
    3. 5つの軸のプログレスバー
    4. メール送信フォーム
    5. CSVダウンロードボタン
    6. やり直しボタン
    """
    # 祝福のバルーンアニメーションを表示
    st.balloons()
    # 診断結果を計算
    result_type, details = calculate_result()
    # セッションから性別を取得
    gender = st.session_state.get("gender_input", "回答しない")
    # AI用のコンテキストデータを生成
    ai_context = generate_ai_context(result_type, details, gender)

    # タイプ情報（グループ名、テーマカラー、画像）を取得
    type_info = get_type_info(result_type)
    theme_color = type_info["color"]     # テーマカラー
    group_name = type_info["group"]       # グループ名（例: "主人公"）
    image_filename = type_info["image"]   # キャラクター画像パス

    # 結果のタイトル表示
    st.markdown("<h1 style='text-align: center;'>あなたの性格タイプ</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: {theme_color}; margin-bottom: 0;'>{group_name}</h3>", unsafe_allow_html=True)

    st.markdown(f"<h2 style='text-align: center; color: {theme_color}; font-size: 4em; margin-top: 0;'>{result_type}</h2>", unsafe_allow_html=True)

    # キャラクター画像を中央に配置（3カラムの中央カラムを使用）
    img_col = st.columns([1, 1, 1])[1]
    with img_col:
        if image_filename:
            try:
                st.image(image_filename, width=220)
            except:
                st.write("No Image")  # 画像読み込み失敗時
        else:
            st.write("No Image")  # 画像パスが空の場合
    
    st.markdown("---")  # 区切り線
    
    # 各軸のプログレスバーに使用する色を定義
    colors = {
        "Mind": "#00ACC1",      # ティール（青緑）- 意識の軸
        "Energy": "#FFA726",    # オレンジ - エネルギーの軸
        "Nature": "#66BB6A",    # グリーン - 気質の軸
        "Tactics": "#7E57C2",   # パープル - 戦術の軸
        "Identity": "#EF5350"   # レッド - アイデンティティの軸
    }
    
    # 5つの軸それぞれのプログレスバーを表示
    # Mind軸: 外向型(E) vs 内向型(I)
    display_progress_bar("意識 (Mind)", "外向型 (E)", "内向型 (I)", details["Mind"]["pct"], details["Mind"]["letter"] == "E", color=colors["Mind"])
    # Energy軸: 直感型(N) vs 現実型(S)
    display_progress_bar("エネルギー (Energy)", "直感型 (N)", "現実型 (S)", details["Energy"]["pct"], details["Energy"]["letter"] == "N", color=colors["Energy"])
    # Nature軸: 道理型(F) vs 論理型(T)
    display_progress_bar("気質 (Nature)", "道理型 (F)", "論理型 (T)", details["Nature"]["pct"], details["Nature"]["letter"] == "F", color=colors["Nature"])
    # Tactics軸: 計画型(J) vs 探索型(P)
    display_progress_bar("戦術 (Tactics)", "計画型 (J)", "探索型 (P)", details["Tactics"]["pct"], details["Tactics"]["letter"] == "J", color=colors["Tactics"])
    # Identity軸: 自己主張型(A) vs 慎重型(T)
    display_progress_bar("アイデンティティ (Identity)", "自己主張型 (A)", "慎重型 (T)", details["Identity"]["pct"], details["Identity"]["letter"] == "A", color=colors["Identity"])

    st.markdown("---")  # 区切り線  # 区切り線
    
    # ============================================
    # メール送信セクション
    # ============================================
    st.markdown("### 📧 結果をメールで送信")
    # 固定の送信先メールアドレス
    recipient_email = "soma@sdxai.jp.honda"
    st.info(f"送信先: {recipient_email}")
    
    # 回答者名入力フィールド（結果ページでも編集可能）
    user_name = st.text_input(
        "回答者名（必須）",
        value=st.session_state.get("user_name", ""),
        placeholder="例: 本田宗一郎",
        key="user_name_result"
    )
    # 入力値をセッションに保存
    st.session_state.user_name = user_name
    
    # ============================================
    # CSVデータの生成
    # ============================================
    # 診断結果をCSV形式で構造化
    csv_data = {
        "User_Name": [user_name if user_name else "未入力"],  # ユーザー名
        "Result_Type": [result_type],                          # 性格タイプコード
        "Gender": [gender],                                     # 性別
        "AI_Prompt_JSON": [ai_context]                          # AI用コンテキスト
    }
    # 各軸の詳細データを追加
    for key, val in details.items():
        csv_data[f"{key}_Trait"] = [val["trait"]]   # 傾向名
        csv_data[f"{key}_Pct"] = [val["pct"]]       # 百分率
    # 全質問への回答データを追加（Q1〜Q60）
    for q in questions_data:
        qid = q["id"]
        val = st.session_state.answers.get(qid, 0)
        csv_data[f"Q{qid+1}"] = [val]  # Qは1から始まる番号
    # DataFrameに変換してCSVバイナリを生成（日本語対応のためUTF-8 BOM付き）
    df = pd.DataFrame(csv_data)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    
    # メール送信ボタン
    if st.button("📧 診断結果をメールで送信", type="primary", use_container_width=True):
        if not user_name:
            # 名前が未入力の場合はエラー表示
            st.error("お名前を入力してください。")
        else:
            # 送信中はスピナーを表示
            with st.spinner("送信中..."):
                success, message = send_result_email(recipient_email, result_type, details, gender, user_name, csv)
                if success:
                    st.success(message)  # 送信成功メッセージ
                else:
                    st.error(message)    # エラーメッセージ

    # ============================================
    # CSVダウンロードセクション
    # ============================================
    st.markdown("### 📥 データのダウンロード")
    # ファイル名用にスペースをアンダースコアに置換
    safe_name = user_name.replace(' ', '_') if user_name else 'user'
    # ダウンロードボタンを表示
    st.download_button("診断結果CSVをダウンロード", data=csv, file_name=f'personality_{safe_name}_{result_type}.csv', mime='text/csv')
    
    st.markdown("---")  # 区切り線
    
    # ============================================
    # やり直しボタン
    # ============================================
    if st.button("最初からやり直す", use_container_width=True):
        # 全ての状態をリセット
        st.session_state.answers = {i: 0 for i in range(len(questions_data))}  # 回答をクリア
        st.session_state.finished = False   # 完了フラグをリセット
        st.session_state.current_page = 0   # 最初のページに戻る
        st.rerun()  # ページを再読み込み


# ==========================================
# 4. メインエントリーポイント
# ==========================================
def main():
    """
    アプリケーションのメイン関数
    
    診断の状態に応じて以下を表示:
    - 未完了: 質問フォーム（ページング形式）
    - 完了済み: 診断結果画面
    """
    # 診断が完了している場合は結果画面を表示
    if st.session_state.finished:
        render_result()
        return

    # ============================================
    # 診断画面（質問フォーム）
    # ============================================
    st.title("🧩 性格タイプ診断")
    
    # 説明メッセージ
    st.info("以下の60問の質問に対し、あなたの感覚に最も近いものを選択してください。")
    
    # ============================================
    # 基本情報入力セクション
    # ============================================
    st.markdown("<div class='gender-section'>", unsafe_allow_html=True)
    st.markdown("### 👤 基本情報")
    
    # ユーザー名入力フィールド
    st.session_state.user_name = st.text_input(
        "お名前（必須）",
        value=st.session_state.user_name,
        placeholder="例: 本田宗一郎",
        key="user_name_input"
    )
    
    # 性別選択ラジオボタン（横並び表示）
    st.session_state.gender_input = st.radio(
        "性別（任意）", 
        ["男性", "女性", "その他", "回答しない"], 
        horizontal=True,  # 横並び表示
        key="gender_radio_main"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")  # 区切り線  # 区切り線

    # ============================================
    # ページング設定
    # 60問を6問ずつ10ページに分割して表示
    # ============================================
    questions_per_page = 6  # 1ページあたりの質問数
    total_pages = math.ceil(len(questions_data) / questions_per_page)  # 総ページ数
    
    # 現在のページ番号を取得し、範囲内にクリップ
    current_page = st.session_state.current_page
    current_page = max(0, min(total_pages - 1, current_page))
    st.session_state.current_page = current_page

    # 現在のページに表示する質問のインデックス範囲を計算
    start_idx = current_page * questions_per_page    # 開始インデックス
    end_idx = min(start_idx + questions_per_page, len(questions_data))  # 終了インデックス
    
    # ページ番号とプログレスバーを表示
    st.markdown(f"#### 質問ページ {current_page + 1} / {total_pages}")
    st.progress((current_page + 1) / total_pages)  # 進捗バー  # 進捗バー

    # ============================================
    # 質問一覧の表示（スライダーで7段階選択）
    # ============================================
    for q in questions_data[start_idx:end_idx]:
        # 質問文を表示
        st.markdown(f"<div class='question-text'>{q['text']}</div>", unsafe_allow_html=True)
        
        # 3カラムレイアウト: 「同意しない」ラベル | スライダー | 「同意する」ラベル
        c1, c2, c3 = st.columns([1.5, 7, 1.5])

        with c1:
            # 左側のラベル「同意しない」
            st.markdown("<div class='disagree-label'>同意しない</div>", unsafe_allow_html=True)
        with c2:
            # 中央にスライダー（7段階選択）
            key = f"slider_{q['id']}"  # 一意のキー
            qid = q['id']

            # 現在の回答値を取得（初期値は0）
            current_val = st.session_state.answers.get(qid, 0)
            if current_val not in OPTIONS:
                current_val = 0  # 不正な値はリセット

            # 7段階のスライダーを表示
            selected = st.select_slider(
                f"q_{qid}",              # ラベル（非表示）
                options=OPTIONS,          # -3〜+3の選択肢
                value=current_val,        # 現在の値
                label_visibility="collapsed",  # ラベルを非表示
                key=key
            )

            # 選択値をセッションに保存
            st.session_state.answers[qid] = int(selected)

        with c3:
            # 右側のラベル「同意する」
            st.markdown("<div class='agree-label'>同意する</div>", unsafe_allow_html=True)

        # 質問間の余白（区切り線の代わりにスペースを確保）
        st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)  # 余白
    
    # ============================================
    # ページナビゲーションボタン
    # ============================================
    nav_left, nav_mid, nav_right = st.columns([1, 2, 1])
    with nav_left:
        # 「前へ」ボタン（最初のページでは無効）
        if st.button("＜ 前へ", disabled=current_page == 0, use_container_width=True):
            st.session_state.current_page = max(0, current_page - 1)
            st.rerun()  # ページを再読み込み
    with nav_right:
        # 「次へ」ボタン（最後のページでは無効）
        if st.button("次へ ＞", disabled=current_page >= total_pages - 1, use_container_width=True):
            st.session_state.current_page = min(total_pages - 1, current_page + 1)
            st.rerun()  # ページを再読み込み  # ページを再読み込み

    # ============================================
    # 診断完了ボタン（最終ページのみ表示）
    # ============================================
    if current_page == total_pages - 1:
        _, submit_col, _ = st.columns([1, 2, 1])  # 中央に配置
        with submit_col:
            if st.button("診断結果を見る ＞", type="primary", use_container_width=True):
                # 全ての回答値を正規化（不正値は0にリセット）
                for q in questions_data:
                    qid = q["id"]
                    val = st.session_state.answers.get(qid, 0)
                    if val not in OPTIONS:
                        val = 0
                    st.session_state.answers[qid] = int(val)
                # 診断完了フラグを立てて結果画面へ
                st.session_state.finished = True
                st.rerun()  # ページを再読み込みして結果画面を表示


# ==========================================
# アプリケーション起動
# ==========================================
# このファイルが直接実行された場合にmain()を呼び出す
if __name__ == "__main__":
    main()
