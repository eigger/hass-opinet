# 공통 규칙 적용 체크리스트

2026-10-20 최초 채택의 작업 트리 검증 기록입니다. 원격 CI·기본 브랜치 반영 전에는 채택 완료로 판정하지 않습니다. [사용법과 판정 기준](https://github.com/eigger/hass-repo-standards/blob/6839346bc5e2a11157fecd800f4cb490fc3197ab/docs/checklist.md)을 읽고, 아래 규칙은 `STANDARDS.md`에 기록한 표준 커밋에서 확인합니다. 태그·릴리스 대신 `main`의 검토 커밋을 기준으로 하며, 위 사용법 링크의 `main`은 채택 시 검토한 커밋 SHA로 바꿉니다.

## 검토 대상

| 항목 | 값 |
|---|---|
| 통합 리포 / 실제 기본 브랜치 | eigger/hass-opinet / main |
| domain / 구현 경로 | opinet / custom_components/opinet/ |
| 검토 대상 통합 커밋 / 채택 PR | Baseline8761e7c; [PR15](https://github.com/eigger/hass-opinet/pull/15), initial published81968c0; subsequent CI fix/evidence below |
| 검토한 표준 전체 커밋 SHA | 6839346bc5e2a11157fecd800f4cb490fc3197ab |
| 검토일 / 조율 담당 | 2026-10-20 (Asia/Seoul) / root(opinet-adoption) |
| 구현 서브 에이전트 / 독립 리뷰·검증 서브 에이전트 | implementation·documentation / review |
| 중앙 현황표 반영일 / 기록 | 2026-10-20 로컬 docs/adoption-status.md 자기 행 갱신, 미게시(다른 세션 변경 보존) |
| 변경 전 지원 최소 HA / 근거 파일(hacs.json·manifest·README) | hacs.json.homeassistant=2026.9.0; manifest·README에 추가 최소 선언 없음 |
| 유지·변경할 지원 최소 / 변경 시 실제 비호환 근거·명시적 승인 | 2026.9.0 유지; 통합 버전 2.0.0·pyproj>=3.6.1 유지 |
| current 테스트 HA / 호환 Python·플러그인 | HA 2026.10.2 / Python 3.14 / pytest-homeassistant-custom-component 0.13.373 (실행 결과 아래) |
| 최소 테스트 HA / 호환 Python·플러그인 | HA 2026.9.0 / Python 3.14 / pytest-homeassistant-custom-component 0.13.363 (실행 결과 아래) |
| profile / 테스트 경로 | integration / ha; tests/components/opinet/ |
| 이전 검토 기록 | 최초 채택 |
| 채택 판정 | PR implementation and CI verified; final squash/main result is maintained in the central adoption-status row |

상태: `TODO` = 미확인·미충족, `PASS` = 근거로 확인, `EXCEPTION` = 적용 대상의 기록된 예외, `N/A` = 적용 조건에 해당 없음. 모든 항목은 미확인으로 시작합니다. `TODO`를 해당 없음으로 처리하지 않습니다. 묶은 규칙의 결과가 다르면 행을 나눕니다. 권장 항목은 별도로 표시했으며 미채택 이유를 기록합니다.

## 채택·구조·사용자 데이터

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| GOV-01, GOV-02 | `STANDARDS.md`에 표준 SHA·profile·실제 기본 브랜치·예외 기록, workflow/action은 검토 SHA로 고정 | PASS | STANDARDS/profile/main and caller SHA recorded. Central PR11 squash6839346 is published main, tree-identical to independently verified source089c86d. Four central PR checks passed. Integration callers use6839346. |
| GOV-03 | 새 표준 채택 변경의 영향·이관 방법과 명시적 채택 PR 확인. 규칙 자체를 변경하면 공통 CHANGELOG 기록 | PASS | Explicit adoption PR15, runtime source81968c0 and CI correction c66ed8f. Final reviewed c66ed8f passed all8 remote checks; central rule fix PR11 is merged with CHANGELOG. Final squash/main evidence is recorded centrally. |
| GOV-04 | 중앙 표에 작업 시작·단계 변경·종료 상태, 담당·적용 내용·검증/리뷰 근거·남은 작업 갱신, 타 리포 기록 보존 | PASS | 2026-10-20 중앙 로컬 docs/adoption-status.md 자기 행만 갱신; 타 세션 변경 보존. 원격 미게시 사실 명시. |
| GOV-05 | 구현과 독립 리뷰·검증을 별도 서브 에이전트에게 위임, 지적 수정·재검증 및 결과 취합 | PASS | implementation/documentation implemented; review independently verified. Fixed schedule trigger, last loaded entry cleanup and caplog findings, then reran 27 tests on both HA versions. |
| HA-01, HA-13 | `custom_components/<domain>/`와 domain 일치, 필요한 모듈·공개 API·생명주기는 Core 대응 구조 | PASS | custom_components/opinet 및 tests/components/opinet, typed runtime_data·ConfigEntry 공개 setup/unload/플랫폼 API 사용. |
| HA-02 | manifest 필드·정렬·동작 선언, 실제 제품 categories 1–3개·주 분류 순서·공식 slug·선택 근거·categories_review 일치 또는 entity/system/virtual 키 생략 이유, 공식 품질 등급 자가 표기 없음 | PASS | manifest 기존 필드·domain·version 2.0.0 유지; categories energy.energy_prices 추가. .hass-standards.json 검토 값/순서/미선언 유형null 일치. |
| HA-03 (권장) | 공통 상수·설정·갱신·플랫폼 역할 및 프로토콜 경계에 맞게 모듈 구성 | PASS | 기존 const/config_flow/coordinator/sensor/api/geo 역할 유지. 불필요한 entity 추상화 추가 없음. |
| HA-04, HA-08 | UI 설정·중복·안정적 식별 및 기능별 options/reauth/reconfigure, entity 의미·registry 영향 확인 | PASS | Real HA flow manager: user, error, duplicate, reauth, options, station ID/search/duplicate. Real registry unique IDs and device parentage verified; identifiers and units retained. |
| HA-01, HA-04, HA-08, REL-01, REL-03 | domain·unique ID·entry schema·상태/통계 계약 변경 시 migration 테스트와 사용자 조치 안내 | N/A | domain/unique ID/entry schema/단위/통계 계약 변경 없음; migration 불필요. |
| HA-05, HA-06 | setup 실패 구분, unload/reload·부분 실패의 task/listener/연결 정리, async·timeout·취소 처리 | PASS | test_init covers actual setup/unload/retry/auth/partial failure/last loaded entry cleanup. Schedules and services register after initial refreshes/platform success. HTTP timeout30s, cancellation propagates. |
| HA-07 | 중복 polling·property I/O 방지, push 보존, unavailable/unknown·실패 후 복구 | PASS | Shared coordinators and province urea deduplication retained. Actual sensor unavailable/recovery verified; no property I/O. |
| HA-11, HA-12 | 번역·action/schema 일치, 로그/diagnostics/fixture 비식별화와 제공 시 redaction 테스트 | PASS | English strings.json=en.json, Korean translations retained; real services/schema and credential redaction/timeout/cancellation regressions PASS. Correct central subentry namespace validation and missing-key negative test PASS with local089c86d; publication tracked by GOV-02. |

## 실제 HA 테스트·호환성·의존성

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| TEST-08 | `tests/components/<domain>/`에 구현과 대응하는 테스트·domain fixture 배치, discovery·CI 경로 일치 | PASS | 기존 API/device/geo 9개 함수의 회귀 보존 및 실제 HA 테스트를 tests/components/opinet/로 전환. 세 package init은 빈 파일, 루트 conftest 중앙 원본과 일치. |
| TEST-02, TEST-03, DEP-07 | 실제 HA·호환 플러그인과 `hass`/`enable_custom_integrations` fixture 사용, HA core stub/복사본/`--no-deps`로 대체하지 않음 | PASS | Real HA/plugin fixtures and entry/platform loading; all HA sys.modules stubs removed. Current2026.10.2/plugin.373 and minimum2026.9.0/plugin.363, Python3.14.5: resolver/pipcheck PASS. |
| TEST-09 | 실제 loader·config entry manager로 setup/플랫폼 로딩, HA 상태·registry·service/action으로 결과 검증 | PASS | test_init/test_sensor/test_services use actual HA entry setup, platforms, states, registry, registered services and unload. |
| TEST-01, TEST-06, TEST-07 | 구현 기능별 성공·실패·중복·migration·unload·복구 회귀 검증, 외부 통신 경계만 mock, skip 사유 | PASS | 27 tests, original API/device/geo regressions retained. Config flows, reauth/options/subentries, sensor recovery, get_around, timeout/cancel/redaction, partial failure and unload. External OpinetApi boundary only mocked; skip0. |
| TEST-04, HACS-01 | 변경 전 지원 최소·current·각 Python/플러그인 분리, 선언한 정확한 최소 검증, 상향 시 비호환 근거·명시적 승인 확인 | PASS | Minimum HA2026.9.0 and integration2.0.0 retained. Exact minimum and current HA2026.10.2 each27passed plus pipcheck. |
| TEST-05, HA-10, DEP-02, DEP-05 | imagespec·blesession 등 최소/현재 라이브러리 별도 환경, 실제 HA 테스트·정확한 설치값·API 경계 검증 | PASS | Current/minimum HA resolver pyproj3.8.0 PASS. Exact pyproj3.6.1 built with PROJ9.6.0/Cython3.0.12; HA2026.10.2 27passed/pipcheck PASS. Earlier unconstrained Cython build25passed2failed preserved as evidence; no package source patch/version bump. |
| DEP-01, DEP-06 | Python runtime은 manifest requirements, HA domain은 dependencies/after_dependencies, 테스트·린트 requirements는 별도 | PASS | runtime pyproj>=3.6.1 원본 manifest 유지; 테스트 requirements_test*.txt와 requirements_lint.txt 분리, 무관한 HA component 의존성 추가 없음. |
| DEP-07, CI-06 | 실제 사용하는 HA 구성요소의 requirements·필수 재귀 의존성·선택 로딩 경로 설치, resolver·`pip check` 통과 | PASS | Actual sensor/API/config entry paths loaded; no additional component manifest requirements required. Both HA environments and exact pyproj3.6.1 environment pipcheck PASS. |
| DEP-02, DEP-03, DEP-08 | 의존성 추가/변경의 버전·extras·marker·선언 위치·지원 플랫폼·라이선스 검토, 실제 HA 테스트와 문서 갱신 | PASS | 이번 작업 runtime package·연산자·하한 변경 없음. updater dry-run만 실행해 >=3.8.0 제안 확인(미적용). |

독립 리뷰는 변경 전후 지원 최소와 current를 비교하고, 봇 PR이 과거 최소 requirements·constraints까지 갱신하거나 expected-ha-version·Python을 누락하지 않았는지 확인합니다. 최신 테스트 실패는 호환 수정 대상으로 처리합니다.

환경마다 아래 행을 복사합니다. 최소 HA와 최소 라이브러리 검증을 혼동하지 않고, marker가 활성인 환경에서 대상 패키지 설치값을 확인합니다. 실행하지 않은 조합은 `TODO` 또는 근거가 있는 `EXCEPTION`으로 남깁니다.

| 검증 축 / 상태 | 통합 커밋 | Python / HA / 플러그인 실제 버전 | 대상 패키지 실제 버전·extras·marker | 명령·테스트 결과·pip check / CI run·job | skip·제외·미검증 범위 |
|---|---|---|---|---|---|
| Current HA / PASS | 8761e7c + working tree | Python3.14.5 / HA2026.10.2 / plugin0.13.373 | pyproj3.8.0 | Implementation27passed(1.05s), independent27passed; pipcheck PASS | skip0; external API mocked |
| Exact minimum HA / PASS | Same working tree | Python3.14.5 / HA2026.9.0 / plugin0.13.363 | pyproj3.8.0 | Implementation27passed(1.07s), independent27passed; pipcheck PASS | skip0; external API mocked |
| Exact minimum package / PASS | Same working tree | LinuxPython3.14.8 / HA2026.10.2 / plugin0.13.373 | pyproj3.6.1 / PROJ9.6.0 | Independent fresh venv/single resolver/source build Cython3.0.12:27passed(0.65s), pipcheck PASS | skip0; no source patch; no package replacement |

## HACS·CI·의존성 업데이트

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| HACS-01, HACS-02 | 루트 README/LICENSE/hacs.json, 검증한 최소 HA, 실제 배포 구조와 필요한 옵션 일치 | PASS | README/LICENSE/hacs.json and custom_components/opinet layout retained. Exact declared minimum2026.9.0 verified. No unnecessary packaging flags. |
| HACS-03, HACS-05 | Default 여부는 목록 근거로 확인, [로컬 brand/icon.png 또는 원격 brands 근거](https://github.com/eigger/hass-repo-standards/blob/6839346bc5e2a11157fecd800f4cb490fc3197ab/docs/hacs.md)와 HACS/Hassfest 실제 실행, ignore는 이유·해제 조건 기록 | PASS | Default listing/local brand confirmed. PR15 c66ed8f official HACS10checks PASS without categories warning; source-built official Coreec18d8 full Hassfest Integrations1/Invalid0 PASS; no ignore flags. Validate39428476087. |
| HACS-06 (권장) | description·topics·issue 경로·brands 및 사용하는 HACS 필드 지원 확인 | PASS | 실제 description/topics와 활성 Issues/Discussions 확인. 기존 로컬 brand/icon.png 유지. |
| CI-01, CI-02 | Validate/Tests 공통화, 확장 job 유지, 공용 파일명·표시 이름·PR 대상 제한 없는 기본 이벤트·실제 기본 브랜치 push·dispatch·기존 schedule, 전용 CI 명명 형식 | PASS | Shared Tests/current+minimumHA, Validate and updater callers retained. PROJ source-build extension minimum_dependency.yml uses central composite, not a replacement Tests caller. PR without branch/paths filters, actualmain push/dispatch. CI-02 requires central weekly Validate cron; prior daily schedule changed accordingly. |
| CI-03, CI-05, CI-08 | 최소 권한·checkout 자격증명 비보존·timeout·concurrency, full SHA·갱신 관리, 비신뢰 입력·secrets 경계 | PASS | contents:read·persist-credentials:false·timeout/concurrency는 중앙 caller/action에 따름. updater job만 PR용 write. full SHA 고정 및 Dependabot. |
| CI-04, CI-07, CI-12 | 실패를 숨기지 않는 실제 `ha` 필수 테스트, 버전별 환경·cache·Ruff 설정과 required checks 이름 확인 | PASS | PR15 c66ed8f all8 checks PASS: exact current/minimumHA, exact pyproj minimum, lint2, HACS, Hassfest, central template. No failure suppression. Branch protection404/no rulesets, settings unchanged. Final squash/main results tracked centrally. |
| DEP-03, DEP-04, CI-09 | updater의 선택 package·연산자/extras/marker 보존, 안정 버전·major 정책, 실제 기본 브랜치·단일 bot branch·PR만 제안 | PASS | updater pyproj 하나 선택, 공용 SHA 고정·기본 dry-run: pyproj>=3.6.1 → >=3.8.0 제안. 실제 파일은 3.6.1 유지. 명령은 아래 참조. |
| CI-09, CI-10, DEP-08 | 변경 tree의 새 하한·실제 HA 검증 후 PR 동기화, 실패 시 중단·변경 없음 시 기존 PR 정리, 후속 required checks 충족 방식 확인 | N/A | No runtime dependency requirement changed, so an actual dependency-update PR/new-floor validation was not triggered. Shared updater wiring and pyproj dry-run verified; no bot PR or repository permission change was made. Future update PRs must satisfy the shared validation/check requirements. |

## README·Bluetooth·유지보수

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| DOC-01, DOC-02, DOC-06 | 중앙 header/support/related-projects/license 관리 영역의 정확한 형식, 기존 공통 내용·고지 보존, 영역 밖 순서·제목·본문 유지, 양언어 같은 구조·내용·상호 링크, 독립 번역 의미·누락 리뷰, 실제 활성 지원 링크·실제 라이선스 | PASS | 중앙 렌더러 관리 영역 적용, 원래 한국어 본문·표·YAML·순서 보존 및 영문 전체 번역. README 양언어 개발안내·상호 링크, Issues/Discussions 활성·MIT 및 copyright 고지 확인. 독립 의미 리뷰는 아래 참조. |
| DOC-03, DOC-04, DOC-05 | 언어 링크 다음 중첩 배지 관리 블록, flat·Release/HACS/HA minimum/Tests/Validate/License/HACS Downloads(Default) 또는 Usage(Custom) 순서·실제 조건·고유 배지 보존, 실제 기본 브랜치·상태별 필수 동적 집계 배지·양언어 설치 절의 실제 저장소 My HACS 배지·미집계와 0 설치 구분 | PASS | Release2.0.0·공식 HACS Default 근거 확인. 중앙 flat 순서·HA2026.9.0·HACS Downloads·My HACS 설치 링크 양언어 적용. 공식 data 레코드 downloads 필드 미제공(0 아님). sync_badges --check PASS. |
| HA-09, HA-10 | BLE 사용 시 HA Bluetooth API·라이브러리 공개 경계, 지원한 proxy 경로·재연결·취소·서비스 변경 검증 | N/A | BLE·imagespec·blesession 사용 없음. 공개 pyproj Transformer API만 executor에서 사용. |
| DOC-07 | blesession 사용 여부(manifest requirement extras·operator·marker/실제 import) 확인. 사용 통합은 중앙 양언어 docs/troubleshooting 템플릿의 고정 제목·순서·증상 표·실제 진단/로그·기존 Issues 연결, README와 로컬 문서의 언어별 상호/공통 blesession 원본 링크·placeholder 제거·공용 Validate 검사. 기존 본문/기기안내 보존, 새 제보 양식 금지. 프록시만 지원하면 기존 기기 조건·사용자 안내를 수동 확인 | N/A | requirements/import에 blesession 없음. Bluetooth/proxy 기기 기능 없음. |
| DOC-08 | imagespec 사용 여부·양언어 docs/payload 여섯 절·언어별 README/공통 원본/상호 링크·실제 액션/대상/전체 YAML·기기 출력/지원/제한·기존 예제/본문 보존·기존 지원 연결, 모든 로컬 연결 예제의 payload.examples 등록·실제 경로/payload_format(list 또는 yaml)/크기/모델 색상 | N/A | requirements/import에 imagespec 없음. payload 문서/액션/예제 계약 대상 아님. |
| DOC-08, TEST-02, TEST-05, TEST-09 | 정확한 중앙 test_payload_examples scaffold·실제 HA entry/등록 action schema·production 준비 context/함수·기기 전송 없는 installed imagespec.validate/render 비교·각 예제 크기/색상, current/정확한 하한 실제 버전·pip check·명령/CI 결과, exact pin 재사용 근거·독립 adapter 리뷰 | N/A | imagespec 미사용; payload scaffold/adapter 없음. |
| DOC-08, CI-05, CI-07, DEP-08 | 공용 Tests/updater의 standards-ref와 reusable full SHA 일치·caller checkout 보존·도구 별도 checkout·resolver 후 패키지 변경 없음·지원 최소 보존·미실행/skip/xfail/deselect를 PASS로 처리하지 않음 | N/A | imagespec 미사용. standards-ref는 각 공용 workflow와 동일 SHA로 명시했으나 payload 검증 대상 없음. |
| DOC-07, HA-12 | 기기별 깨우기·인증·타 앱 연결·전송 제약, 실제 검증 경로와 미검증 범위, 공개 문제 로그 비식별화 | N/A | Bluetooth 기기별 전원/인증/프록시/전송 제약 해당 없음. API key 오류 비식별화 테스트는 HA-12 행 참조. |
| HACS-04, REL-01, REL-02, REL-03, CI-11 | 통합 릴리스 시 같은 검증 commit/tag·manifest 버전·산출물·권한, 사용자 영향·지원 변경·제한 안내 | N/A | 이번 작업 새 릴리스/태그 없음; 기존 정식 2.0.0과 manifest.version 일치. 최소 HA 상향 없음. |
| REL-04 | 이전/중단 시 README 상단 경로·유지보수 상태·재등록 여부, 자동 이전으로 오인하지 않는 안내 | N/A | 리포 이전/중단 작업 아님. |
| REL-05 (권장) | 의존성/HA API 변경과 기능 변경 분리, 표준 변경은 명시적 채택 PR로 반영 | PASS | 기능 추가·런타임 의존성 상향 없이 표준 채택과 필수 생명주기/timeout 결함 수정 범위로 관리. |

## Exceptions and remaining work

No approved exceptions. The user explicitly authorized the central checker fix and squash merge/branch cleanup on2026-10-20. Central PR11 is merged; integration publication and checks are being completed.

| Remaining item | Owner | Completion evidence |
|---|---|---|
| Central fix: completed | root/review | Central PR11 squash6839346 published,4checks PASS, source branch deleted |
| Integration PR verification: completed | root/review | PR15 c66ed8f all8 checks PASS; squash/main evidence tracked centrally |
| Future dependency update PR | Maintainer | N/A for this adoption: no requirement changed; dry-run and shared wiring checked |

The central checkout's adoption-status row was updated locally only; other sessions' edits were preserved. Adoption remains in progress until remote/default-branch evidence exists.

## Central template verification

- Published fixed checker: `uv run --no-project --with pyyaml --with packaging==26.3 --python 3.14 /private/tmp/opinet-standards-subentry-20261020/scripts/check_integration.py .`: PASS. Original central648dad9 reported4 valid subentry keys as config.step false positives; no duplicate translation keys or ignored failures were added.
- Root conftest matches central; three test init files are empty. Real mock_config_entry/mock_client fixtures, actual entry/platform/action tests, original API/device/geo regression cases retained. No blanket network/error allowances.
- Independent review confirmed full bilingual body preservation, translated semantics, notices, badge/installation links and active support links. Original Korean Sensors/Services/Station/API-key bodies preserved; only installation instructions reflect confirmed HACS default availability.
- Shared workflow names/references and dedicated minimum source-build workflow checked with actionlint1.7.12. Ruff0.17.1 check/format27files, badges and diff checks PASS.
- Central fix implementation and independent verification:219 unittest cases,6 skipped solely for a separate imagespec runtime not installed in the central tooling environment;18 focused scaffold tests PASS. Default macOS temporary symlink path first failed CLI guards; canonical TMPDIR rerun passed without changing guards. check_repository37documents7workflows and Ruff92files PASS. Negative test removing station.step.search correctly failed at config_subentries.station.step.search.

## imagespec payload 예제 검증 환경

N/A — manifest/import에 imagespec 없으며 렌더링 payload 액션을 제공하지 않습니다. marker/adapter/출력 검증 대상 없음.

## HA-02 제품 분류 검토 근거

| 항목 | 실제 판단 / 근거 |
|---|---|
| manifest integration_type | 기존 미선언 유지 (`categories_review.integration_type: null`) |
| categories (주 분류 먼저) | `["energy.energy_prices"]` |
| 주/보조 분류 선택 | 오피넷 일반 API의 전국/지역 평균 및 주유소 연료·요소수 가격 제공이라는 실제 서비스 목적. 센서 플랫폼에서 추정하지 않음. 별도 보조 분류 불필요. README 센서/API 표 및 [오피넷](https://www.opinet.co.kr/user/custapi/custApiInfo.do); 2026-10-20 documentation/root/review 검토 |
| metadata 일치 | manifest와 .hass-standards.json 값·순서 일치 |
| taxonomy | Core ec18d8b25d1ee39aa8b85a72a170e42bee33228c snapshot. 공식 published Hassfest의 categories 미지원에 대응하여 중앙 `hassfest-core-ref`로 이 source를 선택, 원본 Dockerfile/entrypoint/전체 validator 사용 |
| 실제 검사 구분 | 로컬 전체 Hassfest Integrations1/Invalid0 PASS. HACS 원격 기준8761e7c는 10checks PASS/categories 누락 warning1; 로컬 변경 트리 HACS는 미검증 |

## Execution evidence

- Implementation: `/private/tmp/opinet-current/bin/python -m pytest tests/components/opinet/ -v`; minimum HA uses `/private/tmp/opinet-minimum-ha/bin/python`. Logs: `/private/tmp/opinet-current-tests.log`, `/private/tmp/opinet-minimum-ha-tests.log`; each27passed. `uv pip check --python <env>/bin/python`: PASS.
- Independent: `/private/tmp/opinet-review-current/bin/python -m pytest tests/components/opinet -q`; minimum HA uses `/private/tmp/opinet-review-minimum-ha/bin/python`. Logs: `/private/tmp/opinet-review-current.log`, `/private/tmp/opinet-review-minimum-ha.log`; each27passed and pipcheck PASS.
- Exact package: fresh Linux venv, test requirements+manifest pyproj>=3.6.1+exactpyproj==3.6.1 installed in one resolver with PIP_BUILD_CONSTRAINT=requirements_build_minimum.txt and PIP_NO_CACHE_DIR=1. Original source build with Cython3.0.12, PROJ9.6.0. Independent Python3.14.8/HA2026.10.2/plugin0.13.373/pyproj3.6.1,27passed0.65s and pipcheck PASS. `/private/tmp/opinet-review-minimum-fresh.log`. Earlier unconstrained build25passed2failed and macOS missingPROJ installation failures preserved in `/private/tmp/opinet-pyproj-minimum.log`, `/private/tmp/opinet-review-minimum-pyproj.log`; later fresh installation resolved the build-tool problem without raising the runtime minimum.
- HACS official amd64 image digest `sha256:187499a09c5d41f9f0d42ff80d203ed87b974c028290140913b61e005fb0aab2`: remote8761e7c ten checks PASS, categories warning1. Token passed through environment and never printed. `/private/tmp/opinet-review-hacs.log`. This does not validate the modified tree.
- Hassfest: `docker run --rm -v /Volumes/HDD/GitHub/hass-opinet:/github/workspace minibig-hassfest:ec18d8`, original official Coreec18d8b25d1ee39aa8b85a72a170e42bee33228c Dockerfile/entrypoint/fullvalidator image d6f981f03145: Integrations1/Invalid0 PASS. `/private/tmp/opinet-review-hassfest.log`.
- Updater dry-run: `uv run --no-project --with packaging==26.3 --python 3.14 ../hass-repo-standards/actions/update-manifest/update.py --manifest custom_components/opinet/manifest.json --packages '["pyproj"]'`: proposes>=3.8.0, exit0, no write. Runtime requirement remains>=3.6.1.
- Central unit log: `/private/tmp/opinet-review-central-tests-canonical.log`; implementation `/private/tmp/opinet-standards-subentry-unittest-physical.log`.
- Official HACS Default record checked2026-10-20. data-v2 record exists but downloads field is absent; this is not zero installs. External live Opinet API key/service calls and HA UI were not tested.

## Remote publication and CI correction

Central PR11 squash6839346 passed all four main checks: https://github.com/eigger/hass-repo-standards/actions/runs/39427843961. Integration PR15 initial head81968c0 passed HACS and central template validation. Initial minimum job39427985968 failed during setup-python cache discovery because PIP_NO_CACHE_DIR was inherited. Replace that broad setting with command-specific pip install no-cache-dir through PIP_CONFIG_FILE, preserving the Cython build constraint. PIP_NO_BINARY alone was tested and rejected: cached built wheels remained reusable, and preparing the latest sdist conflicted with the historical Cython build constraint. This is a workflow-environment fix; runtime code/tests/support minima are unchanged. Final head/squash CI evidence is maintained in the central adoption-status row.

## Verified remote PR snapshot

PR15 runtime/CI source `c66ed8f047f62ffca040f452da5c4eef6efe34e2` passed all eight checks. This documentation update does not change runtime/tests/workflows; final PR and merge SHA checks are recorded in the central adoption status.

- [Tests39428475940](https://github.com/eigger/hass-opinet/actions/runs/39428475940): Python3.14.8, HA2026.10.2/plugin0.13.373 and exact minimumHA2026.9.0/plugin0.13.363, pyproj3.8.0; each27passed, pipcheck and both lint jobs PASS.
- [Minimum39428475073](https://github.com/eigger/hass-opinet/actions/runs/39428475073): exactpyproj3.6.1 original source build with Cython3.0.12 and pip install-only cache configuration; actual HA tests and pipcheck PASS. The full central environment action ran successfully.
- [Validate39428476087](https://github.com/eigger/hass-opinet/actions/runs/39428476087): central template PASS, HACS10checks PASS without category warning, official Coreec18d8 source fetch/HEAD match/original Dockerfile/full Hassfest validator Integrations1/Invalid0 PASS.
- Independent review confirmed the full logs, actual versions and failure counts. Earlier failure/cancelled runs are preserved; they are not reused as evidence of success.

## 2026-10-23 Downloads 배지 부분 검증

- 기준: 중앙 `b54ac48102d6e326c6929071fdc02ba8fade794e`의 DOC-03/05·배지 생성기와 Validate 형식 검사기만 부분 채택. 대상 시작 SHA `58613b9c943cd88c7abc5d3579f6eeafe2d0b057`. 기존 전체 채택 결과·예외는 유지하며 이번 변경으로 전체 재채택 완료를 주장하지 않습니다.
- 계획/자체 리뷰: 양언어 관리 블록을 같은 중앙 렌더러로 생성, 잘못된 HACS 데이터 조회 배지를 Downloads로 교체, 집계 의미와 소스 파일 설치 제외를 양언어로 명시. GOV-02에 따라 중앙 호출 pin과 standards-ref를 같은 SHA로 맞춥니다. 이전 기준과 새 기준의 공용 workflow/action 파일은 동일하며 실행 설정·지원 최소·ZIP 배포 설정을 보존합니다.
- 검증 명령·결과와 최종 head SHA·원격 CI 링크는 이 PR 본문에 기록합니다. 문서·배지·형식 검사기 pin만 변경하므로 로컬 HA 환경을 재구축하지 않으며 실제 기기·HA UI·사용자 다운로드 집계는 미검증입니다.
- 실행 결과: WSL Ubuntu Python 3.14.4/PyYAML 6.0.3/packaging 26.0에서 중앙 `scripts/sync_badges.py <repo> --check`, `scripts/check_integration.py <repo>` 및 actionlint 1.7.12의 전체 caller workflow 검사 PASS. Windows Git의 `git diff --check` PASS. 양언어 배지 외 기존 본문은 집계 설명의 정정·추가만 허용하고 보존했습니다.
- 초기 검사 실패 기록: 단일 기준 SHA 계약에 맞지 않는 검사기 pin만의 갱신은 GOV-02에서 거부되어 모든 중앙 pin을 동일 SHA로 정합화했습니다. Windows 중앙 템플릿 CRLF 비교는 실패하여 LF 중앙 snapshot의 Linux 검사로 재검증했습니다. WSL Git은 Windows worktree gitdir 경로를 해석하지 못해 diff 검사를 실패했고 동일 변경의 Windows Git 검사로 대체했습니다. 실패를 PASS로 소급하지 않습니다.

## 2026-10-23 ZIP 릴리스 적용 검증

- 기준 `0c1592977591ecba077a4666d699840062711201` / 대상 시작 `bc2f403ad471a3bf53f1aa023f95ba7ce52b7d43`. HACS-04/CI-11 부분 갱신이며 기존 전체 채택 이력·예외는 유지합니다.
- 계획: hacs.json에 zip_release:true, filename:opinet.zip을 추가하고 중앙 release.yml을 같은 SHA로 생성합니다. 기존 caller는 중앙 pin/standards-ref만 변경합니다. 지원 최소·통합 버전·의존성·구현·README 본문을 보존합니다.
- 검증: 중앙 생성기/정적 검사·actionlint·실제 packager로 추적된 통합 파일의 ZIP 루트·manifest/번역/brand 등 런타임 자료 포함과 저장소 메타데이터 제외를 확인합니다. CLI 검증 명령·실제 버전·최종 head SHA·ZIP 결과·독립 리뷰·원격 CI 링크는 이 PR 본문에서 한 번 기록합니다.
- 중앙 실행 로직은 독립 zip_release_review 리뷰에서 지적 수정 후 추가 지적 없음. 대상 caller/메타데이터/ZIP도 별도 독립 리뷰합니다. 로컬 HA 환경 재구축·새 릴리스 발행·asset 업로드·기기 설치는 수행하지 않으며 미실행을 PASS로 기록하지 않습니다. immutable-releases는 enabled:false로 확인했습니다.


## 2026-10-25 중앙 검사기 부분 갱신 검증

- 검토한 중앙 SHA: `1863343638014adb8a4001afc8fddc1a27dc500f`; 적용 시작 커밋: `acdc4d1487103153a12472f1046ea148ef97c946`.
- 범위: 중앙 pin·standards-ref·검토 기준 기록 정합화. HA 구현·요구 버전은 유지합니다.
- 로컬: Python 3.14.5 / PyYAML 6.0.3, `python scripts/check_integration.py <target>` (검토한 중앙 source에서 실행): PASS.
- actionlint: PASS. PR CI·독립 리뷰 결과는 PR 링크와 check 결과를 확인합니다. 이 로컬 결과만으로 전체 채택 완료를 주장하지 않습니다.
- 독립 리뷰: 별도 review_checker_rollout 담당자가 19개 리포의 workflow 69개·기존 job 100개를 구조 비교했습니다. 새 CI 회귀 지적 없음. 기존 job ID·입력·권한·지원 최소와 통합 코드 보존 및 새 standards job의 중앙 템플릿 일치 확인. 실행 변경 없는 이 기록 추가 전 작업 트리를 검토했습니다.


### 2026-10-25 Standards workflow 분리 검증

- 분리 시작 커밋: `017c30a8f25a7e27b1702a277c15f31f8d626404`; 검토 중앙 소스 `ca740d88b32fa5dcbc94c41fce2908450c76ed50` (중앙 PR #24). Validate는 HACS/Hassfest job을 그대로 유지하며 중앙 job만 standards.yml로 이동하고 표시 이름을 Standards로 변경합니다.
- 독립 리뷰: root 구현의 19개 리포에 대해 별도 fix_scale_atflee_ci 담당자가 Validate job 19개와 이동 job 19개의 YAML 정의를 비교했습니다. 파일 이동·표시 이름 외 실제 검사 단계·이벤트·권한·timeout·입력 변경 없음. 중앙 위치 인식 변경은 root가 별도 독립 리뷰했습니다.
- 로컬: 새 중앙 검사기·actionlint·diff 검사 PASS. 중앙 전체232개·관련38개 회귀 테스트와 양 배치19개 동등성 검사 PASS. 모든 대상 기본 브랜치의 branch protection·rulesets 조회에서 필수 검사 이름 설정이 없어 이름 변경으로 인한 대기 충돌 없음. 원격 CI는 이 PR의 최신 head에서 확인합니다.
- 검사 기준을 추가하거나 완화하지 않았으며 기존 inline 배치도 같은 기준으로 지원합니다. 실제 runtime·지원 최소·의존성은 이 파일 분리에서 변경하지 않습니다.
