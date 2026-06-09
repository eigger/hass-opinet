# Opinet 유가정보 Home Assistant Integration (hass-opinet)

[![GitHub Release](https://img.shields.io/github/v/release/eigger/hass-opinet?style=flat-square)](https://github.com/eigger/hass-opinet/releases)
[![License](https://img.shields.io/github/license/eigger/hass-opinet?style=flat-square)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![integration usage](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=usage&suffix=%20installs&cacheSeconds=15600&query=%24.opinet.total&url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json)


한국석유공사 **오피넷(Opinet) 일반 API**를 사용해 유가 정보를 가져오는 Home Assistant 커스텀 통합구성요소입니다.

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

제품: 휘발유/고급휘발유, 경유, 등유, LPG. 갱신은 위 시각 +오프셋(기본 10분,
옵션에서 변경)에 이뤄집니다.

주유소를 추가하면 다음도 함께 생성됩니다.

- **위치(device_tracker)**: 주유소 좌표(KATEC→위경도 변환)를 GPS로 들고 있어 지도에 표시됩니다.
- **편의시설 sensor (ENUM)**: 세차장·경정비·편의점은 있음/없음, 품질인증·착한주유소는 예/아니오.

### 지도에 표시하기

위치 엔티티는 `person`과 동일한 GPS device_tracker입니다. 따라서 **상태(state)** 는
존(zone)/집/외출로 표시되고(집 존 밖이면 `외출`), **위치는 지도로** 봅니다.

- 엔티티를 클릭하면 상세창에 지도가 나옵니다.
- 좌측 **지도(Map) 패널**에 자동 포함됩니다.
- 대시보드에 고정하려면 지도 카드를 사용하세요:

```yaml
type: map
entities:
  - entity: device_tracker.<주유소>_위치
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

1. 이 저장소를 HACS의 사용자 지정 저장소로 추가하거나, `custom_components/opinet` 폴더를
   Home Assistant 설정 디렉터리의 `custom_components/` 아래에 복사합니다.
2. Home Assistant를 재시작합니다.
3. **설정 → 기기 및 서비스 → 통합구성요소 추가 → "Opinet 유가정보"** 를 선택하고 API 키를 입력합니다.

## 주유소 추가

통합구성요소 카드의 **"항목 추가"(주유소)** 에서:

- **이름으로 검색**: 상호와(선택) 지역을 입력 → 검색 결과에서 선택
- **주유소 ID로 추가**: 오피넷 주유소 ID(예: `A0019752`)를 입력하면 바로 추가

## API 키 발급

[오피넷 일반 API](https://www.opinet.co.kr/user/custapi/custApiInfo.do)에서 발급받을 수 있습니다.

## 라이선스

MIT
