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

if "pipe_items" not in st.session_state:
    st.session_state.pipe_items = []

if "calculation_results" not in st.session_state:
    st.session_state.calculation_results = []

if "saved_job_id" not in st.session_state:
    st.session_state.saved_job_id = None


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

        return response.data or []

    except Exception as e:
        st.error(f"Unable to retrieve jobs: {e}")
        return []


def get_pipe_items(job_id):
    try:
        response = (
            supabase
            .table("pipe_items")
            .select("*")
            .eq("job_id", job_id)
            .order("id")
            .execute()
        )

        return response.data or []

    except Exception as e:
        st.error(f"Unable to retrieve pipe items: {e}")
        return []


def save_job(job_data):
    try:
        response = (
            supabase
            .table("jobs")
            .insert(job_data)
            .execute()
        )

        if response.data and len(response.data) > 0:
            return True, response.data[0]

        return False, "Job was inserted but no job ID was returned."

    except Exception as e:
        return False, str(e)


def save_pipe_items(pipe_items):
    try:
        response = (
            supabase
            .table("pipe_items")
            .insert(pipe_items)
            .execute()
        )

        return True, response

    except Exception as e:
        return False, str(e)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def reset_new_job():
    st.session_state.job_data = {}
    st.session_state.pipe_items = []
    st.session_state.calculation_results = []
    st.session_state.saved_job_id = None


def calculate_pipe_item(item):
    diameter_m = item["outside_diameter_mm"] / 1000

    surface_area = (
        math.pi
        * diameter_m
        * item["pipe_length_m"]
        * item["pipe_quantity"]
    )

    wft = (
        item["dft_um"]
        / (item["volume_solids_pct"] / 100)
    )

    theoretical_coating = (
        surface_area
        * wft
        / 1000
    )

    result = item.copy()

    result["surface_area_m2"] = surface_area
    result["wft_um"] = wft
    result["theoretical_coating_l"] = theoretical_coating

    return result


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
        reset_new_job()
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
# DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":

    st.title("Maintenance Engineering Estimator")

    st.write(
        "Industrial Maintenance Job Planning & "
        "Engineering Quantity Estimation"
    )

    st.divider()

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
            "Work Modules",
            3
        )

    st.write("")

    st.subheader("Start New Estimation")

    with st.container(border=True):

        col1, col2 = st.columns([3, 1])

        with col1:

            st.subheader(
                "🔧 Engineering Job Estimation"
            )

            st.write(
                "Create a maintenance job, enter site visit "
                "information and estimate engineering quantities "
                "for multiple pipe tags."
            )

            st.write(
                "**Available Module:** "
                "Pipe Painting / Coating"
            )

            st.caption(
                "Pipe Insulation and Insulation Replacement "
                "will be added in the next development stage."
            )

        with col2:

            st.write("")

            if st.button(
                "➕ CREATE NEW JOB",
                type="primary",
                use_container_width=True
            ):
                reset_new_job()
                st.session_state.page = "New Job"
                st.rerun()

    st.write("")

    st.subheader("Recent Jobs")

    if not jobs:

        st.info("No job records available.")

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

                    supervisor = (
                        job.get("supervisor")
                        or "-"
                    )

                    st.caption(
                        f"Supervisor: {supervisor}"
                    )

                with col3:

                    status = job.get(
                        "status",
                        "Draft"
                    )

                    if status == "Completed":
                        st.success(status)
                    else:
                        st.warning(status)


# ============================================================
# NEW JOB
# ============================================================

elif st.session_state.page == "New Job":

    st.title("➕ Create New Job")

    st.write(
        "Enter the general job and site visit information."
    )

    st.divider()

    st.subheader("1. Job Information")

    col1, col2 = st.columns(2)

    with col1:

        job_reference = st.text_input(
            "Job Reference / Work Order *",
            value=st.session_state.job_data.get(
                "job_reference",
                ""
            ),
            placeholder="Example: KH-2026-001"
        )

        location = st.text_input(
            "Work Location / Area",
            value=st.session_state.job_data.get(
                "location",
                ""
            ),
            placeholder="Example: Area 5"
        )

        work_options = [
            "Select Work Type",
            "Pipe Painting / Coating",
            "Pipe Insulation",
            "Insulation Replacement"
        ]

        previous_work_type = (
            st.session_state.job_data.get(
                "work_type",
                "Select Work Type"
            )
        )

        try:
            work_index = work_options.index(
                previous_work_type
            )
        except ValueError:
            work_index = 0

        work_type = st.selectbox(
            "Work Type *",
            work_options,
            index=work_index
        )

    with col2:

        inspection_date = st.date_input(
            "Inspection / Site Visit Date"
        )

        supervisor = st.text_input(
            "Supervisor / Site Visit By *",
            value=st.session_state.job_data.get(
                "supervisor",
                ""
            ),
            placeholder="Name of supervisor who attended site visit"
        )

        prepared_by = st.text_input(
            "Prepared By",
            value=st.session_state.job_data.get(
                "prepared_by",
                ""
            ),
            placeholder="Enter estimator / preparer name"
        )

    st.write("")

    st.subheader("2. Job Description")

    description = st.text_area(
        "Scope / Description of Work",
        value=st.session_state.job_data.get(
            "description",
            ""
        ),
        placeholder=(
            "Example: Surface preparation and external "
            "painting of piping..."
        ),
        height=140
    )

    st.info(
        "Pipe tag numbers will be entered on the next page. "
        "One job can contain multiple pipe tags."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "← Back to Dashboard",
            use_container_width=True
        ):
            st.session_state.page = "Dashboard"
            st.rerun()

    with col2:

        if st.button(
            "Continue to Pipe Tags →",
            type="primary",
            use_container_width=True
        ):

            if not job_reference.strip():

                st.warning(
                    "Please enter the Job Reference / Work Order."
                )

            elif not supervisor.strip():

                st.warning(
                    "Please enter the Supervisor / Site Visit By."
                )

            elif work_type == "Select Work Type":

                st.warning(
                    "Please select a Work Type."
                )

            else:

                st.session_state.job_data = {
                    "job_reference": job_reference.strip(),
                    "location": location.strip(),
                    "work_type": work_type,
                    "inspection_date": str(inspection_date),
                    "supervisor": supervisor.strip(),
                    "prepared_by": prepared_by.strip(),
                    "description": description.strip()
                }

                if work_type == "Pipe Painting / Coating":

                    st.session_state.page = "Pipe Tags"

                elif work_type == "Pipe Insulation":

                    st.session_state.page = (
                        "Insulation Placeholder"
                    )

                else:

                    st.session_state.page = (
                        "Replacement Placeholder"
                    )

                st.rerun()


# ============================================================
# PIPE TAG INPUT
# ============================================================

elif st.session_state.page == "Pipe Tags":

    job = st.session_state.job_data

    st.title("🎨 Pipe Painting / Coating")

    st.write(
        "Multiple Pipe Tag Engineering Estimation"
    )

    st.divider()

    # --------------------------------------------------------
    # JOB SUMMARY
    # --------------------------------------------------------

    st.subheader("Job & Site Visit Information")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.caption("Job Reference")
        st.write(
            f"**{job.get('job_reference', '-')}**"
        )

    with col2:
        st.caption("Location")
        st.write(
            f"**{job.get('location', '-') or '-'}**"
        )

    with col3:
        st.caption("Site Visit By")
        st.write(
            f"**{job.get('supervisor', '-')}**"
        )

    with col4:
        st.caption("Site Visit Date")
        st.write(
            f"**{job.get('inspection_date', '-')}**"
        )

    st.divider()

    st.subheader("Pipe Tags")

    st.write(
        "Enter one row for each pipe tag included "
        "in this maintenance job."
    )

    st.caption(
        "You can add or remove rows as required. "
        "For a job with 50 pipe tags, add 50 rows."
    )

    # --------------------------------------------------------
    # INITIAL TABLE
    # --------------------------------------------------------

    if not st.session_state.pipe_items:

        st.session_state.pipe_items = [
            {
                "tag_number": "",
                "outside_diameter_mm": 114.3,
                "pipe_length_m": 1.0,
                "pipe_quantity": 1,
                "dft_um": 150.0,
                "volume_solids_pct": 75.0
            }
        ]

    # --------------------------------------------------------
    # DATA EDITOR
    # --------------------------------------------------------

    edited_items = st.data_editor(
        st.session_state.pipe_items,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=False,
        column_config={
            "tag_number": st.column_config.TextColumn(
                "Tag Number",
                help="Pipe / line tag number",
                required=True
            ),
            "outside_diameter_mm":
                st.column_config.NumberColumn(
                    "Outside Diameter (mm)",
                    min_value=0.0,
                    format="%.2f"
                ),
            "pipe_length_m":
                st.column_config.NumberColumn(
                    "Length (m)",
                    min_value=0.0,
                    format="%.2f"
                ),
            "pipe_quantity":
                st.column_config.NumberColumn(
                    "Quantity",
                    min_value=1,
                    step=1,
                    format="%d"
                ),
            "dft_um":
                st.column_config.NumberColumn(
                    "Required DFT (µm)",
                    min_value=0.0,
                    format="%.1f"
                ),
            "volume_solids_pct":
                st.column_config.NumberColumn(
                    "Volume Solids (%)",
                    min_value=1.0,
                    max_value=100.0,
                    format="%.1f"
                )
        },
        key="pipe_data_editor"
    )

    st.session_state.pipe_items = edited_items

    st.caption(
        "Tip: In the table, use the bottom row to add "
        "another pipe tag. Rows can also be deleted "
        "from the data editor."
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "← Edit Job Information",
            use_container_width=True
        ):
            st.session_state.page = "New Job"
            st.rerun()

    with col2:

        calculate_button = st.button(
            "🧮 Calculate All Pipe Tags",
            type="primary",
            use_container_width=True
        )

    # --------------------------------------------------------
    # CALCULATION
    # --------------------------------------------------------

    if calculate_button:

        valid_items = []
        errors = []

        for index, item in enumerate(
            st.session_state.pipe_items,
            start=1
        ):

            tag_number = str(
                item.get("tag_number", "")
            ).strip()

            diameter = item.get(
                "outside_diameter_mm",
                0
            )

            length = item.get(
                "pipe_length_m",
                0
            )

            quantity = item.get(
                "pipe_quantity",
                0
            )

            dft = item.get(
                "dft_um",
                0
            )

            volume_solids = item.get(
                "volume_solids_pct",
                0
            )

            # Ignore completely empty dynamic rows
            if (
                not tag_number
                and not diameter
                and not length
            ):
                continue

            if not tag_number:
                errors.append(
                    f"Row {index}: Tag Number is required."
                )
                continue

            if diameter is None or diameter <= 0:
                errors.append(
                    f"{tag_number}: Outside diameter "
                    "must be greater than zero."
                )
                continue

            if length is None or length <= 0:
                errors.append(
                    f"{tag_number}: Pipe length "
                    "must be greater than zero."
                )
                continue

            if quantity is None or quantity < 1:
                errors.append(
                    f"{tag_number}: Quantity must "
                    "be at least 1."
                )
                continue

            if dft is None or dft <= 0:
                errors.append(
                    f"{tag_number}: DFT must "
                    "be greater than zero."
                )
                continue

            if (
                volume_solids is None
                or volume_solids <= 0
                or volume_solids > 100
            ):
                errors.append(
                    f"{tag_number}: Volume solids must "
                    "be between 1% and 100%."
                )
                continue

            clean_item = {
                "tag_number": tag_number,
                "outside_diameter_mm": float(diameter),
                "pipe_length_m": float(length),
                "pipe_quantity": int(quantity),
                "dft_um": float(dft),
                "volume_solids_pct":
                    float(volume_solids)
            }

            valid_items.append(
                calculate_pipe_item(
                    clean_item
                )
            )

        if errors:

            st.session_state.calculation_results = []

            st.error(
                "Please correct the following input:"
            )

            for error in errors:
                st.write(f"• {error}")

        elif not valid_items:

            st.warning(
                "Please enter at least one pipe tag."
            )

            st.session_state.calculation_results = []

        else:

            st.session_state.calculation_results = (
                valid_items
            )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if st.session_state.calculation_results:

        results = (
            st.session_state.calculation_results
        )

        st.divider()

        st.subheader(
            "Engineering Estimation Results"
        )

        result_table = []

        for result in results:

            result_table.append({
                "Tag Number":
                    result["tag_number"],

                "OD (mm)":
                    round(
                        result["outside_diameter_mm"],
                        2
                    ),

                "Length (m)":
                    round(
                        result["pipe_length_m"],
                        2
                    ),

                "Qty":
                    result["pipe_quantity"],

                "DFT (µm)":
                    round(
                        result["dft_um"],
                        1
                    ),

                "Volume Solids (%)":
                    round(
                        result["volume_solids_pct"],
                        1
                    ),

                "Surface Area (m²)":
                    round(
                        result["surface_area_m2"],
                        2
                    ),

                "WFT (µm)":
                    round(
                        result["wft_um"],
                        1
                    ),

                "Theoretical Coating (L)":
                    round(
                        result[
                            "theoretical_coating_l"
                        ],
                        2
                    )
            })

        st.dataframe(
            result_table,
            use_container_width=True,
            hide_index=True
        )

        total_tags = len(results)

        total_area = sum(
            item["surface_area_m2"]
            for item in results
        )

        total_coating = sum(
            item["theoretical_coating_l"]
            for item in results
        )

        total_pipe_length = sum(
            item["pipe_length_m"]
            * item["pipe_quantity"]
            for item in results
        )

        st.write("")

        st.subheader("Overall Job Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Pipe Tags",
                total_tags
            )

        with col2:

            st.metric(
                "Total Pipe Length",
                f"{total_pipe_length:.2f} m"
            )

        with col3:

            st.metric(
                "Total Surface Area",
                f"{total_area:.2f} m²"
            )

        with col4:

            st.metric(
                "Theoretical Coating",
                f"{total_coating:.2f} L"
            )

        st.write("")

        with st.expander(
            "📐 View Calculation Method"
        ):

            st.write(
                "**1. External pipe surface area**"
            )

            st.latex(
                r"A = \pi D L N"
            )

            st.write(
                "Where D is outside diameter in metres, "
                "L is pipe length in metres and N is quantity."
            )

            st.write("")

            st.write(
                "**2. Required Wet Film Thickness**"
            )

            st.latex(
                r"WFT = \frac{DFT}{VS/100}"
            )

            st.write(
                "Volume Solids (VS) should be obtained "
                "from the coating manufacturer's technical "
                "data sheet."
            )

            st.write("")

            st.write(
                "**3. Theoretical wet coating quantity**"
            )

            st.latex(
                r"Q = \frac{A \times WFT}{1000}"
            )

            st.write(
                "Where A is in m² and WFT is in µm. "
                "The result is theoretical coating volume "
                "in litres."
            )

        st.warning(
            "The coating quantity shown is theoretical. "
            "Actual material consumption can be higher due "
            "to application losses, surface profile, overspray, "
            "equipment losses and other project-specific factors."
        )

        st.divider()

        if st.button(
            "💾 Save Job & Engineering Estimation",
            type="primary",
            use_container_width=True
        ):

            database_job = {
                "job_reference":
                    job.get("job_reference"),

                "location":
                    job.get("location"),

                # Old column retained in database.
                # It is no longer used for individual tags.
                "equipment":
                    None,

                "work_type":
                    job.get("work_type"),

                "inspection_date":
                    job.get("inspection_date"),

                "supervisor":
                    job.get("supervisor"),

                "prepared_by":
                    job.get("prepared_by"),

                "description":
                    job.get("description"),

                "status":
                    "Draft"
            }

            job_success, saved_job = save_job(
                database_job
            )

            if not job_success:

                st.error(
                    "The job could not be saved."
                )

                st.error(saved_job)

            else:

                new_job_id = saved_job["id"]

                database_pipe_items = []

                for result in results:

                    database_pipe_items.append({
                        "job_id":
                            new_job_id,

                        "tag_number":
                            result["tag_number"],

                        "outside_diameter_mm":
                            result[
                                "outside_diameter_mm"
                            ],

                        "pipe_length_m":
                            result[
                                "pipe_length_m"
                            ],

                        "pipe_quantity":
                            result[
                                "pipe_quantity"
                            ],

                        "dft_um":
                            result[
                                "dft_um"
                            ],

                        "volume_solids_pct":
                            result[
                                "volume_solids_pct"
                            ],

                        "surface_area_m2":
                            result[
                                "surface_area_m2"
                            ],

                        "wft_um":
                            result[
                                "wft_um"
                            ],

                        "theoretical_coating_l":
                            result[
                                "theoretical_coating_l"
                            ]
                    })

                pipe_success, pipe_response = (
                    save_pipe_items(
                        database_pipe_items
                    )
                )

                if pipe_success:

                    st.session_state.saved_job_id = (
                        new_job_id
                    )

                    st.success(
                        "Job and all pipe tag calculations "
                        "saved successfully."
                    )

                    st.balloons()

                    if st.button(
                        "📋 Go to Job Records",
                        use_container_width=True
                    ):
                        reset_new_job()
                        st.session_state.page = (
                            "Job Records"
                        )
                        st.rerun()

                else:

                    st.error(
                        "The job was created, but the pipe "
                        "items could not be saved."
                    )

                    st.error(pipe_response)

                    st.warning(
                        f"Created Job ID: {new_job_id}. "
                        "Do not press Save again until the "
                        "pipe item error is corrected."
                    )


# ============================================================
# PIPE INSULATION PLACEHOLDER
# ============================================================

elif st.session_state.page == "Insulation Placeholder":

    st.title("🧱 Pipe Insulation")

    st.info(
        "The Pipe Insulation engineering calculation "
        "module will be added in the next development stage."
    )

    if st.button("← Back to Job Information"):
        st.session_state.page = "New Job"
        st.rerun()


# ============================================================
# INSULATION REPLACEMENT PLACEHOLDER
# ============================================================

elif st.session_state.page == "Replacement Placeholder":

    st.title("🔄 Insulation Replacement")

    st.info(
        "The Insulation Replacement engineering calculation "
        "module will be added in the next development stage."
    )

    if st.button("← Back to Job Information"):
        st.session_state.page = "New Job"
        st.rerun()


# ============================================================
# JOB RECORDS
# ============================================================

elif st.session_state.page == "Job Records":

    st.title("📋 Job Records")

    st.write(
        "Saved maintenance engineering jobs "
        "and pipe tag estimations."
    )

    st.divider()

    jobs = get_jobs()

    if not jobs:

        st.info("No job records found.")

    else:

        st.success(
            f"{len(jobs)} job record(s) found."
        )

        search = st.text_input(
            "🔍 Search Jobs",
            placeholder=(
                "Search job reference, location, "
                "supervisor or work type..."
            )
        )

        filtered_jobs = jobs

        if search:

            search_lower = search.lower()

            filtered_jobs = [
                job for job in jobs
                if (
                    search_lower
                    in str(
                        job.get(
                            "job_reference",
                            ""
                        )
                    ).lower()
                    or
                    search_lower
                    in str(
                        job.get(
                            "location",
                            ""
                        )
                    ).lower()
                    or
                    search_lower
                    in str(
                        job.get(
                            "supervisor",
                            ""
                        )
                    ).lower()
                    or
                    search_lower
                    in str(
                        job.get(
                            "work_type",
                            ""
                        )
                    ).lower()
                )
            ]

        st.write("")

        for job_record in filtered_jobs:

            job_id = job_record.get("id")

            pipe_records = get_pipe_items(
                job_id
            )

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [2, 2, 1]
                )

                with col1:

                    st.subheader(
                        job_record.get(
                            "job_reference",
                            "Unknown Job"
                        )
                    )

                    st.write(
                        f"**Work Type:** "
                        f"{job_record.get('work_type', '-')}"
                    )

                    st.write(
                        f"**Location:** "
                        f"{job_record.get('location', '-') or '-'}"
                    )

                with col2:

                    st.write(
                        f"**Site Visit:** "
                        f"{job_record.get('inspection_date', '-')}"
                    )

                    st.write(
                        f"**Supervisor / Site Visit By:** "
                        f"{job_record.get('supervisor', '-') or '-'}"
                    )

                    st.write(
                        f"**Prepared By:** "
                        f"{job_record.get('prepared_by', '-') or '-'}"
                    )

                with col3:

                    st.write("**Status**")

                    status = job_record.get(
                        "status",
                        "Draft"
                    )

                    if status == "Completed":
                        st.success(status)
                    else:
                        st.warning(status)

                    st.metric(
                        "Pipe Tags",
                        len(pipe_records)
                    )

                if pipe_records:

                    total_area = sum(
                        item.get(
                            "surface_area_m2",
                            0
                        ) or 0
                        for item in pipe_records
                    )

                    total_coating = sum(
                        item.get(
                            "theoretical_coating_l",
                            0
                        ) or 0
                        for item in pipe_records
                    )

                    with st.expander(
                        "View Engineering Estimation"
                    ):

                        col_a, col_b, col_c = (
                            st.columns(3)
                        )

                        with col_a:
                            st.metric(
                                "Pipe Tags",
                                len(pipe_records)
                            )

                        with col_b:
                            st.metric(
                                "Total Area",
                                f"{total_area:.2f} m²"
                            )

                        with col_c:
                            st.metric(
                                "Theoretical Coating",
                                f"{total_coating:.2f} L"
                            )

                        table_data = []

                        for item in pipe_records:

                            table_data.append({
                                "Tag Number":
                                    item.get(
                                        "tag_number",
                                        "-"
                                    ),

                                "OD (mm)":
                                    item.get(
                                        "outside_diameter_mm",
                                        0
                                    ),

                                "Length (m)":
                                    item.get(
                                        "pipe_length_m",
                                        0
                                    ),

                                "Qty":
                                    item.get(
                                        "pipe_quantity",
                                        0
                                    ),

                                "DFT (µm)":
                                    item.get(
                                        "dft_um",
                                        0
                                    ),

                                "VS (%)":
                                    item.get(
                                        "volume_solids_pct",
                                        0
                                    ),

                                "Area (m²)":
                                    round(
                                        item.get(
                                            "surface_area_m2",
                                            0
                                        ) or 0,
                                        2
                                    ),

                                "WFT (µm)":
                                    round(
                                        item.get(
                                            "wft_um",
                                            0
                                        ) or 0,
                                        1
                                    ),

                                "Coating (L)":
                                    round(
                                        item.get(
                                            "theoretical_coating_l",
                                            0
                                        ) or 0,
                                        2
                                    )
                            })

                        st.dataframe(
                            table_data,
                            use_container_width=True,
                            hide_index=True
                        )

                        description = (
                            job_record.get(
                                "description",
                                ""
                            )
                        )

                        if description:

                            st.write(
                                "**Job Description / Scope**"
                            )

                            st.write(description)

                else:

                    st.caption(
                        "No pipe tag calculation data "
                        "stored for this job."
                    )


# ============================================================
# REPORTS
# ============================================================

elif st.session_state.page == "Reports":

    st.title("📊 Reports")

    st.write(
        "Maintenance Engineering Estimation Summary"
    )

    st.divider()

    jobs = get_jobs()

    if not jobs:

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

        all_pipe_items = []

        try:

            response = (
                supabase
                .table("pipe_items")
                .select("*")
                .execute()
            )

            all_pipe_items = response.data or []

        except Exception as e:

            st.warning(
                f"Unable to load pipe item report data: {e}"
            )

        total_tags = len(all_pipe_items)

        total_area = sum(
            item.get(
                "surface_area_m2",
                0
            ) or 0
            for item in all_pipe_items
        )

        total_coating = sum(
            item.get(
                "theoretical_coating_l",
                0
            ) or 0
            for item in all_pipe_items
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Jobs",
                total_jobs
            )

        with col2:
            st.metric(
                "Painting Jobs",
                coating_jobs
            )

        with col3:
            st.metric(
                "Total Pipe Tags",
                total_tags
            )

        with col4:
            st.metric(
                "Total Estimated Area",
                f"{total_area:.2f} m²"
            )

        st.write("")

        col5, col6, col7 = st.columns(3)

        with col5:
            st.metric(
                "Theoretical Coating",
                f"{total_coating:.2f} L"
            )

        with col6:
            st.metric(
                "Insulation Jobs",
                insulation_jobs
            )

        with col7:
            st.metric(
                "Replacement Jobs",
                replacement_jobs
            )

        st.info(
            "More detailed engineering reporting will be "
            "developed as the insulation modules are added."
        )
