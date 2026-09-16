다음 지침에 따라 Vietgil 블로그 글을 작성하고 WordPress에 업로드하세요.

## 입력값
$ARGUMENTS

입력 형식: `[주제] / [포커스 키워드] / [시리즈 편수(선택)]`

예시:
- `판시판 트레킹 / 판시판`
- `사파 가는 법 / 사파 가는 법 / 시리즈 2편`
- `하롱베이 크루즈 / 하롱베이 크루즈`

---

## 실행 순서

### Step 1 — 글 작성

CLAUDE.md의 모든 지침을 적용해서 글을 작성하세요.

**반드시 확인:**
- 글 유형 파악 (투어 소개 / 정보 / 에세이) → CTA 전략 결정
- 장면 → 관찰 → 질문 → 통찰 구조
- H2만 사용 (H3 절대 금지)
- 포커스 키워드: 제목, 첫 문단, H2 1~2개, Alt Text, 메타 디스크립션 포함
- 투어 CTA 2회 (첫 3문단 이후부터)
- 이미지 삽입 가이드 (파일명 + Alt Text) 각 위치마다 표기
- 내부 링크 1개 이상
- 다음 편 예고로 마무리
- 작성자 서명 포함

### Step 2 — 파일 저장

아래 형식으로 파일명을 생성하세요:
`posts/YYYY-MM-DD-slug.md`

오늘 날짜와 슬러그를 사용해서 `posts/` 폴더에 저장하세요.

Frontmatter 필수 포함:
```
title, slug, focus_keyword, meta_title, meta_description,
categories, tags, excerpt, series, series_part
```

### Step 3 — WordPress 업로드

파일 저장 후 즉시 아래 명령어를 실행하세요:

```bash
python3 upload_to_wp.py posts/[저장한파일명].md
```

### Step 4 — 결과 보고

업로드 완료 후 아래 내용을 한국어로 보고하세요:

```
✅ 완료

제목: [글 제목]
슬러그: /[slug]/
포커스 키워드: [키워드]

🔗 WordPress 편집 링크: [링크]

📋 남은 작업:
- 대표 이미지 업로드 (1200×675): [파일명]
- 본문 이미지 [N]개 업로드
- Rank Math SEO 점수 확인 (80점 이상)
- 최종 검토 후 발행
```
