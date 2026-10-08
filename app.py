
# ============================================================
# ENGINEERING PDF REPORT MODULE
# ============================================================

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def report_pdf(job, pipes, spots_by_pipe, coats_by_pipe):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportHeading",
            parent=styles["Heading1"],
            alignment=TA_CENTER,
            fontSize=15,
            leading=19,
            spaceAfter=12,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportSection",
            parent=styles["Heading2"],
            fontSize=11,
            leading=14,
            spaceBefore=12,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportCell",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
        )
    )

    story = []

    def text(value):
        return escape(str(value if value is not None else "-"))

    def paragraph(value):
        return Paragraph(
            text(value),
            styles["ReportCell"]
        )

    def section(title):
        story.append(
            Paragraph(
                text(title),
                styles["ReportSection"]
            )
        )

    def make_table(headers, data, widths=None):

        table_data = [
            [paragraph(h) for h in headers]
        ]

        for row in data:
            table_data.append([
                paragraph(v) for v in row
            ])

        table = Table(
            table_data,
            colWidths=widths,
            repeatRows=1,
            hAlign="LEFT"
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#DCE6D0")
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
            ])
        )

        story.append(table)
        story.append(Spacer(1, 8 * mm))

    # --------------------------------------------------------
    # REPORT TITLE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "ENGINEERING SITE VISIT & "
            "ESTIMATION REPORT",
            styles["ReportHeading"]
        )
    )

    story.append(
        Paragraph(
            "Industrial Maintenance Engineering "
            "- FYP Prototype",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 8 * mm))

    # --------------------------------------------------------
    # SECTION 1 - JOB INFORMATION
    # --------------------------------------------------------

    section("1. Job Information")

    job_details = [
        [
            "Job Reference",
            job.get("job_reference", "-")
        ],
        [
            "Site Visit Date",
            job.get("inspection_date", "-")
        ],
        [
            "Work Type",
            job.get("work_type", "-")
        ],
        [
            "Work Activity",
            job.get("work_activity", "-")
        ],
        [
            "Location",
            job.get("location", "-")
        ],
        [
            "Supervisor",
            job.get("supervisor", "-")
        ],
        [
            "Prepared By",
            job.get("prepared_by", "-")
        ],
        [
            "Job Status",
            job.get("status", "-")
        ],
    ]

    make_table(
        ["Description", "Information"],
        job_details,
        [55 * mm, 123 * mm]
    )

    section("2. Scope of Work")

    story.append(
        Paragraph(
            text(
                job.get("description")
                or "No scope description provided."
            ),
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 6 * mm))

    # --------------------------------------------------------
    # SECTION 3 - PIPE MEASUREMENTS
    # --------------------------------------------------------

    section("3. Equipment / Pipe Measurements")

    pipe_data = []

    for pipe in pipes:

        pipe_data.append([
            pipe.get("tag_number", "-"),
            pipe.get("coating_system_id", "-"),
            pipe.get("area_method", "-"),
            (
                f"{float(pipe.get('surface_area_m2') or 0):.3f}"
            ),
        ])

    if pipe_data:

        make_table(
            [
                "Equipment / Tag",
                "Coating System",
                "Area Method",
                "Area (m2)"
            ],
            pipe_data,
            [
                49 * mm,
                43 * mm,
                46 * mm,
                40 * mm
            ]
        )

    # --------------------------------------------------------
    # SECTION 4 - SPOT MEASUREMENTS
    # --------------------------------------------------------

    spot_data = []

    for pipe in pipes:

        pipe_id = pipe["id"]

        for spot in spots_by_pipe.get(
            pipe_id, []
        ):

            spot_data.append([
                pipe.get("tag_number", "-"),
                spot.get("spot_number", "-"),
                (
                    f"{float(spot.get('spot_length_m') or 0):.3f}"
                ),
                (
                    f"{float(spot.get('spot_width_m') or 0):.3f}"
                ),
                spot.get("spot_quantity", 0),
                (
                    f"{float(spot.get('spot_area_m2') or 0):.3f}"
                ),
            ])

    if spot_data:

        section("4. Repair Spot Measurements")

        make_table(
            [
                "Tag",
                "Spot",
                "Length (m)",
                "Width (m)",
                "Qty",
                "Area (m2)"
            ],
            spot_data,
            [
                39 * mm,
                27 * mm,
                29 * mm,
                29 * mm,
                19 * mm,
                35 * mm
            ]
        )

    # --------------------------------------------------------
    # SECTION 5 - COATING CALCULATIONS
    # --------------------------------------------------------

    section("5. Coating Layer Estimation")

    coat_data = []

    for pipe in pipes:

        pipe_id = pipe["id"]

        coats = coats_by_pipe.get(
            pipe_id, []
        )

        coats = sorted(
            coats,
            key=lambda c: c.get(
                "coat_number", 0
            )
        )

        for coat in coats:

            coat_data.append([
                pipe.get("tag_number", "-"),
                coat.get("coat_number", "-"),
                coat.get(
                    "coating_description", "-"
                ),
                (
                    f"{float(coat.get('dft_um') or 0):.0f}"
                ),
                (
                    f"{float(coat.get('volume_solids_pct') or 0):.1f}"
                ),
                (
                    f"{float(coat.get('wft_um') or 0):.1f}"
                ),
                (
                    f"{float(coat.get('theoretical_coating_l') or 0):.3f}"
                ),
            ])

    if coat_data:

        make_table(
            [
                "Tag",
                "Coat",
                "Coating",
                "DFT",
                "VS %",
                "WFT",
                "Litre"
            ],
            coat_data,
            [
                28 * mm,
                14 * mm,
                65 * mm,
                16 * mm,
                16 * mm,
                17 * mm,
                22 * mm
            ]
        )

    else:

        story.append(
            Paragraph(
                "No coating layer records available.",
                styles["Normal"]
            )
        )

    # --------------------------------------------------------
    # SECTION 6 - ENGINEERING SUMMARY
    # --------------------------------------------------------

    section("6. Engineering Estimation Summary")

    total_area = sum(
        float(
            pipe.get("surface_area_m2") or 0
        )
        for pipe in pipes
    )

    total_coating = sum(
        float(
            pipe.get("theoretical_coating_l") or 0
        )
        for pipe in pipes
    )

    summary = [
        [
            "Number of Equipment / Pipe Tags",
            len(pipes)
        ],
        [
            "Total Estimated Surface Area",
            f"{total_area:.3f} m2"
        ],
        [
            "Total Theoretical Coating Quantity",
            f"{total_coating:.3f} L"
        ],
    ]

    make_table(
        ["Parameter", "Result"],
        summary,
        [
            105 * mm,
            73 * mm
        ]
    )

    # --------------------------------------------------------
    # SECTION 7 - REMARKS
    # --------------------------------------------------------

    section("7. Engineering Notes")

    story.append(
        Paragraph(
            "The estimated coating quantities are "
            "theoretical and exclude application "
            "losses, overspray, wastage and other "
            "project-specific allowances.",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 4 * mm))

    story.append(
        Paragraph(
            "Coating specifications, nominal DFT "
            "and manufacturer volume solids must "
            "be verified against the applicable "
            "project requirements and technical "
            "data sheets.",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 8 * mm))

    story.append(
        Paragraph(
            "Generated by Maintenance Engineering "
            "Estimator - Academic FYP Prototype",
            styles["Normal"]
        )
    )

    document.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf
