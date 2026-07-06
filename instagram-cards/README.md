# Instagram 카드뉴스 (money7line)

블로그(money7line.blogspot.com) 글을 **Claude 디자인 스타일**로 재구성한 인스타그램
카드뉴스 이미지입니다. 각 글은 4장 캐러셀(표지 + 핵심 3장)로 구성됩니다.

## 구성

```
instagram-cards/20260705/
├── 01-dongtan-giheung-guri-regulation-20260705/
│   ├── 01-cover.png      # 표지
│   ├── 02-point1.png     # 핵심 1
│   ├── 03-point2.png     # 핵심 2
│   └── 04-point3.png     # 핵심 3
├── ... (총 15개 글)
└── captions.md           # 글별 인스타 캡션 + 해시태그
```

- 규격: **1080 × 1350 px** (인스타그램 4:5 세로형)
- 폰트: Pretendard · 배경 크림(#F0EEE6) · 포인트 코럴(#CC785C)
- 대상: 저장소 `20260705/mapping.json` 의 7/5자 15개 글

## 게시 방법

### ⚠️ 왜 여기서 자동 게시가 안 되나
이 카드뉴스는 Claude Code 웹 환경에서 생성했는데, 해당 환경의 네트워크 정책이
`graph.facebook.com`(인스타그램 그래프 API)을 **차단**합니다. 그래서 이미지 생성까지만
이곳에서 하고, **실제 게시는 아래 두 방법 중 하나로** 진행하세요.

### 방법 A — 수동 업로드 (가장 간단)
1. 각 글 폴더의 4장을 순서대로(01→04) 인스타 앱에서 캐러셀로 업로드
2. `captions.md` 에서 해당 글 캡션을 복사해 붙여넣기
3. 프로필 링크를 `money7line.blogspot.com` 으로 설정(캡션 내 링크는 클릭 불가)

### 방법 B — Graph API 자동 게시 (`tools/publish_to_instagram.py`)
graph.facebook.com 접근이 가능한 본인 PC에서 실행합니다.

```bash
export IG_USER_ID="17841..."        # 인스타 비즈니스 계정 ID
export IG_ACCESS_TOKEN="EAAG..."    # instagram_content_publish 권한 토큰
export RAW_BASE="https://raw.githubusercontent.com/gawaguci/money7line-blog-assets/main"

python3 tools/publish_to_instagram.py --dry-run   # URL 확인
python3 tools/publish_to_instagram.py             # 15개 전체 게시
```

전제: 인스타 **비즈니스/크리에이터** 계정 + 연결된 페이스북 페이지 + 그래프 API 토큰.
이미지는 이 저장소가 push된 뒤 `raw.githubusercontent.com` 공개 URL로 제공됩니다.

## 재생성 / 수정

카드 문구는 `tools/card_content.json` 에서 편집한 뒤 재생성합니다.

```bash
python3 tools/generate_cards.py     # 60장 PNG + captions.md 다시 생성
```
