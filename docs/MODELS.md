# Ollama 추천 모델 (16GB RAM)

16GB RAM 환경에서 실행 가능한 Ollama 로컬 LLM 모델 목록입니다.

## RAM 요구사항 가이드

| 모델 크기 | 최소 RAM | 권장 RAM | 예시 |
|----------|----------|----------|------|
| 1B-3B | 4GB | 8GB | TinyLlama, Phi-3 Mini |
| 7B-8B | 8GB | 16GB | Llama 3.2, Mistral 7B |
| 13B-14B | 16GB | 32GB | Qwen2.5 14B, Phi-4 |

> **16GB RAM 환경**: 7B~8B 모델 권장. 13B+ 모델은 Q4_K_M 양자화 필수.

## 용도별 추천 모델

### 일반 대화 / 글쓰기

| 모델 | 설치 명령어 | 메모리 | 특징 |
|------|------------|--------|------|
| **Llama 3.2 8B** | `ollama pull llama3.2` | ~5GB | Meta의 최신 모델, 범용 성능 우수 |
| **Mistral 7B** | `ollama pull mistral` | ~4GB | 빠른 추론, 높은 품질 |
| **Gemma 2 9B** | `ollama pull gemma2:9b` | ~5GB | Google, 균형 잡힌 성능 |

### 코딩 / 개발

| 모델 | 설치 명령어 | 메모리 | 특징 |
|------|------------|--------|------|
| **Qwen2.5-Coder 7B** | `ollama pull qwen2.5-coder:7b` | ~4GB | 코딩 특화, 한국어 지원 |
| **DeepSeek-Coder V2** | `ollama pull deepseek-coder-v2` | ~5GB | 코드 생성/분석 최적화 |
| **CodeLlama 7B** | `ollama pull codellama:7b` | ~4GB | Meta 코딩 모델 |

### 추론 / 분석

| 모델 | 설치 명령어 | 메모리 | 특징 |
|------|------------|--------|------|
| **Phi-4 14B** | `ollama pull phi4` | ~8GB | Microsoft, 작은 크기 대비 뛰어난 추론 |
| **Qwen2.5 7B** | `ollama pull qwen2.5:7b` | ~4GB | 29개 언어 지원, 복잡한 지시 이해 |

### 경량 모델 (저사양용)

| 모델 | 설치 명령어 | 메모리 | 특징 |
|------|------------|--------|------|
| **Phi-3 Mini** | `ollama pull phi3:mini` | ~2GB | Microsoft, 소형 고성능 |
| **TinyLlama** | `ollama pull tinyllama` | ~1GB | 초경량, 빠른 응답 |
| **Orca Mini 3B** | `ollama pull orca-mini:3b` | ~2GB | 기본 작업용 |

## 이 프로젝트 추천 조합

문서 분석 및 Neo4j 변환 작업에 최적화된 조합:

```bash
# 1. 메인 분석 모델 (개념 추출, 관계 분석)
ollama pull qwen2.5:7b

# 2. 코딩/구조화 보조 (JSON 출력 등)
ollama pull qwen2.5-coder:7b

# 3. 경량 백업 (빠른 분류 작업)
ollama pull phi3:mini
```

### 권장 설정

```python
# src/core/llm.py 에서 사용
DEFAULT_MODEL = "qwen2.5:7b"        # 메인 분석
CODING_MODEL = "qwen2.5-coder:7b"   # 구조화 출력
FAST_MODEL = "phi3:mini"            # 빠른 분류
```

## 양자화 (Quantization)

메모리 절약을 위해 양자화된 버전 사용:

```bash
# Q4_K_M 양자화 (권장) - 메모리 75% 절약
ollama pull llama3.2:8b-instruct-q4_K_M

# Q5_K_M 양자화 - 품질/메모리 균형
ollama pull mistral:7b-instruct-q5_K_M
```

| 양자화 | 메모리 절약 | 품질 손실 | 용도 |
|--------|------------|----------|------|
| Q4_K_M | ~75% | 최소 | 일반 사용 (권장) |
| Q5_K_M | ~65% | 거의 없음 | 품질 중시 |
| Q8_0 | ~50% | 없음 | 고품질 필요 시 |

## 성능 최적화 팁

1. **컨텍스트 윈도우 제한**: 긴 컨텍스트는 메모리 급증
   ```bash
   # 컨텍스트 크기 제한 (기본 2048)
   ollama run llama3.2 --num-ctx 2048
   ```

2. **GPU 오프로딩**: GPU가 있다면 활용
   ```bash
   # GPU 레이어 수 설정
   ollama run llama3.2 --num-gpu 35
   ```

3. **배치 처리**: 여러 요청 동시 처리 시 배치 크기 조절

## 참고 자료

- [Ollama 공식 모델 라이브러리](https://ollama.com/library)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Collabnix - Best Ollama Models 2025](https://collabnix.com/best-ollama-models-in-2025-complete-performance-comparison/)
- [LocalLLM - VRAM Requirements Guide](https://localllm.in/blog/ollama-vram-requirements-for-local-llms)
