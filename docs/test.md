# Knowledge Graph UI 프로젝트 계획

## 프로젝트 분리 구조

```
projects/langgraph/
├── my-agent-system/           # Python 백엔드 (현재)
│   ├── src/
│   │   ├── agents/
│   │   ├── core/
│   │   ├── graphs/
│   │   └── tools/
│   ├── venv/
│   ├── main.py
│   └── requirements.txt
│
└── knowledge-graph-ui/        # Next.js 프론트엔드 (새로 생성)
    ├── app/
    ├── components/
    ├── lib/
    └── package.json
```

## 분리 이유

| 항목 | my-agent-system | knowledge-graph-ui |
|-----|-----------------|-------------------|
| 언어 | Python 3.11+ | TypeScript 5.8.x |
| 패키지 관리 | pip, venv | pnpm |
| 의존성 파일 | requirements.txt | package.json |
| 환경 | venv/ | node_modules/ |
| 역할 | 백엔드 로직, LLM 처리 | UI/UX, 시각화 |

**혼합 시 문제점:**
- venv/와 node_modules/ 혼재로 복잡
- .gitignore, 설정 파일 충돌
- 배포 파이프라인 복잡화
- 관심사 분리 위반

---

## knowledge-graph-ui 기술 스택

### 언어
- TypeScript 5.8.x

### 프레임워크
- Next.js 15 (App Router, Turbopack)
- Turborepo (모노레포 관리) - 선택사항

### UI/스타일링
- Tailwind CSS
- shadcn/ui (Radix UI 기반 컴포넌트)
- next-themes (다크/라이트 모드)

### 상태 관리
- Zustand 또는 React Query

### API 통신
- fetch 또는 axios
- SWR / TanStack Query

---

## 백엔드 연동 방식

### 옵션 1: FastAPI 추가 (권장)
```
my-agent-system/
├── src/
│   └── api/              # 새로 추가
│       ├── __init__.py
│       ├── main.py       # FastAPI 앱
│       └── routes/
│           ├── workflow.py
│           └── graph.py
```

**장점:**
- Python 생태계와 자연스러운 통합
- 비동기 지원
- 자동 OpenAPI 문서 생성

### 옵션 2: LangServe
- LangGraph 워크플로우를 직접 API로 노출
- LangChain 생태계와 통합

---

## 프론트엔드 주요 기능

### 1. 파일 업로드 및 처리
- 드래그 앤 드롭 파일 업로드
- 지원 형식: .md, .txt, .csv, .docx, .json
- 처리 진행 상태 표시

### 2. 결과 확인
- 생성된 Cypher 쿼리 보기
- 추출된 개념/관계 목록
- 처리 로그

### 3. 그래프 시각화 (선택)
- D3.js 또는 vis.js로 노드/관계 시각화
- 인터랙티브 탐색

### 4. 대시보드
- 처리 통계
- 최근 작업 목록
- 시스템 상태

---

## 실행 방법 (구현 후)

### 백엔드 (my-agent-system)
```bash
cd my-agent-system
source venv/bin/activate
uvicorn src.api.main:app --reload --port 8000
```

### 프론트엔드 (knowledge-graph-ui)
```bash
cd knowledge-graph-ui
pnpm install
pnpm dev
# http://localhost:3000
```

---

## 다음 단계

1. [ ] my-agent-system에 FastAPI 추가
2. [ ] API 엔드포인트 설계
3. [ ] knowledge-graph-ui 프로젝트 생성
4. [ ] 기본 UI 구현
5. [ ] API 연동
6. [ ] 그래프 시각화 (선택)
