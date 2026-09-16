---
title: "[테스트] 이미지 자동화 파이프라인 점검용 글"
slug: test-pipeline-check
categories: []
tags: []
excerpt: "이미지 자동 생성 파이프라인 테스트용 글입니다. 발행하지 마세요."
focus_keyword: "테스트"
meta_description: "테스트용 글입니다."
meta_title: "테스트"
featured_image_filename: test-pipeline-thumbnail.jpg
---

이 글은 사람이 읽는 글이 아닙니다. `upload_to_wp.py`의 이미지 자동 생성 → 리사이즈 → 워드프레스 업로드 → Alt Text 삽입 파이프라인이 실제로 끝까지 작동하는지 확인하기 위한 테스트 원고입니다.

<!-- wp:image -->
<div class="wp-block-image"><figure class="aligncenter"><img src="test-pipeline-coffee.jpg" alt="베트남식 커피 한 잔"/></figure></div>
<!-- /wp:image -->

위 사진 자리에 자동 생성된 이미지가 들어가야 정상입니다.

## 이미지 가이드

| 번호 | 파일명 | Alt Text | 비고 |
|---|---|---|---|
| 1 | test-pipeline-thumbnail.jpg | 비엣길 테스트 썸네일 | 대표 이미지 |
| 2 | test-pipeline-coffee.jpg | 베트남식 커피 한 잔 | 본문 이미지 |

## Gemini 이미지 생성 프롬프트

파일명: test-pipeline-thumbnail.jpg
크기: 1200x675

프롬프트:
A cozy rooftop cafe overlooking Halong Bay at sunrise, misty limestone karsts in the background, photorealistic, warm golden light, travel photography style

---

파일명: test-pipeline-coffee.jpg

프롬프트:
A traditional Vietnamese drip coffee (ca phe sua da) on a rustic wooden table, condensed milk swirl visible, soft morning light, photorealistic, shallow depth of field

---
