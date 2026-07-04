from job_application_agent.integrations.sheets import SheetHeaders, TrackerHeadersSummary
from job_application_agent.tracker_schema import map_sheet_headers, map_tracker_headers


def test_maps_application_headers_to_required_canonical_fields() -> None:
    mapping = map_sheet_headers(
        SheetHeaders(
            title="Applications",
            index=1,
            header_row=1,
            headers=("Company", "Job Title", "Application Status", "Job URL"),
        )
    )

    assert mapping.is_complete is True
    assert [field.canonical_field for field in mapping.mapped_fields] == [
        "company",
        "role",
        "status",
        "job_url",
    ]
    assert mapping.missing_required_fields == ()


def test_reports_unmapped_headers_and_missing_required_fields() -> None:
    mapping = map_sheet_headers(
        SheetHeaders(
            title="Applications",
            index=1,
            header_row=1,
            headers=("Company", "Custom Notes"),
        )
    )

    assert mapping.is_complete is False
    assert mapping.unmapped_headers == ("Custom Notes",)
    assert mapping.missing_required_fields == ("role", "status")


def test_maps_multiple_tabs() -> None:
    summary = TrackerHeadersSummary(
        tabs=(
            SheetHeaders(
                title="Applications",
                index=1,
                header_row=1,
                headers=("Company", "Role", "Status"),
            ),
            SheetHeaders(
                title="Contacts",
                index=3,
                header_row=1,
                headers=("Name", "Email"),
            ),
        )
    )

    mapping = map_tracker_headers(summary)

    assert mapping.is_complete is True
    assert mapping.tabs[0].title == "Applications"
    assert mapping.tabs[1].title == "Contacts"
    assert mapping.tabs[1].mapped_fields[0].canonical_field == "contact_name"


def test_unknown_tabs_are_marked_unmapped_without_required_fields() -> None:
    mapping = map_sheet_headers(
        SheetHeaders(
            title="Unknown Tab",
            index=99,
            header_row=1,
            headers=("Company", "Role"),
        )
    )

    assert mapping.is_complete is True
    assert mapping.missing_required_fields == ()
    assert mapping.unmapped_headers == ("Company", "Role")
