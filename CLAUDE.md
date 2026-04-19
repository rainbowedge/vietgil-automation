# Vietgil 블로그 자동화

도메인: vietgil.com | 플랫폼: WordPress | 언어: 한국어
필명: Vietgil | 거주지: 하롱베이 | 경력: 10년
슬로건: "베트남 북부 여행 — 패키지가 보여주지 않는 것들"
타겟: 베트남 북부 개인 여행 준비 중인 한국인

---

## 글쓰기 원칙

구조: 장면 → 관찰 → 질문 → 통찰
시점: 10년 거주 현지 가이드
첫 3문단: 감성적 장면, 링크 없음
시리즈: 마지막은 항상 다음 편 예고

금지:
- 정보 나열식, 관광지 소개 형식
- AI 느낌 문장, "~입니다" 반복
- H3 사용 (H2만 허용)
- 첫 3문단 링크

---

## 수익화 (Phase 1A)

투어 CTA 2회만 (중간 1회 부드럽게, 마지막 1회 명확하게)
링크: https://pf.kakao.com/_xfVKVX
Booking.com, GetYourGuide 링크 금지

글 마지막 필수 3단계:
1. 다음 편 예고
2. 글쓴이 소개: "하롱베이에 거주하며 투어가이드·여행사 운영·현지 투자를 병행하고 있습니다. 개인 투어 상담 및 여행 문의는 상단 메뉴의 '투어 문의'를 이용해 주세요."

---

## SEO 규칙

Rank Math 80점 이상 목표

포커스 키워드 필수 삽입 5곳:
- 제목 (H1)
- 첫 문단 (1~3번째 문단 안에 자연스럽게 착지, 없으면 10~15점 감점)
- H2 1~2개
- 대표 이미지 Alt Text
- 메타 디스크립션

본문 구조:
- 최소 2,500자 이상
- H2 3~5개 (H3 사용 금지)
- 내부 링크 2개 권장 (전체 HTTPS URL 필수, 상대경로 금지)
- 외부 링크 1~2개 필수 (공식 출처만: 유네스코, 베트남관광청, 빈그룹, 외교부 등)
  → 외부 링크 없으면 Rank Math 해당 항목 미달 처리됨

슬러그: 영문 소문자 하이픈 (예: sapa-trekking), 20자 이내
메타 디스크립션: 120~155자, 반드시 직접 입력 (Rank Math 자동생성 금지)
  → 비어있으면 회색 미리보기만 표시 → 해당 항목 감점

카테고리 (1개): 사파 여행 / 하롱베이 여행 / 하노이 여행 / 닌빈 여행 / 여행 준비 / 여행 철학
태그 (5~7개): 지역명 + 주제 2~3개 + 감성 1개 + 포커스 키워드

글 유형별 외부 링크 권장 출처:
- 하롱베이: https://whc.unesco.org/en/list/672 (유네스코)
- 사파/베트남 전반: https://vietnam.travel (베트남관광청)
- 개발/투자: https://vinhomes.vn (빈그룹 공식)
- 안전/준비: https://www.0404.go.kr (외교부 해외안전여행)

---

## 이미지 규칙

파일명: 영문 소문자 하이픈, 키워드 포함 (예: sapa-trekking-rice-field.jpg)
대표 이미지: 1200×675px (16:9)
본문 이미지: 가로 1200px, JPG
Alt Text: 포커스 키워드 포함, 20~30자
리사이즈: sips -Z 1200 *.jpg

---

## 키워드 데이터

| 키워드 | 검색량 | 난이도 |
|--------|--------|--------|
| 사파 여행 | 590 | 18 |
| 판시판 | 590 | 17 |
| 사파 가는 법 | 110 | 20 |
| 사파 트레킹 | 50 | 14 |
| 라오까이 여행 | 30 | 34 |

---

## 발행된 글 (내부 링크용)

1. https://vietgil.com/vietnam-north-travel-guide/
2. https://vietgil.com/sapa-travel-guide/ (사파 1편)
3. https://vietgil.com/sapa-getting-there/ (사파 2편)
4. https://vietgil.com/lao-cai-travel/ (사파 3편)
5. https://vietgil.com/sapa-trekking/ (사파 4편)

---

## 파일 규칙

파일명: posts/YYYY-MM-DD-slug.md

Frontmatter:
```yaml
---
title: ""
slug: 
focus_keyword: 
meta_title: " | Vietgil"
meta_description: ""
categories:
  - 
tags:
  - 
excerpt: ""
series: 사파 시리즈
series_part: 
---
```

---

## 워크플로우 실행 순서

Phase 1: 글 작성 → posts/YYYY-MM-DD-slug.md 저장
Phase 2: 이미지 가이드 생성 (파일명 + Alt Text + 추천 구도)
Phase 3: 썸네일 가이드 (Canva 기반, 실제 사진, 1200×675px)
Phase 4: 리사이즈 안내 (sips -Z 1200 *.jpg)
Phase 5: python3 upload_to_wp.py posts/파일명.md 실행
