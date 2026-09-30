from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 기존 AI 함수 임포트 (DB 연동은 빼고 AI만 남김)
from ai_service import analyze_survey_answers

app = FastAPI(title="Stockmaster API (Demo Mode)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# [핵심] 시연용 메모리 DB (서버가 켜져 있는 동안만 임시 기억)
# -------------------------------------------------------------
DEMO_STORAGE = {}

# -------------------------------------------------------------
# 1. AI 설문 분석 (분석 후 메모리에 덮어쓰기)
# -------------------------------------------------------------
@app.post("/api/ai/survey")
def handle_survey_analysis(request: Dict[str, Any]):
    try:
        # AI로 데이터 넘겨서 결과 받기
        result = analyze_survey_answers(request)
        
        # 마이페이지에서 다시 볼 수 있도록 메모리(DEMO_STORAGE)에 결과 보관
        DEMO_STORAGE["latest_result"] = result
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/survey")
def get_survey_history():
    # 프론트엔드에게 "아직 과거 설문 기록이 없어"라고 빈 배열을 돌려줍니다.
    return []

# -------------------------------------------------------------
# 2. 마이페이지용 결과 불러오기 (메모리에서 꺼내기)
# -------------------------------------------------------------
@app.get("/api/ai/survey/latest")
def get_latest_survey():
    # 보관된 결과가 없으면 프론트엔드가 오해하지 않도록 404 에러 반환
    if "latest_result" not in DEMO_STORAGE:
        raise HTTPException(status_code=404, detail="저장된 설문 결과가 없습니다.")
        
    # 보관된 결과가 있으면 마이페이지로 전달
    return {
        "status": "success",
        "data": DEMO_STORAGE["latest_result"]
    }

# -------------------------------------------------------------
# 3. 가짜 로그인 / 회원가입 (가입 시 메모리 초기화)
# -------------------------------------------------------------
@app.post("/api/users/register")
def mock_register(payload: Dict[str, Any]):
    # 새 회원가입을 하면 프론트엔드 꼬임 방지를 위해 메모리를 싹 비움
    DEMO_STORAGE.clear()
    return {"msg": "회원가입 성공"}

@app.post("/api/users/login")
def mock_login(payload: Dict[str, Any]):
    DEMO_STORAGE.clear()
    return {
        "access_token": "mock_jwt_token_12345",
        "token_type": "bearer"
    }

@app.get("/api/users/me")
def mock_get_me():
    # 1. 기본 상태는 설문을 안 한 상태 (None)
    current_style = None
    
    # 2. 만약 설문을 완료해서 메모리(DEMO_STORAGE)에 결과가 있다면?
    if "latest_result" in DEMO_STORAGE:
        # AI가 분석해준 투자 성향(예: 위험중립형)을 꺼내옵니다.
        current_style = DEMO_STORAGE["latest_result"].get("investment_style", "위험중립형")

    return {
        "user_id": 1,
        "login_id": "rlawlsvy",
        "user_name": "김진표",
        "email": "a32088155@gmail.com",
        "investment_style": current_style  # 이제 고정된 값이 아니라 상황에 따라 바뀝니다!
    }

@app.get("/api/trading/accounts")
def mock_get_accounts():
    return [
        {
            "account_id": "acc_001",
            "balance": "10000000",
            "withdrawable_cash": "10000000"
        }
    ]