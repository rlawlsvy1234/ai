import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2단계: 프론트엔드의 영문 코드를 한글로 바꿔주는 번역 사전
CODE_MAP = {
    "MINUS_20": "-10% ~ -20% 손실 감수",
    "MINUS_10": "-10% 이내 손실 감수",
    "HIGH_RISK": "시장 평균을 뛰어넘는 고수익",
    # 빈칸에 프론트엔드가 보내는 영문 코드를 계속 추가하시면 됩니다.
}

def analyze_survey_answers(answers: dict) -> dict:
    # 딕셔너리로 넘어온 데이터를 번역 사전을 거쳐 한글로 변환
    # (프론트엔드가 변수명을 q1, q2로 보낸다고 가정한 예시입니다)
    q1 = CODE_MAP.get(answers.get('q1', ''), answers.get('q1', '전혀 없음'))
    q2 = CODE_MAP.get(answers.get('q2', ''), answers.get('q2', '여유 자금'))
    q3 = CODE_MAP.get(answers.get('q3', ''), answers.get('q3', '약간의 손실 감수'))
    q4 = CODE_MAP.get(answers.get('q4', ''), answers.get('q4', '원금 보존'))
    q5 = CODE_MAP.get(answers.get('q5', ''), answers.get('q5', '1~3년'))
    q6 = CODE_MAP.get(answers.get('q6', ''), answers.get('q6', '안정적 수익'))

    prompt = f"""
    당신은 주식 모의투자 플랫폼의 금융 AI 전문가입니다.
    사용자의 설문 응답을 분석하여 최적의 투자 성향 프로필을 도출하세요.

    [사용자 설문 응답]
    1. 투자 경험: {q1}
    2. 자금 성격: {q2}
    3. 감당 가능한 손실 범위: {q3}
    4. 원금 보존 중요도: {q4}
    5. 예상 투자 기간: {q5}
    6. 투자 목표: {q6}

    [출력 규칙]
    - investor_type: 반드시 ["안정형", "안정추구형", "위험중립형", "적극투자형", "공격투자형"] 중 하나
    - risk_score: 0~100 사이의 정수
    - summary: 사용자 성향 요약 (1~2문장)
    - advice: 모의투자 실천 조언 (1~2문장)
    - learning_roadmap: 단계별 학습 주제 3가지 문자열 배열

    반드시 순수 JSON 포맷으로만 응답하세요.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"AI 오류: {e}")
        return {"investor_type": "위험중립형", "risk_score": 50, "summary": "분석 오류입니다.", "advice": "다시 시도해주세요.", "learning_roadmap": []}