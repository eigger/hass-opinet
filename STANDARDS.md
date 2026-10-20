# 적용한 공통 규칙

- 표준: https://github.com/eigger/hass-repo-standards/tree/6839346bc5e2a11157fecd800f4cb490fc3197ab
- 참조 커밋 SHA: `6839346bc5e2a11157fecd800f4cb490fc3197ab`
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
