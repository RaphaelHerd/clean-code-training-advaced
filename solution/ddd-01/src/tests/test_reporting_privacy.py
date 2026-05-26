from dataclasses import fields
from datetime import datetime

from clinicare.domain.events import PatientRegistered
from clinicare.infrastructure.projections import MonthlyReport, ReportingProjection


def test_report_contains_only_monthly_counts_not_pii() -> None:
    field_names = {field.name for field in fields(MonthlyReport)}

    assert field_names == {"new_patients", "cases_opened", "meds_prescribed"}
    assert all(field.type is int for field in fields(MonthlyReport))


def test_projection_does_not_store_patient_identifier() -> None:
    projection = ReportingProjection()
    projection.on_patient_registered(
        PatientRegistered(
            id="evt-1",
            occurred_at=datetime(2026, 5, 16, 12, 0, 0),
            patient_id="patient-secret",
        )
    )

    report = projection.get_report(2026, 5)

    assert report.new_patients == 1
    assert "patient-secret" not in repr(report)
