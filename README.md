# TurKMedBench Public Research Preview

TurKMedBench is a clinician-led research project for Turkey-specific clinical AI evaluation. This public preview currently tracks 84 synthetic case drafts across 21 specialties (wave-1 expansion applied 2026-08-22); the initially published case set contained 22 cases across 11 specialties.

## Current status

- Research preview, not a clinically validated benchmark release.
- Synthetic cases only; no patient-level data or direct identifiers.
- No expected answers, scoring keys, reviewer records, model outputs, rankings, or clinical performance claims.
- All cases still require source freshness review and independent clinician adjudication before any scored release.
- Not for diagnosis, treatment, triage, or other clinical use.

## Contents

- `cases/`: synthetic Turkish clinical evaluation inputs.
- `contracts/`: machine-readable case schema and local implementation policy.
- `docs/TurKMedBench_DATA_CARD_v1.md`: data scope and limitations.
- `docs/TurKMedBench_CLINICIAN_REVIEWER_INVITATION_PUBLIC_v1.md`: public reviewer-interest boundary.
- `manifest/`: exact public file inventory and SHA-256 evidence.

## Integrity check

On systems with `sha256sum`:

```bash
sha256sum -c SHA256SUMS
```

## License and citation

No reuse license is granted yet. Public visibility permits inspection, but redistribution or adaptation rights are not granted until the owner selects a license. Citation metadata is also pending final owner approval.

## Private material

The internal research repository remains private. Restricted scoring keys, expected responses, source-review work, adjudication packets, reviewer operations, and model-run artifacts are intentionally excluded from this repository and its Git history.
