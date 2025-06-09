FROM python:3.10-slim

# 작업 디렉토리
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 실행 (uvicorn 사용 시)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]