#!/usr/bin/env python3
"""Knowledge Graph Builder CLI

문서에서 지식 그래프를 구축하는 멀티 에이전트 시스템.

사용법:
    python main.py                          # 기본 실행
    python main.py --input ./notes          # 입력 디렉토리 지정
    python main.py --output ./out/graph.cypher  # 출력 파일 지정
    python main.py --model qwen2.5:7b       # LLM 모델 지정
    python main.py --verbose                # 디버그 로깅
"""

import argparse
import sys
from pathlib import Path

from core.logger import setup_logger, set_log_level
from graphs import KnowledgeGraphBuilder


def main():
    parser = argparse.ArgumentParser(
        description="문서에서 지식 그래프를 구축합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python main.py
  python main.py --input ./notes --output ./out/graph.cypher
  python main.py --model qwen2.5:7b --verbose

워크플로우:
  1. Research Agent: 문서 파싱, 개념 추출, 메타데이터 수집
  2. Analyst Agent: 카테고리 분류, 관계 분석, 기존 그래프 비교
  3. Writer Agent: Cypher 쿼리 생성, 중복 체크, 파일 저장
        """
    )

    parser.add_argument(
        "--input", "-i",
        default="data/input",
        help="입력 파일 디렉토리 (기본: data/input)"
    )

    parser.add_argument(
        "--output", "-o",
        default="data/output/graph.cypher",
        help="출력 Cypher 파일 (기본: data/output/graph.cypher)"
    )

    parser.add_argument(
        "--config", "-c",
        default="configs/settings.yaml",
        help="설정 파일 경로 (기본: configs/settings.yaml)"
    )

    parser.add_argument(
        "--model", "-m",
        default=None,
        help="LLM 모델명 (예: qwen2.5:7b)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="디버그 로깅 활성화"
    )

    args = parser.parse_args()

    # 로거 설정
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logger(level=log_level)

    if args.verbose:
        set_log_level("DEBUG")

    # 입력 디렉토리 확인/생성
    input_dir = Path(args.input)
    if not input_dir.exists():
        input_dir.mkdir(parents=True, exist_ok=True)
        print(f"입력 디렉토리 생성됨: {input_dir}")
        print("파일을 추가한 후 다시 실행하세요.")
        print("지원 형식: .md, .txt, .csv, .docx, .json")
        return 0

    # 입력 파일 확인
    input_files = list(input_dir.glob("*"))
    supported_ext = {".md", ".txt", ".csv", ".docx", ".json"}
    valid_files = [f for f in input_files if f.suffix.lower() in supported_ext]

    if not valid_files:
        print(f"입력 디렉토리에 파일이 없습니다: {input_dir}")
        print("지원 형식: .md, .txt, .csv, .docx, .json")
        return 0

    print(f"입력 파일 {len(valid_files)}개 발견")

    # 출력 디렉토리 생성
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 워크플로우 실행
    print("\n" + "=" * 50)
    print("Knowledge Graph Builder")
    print("=" * 50)
    print(f"입력: {args.input}")
    print(f"출력: {args.output}")
    if args.model:
        print(f"모델: {args.model}")
    print("=" * 50 + "\n")

    builder = KnowledgeGraphBuilder(
        input_dir=args.input,
        output_file=args.output,
        model_name=args.model
    )

    result = builder.run()

    # 결과 출력
    print("\n" + "=" * 50)
    if result["success"]:
        print("완료!")
        r = result.get("result", {})
        print(f"  - 처리된 문서: {r.get('processed_docs', 0)}개")
        print(f"  - 새 노드: {r.get('new_nodes', 0)}개")
        print(f"  - 새 관계: {r.get('new_relationships', 0)}개")
        print(f"  - 총 쿼리: {r.get('total_queries', 0)}개")
        print(f"  - 출력 파일: {r.get('output_file', args.output)}")
    else:
        print("실패!")
        for error in result.get("errors", []):
            print(f"  - {error}")

    print("=" * 50)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
