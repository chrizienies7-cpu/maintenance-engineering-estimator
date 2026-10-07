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


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_jobs():
    """
    Retrieve all jobs from Supabase.
    """
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
        st.error(f"Unable to retrieve jobs: {e}")
        return []


def save_job(job_data):
    """
    Save a new job to Supabase.
    """
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
    st.caption("Maintenance Engineering")

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

    st.caption("Engineering Estimation System")
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

    st.subheader("Dashboard")

    # Get jobs from database
    jobs = get_jobs()

    total_jobs = len(jobs)

    draft_jobs = sum(
        1 for job in jobs
        if job.get("status") == "Draft"
    )

    completed_jobs = sum(
        1 for job in jobs
        if job.get("status") == "Completed"
    )

    # Dashboard cards
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

            st.write("**Current Work Modules**")

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
            st.session_state.page = "New Job"
            st.rerun()

    st.write("")

    # ========================================================
    # RECENT JOBS
    # ========================================================

    st.subheader("Recent Jobs")

    if len(jobs) == 0:

        st.info(
            "No job records available. "
            "Create your first maintenance estimation job."
        )

    else:

        recent_jobs = jobs[:5]

        for job in recent_jobs:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [2, 2, 1]
                )

                with col1:

                    st.write(
                        f"**{job.get('job_reference', '-') }**"
                    )

                    st.caption(
                        job.get(
                            "work_type",
                            "No work type"
                        )
                    )

                with col2:

                    st.write(
                        job.get(
                            "location",
                            "No location"
                        )
                    )

                    st.caption(
                        job.get(
                            "equipment",
                            "No equipment"
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

    # ========================================================
    # JOB DESCRIPTION
    # ========================================================

    st.subheader("2. Job Description")

    job_description = st.text_area(
        "Scope / Description of Work",
        placeholder=(
            "Example: External surface preparation "
            "and painting of piping..."
        ),
        height=150
    )

    st.divider()

    # ========================================================
    # BUTTONS
    # ========================================================

    back_col, save_col = st.columns(2)

    with back_col:

        if st.button(
            "← Back to Dashboard",
            use_container_width=True
        ):
            st.session_state.page = "Dashboard"
            st.rerun()

    with save_col:

        if st.button(
            "💾 Save Job",
            type="primary",
            use_container_width=True
        ):

            # Validation
            if not job_reference:

                st.warning(
                    "Please enter the Job Reference."
                )

            elif work_type == "Select Work Type":

                st.warning(
                    "Please select a Work Type."
                )

            else:

                # Prepare data
                job_data = {

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
                        job_description,

                    "status":
                        "Draft"
                }

                # Save to Supabase
                success, result = save_job(
                    job_data
                )

                if success:

                    st.success(
                        f"Job {job_reference} "
                        "saved successfully!"
                    )

                    st.balloons()

                    st.info(
                        "You can now view this job "
                        "under Job Records."
                    )

                else:

                    st.error(
                        "Unable to save the job."
                    )

                    st.error(result)


# ============================================================
# JOB RECORDS PAGE
# ============================================================

elif st.session_state.page == "Job Records":

    st.title("📋 Job Records")

    st.write(
        "Saved industrial maintenance "
        "job records."
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

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

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

                if search_lower in str(
                    job.get(
                        "job_reference",
                        ""
                    )
                ).lower()

                or search_lower in str(
                    job.get(
                        "location",
                        ""
                    )
                ).lower()

                or search_lower in str(
                    job.get(
                        "equipment",
                        ""
                    )
                ).lower()
            ]

        st.write("")

        # ----------------------------------------------------
        # DISPLAY JOBS
        # ----------------------------------------------------

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

                        st.write(
                            "**Description:**"
                        )

                        st.write(
                            description
                        )

                with col2:

                    st.write("**Status**")

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
# REPORTS PAGE
# ============================================================

elif st.session_state.page == "Reports":

    st.title("📊 Reports")

    st.write(
        "Maintenance engineering "
        "estimation reports."
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
            1 for job in jobs
            if job.get("work_type")
            == "Pipe Painting / Coating"
        )

        insulation_jobs = sum(
            1 for job in jobs
            if job.get("work_type")
            == "Pipe Insulation"
        )

        replacement_jobs = sum(
            1 for job in jobs
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
            "Detailed engineering reports "
            "will be developed in the next stage."
        )
