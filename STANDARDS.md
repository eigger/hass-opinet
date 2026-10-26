# 적용한 공통 규칙

- 표준: https://github.com/eigger/hass-repo-standards/tree/v1.1.0
- 참조 커밋 SHA: a6c3f20cea07bb2ccaadd61d3d8048b76f8ded58
- Standards release: v1.1.0
- Resolved standards SHA: a6c3f20cea07bb2ccaadd61d3d8048b76f8ded58
- 기준 확인: 2026-10-20 origin/main `648dad941a118c80325f44c7a13cb5b5b9c1c788`, subsequent published squash fix `6839346bc5e2a11157fecd800f4cb490fc3197ab`; `git ls-remote`로 main 확인
- 검토일: 2026-10-20 (Asia/Seoul), 최초 채택 진행 중
- profile: integration / ha
- 적용 점검표: [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md)
- 중앙 현황표: https://github.com/eigger/hass-repo-standards/blob/main/docs/adoption-status.md
- 조율 / 구현 / 독립 리뷰·검증: root(opinet-adoption) / implementation·documentation / review
- 중앙 현황 갱신: 2026-10-20 로컬 자기 리포 행만 갱신; 원격 미게시, 다른 세션 변경 보존
- 실제 원격 / 기본 브랜치: https://github.com/eigger/hass-opinet.git / main
- 검토 대상: `8761e7c4fe6091df61a622568b011369a65d6568` + adoption PR #15 (https://github.com/eigger/hass-opinet/pull/15); review baseline81968c0, later fixes/evidence are recorded below
- 테스트 경로: `tests/components/opinet/`
- 변경 전·후 지원 최소 HA: `2026.9.0` (`hacs.json.homeassistant`), 상향 없음
- 통합 버전 / 런타임 의존성: `2.0.0` / `pyproj>=3.6.1` 유지
- current 환경: HA 2026.10.2 / Python 3.14 / pytest-homeassistant-custom-component 0.13.373
- 최소 HA 환경: HA 2026.9.0 / Python 3.14 / pytest-homeassistant-custom-component 0.13.363
- 실제 설치 버전·실행 결과·최소 라이브러리 검증: 점검표 참조. 실행하지 않은 조합은 검증 완료로 취급하지 않음
- imagespec·blesession·BLE: requirements/import 없음, DOC-07·DOC-08·HA-09 해당 없음
- HACS Default 근거: [공식 목록](https://github.com/hacs/default/blob/a75c02e2cb94db482c5aaddcc83d0dad00cc20a0/integration#L1025), 2026-10-20 `eigger/hass-opinet` 등재 확인
- Release 근거: [2.0.0](https://github.com/eigger/hass-opinet/releases/tag/2.0.0), 기존 버전 유지
- Default 집계: 공식 HACS integration/data.json의 해당 저장소 downloads를 사용. 필드 미제공·조회 실패는 0 설치를 뜻하지 않음
- 제품 분류: `energy.energy_prices`; 전국/지역/주유소 연료·요소수 가격을 제공하는 실제 서비스 목적에 근거. integration_type 기존 미선언 유지. 상세 근거는 점검표와 `.hass-standards.json`

## 예외

승인한 예외 없음. 검증 미완료·필수 미충족은 점검표의 TODO로 관리하며 예외 승인으로 간주하지 않습니다.

## 변경 영향과 적용

기존 센서·주유소 하위 항목·액션·식별자 계약을 유지하며 테스트를 실제 HA fixture와 entry/platform 로딩으로 전환합니다. README 영문/한국어의 기존 설명·예제를 보존하고 중앙 관리 영역·Default 배지·설치 링크를 적용합니다. Tests/Validate와 의존성 갱신은 검토 SHA로 고정한 공용 workflow를 사용합니다. 지원 최소와 배포 버전은 변경하지 않습니다.

기본 브랜치 반영·원격 CI 전에는 채택 완료로 표시하지 않습니다. 이 작업에서 태그·GitHub Release를 생성하지 않습니다.

## Central checker fix

The user explicitly authorized the central checker fix and squash merging/branch cleanup on 2026-10-20. [Central PR11](https://github.com/eigger/hass-repo-standards/pull/11) was squash merged as `6839346bc5e2a11157fecd800f4cb490fc3197ab` after all four PR checks passed. The original reviewed main was `648dad941a118c80325f44c7a13cb5b5b9c1c788`; the source head was `089c86d48409ae3998078b0466f19849c75fbb9b`. The squash commit has the identical tree. All integration caller references use the new published main commit. [Central CI](https://github.com/eigger/hass-repo-standards/actions/runs/39427564265) passed219 unit tests with7 skips (one local Python syntax case and6 separately exercised payload tests), and the dedicated actual HA payload job passed all6 tests without skips. Local independent checks also passed. Central PR branch was deleted.

The separate Minimum dependency job is a repository-specific PROJ source-build extension using the central python-environment composite action. Shared Tests remains responsible for current/minimum HA and lint. This does not replace the shared Tests caller. Build constraints pin Cython3.0.12 (upstream pyproj issue1451); pip26.2.1 enables isolated build constraints, and the exact runtime requirement remains pyproj>=3.6.1.

## Published integration review

[Integration PR15](https://github.com/eigger/hass-opinet/pull/15) targets main. Central squash6839346 passed all four [main CI jobs](https://github.com/eigger/hass-repo-standards/actions/runs/39427843961). The final integration PR and squash-merge commit checks are recorded in the [central adoption status](https://github.com/eigger/hass-repo-standards/blob/main/docs/adoption-status.md); this checklist is an implementation snapshot, not a claim about an unverified later commit.

The initial remote minimum-dependency job failed before installation because disabling pip caching also reached setup-python's pip-cache discovery. The fix scopes no-cache-dir to pip install through a dedicated PIP_CONFIG_FILE, while keeping setup-python cache discovery functional. PIP_NO_BINARY was considered but rejected after actual resolver/cached-wheel experiments. No failure was ignored and the exact runtime minimum remains3.6.1.

PR15 reviewed source `c66ed8f047f62ffca040f452da5c4eef6efe34e2` passed all eight remote checks (Tests39428475940, Minimum39428475073, Validate39428476087). Final documentation records this verified snapshot. Squash/default-branch CI evidence is maintained in the central adoption-status row after merging.

## 2026-10-23 다운로드 배지 부분 갱신

- 배지·DOC-03/05와 Validate 형식 검사기만 중앙 [`b54ac48102d6e326c6929071fdc02ba8fade794e`](https://github.com/eigger/hass-repo-standards/tree/b54ac48102d6e326c6929071fdc02ba8fade794e)를 채택합니다. 이전 기준 SHA `6839346bc5e2a11157fecd800f4cb490fc3197ab`의 채택 이력·예외는 보존합니다. 모든 중앙 workflow/action pin과 standards-ref는 GOV-02의 단일 기준 SHA 계약에 맞춰 갱신합니다. 중앙 diff에서 공용 workflow/action 실행 파일은 이전 기준과 동일함을 확인했습니다.
- 대상 기본 브랜치 커밋: `58613b9c943cd88c7abc5d3579f6eeafe2d0b057`. 주 에이전트 직접 구현·자체 리뷰(GOV-05의 배지/생성물 변경 범위), 검증은 [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md#2026-10-23-downloads-배지-부분-검증)에 기록합니다.
- Downloads는 모든 릴리스 첨부 asset 다운로드 합계입니다. 사용자 지시에 따라 ZIP 배포를 도입하지 않으며 현재 HACS 소스 파일 설치는 이 수치에 집계되지 않습니다. 통합 코드·의존성·지원 최소·기존 설치 안내는 변경하지 않습니다.

## 2026-10-23 ZIP 릴리스 배포

- 기준 중앙 SHA: `0c1592977591ecba077a4666d699840062711201` ([중앙 PR15](https://github.com/eigger/hass-repo-standards/pull/15) 스쿼시 머지). 이전 `b54ac48102d6e326c6929071fdc02ba8fade794e` 채택 이력·예외를 보존하며 HACS-04·CI-11의 ZIP 배포 계약을 추가합니다.
- 대상 시작 SHA: `bc2f403ad471a3bf53f1aa023f95ba7ce52b7d43`. hacs.json의 zip_release/filename과 중앙 release caller를 함께 적용합니다. archive 파일명은 `opinet.zip`, ZIP 루트는 해당 통합 파일입니다.
- 중앙 workflow/action pin과 standards-ref는 단일 SHA로 정합화합니다. release:published에서 기존 해당 릴리스에 ZIP만 첨부하며 소스 버전·태그·릴리스 발행은 자동 변경하지 않습니다. 기존 asset 덮어쓰기를 거부합니다.
- 기존 지원 최소 HA `2026.9.0`와 통합 버전 `2.0.1` 및 의존성·구현은 보존합니다. 기존 태그의 hacs.json은 소급 수정하지 않으므로 다음 릴리스부터 ZIP 설치로 전환됩니다.
- immutable-releases 설정은 enabled=false/enforced_by_owner=false로 확인했습니다. 업로드 지연·실패 및 기존 asset 복구는 중앙 [릴리스 계약](https://github.com/eigger/hass-repo-standards/blob/0c1592977591ecba077a4666d699840062711201/docs/releases.md#zip-릴리스-첨부)을 따릅니다. 실제 새 릴리스 발행·설치·기기 검증은 이번 작업에 포함하지 않습니다.

## 2026-10-25 중앙 검사기 갱신

- 검토한 중앙 main: `1863343638014adb8a4001afc8fddc1a27dc500f` (git ls-remote 확인). 이전 기본 기준 `0c1592977591ecba077a4666d699840062711201`의 채택 이력은 위 기록을 보존합니다.
- 모든 중앙 workflow/action pin과 reusable workflow의 standards-ref를 같은 검토 SHA로 맞춥니다. HACS-04는 actions/*의 full SHA 고정을 유지하면서 SHA 값 차이를 허용합니다.
- 통합 코드·런타임 의존성·지원 최소·배포 버전은 이번 변경 대상이 아닙니다. 기존 채택 범위를 전체 완료로 바꾸지 않으며 실제 검증 결과와 남은 항목은 ADOPTION_CHECKLIST.md의 같은 날짜 기록을 참조합니다.


### 2026-10-25 Standards 파일·표시 이름 분리

- 기존 Validate의 중앙 검사 job을 `standards.yml`로 옮기고 workflow/job 표시 이름을 `Standards`로 줄였습니다. Validate의 HACS/Hassfest, 검사 항목·통과 기준·실행 단계·조건·권한은 유지합니다.
- 위치 인식과 중앙 명명 안내를 맞춘 검토 소스: `ca740d88b32fa5dcbc94c41fce2908450c76ed50` ([중앙 PR #24](https://github.com/eigger/hass-repo-standards/pull/24), 현재 이 PR의 의존 변경). 이전 기준 `1863343638014adb8a4001afc8fddc1a27dc500f`의 검증 이력은 앞 기록으로 보존합니다. 모든 중앙 pin·standards-ref는 같은 새 검토 소스로 맞춥니다.

## 2026-10-25 중앙 immutable release 참조 전환

- 사용자 요청에 따라 현재 중앙 참조를 immutable `v1.0.0` / resolved SHA `44349ee5621eea5d80e5c427f7a2435d2c2491bb`로 전환했습니다. 중앙 workflow/action caller는 exact release tag를, `standards-ref`는 resolved full SHA를 사용합니다.
- 범위는 중앙 참조·기록 정합화뿐입니다. 기존 지원 최소, 통합 버전, manifest, 런타임 요구사항, 구현, 테스트와 CI의 caller-owned 설정은 보존했습니다.
- 과거 SHA·검증·예외 기록은 역사적 증거로 보존합니다. 이번 변경은 generated reference-only 범위이므로 GOV-05 자체 검토이며 PR CI/병합은 대기 상태입니다.
