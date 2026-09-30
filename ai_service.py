import os
import json
from dotenv import load_dotenv

# 🚨 완전히 새로 바뀐 구글 최신 패키지 임포트 방식
from google import genai
from google.genai import types

load_dotenv()

# API 클라이언트 초기화 (새로운 방식)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CODE_MAP = {
    "MINUS_20": "-10% ~ -20% 손실 감수",
    "MINUS_10": "-10% 이내 손실 감수",
    "HIGH_RISK": "시장 평균을 뛰어넘는 고수익",
    # (필요한 코드 맵핑 계속 추가)
}

def analyze_survey_answers(payload: dict) -> dict:
    print("====================================")
    print("프론트가 보낸 데이터:", payload)
    print("====================================")

    # 1. 프론트엔드가 보낸 'answers' 배열 꺼내기
    answers_list = payload.get('answers', [])
    
    # 2. 배열 데이터를 q1, q2 형태로 예쁘게 정리하기
    q_dict = {}
    for item in answers_list:
        q_num = item.get('question_number')
        ans_text = item.get('selected_answer', '')
        if q_num:
            q_dict[f'q{q_num}'] = ans_text

    # 3. 정리된 데이터로 매핑 (기본값 설정)
    q1 = q_dict.get('q1', '전혀 없습니다')
    q2 = q_dict.get('q2', '여유 자금')
    q3 = q_dict.get('q3', '약간의 손실 감수')
    q4 = q_dict.get('q4', '원금 보존')
    q5 = q_dict.get('q5', '1~3년')
    q6 = q_dict.get('q6', '안정적 수익')

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
        # 모델 이름은 기본 1.5-flash로 원복합니다.
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"최종 AI 오류: {e}")
        # 프론트엔드가 에러 없이 다음 화면으로 넘어갈 수 있도록 기본 세팅
        return {"investor_type": "위험중립형", "risk_score": 50, "summary": "AI 분석 지연으로 기본 성향이 부여되었습니다.", "advice": "기본 성향으로 모의투자를 시작해보세요.", "learning_roadmap": ["주식 기초", "시장 지표 이해", "위험 관리"]}