"""pytest 설정 — homeassistant/aiohttp 가 없는 환경을 위한 fallback mock."""
import sys
from unittest.mock import MagicMock

try:
    import homeassistant  # noqa: F401
    import homeassistant.helpers.device_registry  # noqa: F401
    import homeassistant.helpers.update_coordinator  # noqa: F401
    _HA_INSTALLED = True
except ImportError:
    _HA_INSTALLED = False

if not _HA_INSTALLED:
    class _MockBase:
        """제네릭 서브클래싱(예: DataUpdateCoordinator[T])을 지원하는 기본 Mock 클래스."""

        def __init__(self, *args, **kwargs):
            self.data = None

        def __class_getitem__(cls, item):
            return cls

        async def async_config_entry_first_refresh(self):
            pass

        def async_setup_schedule(self):
            pass

        async def async_request_refresh(self):
            pass

    class _MockUpdateFailed(Exception):
        """UpdateFailed mock — raise UpdateFailed(...) 구문을 허용."""

    _mock_ha_coordinator = MagicMock()
    _mock_ha_coordinator.DataUpdateCoordinator = _MockBase
    _mock_ha_coordinator.CoordinatorEntity = _MockBase
    _mock_ha_coordinator.UpdateFailed = _MockUpdateFailed
    sys.modules["homeassistant.helpers.update_coordinator"] = _mock_ha_coordinator

    class MockDeviceInfo(dict):
        """DeviceInfo mock that acts like dict and object."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            for k, v in kwargs.items():
                setattr(self, k, v)

    _mock_ha_dr = MagicMock()
    _mock_ha_dr.DeviceInfo = MockDeviceInfo
    sys.modules["homeassistant.helpers.device_registry"] = _mock_ha_dr

    for _mod in [
        "homeassistant",
        "homeassistant.config_entries",
        "homeassistant.const",
        "homeassistant.core",
        "homeassistant.data_entry_flow",
        "homeassistant.helpers",
        "homeassistant.helpers.aiohttp_client",
        "homeassistant.helpers.entity",
        "homeassistant.helpers.entity_platform",
        "homeassistant.helpers.selector",
        "homeassistant.helpers.config_validation",
        "homeassistant.helpers.service",
        "homeassistant.helpers.event",
        "homeassistant.exceptions",
        "homeassistant.components",
        "homeassistant.components.binary_sensor",
        "homeassistant.components.button",
        "homeassistant.components.sensor",
        "homeassistant.components.device_tracker",
        "homeassistant.util",
        "homeassistant.util.dt",
        "aiohttp",
    ]:
        sys.modules[_mod] = MagicMock()
