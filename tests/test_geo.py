"""geo.py 단위 테스트."""
import pytest
from custom_components.opinet.geo import katec_to_wgs84, wgs84_to_katec


def test_coordinate_conversion_loop():
    """WGS84 -> KATEC -> WGS84 변환이 올바르게 왕복되는지 검증."""
    lat, lon = 37.5665, 126.9780

    # 위경도 -> KATEC
    x, y = wgs84_to_katec(lat, lon)
    assert isinstance(x, float)
    assert isinstance(y, float)

    # KATEC -> 위경도
    lat_new, lon_new = katec_to_wgs84(x, y)

    assert lat_new == pytest.approx(lat, abs=1e-5)
    assert lon_new == pytest.approx(lon, abs=1e-5)
