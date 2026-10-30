<!-- hass-standards:header:start -->
# Opinet 유가정보 Home Assistant Integration (hass-opinet)

A Home Assistant custom integration that retrieves fuel prices using the Korea National Oil Corporation’s Opinet general API.

**English** | [한국어](README.ko.md)

<!-- hass-standards:badges:start -->
[![Release](https://img.shields.io/github/v/release/eigger/hass-opinet?style=flat)](https://github.com/eigger/hass-opinet/releases)
[![HACS Default](https://img.shields.io/badge/HACS-Default-41BDF5?style=flat)](#installation)
[![Home Assistant minimum](https://img.shields.io/badge/HA-%E2%89%A5%202026.9.0-41BDF5?style=flat)](hacs.json)
[![Tests](https://img.shields.io/github/actions/workflow/status/eigger/hass-opinet/tests.yml?branch=main&style=flat&label=Tests)](https://github.com/eigger/hass-opinet/actions/workflows/tests.yml)
[![Validate](https://img.shields.io/github/actions/workflow/status/eigger/hass-opinet/validate.yml?branch=main&style=flat&label=Validate)](https://github.com/eigger/hass-opinet/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/eigger/hass-opinet?style=flat)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/eigger/hass-opinet/latest/total?style=flat&color=41BDF5&label=Downloads)](https://github.com/eigger/hass-opinet/releases)
<!-- hass-standards:badges:end -->
<!-- hass-standards:header:end -->

The Downloads badge counts GitHub release asset downloads of the current release, not active installations.

- Enter your **API key** during initial setup to create the shared **national average price sensors**.
- **Add a gas station** afterward to create sensors for each product sold by that station.
- Add a station by **searching its name (business name)** or **entering its station ID directly**.

## Sensors

| Device | Sensor | API | Update time |
| --- | --- | --- | --- |
| Opinet national average | Current \<product\> | `avgAllPrice.do` | 01:00, 02:00, 09:00, 12:00, 16:00, 19:00 |
| Opinet national average | Daily \<product\> | `avgRecentPrice.do` | Every day at 00:00 |
| Opinet national average | Weekly \<product\> | `avgLastWeek.do` | Friday at 10:00 |
| Gas station (when added) | \<product\> selling price | `detailById.do` | 01:00, 02:00, 09:00, 12:00, 16:00, 19:00 |
| Gas station (when added) | Urea solution / urea solution stock | `ureaPrice.do` | 07:00, 13:00, 18:00, 24:00 |

Products: regular/premium gasoline, diesel, kerosene, and LPG. Updates run at the times above plus an offset (10 minutes by default, configurable in options).

Adding a station also creates the following sensors, classified as diagnostic entities.

- **Location sensor**: its state is the address, with latitude/longitude attributes converted from KATEC coordinates so it can appear as a pin on a map card.
- **Amenities sensor (ENUM)**: car wash, light maintenance, and convenience store use available/unavailable; quality certification and Good Gas Station status use yes/no.
- **Urea solution stock sensor (ENUM)**: available/unavailable.

Station fuel price and urea solution selling price sensors are regular sensors, separate from the diagnostic sensors above.

- **Urea solution selling price sensor**: the station's city/county code is used to query urea solution prices in the corresponding province. If the ID (`UNI_ID`) matches the registered station, **urea solution selling price** and **stock (available/unavailable)** sensors are created. These are not created for stations that do not sell urea solution.

### Displaying a station on a map

The location sensor is a regular sensor entity with latitude/longitude attributes (not a device_tracker).
To display it on a dashboard map card:

```yaml
type: map
entities:
  - entity: sensor.<station>_위치
```

> If your API key expires or becomes invalid, a **reauthentication (reauth)** notification appears automatically so you can enter a new key.

## Services (all API queries)

APIs that are awkward to expose as sensors (coordinates, dates, search terms, TOP-N results, and lists) are all provided as **services**.
Use `response_variable` to receive the result in Developer Tools or automations.

```yaml
action: opinet.get_low_top
data:
  prodcd: B027
  area: "0101"
  cnt: 5
response_variable: result
```

`get_around` (stations within a radius) takes **latitude/longitude** as input (converted internally to KATEC).
The location is resolved in this order: entity → latitude/longitude → Home location.

```yaml
# 1) Use a phone's location (device_tracker)
action: opinet.get_around
data:
  entity_id: device_tracker.my_phone
  radius: 3000
  prodcd: B027
  sort: 1
response_variable: result

# 2) Enter latitude/longitude directly (uses HA Home coordinates if omitted)
action: opinet.get_around
data:
  latitude: 37.5665
  longitude: 126.9780
  radius: 3000
  prodcd: B027
response_variable: result
```

| Service | API |
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

Responses have the form `{"oil": [ ... ]}`. The free API limit is 1,500 requests per day.

## Installation

<!-- hass-standards:installation:start -->
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eigger&repository=hass-opinet)
<!-- hass-standards:installation:end -->

1. Install [HACS](https://hacs.xyz/docs/use/download/download/) first, then search for **Opinet** in HACS and download this integration. Alternatively, copy the `custom_components/opinet` folder into `custom_components/` in your Home Assistant configuration directory.
2. Restart Home Assistant.
3. Select **Settings → Devices & services → Add integration → "Opinet 유가정보"** and enter your API key.

## Adding a gas station

Select **"Add entry" (gas station)** on the integration card:

- **Search by name**: enter the business name and, optionally, a region → select a search result.
- **Add by station ID**: enter the Opinet station ID (for example, `A0019752`) to add it directly.

## Obtaining an API key

Request a key from the [Opinet general API](https://www.opinet.co.kr/user/custapi/custApiInfo.do).

## Development

See the [development guide (Korean)](docs/development.md) for the repository structure, dependency procedures, test commands, and validation environments.

<!-- hass-standards:support:start -->
## Support

- [Issues](https://github.com/eigger/hass-opinet/issues): Report bugs or request features.
- [Discussions](https://github.com/eigger/hass-opinet/discussions): Ask questions and share your experience.
<!-- hass-standards:support:end -->

<!-- hass-standards:related-projects:start -->
<!-- hass-standards:related-projects:end -->

<!-- hass-standards:license:start -->
## License

Released under the [MIT License](LICENSE).

Copyright (c) 2026 eigger
<!-- hass-standards:license:end -->
