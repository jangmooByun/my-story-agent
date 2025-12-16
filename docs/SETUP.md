# 설정 가이드

## 1. Ollama 설치

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
[ollama.com](https://ollama.com/download) 에서 설치 파일 다운로드

## 2. 모델 다운로드

### 추천 모델

| 모델 | 크기 | 용도 | 명령어 |
|------|------|------|--------|
| llama3.2:3b | 2GB | 경량, 빠른 처리 | `ollama pull llama3.2:3b` |
| mistral:7b | 4GB | 균형 잡힌 성능 | `ollama pull mistral:7b` |
| llama3.1:8b | 4.7GB | 높은 정확도 | `ollama pull llama3.1:8b` |

### 권장 사양

| 모델 크기 | 최소 RAM | 권장 RAM |
|-----------|----------|----------|
| 3B | 8GB | 16GB |
| 7B | 16GB | 32GB |
| 8B | 16GB | 32GB |

### 모델 다운로드
```bash
# 경량 모델 (추천 - 시작용)
ollama pull llama3.2:3b

# 또는 더 나은 성능
ollama pull mistral:7b
```

### Ollama 실행 확인
```bash
# 서버 시작 (백그라운드)
ollama serve

# 테스트
ollama run llama3.2:3b "Hello, world!"
```

## 3. Python 환경 설정

### 요구사항
- Python 3.11 이상

### 가상환경 생성
```bash
# venv 사용
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 또는 conda 사용
conda create -n agent-system python=3.11
conda activate agent-system
```

### 의존성 설치
```bash
pip install -e .
```

## 4. 환경 변수 설정

`.env.example`을 `.env`로 복사 후 수정:

```bash
cp .env.example .env
```

`.env` 내용:
```env
# Ollama 설정
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# 입출력 경로
INPUT_DIR=data/input
OUTPUT_DIR=data/output

# 로깅
LOG_LEVEL=INFO
```

## 5. Neo4j 설정 (선택)

결과를 직접 Neo4j에 로드하려면:

### Neo4j Desktop 설치
[neo4j.com/download](https://neo4j.com/download/) 에서 다운로드

### Docker로 실행
```bash
docker run \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 연결 정보 (선택적)
`.env`에 추가:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## 6. 설정 파일

`configs/settings.yaml`:

```yaml
# LLM 설정
llm:
  provider: ollama
  model: llama3.2:3b
  temperature: 0.7

# 에이전트 설정
agents:
  research:
    max_concepts_per_doc: 10
  analyst:
    similarity_threshold: 0.7
  writer:
    output_format: markdown  # markdown, csv, cypher

# 경로
paths:
  input: data/input
  output: data/output

# Neo4j (선택)
neo4j:
  enabled: false
  uri: bolt://localhost:7687
```

## 7. 설치 확인

```bash
# 전체 확인 스크립트
python -c "
import ollama
from langchain_ollama import OllamaLLM

# Ollama 연결 확인
client = ollama.Client()
models = client.list()
print(f'Ollama 연결 성공! 모델 수: {len(models[\"models\"])}')

# LangChain 연동 확인
llm = OllamaLLM(model='llama3.2:3b')
response = llm.invoke('Say hello in Korean')
print(f'LLM 응답: {response[:50]}...')

print('설정 완료!')
"
```

## 문제 해결

### Ollama 연결 실패
```bash
# Ollama 서비스 상태 확인
curl http://localhost:11434/api/tags

# 서비스 재시작
ollama serve
```

### 메모리 부족
- 더 작은 모델 사용: `llama3.2:1b`
- 또는 quantized 모델: `llama3.2:3b-q4_0`

### GPU 사용 안됨
```bash
# NVIDIA GPU 확인
nvidia-smi

# Ollama가 GPU 사용하는지 확인
ollama run llama3.2:3b --verbose
```
