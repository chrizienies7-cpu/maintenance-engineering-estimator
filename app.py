import math
import streamlit as st
from supabase import create_client, Client


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
# SUPABASE CONNECTION
# ============================================================

@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase: Client = init_supabase()


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "job_data" not in st.session_state:
    st.session_state.job_data = {}

if "calculation_result" not in st.session_state:
    st.session_state.calculation_result = {}


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_jobs():

    try:

        response = (
            supabase
            .table("jobs")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:

        st.error(
            f"Unable to retrieve jobs: {e}"
        )

        return []


def save_job(job_data):

    try:

        response = (
            supabase
            .table("jobs")
            .insert(job_data)
            .execute()
        )

        return True, response

    except Exception as e:

        return False, str(e)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🔧 KHAL")

    st.caption(
        "Maintenance Engineering"
    )

    st.divider()

    st.subheader("Navigation")

    if st.button(
        "🏠 Dashboard",
        use_container_width=True
    ):

        st.session_state.page = "Dashboard"
        st.rerun()

    if st.button(
        "➕ New Job",
        use_container_width=True
    ):

        st.session_state.job_data = {}
        st.session_state.calculation_result = {}

        st.session_state.page = "New Job"

        st.rerun()

    if st.button(
        "📋 Job Records",
        use_container_width=True
    ):

        st.session_state.page = "Job Records"
        st.rerun()

    if st.button(
        "📊 Reports",
        use_container_width=True
    ):

        st.session_state.page = "Reports"
        st.rerun()

    st.divider()

    st.caption(
        "Engineering Estimation System"
    )

    st.caption(
        "FYP Prototype • 2026"
    )


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":

    st.title(
        "Maintenance Engineering Estimator"
    )

    st.write(
        "Industrial Maintenance Job Planning & "
        "Engineering Quantity Estimation"
    )

    st.divider()

    jobs = get_jobs()

    total_jobs = len(jobs)

    draft_jobs = sum(
        1
        for job in jobs
        if job.get("status") == "Draft"
    )

    completed_jobs = sum(
        1
        for job in jobs
        if job.get("status") == "Completed"
    )

    st.subheader("Dashboard")

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
            3
        )

    st.write("")

    st.subheader(
        "Start New Estimation"
    )

    left, right = st.columns([3, 1])

    with left:

        with st.container(border=True):

            st.subheader(
                "🔧 Engineering Job Estimation"
            )

            st.write(
                "Create a new industrial maintenance job "
                "and calculate engineering work quantities "
                "based on site measurements."
            )

            st.write(
                "**Current Work Modules**"
            )

            st.write(
                "🎨 Pipe Painting / Coating"
            )

            st.write(
                "🧱 Pipe Insulation"
            )

            st.write(
                "🔄 Insulation Replacement"
            )

    with right:

        st.write("")
        st.write("")

        if st.button(
            "➕ CREATE NEW JOB",
            type="primary",
            use_container_width=True
        ):

            st.session_state.job_data = {}
            st.session_state.calculation_result = {}

            st.session_state.page = "New Job"

            st.rerun()

    st.write("")

    st.subheader("Recent Jobs")

    if len(jobs) == 0:

        st.info(
            "No job records available."
        )

    else:

        for job in jobs[:5]:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [2, 2, 1]
                )

                with col1:

                    st.write(
                        f"**{job.get('job_reference', '-')}**"
                    )

                    st.caption(
                        job.get(
                            "work_type",
                            "-"
                        )
                    )

                with col2:

                    st.write(
                        job.get(
                            "location",
                            "-"
                        )
                    )

                    st.caption(
                        job.get(
                            "equipment",
                            "-"
                        )
                    )

                with col3:

                    st.write(
                        f"**{job.get('status', 'Draft')}**"
                    )


# ============================================================
# NEW JOB PAGE
# ============================================================

elif st.session_state.page == "New Job":

    st.title(
        "➕ Create New Job"
    )

    st.write(
        "Enter the basic information for the "
        "industrial maintenance activity."
    )

    st.divider()

    st.subheader(
        "1. Job Information"
    )

    col1, col2 = st.columns(2)

    with col1:

        job_reference = st.text_input(
            "Job Reference / Work Order *",
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
            "Work Type *",
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

    st.subheader(
        "2. Job Description"
    )

    job_description = st.text_area(
        "Scope / Description of Work",
        placeholder=(
            "Example: External surface preparation "
            "and painting of piping..."
        ),
        height=150
    )

    st.divider()

    back_col, continue_col = st.columns(2)

    with back_col:

        if st.button(
            "← Back to Dashboard",
            use_container_width=True
        ):

            st.session_state.page = "Dashboard"

            st.rerun()

    with continue_col:

        if st.button(
            "Continue to Engineering Input →",
            type="primary",
            use_container_width=True
        ):

            if not job_reference:

                st.warning(
                    "Please enter the Job Reference."
                )

            elif work_type == "Select Work Type":

                st.warning(
                    "Please select a Work Type."
                )

            else:

                st.session_state.job_data = {

                    "job_reference":
                        job_reference,

                    "location":
                        location,

                    "equipment":
                        equipment,

                    "work_type":
                        work_type,

                    "inspection_date":
                        str(inspection_date),

                    "prepared_by":
                        prepared_by,

                    "description":
                        job_description
                }

                if work_type == "Pipe Painting / Coating":

                    st.session_state.page = (
                        "Coating Calculation"
                    )

                elif work_type == "Pipe Insulation":

                    st.session_state.page = (
                        "Insulation Calculation"
                    )

                elif work_type == "Insulation Replacement":

                    st.session_state.page = (
                        "Replacement Calculation"
                    )

                st.rerun()


# ============================================================
# PIPE PAINTING / COATING CALCULATION
# ============================================================

elif st.session_state.page == "Coating Calculation":

    job = st.session_state.job_data

    st.title(
        "🎨 Pipe Painting / Coating"
    )

    st.write(
        "Engineering Quantity Estimation"
    )

    st.divider()

    # --------------------------------------------------------
    # JOB SUMMARY
    # --------------------------------------------------------

    st.subheader("Job Summary")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            "**Job Reference**"
        )

        st.write(
            job.get(
                "job_reference",
                "-"
            )
        )

    with col2:

        st.write(
            "**Location**"
        )

        st.write(
            job.get(
                "location",
                "-"
            )
        )

    with col3:

        st.write(
            "**Equipment / Tag**"
        )

        st.write(
            job.get(
                "equipment",
                "-"
            )
        )

    st.divider()

    # --------------------------------------------------------
    # PIPE INPUT
    # --------------------------------------------------------

    st.subheader(
        "1. Pipe Dimensions"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        diameter_mm = st.number_input(
            "Pipe Outside Diameter (mm)",
            min_value=0.0,
            value=114.3,
            step=1.0
        )

    with col2:

        pipe_length = st.number_input(
            "Pipe Length (m)",
            min_value=0.0,
            value=10.0,
            step=0.5
        )

    with col3:

        pipe_quantity = st.number_input(
            "Number of Pipes",
            min_value=1,
            value=1,
            step=1
        )

    st.write("")

    # --------------------------------------------------------
    # COATING INPUT
    # --------------------------------------------------------

    st.subheader(
        "2. Coating Parameters"
    )

    col1, col2 = st.columns(2)

    with col1:

        dft = st.number_input(
            "Required DFT (µm)",
            min_value=0.0,
            value=150.0,
            step=10.0,
            help=(
                "Required dry film thickness "
                "for the coating layer."
            )
        )

    with col2:

        volume_solids = st.number_input(
            "Volume Solids (%)",
            min_value=1.0,
            max_value=100.0,
            value=75.0,
            step=1.0,
            help=(
                "Obtain this value from the "
                "coating manufacturer's technical data sheet."
            )
        )

    st.write("")

    st.caption(
        "Volume solids and required DFT should be based "
        "on the applicable coating specification or "
        "manufacturer technical data."
    )

    st.divider()

    # --------------------------------------------------------
    # CALCULATE
    # --------------------------------------------------------

    if st.button(
        "🧮 CALCULATE ESTIMATION",
        type="primary",
        use_container_width=True
    ):

        if diameter_mm <= 0:

            st.error(
                "Pipe diameter must be greater than zero."
            )

        elif pipe_length <= 0:

            st.error(
                "Pipe length must be greater than zero."
            )

        else:

            diameter_m = (
                diameter_mm / 1000
            )

            surface_area = (
                math.pi
                * diameter_m
                * pipe_length
                * pipe_quantity
            )

            wft = (
                dft
                / (volume_solids / 100)
            )

            theoretical_litres = (
                surface_area
                * wft
                / 1000
            )

            st.session_state.calculation_result = {

                "diameter_mm":
                    diameter_mm,

                "pipe_length":
                    pipe_length,

                "pipe_quantity":
                    pipe_quantity,

                "dft":
                    dft,

                "volume_solids":
                    volume_solids,

                "surface_area":
                    surface_area,

                "wft":
                    wft,

                "theoretical_litres":
                    theoretical_litres
            }

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if st.session_state.calculation_result:

        result = (
            st.session_state.calculation_result
        )

        st.write("")

        st.subheader(
            "3. Engineering Calculation Results"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "External Surface Area",
                f"{result['surface_area']:.2f} m²"
            )

        with col2:

            st.metric(
                "Required WFT",
                f"{result['wft']:.1f} µm"
            )

        with col3:

            st.metric(
                "Theoretical Coating Quantity",
                f"{result['theoretical_litres']:.2f} L"
            )

        st.write("")

        with st.expander(
            "📐 View Engineering Calculation"
        ):

            st.write(
                "**External Pipe Surface Area**"
            )

            st.latex(
                r"A = \pi D L N"
            )

            st.write(
                f"A = π × "
                f"{result['diameter_mm']/1000:.4f} × "
                f"{result['pipe_length']:.2f} × "
                f"{result['pipe_quantity']}"
            )

            st.write(
                f"**A = "
                f"{result['surface_area']:.2f} m²**"
            )

            st.write("---")

            st.write(
                "**Wet Film Thickness (WFT)**"
            )

            st.latex(
                r"WFT = \frac{DFT}{VS/100}"
            )

            st.write(
                f"WFT = {result['dft']:.1f} "
                f"/ ({result['volume_solids']:.1f}/100)"
            )

            st.write(
                f"**WFT = "
                f"{result['wft']:.1f} µm**"
            )

            st.write("---")

            st.write(
                "**Theoretical Wet Coating Volume**"
            )

            st.latex(
                r"Q = \frac{A \times WFT}{1000}"
            )

            st.write(
                f"Q = "
                f"{result['surface_area']:.2f} × "
                f"{result['wft']:.1f} / 1000"
            )

            st.write(
                f"**Q = "
                f"{result['theoretical_litres']:.2f} L**"
            )

        st.info(
            "The calculated coating quantity is theoretical. "
            "Actual material requirements may be higher due "
            "to application losses, surface profile, overspray, "
            "equipment losses and other project-specific factors."
        )

        st.divider()

        back_col, save_col = st.columns(2)

        with back_col:

            if st.button(
                "← Edit Job Information",
                use_container_width=True
            ):

                st.session_state.calculation_result = {}

                st.session_state.page = "New Job"

                st.rerun()

        with save_col:

            if st.button(
                "💾 Save Job & Calculation",
                type="primary",
                use_container_width=True
            ):

                # ------------------------------------------------
                # At the moment the existing jobs table stores
                # the main job information.
                # Calculation values are included in description
                # until a dedicated calculation table is added.
                # ------------------------------------------------

                original_description = (
                    job.get(
                        "description",
                        ""
                    )
                )

                calculation_summary = (
                    "\n\n"
                    "ENGINEERING ESTIMATION\n"
                    f"Pipe OD: "
                    f"{result['diameter_mm']:.1f} mm\n"
                    f"Pipe Length: "
                    f"{result['pipe_length']:.2f} m\n"
                    f"Pipe Quantity: "
                    f"{result['pipe_quantity']}\n"
                    f"DFT: "
                    f"{result['dft']:.1f} µm\n"
                    f"Volume Solids: "
                    f"{result['volume_solids']:.1f}%\n"
                    f"Surface Area: "
                    f"{result['surface_area']:.2f} m²\n"
                    f"WFT: "
                    f"{result['wft']:.1f} µm\n"
                    f"Theoretical Coating Quantity: "
                    f"{result['theoretical_litres']:.2f} L"
                )

                database_job = {

                    "job_reference":
                        job.get(
                            "job_reference"
                        ),

                    "location":
                        job.get(
                            "location"
                        ),

                    "equipment":
                        job.get(
                            "equipment"
                        ),

                    "work_type":
                        job.get(
                            "work_type"
                        ),

                    "inspection_date":
                        job.get(
                            "inspection_date"
                        ),

                    "prepared_by":
                        job.get(
                            "prepared_by"
                        ),

                    "description":
                        original_description
                        + calculation_summary,

                    "status":
                        "Draft"
                }

                success, response = save_job(
                    database_job
                )

                if success:

                    st.success(
                        "Job and engineering calculation "
                        "saved successfully!"
                    )

                    st.balloons()

                    st.session_state.job_data = {}
                    st.session_state.calculation_result = {}

                    if st.button(
                        "📋 View Job Records",
                        use_container_width=True
                    ):

                        st.session_state.page = (
                            "Job Records"
                        )

                        st.rerun()

                else:

                    st.error(
                        "Unable to save the job."
                    )

                    st.error(response)


# ============================================================
# PIPE INSULATION
# ============================================================

elif st.session_state.page == "Insulation Calculation":

    st.title(
        "🧱 Pipe Insulation"
    )

    st.write(
        "Engineering Estimation Module"
    )

    st.divider()

    st.info(
        "The Pipe Insulation calculation module "
        "will be developed in the next stage."
    )

    st.write(
        "Planned engineering inputs include:"
    )

    st.write(
        "• Pipe outside diameter"
    )

    st.write(
        "• Pipe length"
    )

    st.write(
        "• Insulation thickness"
    )

    st.write(
        "• Number of pipes"
    )

    st.write(
        "• Insulation material"
    )

    if st.button(
        "← Back to Job Information"
    ):

        st.session_state.page = "New Job"
        st.rerun()


# ============================================================
# INSULATION REPLACEMENT
# ============================================================

elif st.session_state.page == "Replacement Calculation":

    st.title(
        "🔄 Insulation Replacement"
    )

    st.write(
        "Engineering Estimation Module"
    )

    st.divider()

    st.info(
        "The Insulation Replacement module "
        "will be developed in the next stage."
    )

    if st.button(
        "← Back to Job Information"
    ):

        st.session_state.page = "New Job"
        st.rerun()


# ============================================================
# JOB RECORDS
# ============================================================

elif st.session_state.page == "Job Records":

    st.title(
        "📋 Job Records"
    )

    st.write(
        "Saved industrial maintenance "
        "engineering job records."
    )

    st.divider()

    jobs = get_jobs()

    if len(jobs) == 0:

        st.info(
            "No job records found."
        )

    else:

        st.success(
            f"{len(jobs)} job record(s) found."
        )

        search = st.text_input(
            "🔍 Search Jobs",
            placeholder=(
                "Search job reference, "
                "location or equipment..."
            )
        )

        filtered_jobs = jobs

        if search:

            search_lower = search.lower()

            filtered_jobs = [

                job for job in jobs

                if search_lower
                in str(
                    job.get(
                        "job_reference",
                        ""
                    )
                ).lower()

                or search_lower
                in str(
                    job.get(
                        "location",
                        ""
                    )
                ).lower()

                or search_lower
                in str(
                    job.get(
                        "equipment",
                        ""
                    )
                ).lower()
            ]

        st.write("")

        for job in filtered_jobs:

            with st.container(border=True):

                col1, col2 = st.columns(
                    [3, 1]
                )

                with col1:

                    st.subheader(
                        job.get(
                            "job_reference",
                            "Unknown Job"
                        )
                    )

                    st.write(
                        f"**Work Type:** "
                        f"{job.get('work_type', '-')}"
                    )

                    st.write(
                        f"**Location:** "
                        f"{job.get('location', '-')}"
                    )

                    st.write(
                        f"**Equipment / Tag:** "
                        f"{job.get('equipment', '-')}"
                    )

                    st.write(
                        f"**Inspection Date:** "
                        f"{job.get('inspection_date', '-')}"
                    )

                    st.write(
                        f"**Prepared By:** "
                        f"{job.get('prepared_by', '-')}"
                    )

                    description = job.get(
                        "description",
                        ""
                    )

                    if description:

                        with st.expander(
                            "View Job Details & Calculation"
                        ):

                            st.text(
                                description
                            )

                with col2:

                    st.write(
                        "**Status**"
                    )

                    status = job.get(
                        "status",
                        "Draft"
                    )

                    if status == "Completed":

                        st.success(
                            "Completed"
                        )

                    else:

                        st.warning(
                            status
                        )


# ============================================================
# REPORTS
# ============================================================

elif st.session_state.page == "Reports":

    st.title(
        "📊 Reports"
    )

    st.write(
        "Maintenance Engineering "
        "Estimation Reports"
    )

    st.divider()

    jobs = get_jobs()

    if len(jobs) == 0:

        st.info(
            "No job data available for reporting."
        )

    else:

        total_jobs = len(jobs)

        coating_jobs = sum(
            1
            for job in jobs
            if job.get("work_type")
            == "Pipe Painting / Coating"
        )

        insulation_jobs = sum(
            1
            for job in jobs
            if job.get("work_type")
            == "Pipe Insulation"
        )

        replacement_jobs = sum(
            1
            for job in jobs
            if job.get("work_type")
            == "Insulation Replacement"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Jobs",
                total_jobs
            )

        with col2:

            st.metric(
                "Painting / Coating",
                coating_jobs
            )

        with col3:

            st.metric(
                "Pipe Insulation",
                insulation_jobs
            )

        with col4:

            st.metric(
                "Insulation Replacement",
                replacement_jobs
            )

        st.write("")

        st.info(
            "Detailed engineering reporting "
            "will be developed after the "
            "calculation modules are completed."
        )
