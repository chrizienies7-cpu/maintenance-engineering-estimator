import streamlit as st
import math

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Maintenance Engineering Estimator",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "current_job" not in st.session_state:
    st.session_state.current_job = {}

if "jobs" not in st.session_state:
    st.session_state.jobs = []

if "painting_results" not in st.session_state:
    st.session_state.painting_results = None


# ============================================================
# NAVIGATION FUNCTION
# ============================================================

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🔧 KHAL")
    st.caption("Maintenance Engineering")
    st.caption("Engineering Estimation System")

    st.divider()

    st.subheader("Navigation")

    if st.button(
        "🏠 Dashboard",
        use_container_width=True
    ):
        go_to("Dashboard")

    if st.button(
        "➕ New Job",
        use_container_width=True
    ):
        go_to("New Job")

    if st.button(
        "📋 Job Records",
        use_container_width=True
    ):
        go_to("Job Records")

    if st.button(
        "📊 Reports",
        use_container_width=True
    ):
        go_to("Reports")

    st.divider()

    st.caption("FYP Prototype • 2026")


# ============================================================
# DASHBOARD PAGE
# ============================================================

if st.session_state.page == "Dashboard":

    st.title("Maintenance Engineering Estimator")

    st.write(
        "Industrial Maintenance Job Planning & "
        "Engineering Quantity Estimation"
    )

    st.divider()

    # ========================================================
    # DASHBOARD METRICS
    # ========================================================

    st.subheader("Dashboard")

    total_jobs = len(st.session_state.jobs)

    draft_jobs = sum(
        1 for job in st.session_state.jobs
        if job.get("Status") == "Draft"
    )

    completed_jobs = sum(
        1 for job in st.session_state.jobs
        if job.get("Status") == "Completed"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Jobs",
            total_jobs
        )

    with col2:
        st.metric(
            "Draft Jobs",
            draft_jobs
        )

    with col3:
        st.metric(
            "Completed Jobs",
            completed_jobs
        )

    with col4:
        st.metric(
            "Work Types",
            "3"
        )

    st.write("")

    # ========================================================
    # START NEW ESTIMATION
    # ========================================================

    st.subheader("Start New Estimation")

    with st.container(border=True):

        left, right = st.columns([3, 1])

        with left:

            st.subheader("🔧 Engineering Job Estimation")

            st.write(
                "Create a new industrial maintenance job "
                "and calculate engineering work quantities "
                "based on site measurements."
            )

            st.write("**Current Work Modules**")

            st.write("🎨 Pipe Painting / Coating")
            st.write("🧱 Pipe Insulation")
            st.write("🔄 Insulation Replacement")

        with right:

            st.write("")
            st.write("")

            if st.button(
                "➕ CREATE NEW JOB",
                type="primary",
                use_container_width=True,
                key="dashboard_create_job"
            ):
                go_to("New Job")

    st.write("")

    # ========================================================
    # RECENT JOBS
    # ========================================================

    st.subheader("Recent Jobs")

    if len(st.session_state.jobs) == 0:

        st.info(
            "No job records available. "
            "Create your first maintenance estimation job."
        )

    else:

        st.dataframe(
            st.session_state.jobs,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# NEW JOB PAGE
# ============================================================

elif st.session_state.page == "New Job":

    st.title("➕ Create New Job")

    st.write(
        "Enter the basic information for the "
        "industrial maintenance activity."
    )

    st.divider()

    # ========================================================
    # JOB INFORMATION
    # ========================================================

    st.subheader("1. Job Information")

    col1, col2 = st.columns(2)

    with col1:

        job_reference = st.text_input(
            "Job Reference / Work Order",
            placeholder="Example: KH-2026-001"
        )

        location = st.text_input(
            "Work Location / Area",
            placeholder="Example: Area 5"
        )

        equipment = st.text_input(
            "Equipment / Tag Number",
            placeholder="Example: 4720-P-002A"
        )

    with col2:

        work_type = st.selectbox(
            "Work Type",
            [
                "Select Work Type",
                "Pipe Painting / Coating",
                "Pipe Insulation",
                "Insulation Replacement"
            ]
        )

        inspection_date = st.date_input(
            "Inspection / Assessment Date"
        )

        prepared_by = st.text_input(
            "Prepared By",
            placeholder="Enter name"
        )

    st.write("")

    # ========================================================
    # JOB DESCRIPTION
    # ========================================================

    st.subheader("2. Job Description")

    job_description = st.text_area(
        "Scope / Description of Work",
        placeholder=(
            "Example: External surface preparation "
            "and painting of industrial piping."
        ),
        height=120
    )

    st.divider()

    # ========================================================
    # NAVIGATION BUTTONS
    # ========================================================

    back_col, continue_col = st.columns(2)

    with back_col:

        if st.button(
            "← Back to Dashboard",
            use_container_width=True
        ):
            go_to("Dashboard")

    with continue_col:

        if st.button(
            "Save & Continue →",
            type="primary",
            use_container_width=True
        ):

            if not job_reference:

                st.warning(
                    "Please enter the Job Reference / Work Order."
                )

            elif work_type == "Select Work Type":

                st.warning(
                    "Please select a Work Type."
                )

            else:

                # Save job information
                st.session_state.current_job = {

                    "Job Reference": job_reference,
                    "Location": location,
                    "Equipment": equipment,
                    "Work Type": work_type,
                    "Inspection Date": str(
                        inspection_date
                    ),
                    "Prepared By": prepared_by,
                    "Description": job_description,
                    "Status": "Draft"
                }

                # Clear old calculation
                st.session_state.painting_results = None

                # Go to selected module
                if work_type == "Pipe Painting / Coating":

                    go_to("Painting Calculator")

                elif work_type == "Pipe Insulation":

                    go_to("Insulation Calculator")

                elif work_type == "Insulation Replacement":

                    go_to("Replacement Calculator")


# ============================================================
# PAINTING / COATING CALCULATOR
# ============================================================

elif st.session_state.page == "Painting Calculator":

    job = st.session_state.current_job

    st.title("🎨 Pipe Painting / Coating")

    st.write(
        "Engineering quantity estimation for "
        "industrial piping coating work."
    )

    st.divider()

    # ========================================================
    # JOB SUMMARY
    # ========================================================

    st.subheader("Job Summary")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write("**Job Reference**")

        st.write(
            job.get(
                "Job Reference",
                "-"
            )
        )

    with col2:

        st.write("**Equipment / Tag**")

        st.write(
            job.get(
                "Equipment",
                "-"
            )
        )

    with col3:

        st.write("**Work Location**")

        st.write(
            job.get(
                "Location",
                "-"
            )
        )

    st.divider()

    # ========================================================
    # PIPE DIMENSIONS
    # ========================================================

    st.subheader("1. Pipe Dimensions")

    st.caption(
        "Enter pipe dimensions based on site measurements "
        "or available technical information."
    )

    dim1, dim2, dim3 = st.columns(3)

    with dim1:

        diameter_mm = st.number_input(
            "Outside Diameter (mm)",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

    with dim2:

        length_m = st.number_input(
            "Pipe Length (m)",
            min_value=0.0,
            value=0.0,
            step=0.1
        )

    with dim3:

        quantity = st.number_input(
            "Number of Pipes",
            min_value=1,
            value=1,
            step=1
        )

    st.write("")

    # ========================================================
    # COATING PARAMETERS
    # ========================================================

    st.subheader("2. Coating Parameters")

    st.caption(
        "Use coating parameters from the applicable "
        "specification or manufacturer's technical data sheet."
    )

    coat1, coat2 = st.columns(2)

    with coat1:

        dft_um = st.number_input(
            "Required DFT (µm)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            help="Required Dry Film Thickness"
        )

    with coat2:

        volume_solids = st.number_input(
            "Volume Solids (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
            help=(
                "Obtain this value from the coating "
                "manufacturer's technical data sheet."
            )
        )

    st.write("")

    # ========================================================
    # CALCULATE BUTTON
    # ========================================================

    if st.button(
        "🧮 CALCULATE ENGINEERING QUANTITY",
        type="primary",
        use_container_width=True
    ):

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if diameter_mm <= 0:

            st.warning(
                "Please enter a valid outside diameter."
            )

        elif length_m <= 0:

            st.warning(
                "Please enter a valid pipe length."
            )

        elif dft_um <= 0:

            st.warning(
                "Please enter the required DFT."
            )

        elif volume_solids <= 0:

            st.warning(
                "Please enter the coating volume solids."
            )

        else:

            # ------------------------------------------------
            # CALCULATION 1:
            # CONVERT DIAMETER mm -> m
            # ------------------------------------------------

            diameter_m = diameter_mm / 1000


            # ------------------------------------------------
            # CALCULATION 2:
            # PIPE EXTERNAL SURFACE AREA
            #
            # A = π × D × L × N
            # ------------------------------------------------

            surface_area = (
                math.pi
                * diameter_m
                * length_m
                * quantity
            )


            # ------------------------------------------------
            # CALCULATION 3:
            # VOLUME SOLIDS
            # ------------------------------------------------

            volume_solids_decimal = (
                volume_solids / 100
            )


            # ------------------------------------------------
            # CALCULATION 4:
            # WET FILM THICKNESS
            #
            # WFT = DFT / Volume Solids
            # ------------------------------------------------

            wft_um = (
                dft_um
                / volume_solids_decimal
            )


            # ------------------------------------------------
            # CALCULATION 5:
            # THEORETICAL COATING QUANTITY
            #
            # Litres = Area × WFT / 1000
            # ------------------------------------------------

            theoretical_paint_l = (
                surface_area
                * wft_um
                / 1000
            )


            # ------------------------------------------------
            # SAVE RESULTS
            # ------------------------------------------------

            st.session_state.painting_results = {

                "Surface Area": surface_area,
                "DFT": dft_um,
                "WFT": wft_um,
                "Volume Solids": volume_solids,
                "Theoretical Paint": theoretical_paint_l
            }


    # ========================================================
    # RESULTS
    # ========================================================

    if st.session_state.painting_results is not None:

        results = st.session_state.painting_results

        st.divider()

        st.subheader("3. Engineering Results")

        result1, result2, result3 = st.columns(3)

        with result1:

            st.metric(
                "Total Surface Area",
                f"{results['Surface Area']:.2f} m²"
            )

        with result2:

            st.metric(
                "Required WFT",
                f"{results['WFT']:.2f} µm"
            )

        with result3:

            st.metric(
                "Theoretical Coating Quantity",
                f"{results['Theoretical Paint']:.2f} L"
            )

        st.write("")

        # ====================================================
        # CALCULATION SUMMARY
        # ====================================================

        with st.container(border=True):

            st.subheader("Calculation Summary")

            summary1, summary2 = st.columns(2)

            with summary1:

                st.write(
                    "**Total External Surface Area:**"
                )

                st.write(
                    f"{results['Surface Area']:.2f} m²"
                )

                st.write(
                    "**Required DFT:**"
                )

                st.write(
                    f"{results['DFT']:.2f} µm"
                )

            with summary2:

                st.write(
                    "**Volume Solids:**"
                )

                st.write(
                    f"{results['Volume Solids']:.1f}%"
                )

                st.write(
                    "**Calculated WFT:**"
                )

                st.write(
                    f"{results['WFT']:.2f} µm"
                )

            st.write("")

            st.write(
                "**Theoretical Coating Quantity:**"
            )

            st.write(
                f"{results['Theoretical Paint']:.2f} L"
            )

        st.info(
            "The theoretical coating quantity does not "
            "include practical application losses, "
            "overspray, surface profile effects, wastage "
            "or other site-related allowances."
        )

    st.write("")

    # ========================================================
    # BOTTOM NAVIGATION
    # ========================================================

    nav1, nav2 = st.columns(2)

    with nav1:

        if st.button(
            "← Back to Job Information",
            use_container_width=True
        ):

            st.session_state.painting_results = None

            go_to("New Job")

    with nav2:

        if st.button(
            "🏠 Return to Dashboard",
            use_container_width=True
        ):

            go_to("Dashboard")


# ============================================================
# PIPE INSULATION PAGE
# ============================================================

elif st.session_state.page == "Insulation Calculator":

    st.title("🧱 Pipe Insulation")

    st.write(
        "Engineering estimation for "
        "industrial pipe insulation work."
    )

    st.divider()

    st.info(
        "The pipe insulation engineering calculation "
        "module will be developed next."
    )

    if st.button(
        "← Back to Job Information"
    ):
        go_to("New Job")


# ============================================================
# INSULATION REPLACEMENT PAGE
# ============================================================

elif st.session_state.page == "Replacement Calculator":

    st.title("🔄 Insulation Replacement")

    st.write(
        "Engineering estimation for industrial "
        "pipe insulation replacement work."
    )

    st.divider()

    st.info(
        "The insulation replacement engineering "
        "calculation module will be developed next."
    )

    if st.button(
        "← Back to Job Information"
    ):
        go_to("New Job")


# ============================================================
# JOB RECORDS PAGE
# ============================================================

elif st.session_state.page == "Job Records":

    st.title("📋 Job Records")

    st.write(
        "Maintenance engineering estimation records."
    )

    st.divider()

    if len(st.session_state.jobs) == 0:

        st.info(
            "No saved job records are available yet."
        )

    else:

        st.dataframe(
            st.session_state.jobs,
            use_container_width=True,
            hide_index=True
        )

    st.write("")

    if st.button(
        "➕ Create New Job",
        type="primary"
    ):
        go_to("New Job")


# ============================================================
# REPORTS PAGE
# ============================================================

elif st.session_state.page == "Reports":

    st.title("📊 Engineering Reports")

    st.write(
        "Engineering estimation reports "
        "and job summaries."
    )

    st.divider()

    st.info(
        "Report generation will be developed "
        "in a later stage of the application."
    )
