다음 5단계를 순서대로 실행하세요. 각 단계 완료 후 다음 단계로 넘어가세요.

## 입력값
$ARGUMENTS

입력 형식: `[주제] / [포커스 키워드] / [시리즈 편수(선택)]`

예시:
- `판시판 트레킹 / 판시판`
- `사파 가는 법 / 사파 가는 법 / 시리즈 2편`
- `하롱베이 크루즈 / 하롱베이 크루즈`

---

## Phase 1 — 원고 작성

CLAUDE.md의 모든 지침을 적용해서 글을 작성하세요.

**반드시 확인:**
- 글 유형 파악 (투어 소개 / 정보 / 에세이) → CTA 전략 결정
- 장면 → 관찰 → 질문 → 통찰 구조
- H2만 사용 (H3 절대 금지)
- 포커스 키워드: 제목, 첫 문단, H2 1~2개, Alt Text, 메타 디스크립션 포함
- 투어 CTA 2회 (첫 3문단 이후부터)
- 내부 링크 1개 이상
- 다음 편 예고로 마무리
- 작성자 서명 포함

**본문은 Gutenberg 블록 형식으로 작성:**

단락:
```
<!-- wp:paragraph -->
<p>본문 내용</p>
<!-- /wp:paragraph -->
```

H2 제목:
```
<!-- wp:heading {"level":2} -->
<h2>소제목</h2>
<!-- /wp:heading -->
```

이미지 자리표시자:
```
<!-- wp:image -->
<figure class="wp-block-image"><img src="" alt="[Alt Text]"/></figure>
<!-- /wp:image -->
```

CTA 버튼:
```
<!-- wp:buttons -->
<div class="wp-block-buttons">
  <div class="wp-block-button">
    <a class="wp-block-button__link" href="투어문의링크">투어 문의하기</a>
  </div>
</div>
<!-- /wp:buttons -->
```

아래 형식으로 파일 저장:
`posts/YYYY-MM-DD-[slug].md`

Frontmatter 필수 포함:
```
title, slug, focus_keyword, meta_title, meta_description,
categories, tags, excerpt, series, series_part
```

---

## Phase 2 — 이미지 가이드 생성

원고를 분석해서 이미지 삽입 가이드를 생성하세요.

**각 삽입 위치 직후에 아래 코드블록을 원고 안에 삽입:**

```
📷 이미지 정보
파일명: sapa-trekking-example.jpg
Alt Text: 사파 트레킹 타반 마을 계단식 논
위치: [H2 제목] 문단 직후
```

**파일명 규칙:**
- 영문 소문자 + 하이픈
- 포커스 키워드 포함
- 예: `sapa-trekking-terraced-field-morning.jpg`

**이미지 가이드 별도 섹션을 원고 맨 아래에 추가:**

```
---
## 📷 이미지 가이드

| 번호 | 파일명 | Alt Text | 삽입 위치 |
|------|--------|----------|-----------|
| 대표 | [파일명] | [Alt] | 썸네일 |
| 1 | [파일명] | [Alt] | [위치] |
| 2 | [파일명] | [Alt] | [위치] |
```

---

## Phase 3 — 이미지 생성 프롬프트 가이드

Gemini + 나노바나나로 이미지를 생성할 수 있도록 각 이미지마다 영문 프롬프트를 작성하세요.

**원고 맨 아래 이미지 가이드 다음에 추가:**

```
---
## 🎨 Gemini 이미지 생성 프롬프트

### 대표 이미지 (썸네일)
파일명: [slug]-thumbnail.jpg
크기: 1200 × 675px

프롬프트:
[영문 프롬프트 — 장소, 시간대, 분위기, 구도, 스타일 포함]
예: "Morning mist over Sapa terraced rice fields, golden hour light,
wide landscape shot, photorealistic, travel photography style,
no people, vibrant green colors"

---

### 본문 이미지 1
파일명: [파일명].jpg

프롬프트:
[영문 프롬프트]

---

### 본문 이미지 2
파일명: [파일명].jpg

프롬프트:
[영문 프롬프트]
```

**프롬프트 작성 원칙:**
- 장소 + 시간대 + 날씨/분위기 + 구도 + 스타일 순서로 작성
- `photorealistic, travel photography style` 항상 포함
- 사람이 필요한 경우: `Vietnamese local people, natural candid`
- 사람 불필요한 경우: `no people` 명시
- 부정적 요소 제거: `no watermark, no text, high quality`

---

## Phase 4 — 이미지 업로드 전 체크리스트

```
---
## 📐 이미지 업로드 체크리스트

**본문 이미지 (총 N장):**
- 권장 크기: 가로 1200px 이상
- 파일 형식: JPG (품질 80~85%)
- 파일명: 영문 소문자 + 하이픈 (위 이미지 가이드 참조)

**썸네일:**
- 크기: 정확히 1200 × 675px
- 파일명: [slug]-thumbnail.jpg

**Mac 터미널 일괄 리사이즈 명령어:**
sips -Z 1200 *.jpg

**업로드 순서:**
1. 썸네일 → 대표 이미지로 설정
2. 본문 이미지 → 각 이미지 가이드 위치에 삽입
3. 각 이미지 Alt Text 입력 (이미지 가이드 참조)
```

---

## Phase 5 — WordPress 업로드

파일 저장 완료 후 즉시 실행:

```bash
python3 upload_to_wp.py posts/[저장한파일명].md
```

업로드 완료 후 아래 형식으로 최종 보고:

```
✅ 5단계 완료

━━━━━━━━━━━━━━━━━━━━━━
제목: [글 제목]
포커스 키워드: [키워드]
슬러그: /[slug]/
━━━━━━━━━━━━━━━━━━━━━━
Phase 1 원고 작성        ✅
Phase 2 이미지 가이드    ✅  [N]곳
Phase 3 이미지 프롬프트  ✅  [N]개
Phase 4 리사이즈 안내    ✅
Phase 5 WP 업로드        ✅
━━━━━━━━━━━━━━━━━━━━━━

🔗 WordPress 편집 링크: [링크]

📋 남은 작업:
□ Gemini에서 이미지 [N]장 생성 (프롬프트 가이드 참조)
□ 이미지 리사이즈 (sips -Z 1200 *.jpg)
□ WordPress에서 이미지 업로드 및 삽입
□ Alt Text 입력
□ Rank Math SEO 점수 확인 (80점 이상)
□ 최종 검토 후 발행
```
