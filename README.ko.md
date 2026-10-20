<!-- hass-standards:header:start -->
# Opinet 유가정보 Home Assistant Integration (hass-opinet)

한국석유공사 **오피넷(Opinet) 일반 API**를 사용해 유가 정보를 가져오는 Home Assistant 커스텀 통합구성요소입니다.

[English](README.md) | **한국어**

<!-- hass-standards:badges:start -->
[![Release](https://img.shields.io/github/v/release/eigger/hass-opinet?style=flat)](https://github.com/eigger/hass-opinet/releases)
[![HACS Default](https://img.shields.io/badge/HACS-Default-41BDF5?style=flat)](#설치)
[![Home Assistant minimum](https://img.shields.io/badge/HA-%E2%89%A5%202026.9.0-41BDF5?style=flat)](hacs.json)
[![Tests](https://img.shields.io/github/actions/workflow/status/eigger/hass-opinet/tests.yml?branch=main&style=flat&label=Tests)](https://github.com/eigger/hass-opinet/actions/workflows/tests.yml)
[![Validate](https://img.shields.io/github/actions/workflow/status/eigger/hass-opinet/validate.yml?branch=main&style=flat&label=Validate)](https://github.com/eigger/hass-opinet/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/eigger/hass-opinet?style=flat)](LICENSE)
[![HACS Downloads](https://img.shields.io/badge/dynamic/json?style=flat&color=41BDF5&label=HACS+Downloads&query=%24%5B%3F%28%40.full_name%3D%3D%22eigger%2Fhass-opinet%22%29%5D.downloads&url=https%3A%2F%2Fdata-v2.hacs.xyz%2Fintegration%2Fdata.json)](https://www.hacs.xyz/)
<!-- hass-standards:badges:end -->
<!-- hass-standards:header:end -->

- 처음 구성 시 **API 키**를 입력하면 **전국 평균가격 공통 센서**가 생성됩니다.
- 이후 **주유소를 추가**하면 해당 주유소의 제품별 유가 센서가 추가됩니다.
- 주유소는 **이름(상호)으로 검색**하거나 **주유소 ID를 직접 입력**해 추가할 수 있습니다.

## 센서

| 기기 | 센서 | 사용 API | 갱신 시각 |
| --- | --- | --- | --- |
| 오피넷 전국 평균 | 현재 \<제품\> | `avgAllPrice.do` | 1·2·9·12·16·19시 |
| 오피넷 전국 평균 | 일일 \<제품\> | `avgRecentPrice.do` | 매일 0시 |
| 오피넷 전국 평균 | 주간 \<제품\> | `avgLastWeek.do` | 금요일 10시 |
| 주유소(추가 시) | \<제품\> 판매가격 | `detailById.do` | 1·2·9·12·16·19시 |
| 주유소(추가 시) | 요소수 / 요소수 재고 | `ureaPrice.do` | 7·13·18·24시 |

제품: 휘발유/고급휘발유, 경유, 등유, LPG. 갱신은 위 시각 +오프셋(기본 10분,
옵션에서 변경)에 이뤄집니다.

주유소를 추가하면 다음도 함께 생성됩니다(진단 항목으로 분류).

- **위치 sensor**: 상태값은 주소이고, 위도/경도(KATEC→위경도 변환) 속성을 가지고 있어
  지도 카드에 핀으로 표시할 수 있습니다.
- **편의시설 sensor (ENUM)**: 세차장·경정비·편의점은 있음/없음, 품질인증·착한주유소는 예/아니오.
- **요소수 재고 sensor (ENUM)**: 있음/없음.

주유소 판매가격/요소수 판매가격 센서는 일반 센서로, 위 진단 센서와 구분됩니다.

- **요소수 판매가격 sensor**: 주유소의 시군코드로 해당 시도의 요소수 가격을 조회해, 등록 주유소와
  ID(UNI_ID)가 일치하면 **요소수 판매가격**과 **재고(있음/없음)** 센서를 생성합니다.
  요소수를 취급하지 않는 주유소에는 생성되지 않습니다.

### 지도에 표시하기

위치 센서는 위도/경도 속성을 가진 일반 sensor 엔티티입니다(device_tracker 아님).
대시보드에서 지도 카드로 표시하려면:

```yaml
type: map
entities:
  - entity: sensor.<주유소>_위치
```

> API 키가 만료/무효화되면 자동으로 **재인증(reauth)** 알림이 떠서 새 키를 입력할 수 있습니다.

## 서비스 (전 API 조회)

센서로 노출하기 애매한(좌표·날짜·검색어·TOP-N·목록 반환) API는 모두 **서비스**로 제공합니다.
개발자 도구나 자동화에서 `response_variable` 로 결과를 받습니다.

```yaml
action: opinet.get_low_top
data:
  prodcd: B027
  area: "0101"
  cnt: 5
response_variable: result
```

`get_around`(반경 내 주유소)은 **위도/경도**로 입력합니다(내부에서 KATEC 으로 변환).
위치는 엔티티 → 위경도 → 홈(Home) 순으로 결정됩니다.

```yaml
# 1) 휴대폰 위치(device_tracker) 기준
action: opinet.get_around
data:
  entity_id: device_tracker.my_phone
  radius: 3000
  prodcd: B027
  sort: 1
response_variable: result

# 2) 위경도 직접 입력 (생략 시 HA 홈 좌표 사용)
action: opinet.get_around
data:
  latitude: 37.5665
  longitude: 126.9780
  radius: 3000
  prodcd: B027
response_variable: result
```

| 서비스 | API |
| --- | --- |
| `opinet.get_avg_all_price` | ① avgAllPrice |
| `opinet.get_avg_sido_price` | ② avgSidoPrice |
| `opinet.get_avg_sigun_price` | ③ avgSigunPrice |
| `opinet.get_avg_recent_price` | ④ avgRecentPrice |
| `opinet.get_poll_avg_recent_price` | ⑤ pollAvgRecentPrice |
| `opinet.get_area_avg_recent_price` | ⑥ areaAvgRecentPrice |
| `opinet.get_avg_last_week` | ⑦ avgLastWeek |
| `opinet.get_low_top` | ⑧ lowTop10(TOP20) |
| `opinet.get_around` | ⑨ aroundAll |
| `opinet.get_station_detail` | ⑩ detailById |
| `opinet.search_station` | ⑪ searchByName |
| `opinet.get_taxfree_avg_recent_price` | ⑫ taxfreeAvgRecentPrice |
| `opinet.get_taxfree_poll_avg_recent_price` | ⑬ taxPollAvgRecentPrice |
| `opinet.get_taxfree_low_top` | ⑭ taxfreeLowTop20 |
| `opinet.get_urea_price` | ⑮ ureaPrice |
| `opinet.get_area_code` | ⑯ areaCode |
| `opinet.get_date_avg_recent_price` | ⑰ dateAvgRecentPrice |
| `opinet.get_date_poll_avg_recent_price` | ⑱ datePollAvgRecentPrice |
| `opinet.get_date_area_avg_recent_price` | ⑲ dateAreaAvgRecentPrice |

응답은 `{"oil": [ ... ]}` 형태로 반환됩니다. 무료 API 호출 제한은 1,500건/일입니다.

## 설치

<!-- hass-standards:installation:start -->
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eigger&repository=hass-opinet)
<!-- hass-standards:installation:end -->

1. 먼저 [HACS](https://hacs.xyz/docs/use/download/download/)를 설치한 뒤 HACS에서 **Opinet**을 검색해 이 통합을 다운로드합니다. 또는 `custom_components/opinet` 폴더를
   Home Assistant 설정 디렉터리의 `custom_components/` 아래에 복사합니다.
2. Home Assistant를 재시작합니다.
3. **설정 → 기기 및 서비스 → 통합구성요소 추가 → "Opinet 유가정보"** 를 선택하고 API 키를 입력합니다.

## 주유소 추가

통합구성요소 카드의 **"항목 추가"(주유소)** 에서:

- **이름으로 검색**: 상호와(선택) 지역을 입력 → 검색 결과에서 선택
- **주유소 ID로 추가**: 오피넷 주유소 ID(예: `A0019752`)를 입력하면 바로 추가

## API 키 발급

[오피넷 일반 API](https://www.opinet.co.kr/user/custapi/custApiInfo.do)에서 발급받을 수 있습니다.

## 개발

저장소 구조, 의존성 추가 절차, 테스트 명령과 검증 환경은 [개발 안내 (한국어)](docs/development.md)를 참고하세요.

<!-- hass-standards:support:start -->
## 지원

- [Issues](https://github.com/eigger/hass-opinet/issues): 버그를 신고하거나 기능을 요청하세요.
- [Discussions](https://github.com/eigger/hass-opinet/discussions): 질문하고 사용 경험을 공유하세요.
<!-- hass-standards:support:end -->

<!-- hass-standards:related-projects:start -->
<!-- hass-standards:related-projects:end -->

<!-- hass-standards:license:start -->
## 라이선스

[MIT License](LICENSE) 라이선스로 배포됩니다.

Copyright (c) 2026 eigger
<!-- hass-standards:license:end -->
