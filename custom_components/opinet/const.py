"""Constants for the Opinet integration."""

from __future__ import annotations

from typing import Any

DOMAIN = "opinet"

# Config / subentry keys
CONF_API_KEY = "api_key"
CONF_STATION_ID = "station_id"
CONF_OSNM = "osnm"
CONF_AREA = "area"
CONF_REFRESH_OFFSET = "refresh_offset"

SUBENTRY_TYPE_STATION = "station"

# 오피넷 가격 업데이트 시각 (가이드 문서 기준). 고정 인터벌 폴링 대신
# 아래 시각(분/초 0)에 맞춰 갱신한다. 24시는 0시로 표현.
#
# 현재 판매가격: 1, 2, 9, 12, 16, 19시
PRICE_UPDATE_HOURS: tuple[int, ...] = (1, 2, 9, 12, 16, 19)
# 일일 평균가격: 24시(=0시)
DAILY_AVG_UPDATE_HOURS: tuple[int, ...] = (0,)
# 요소수 판매가격: 7, 13, 18, 24시(=0시)
UREA_UPDATE_HOURS: tuple[int, ...] = (0, 7, 13, 18)
# 주간 평균가격: 금요일 10시 (weekday: 월=0 … 금=4)
WEEKLY_UPDATE_HOURS: tuple[int, ...] = (10,)
WEEKLY_UPDATE_WEEKDAY: int = 4

# 서버는 위 '정시'에 데이터를 갱신하므로, 그 시각 직후(+오프셋 분)에 조회한다.
# 기본 10분이며 옵션에서 0~59분으로 조정 가능.
DEFAULT_REFRESH_OFFSET_MINUTES: int = 10
MIN_REFRESH_OFFSET_MINUTES: int = 0
MAX_REFRESH_OFFSET_MINUTES: int = 59

# Opinet API base url
API_BASE = "https://www.opinet.co.kr/api"

# Product codes used by avgAllPrice.do / detailById.do.
PRODUCTS: dict[str, str] = {
    "B027": "휘발유",
    "B034": "고급휘발유",
    "D047": "경유",
    "C004": "등유",
    "K015": "LPG",
}

# 면세유 제품코드.
TAXFREE_PRODUCTS: dict[str, str] = {
    "B127": "면세휘발유",
    "D147": "면세경유",
    "C104": "면세등유",
}

# Brand (POLL_DIV) codes — docs say POLL_DIV_CD; API JSON/XML use POLL_DIV_CO.
BRANDS: dict[str, str] = {
    "SKE": "SK에너지",
    "GSC": "GS칼텍스",
    "HDO": "현대오일뱅크",
    "SOL": "S-OIL",
    "RTE": "자영알뜰",
    "RTX": "고속도로알뜰",
    "NHO": "농협알뜰",
    "E1G": "E1",
    "SKG": "SK가스",
    "ETC": "자가상표",
}


def poll_div_code(row: dict[str, Any]) -> str | None:
    """Extract brand code from an Opinet API row."""
    code = row.get("POLL_DIV_CO") or row.get("POLL_DIV_CD")
    if code is None:
        return None
    code = str(code).strip()
    return code or None


def brand_label(code: str | None) -> str | None:
    """Resolve a POLL_DIV code to a human-readable brand name."""
    if not code:
        return None
    return BRANDS.get(code, code)


# LPG_YN — 업종구분 (detailById.do).
STATION_TYPES: dict[str, str] = {
    "N": "Gas station",
    "Y": "LPG station",
    "C": "Gas & LPG station",
}


def station_type_label(code: str | None) -> str:
    """Resolve LPG_YN to a device model label."""
    if not code:
        return STATION_TYPES["N"]
    return STATION_TYPES.get(str(code).strip().upper(), STATION_TYPES["N"])


# 시도 지역코드 (searchByName.do / avg* 의 area 파라미터)
AREAS: dict[str, str] = {
    "01": "서울",
    "02": "경기",
    "03": "강원",
    "04": "충북",
    "05": "충남",
    "06": "전북",
    "07": "전남",
    "08": "경북",
    "09": "경남",
    "10": "부산",
    "11": "제주",
    "14": "대구",
    "15": "인천",
    "16": "광주",
    "17": "대전",
    "18": "울산",
    "19": "세종",
}

PRICE_UNIT = "원/L"

# 편의시설 ENUM 센서 상태 (내부값 yes/no → UI 번역: 있음/없음).
AMENITY_YES = "yes"
AMENITY_NO = "no"
AMENITY_OPTIONS: tuple[str, ...] = (AMENITY_YES, AMENITY_NO)
