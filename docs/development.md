# 개발 안내

[English README](../README.md) | [한국어 README](../README.ko.md)

이 저장소는 HACS에서 배포하는 Home Assistant 커스텀 통합입니다. 지원 최소는 `hacs.json`의 Home Assistant **2026.9.0**이며 최신 테스트 환경과 별도로 유지합니다. 중앙 기준은 [hass-repo-standards](https://github.com/eigger/hass-repo-standards/tree/6839346bc5e2a11157fecd800f4cb490fc3197ab)입니다. 채택 범위와 미완료 검증은 [STANDARDS.md](../STANDARDS.md)와 [ADOPTION_CHECKLIST.md](../ADOPTION_CHECKLIST.md)에 기록합니다.

## 구조

Core의 `homeassistant/components/<domain>/`에 대응하는 구현은 `custom_components/opinet/`에 두고, 테스트는 같은 domain 계층인 `tests/components/opinet/`에 둡니다. `config_flow.py`는 UI 설정·재인증·주유소 추가, `coordinator.py`는 데이터 갱신, `sensor.py`는 센서, `api.py`는 외부 API, `geo.py`는 좌표 변환을 담당합니다. `__init__.py`는 config entry와 서비스 생명주기를 관리합니다. 필요한 역할에 따라 모듈을 유지하며 공식 Core 포함이나 품질 등급을 주장하지 않습니다.

테스트는 실제 Home Assistant와 `pytest-homeassistant-custom-component` fixture를 사용합니다. 실제 config entry setup·센서 플랫폼·unload 경로를 실행하고 외부 API 통신 경계를 mock합니다. 독립 API·좌표·장치 회귀 테스트도 같은 domain 아래에 유지합니다. Home Assistant 자체를 가짜 모듈로 바꾸지 않습니다.

## 개발 환경과 명령

Python 3.14 환경에서 실행합니다. current와 minimum HA는 서로 다른 가상환경을 사용합니다. 다음 current 예시는 통합 manifest 요구사항을 읽어 함께 설치하므로 통합 의존성을 별도 목록으로 복제하지 않습니다.

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python - <<'PY'
import json
import subprocess
import sys
from pathlib import Path
manifest = json.loads(Path("custom_components/opinet/manifest.json").read_text())
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_test.txt", "-r", "requirements_lint.txt", *manifest["requirements"]])
PY
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m pytest tests/components/opinet/ -v
```

최소 HA는 별도 가상환경에서 `requirements_test.txt` 대신 `requirements_test_minimum_ha.txt`를 설치한 뒤 같은 manifest 설치·`pip check`·pytest 명령을 실행합니다. Python·HA·플러그인의 정확한 설치 버전을 기록하며, 최신 HA 환경의 성공을 최소 HA 검증으로 대신하지 않습니다.

중앙 체크아웃을 같은 부모 디렉터리에 두고 [uv](https://docs.astral.sh/uv/)를 설치하면 README 관리 영역·메타데이터·테스트 구조·공용 CI를 검사할 수 있습니다. 중앙 검사 도구가 사용하는 PyYAML과 packaging 26.3은 아래 명령에서 별도 도구 환경에 설치합니다.

```bash
uv run --no-project --with pyyaml --with packaging==26.3 --python 3.14 ../hass-repo-standards/scripts/check_integration.py .
uv run --no-project --with pyyaml --with packaging==26.3 --python 3.14 ../hass-repo-standards/scripts/sync_badges.py . --check
```

[Tests](../.github/workflows/tests.yml)는 실제 HA 테스트를 current 및 지원 최소 환경에서 실행합니다. [Minimum dependency](../.github/workflows/minimum_dependency.yml)는 Python 3.14 wheel이 없는 `pyproj==3.6.1`을 빌드하도록 PROJ 개발 패키지와 컴파일러를 설치한 뒤 중앙 `python-environment`의 minimum 모드에서 의존성을 함께 해결하고 current HA의 실제 테스트를 실행합니다. [Validate](../.github/workflows/validate.yml)는 중앙 검사·린트·Hassfest·HACS를 수행합니다. 로컬 정적 검사, 실제 HA 실행, 원격 workflow, 실서비스 연결 검증은 각각 구분합니다.

## 의존성 변경

직접 사용하는 외부 Python 패키지는 `custom_components/opinet/manifest.json`의 `requirements`가 원본입니다. `pyproj>=3.6.1`은 기존 지원 계약이므로 자동화 편의로 연산자나 하한을 변경하지 않습니다. 필수 HA 구성요소는 `dependencies`, 선택 로딩 순서는 `after_dependencies`로 구분하며 현재 필요하지 않은 의존성을 추가하지 않습니다. HA·테스트 fixture는 `requirements_test*.txt`, 린트는 `requirements_lint.txt`에 둡니다.

의존성을 추가·변경할 때는 사용 API와 지원 Python/HA·extras·marker를 확인하고 manifest·관련 requirements·공용 updater의 선택 목록을 함께 검토합니다. 각 환경에서 resolver로 함께 설치한 뒤 실제 설치 버전과 `pip check`를 기록하고 실제 HA 테스트를 실행합니다. 범위 requirement의 정확한 하한도 별도 검증하며 빌드·해결 실패를 숨기거나 설치 후 다른 버전으로 덮어쓰지 않습니다. 하한 상향이나 지원 최소 HA 변경은 별도 지원 정책 변경으로 검토합니다.

## 검증 환경

2026-10-20 로컬 작업 트리에서 실행한 결과입니다. 상세 명령·실행 근거와 미완료 항목은 [채택 체크리스트](../ADOPTION_CHECKLIST.md)에 기록합니다.

| 범위 | Python | Home Assistant | pytest-homeassistant-custom-component | pyproj | 결과 |
| --- | --- | --- | --- | --- | --- |
| current HA / current 의존성 | 3.14.5 | 2026.10.2 | 0.13.373 | 3.8.0 | pytest 27 passed (1.05초); uv pip check 통과 |
| current HA / minimum dependencies | 3.14.8 (Linux) | 2026.10.2 | 0.13.373 | 3.6.1 / PROJ9.6.0 | Independent fresh environment: 27 passed, pip check PASS; Cython3.0.12 source build |
| 지원 최소 HA | 3.14.5 | 2026.9.0 | 0.13.363 | 3.8.0 | pytest 27 passed (1.07초); uv pip check 통과 |

Current: `/tmp/opinet-current/bin/python -m pytest tests/components/opinet/ -v`; minimum HA: `/tmp/opinet-minimum-ha/bin/python -m pytest tests/components/opinet/ -v`. Ruff0.17.1 check/format and all three dependency checks passed. The exact pyproj minimum was independently installed in a fresh Linux venv with HA/plugin requirements and pyproj==3.6.1 resolved together; original sdist, PROJ9.6.0 and Cython3.0.12 build constraint, no source patch or package replacement.

실제 오피넷 API 키를 사용한 실서비스 호출은 자동 테스트에서 실행하지 않습니다. API 통신을 mock한 테스트 결과는 실제 API 접근·키 유효성·서비스 호출 제한의 실증 근거가 아닙니다. 원격 CI는 변경 커밋이 반영된 뒤 해당 실행 링크로 별도 확인합니다.

The central checker fix was published in [PR11](https://github.com/eigger/hass-repo-standards/pull/11) and squash merged as `6839346bc5e2a11157fecd800f4cb490fc3197ab`. It correctly validates `config_subentries.station.step`; all four central CI jobs passed. The pinned integration callers use this published main commit.

For the minimum source build, install the PROJ development tools and compiler, use `pip==26.2.1`, set `PIP_BUILD_CONSTRAINT` to the absolute path of `requirements_build_minimum.txt`, and `PIP_CONFIG_FILE` to the absolute path of `.github/pip_minimum.ini`. Its `[install] no-cache-dir = true` setting prevents installation from reusing a wheel built with incompatible Cython while preserving the `pip cache dir` lookup used by `actions/setup-python`. The dedicated workflow records these steps. The Cython constraint addresses [upstream pyproj issue1451](https://github.com/pyproj4/pyproj/issues/1451); it does not change the runtime minimum.
