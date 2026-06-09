"""WGS84(위경도) ↔ KATEC(TM128) 좌표 변환.

오피넷 ``aroundAll`` 은 KATEC 좌표만 받으므로, 위경도를 KATEC 로 변환한다.
pyproj 임포트는 무겁고 블로킹이므로, 변환은 반드시 executor 에서 호출한다
(아래 함수를 ``hass.async_add_executor_job`` 으로 실행).
"""

from __future__ import annotations

from functools import lru_cache

# KATEC(TM128): Bessel 타원체, 중앙자오선 128°E, 원점위도 38°N,
# 축척 0.9999, false easting 400000, false northing 600000.
# Bessel→WGS84 7-파라미터 데이텀 변환(한국) 포함.
_KATEC_PROJ = (
    "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 "
    "+x_0=400000 +y_0=600000 +ellps=bessel +units=m +no_defs "
    "+towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43"
)


@lru_cache(maxsize=1)
def _transformer():  # type: ignore[no-untyped-def]
    """Cache the pyproj transformer (lazy import → executor 안에서만 호출)."""
    from pyproj import Transformer

    return Transformer.from_crs("EPSG:4326", _KATEC_PROJ, always_xy=True)


@lru_cache(maxsize=1)
def _inverse_transformer():  # type: ignore[no-untyped-def]
    """KATEC → WGS84 역변환기 (lazy import → executor 안에서만 호출)."""
    from pyproj import Transformer

    return Transformer.from_crs(_KATEC_PROJ, "EPSG:4326", always_xy=True)


def wgs84_to_katec(latitude: float, longitude: float) -> tuple[float, float]:
    """위경도(WGS84)를 KATEC (x=동거리, y=북거리) 로 변환한다."""
    x, y = _transformer().transform(longitude, latitude)
    return x, y


def katec_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """KATEC (x=동거리, y=북거리) 를 위경도(WGS84, lat, lon) 로 변환한다."""
    longitude, latitude = _inverse_transformer().transform(x, y)
    return latitude, longitude
