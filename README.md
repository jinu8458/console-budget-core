# console-budget-core

Python 표준 라이브러리만 사용하는 파일 기반 가계부의 핵심 코드입니다. Python 3.10 이상에서 실행합니다.

| 파일 | 역할 |
|---|---|
| `budget_app/models.py` | 거래·예산 모델, 날짜·금액·타입 검증 |
| `budget_app/storage.py` | JSONL 스트리밍 읽기, 저장소, 임시 파일을 통한 안전한 재작성 |
| `budget_app/services.py` | 거래 CRUD, 조건 검색, 월별 집계·예산, 카테고리와 CSV 처리 |
| `budget_app/errors.py` | 검증 실패와 데이터 조회 오류 |

## 실행

```bash
python examples/basic_usage.py
python -m unittest discover -s tests -v
```

실행 예제와 테스트는 임시 폴더와 가상 거래를 사용합니다. 별도의 패키지 설치는 필요하지 않습니다.

## 원본과 범위

[console-budget-app](https://github.com/wlsdn66597/console-budget-app)의 핵심 모듈을 기능 수정 없이 추출했습니다. 원본 기준 커밋: [`d56df4a`](https://github.com/wlsdn66597/console-budget-app/commit/d56df4a485c5905823f492654a66faa7aba11b0e).

원본의 콘솔 명령·대화형 입력, 명령 데코레이터, 실행 증빙·스크린샷·샘플 데이터는 포함하지 않습니다. 따라서 원본의 `python -m budget_app` 명령 대신 위 예제 또는 Python에서 `LedgerService`를 직접 사용합니다. 실제 가계부 데이터와 실행 로그도 저장소에 포함하지 않습니다.
