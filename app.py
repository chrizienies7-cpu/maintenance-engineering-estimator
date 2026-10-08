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

defaults = {
    "page": "Dashboard",
    "job_data": {},
    "pipe_items": [],
    "calculation_results": [],
    "editing_index": None,
    "job_saved": False,
    "saved_job_id": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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

        if response.data:
            return True, response.data[0]

        return False, "No job data was returned."

    except Exception as e:
        return False, str(e)


def save_pipe_items(items):
    try:
        response = (
            supabase
            .table("pipe_items")
            .insert(items)
            .execute()
        )
        return True, response

    except Exception as e:
        return False, str(e)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def reset_job():
    st.session_state.job_data = {}
    st.session_state.pipe_items = []
    st.session_state.calculation_results = []
    st.session_state.editing_index = None
    st.session_state.job_saved = False
    st.session_state.saved_job_id = None


def calculate_pipe(item):
    diameter_m = item["outside_diameter_mm"] / 1000

    area = (
        math.pi
        * diameter_m
        * item["pipe_length_m"]
        * item["pipe_quantity"]
    )

    wft = (
        item["dft_um"]
        / (item["volume_solids_pct"] / 100)
    )

    coating = (
        area
        * wft
        / 1000
    )

    result = item.copy()
    result["surface_area_m2"] = area
    result["wft_um"] = wft
    result["theoretical_coating_l"] = coating

    return result


def recalculate_all():
    results = []

    for item in st.session_state.pipe_items:
        results.append(
            calculate_pipe(item)
        )

    st.session_state.calculation_results = results


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🔧 KHAL")
    st.caption("Maintenance Engineering")

    st.divider()

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
        reset_job()
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
        st.metric("Total Jobs", total_jobs)

    with col2:
        st.metric("Draft Jobs", draft_jobs)

    with col3:
        st.metric(
            "Completed Jobs",
            completed_jobs
        )

    with col4:
        st.metric("Work Modules", 3)

    st.write("")

    with st.container(border=True):

        col1, col2 = st.columns([3, 1])

        with col1:

            st.subheader(
                "🔧 New Engineering Estimation"
            )

            st.write(
                "Create a maintenance job, record site "
                "visit information and estimate engineering "
                "quantities for multiple pipe tags."
            )

        with col2:

            st.write("")

            if st.button(
                "➕ CREATE NEW JOB",
                type="primary",
                use_container_width=True
            ):
                reset_job()
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
                        job.get("work_type", "-")
                    )

                with col2:

                    st.write(
                        job.get("location", "-")
                        or "-"
                    )

                    st.caption(
                        "Supervisor: "
                        f"{job.get('supervisor') or '-'}"
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
        "Enter the job and site visit information."
    )

    st.divider()

    with st.form("job_information_form"):

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

            old_work_type = (
                st.session_state.job_data.get(
                    "work_type",
                    "Select Work Type"
                )
            )

            try:
                work_index = work_options.index(
                    old_work_type
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
                placeholder="Supervisor who attended site visit"
            )

            prepared_by = st.text_input(
                "Prepared By",
                value=st.session_state.job_data.get(
                    "prepared_by",
                    ""
                ),
                placeholder="Estimator / preparer name"
            )

        st.subheader("2. Job Description")

        description = st.text_area(
            "Scope / Description of Work",
            value=st.session_state.job_data.get(
                "description",
                ""
            ),
            height=130,
            placeholder=(
                "Example: Surface preparation and "
                "painting of external piping..."
            )
        )

        st.info(
            "Pipe tags are entered separately on the "
            "next page. One job can contain many pipe tags."
        )

        continue_job = st.form_submit_button(
            "Continue to Pipe Tags →",
            type="primary",
            use_container_width=True
        )

    if continue_job:

        if not job_reference.strip():

            st.warning(
                "Please enter the Job Reference."
            )

        elif work_type == "Select Work Type":

            st.warning(
                "Please select a Work Type."
            )

        elif not supervisor.strip():

            st.warning(
                "Please enter the Supervisor / Site Visit By."
            )

        else:

            st.session_state.job_data = {
                "job_reference":
                    job_reference.strip(),

                "location":
                    location.strip(),

                "work_type":
                    work_type,

                "inspection_date":
                    str(inspection_date),

                "supervisor":
                    supervisor.strip(),

                "prepared_by":
                    prepared_by.strip(),

                "description":
                    description.strip()
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
# PIPE TAG PAGE
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
            f"**{job.get('location') or '-'}**"
        )

    with col3:
        st.caption("Supervisor / Site Visit By")
        st.write(
            f"**{job.get('supervisor', '-')}**"
        )

    with col4:
        st.caption("Site Visit Date")
        st.write(
            f"**{job.get('inspection_date', '-')}**"
        )

    st.divider()

    # --------------------------------------------------------
    # ADD / EDIT PIPE
    # --------------------------------------------------------

    editing = (
        st.session_state.editing_index
        is not None
    )

    if editing:

        edit_index = (
            st.session_state.editing_index
        )

        existing = (
            st.session_state.pipe_items[
                edit_index
            ]
        )

        st.subheader(
            f"✏️ Edit Pipe Tag "
            f"{existing['tag_number']}"
        )

    else:

        existing = {
            "tag_number": "",
            "outside_diameter_mm": 114.3,
            "pipe_length_m": 1.0,
            "pipe_quantity": 1,
            "dft_um": 150.0,
            "volume_solids_pct": 75.0
        }

        st.subheader("➕ Add Pipe Tag")

    st.caption(
        "Complete the pipe information and press "
        "Add Pipe Tag. The page will not update while "
        "you are filling in the form."
    )

    form_key = (
        f"pipe_form_{st.session_state.editing_index}"
        if editing
        else "new_pipe_form"
    )

    with st.form(
        form_key,
        clear_on_submit=not editing
    ):

        col1, col2, col3 = st.columns(3)

        with col1:

            tag_number = st.text_input(
                "Tag Number *",
                value=existing[
                    "tag_number"
                ],
                placeholder="Example: 4720-P-001"
            )

            outside_diameter = (
                st.number_input(
                    "Outside Diameter (mm) *",
                    min_value=0.01,
                    value=float(
                        existing[
                            "outside_diameter_mm"
                        ]
                    ),
                    step=1.0,
                    format="%.2f"
                )
            )

        with col2:

            pipe_length = st.number_input(
                "Pipe Length (m) *",
                min_value=0.01,
                value=float(
                    existing[
                        "pipe_length_m"
                    ]
                ),
                step=0.5,
                format="%.2f"
            )

            pipe_quantity = st.number_input(
                "Pipe Quantity *",
                min_value=1,
                value=int(
                    existing[
                        "pipe_quantity"
                    ]
                ),
                step=1
            )

        with col3:

            dft = st.number_input(
                "Required DFT (µm) *",
                min_value=0.1,
                value=float(
                    existing[
                        "dft_um"
                    ]
                ),
                step=10.0,
                format="%.1f"
            )

            volume_solids = st.number_input(
                "Volume Solids (%) *",
                min_value=0.1,
                max_value=100.0,
                value=float(
                    existing[
                        "volume_solids_pct"
                    ]
                ),
                step=1.0,
                format="%.1f"
            )

        if editing:

            submit_pipe = (
                st.form_submit_button(
                    "💾 Update Pipe Tag",
                    type="primary",
                    use_container_width=True
                )
            )

        else:

            submit_pipe = (
                st.form_submit_button(
                    "➕ Add Pipe Tag",
                    type="primary",
                    use_container_width=True
                )
            )

    # --------------------------------------------------------
    # PROCESS PIPE FORM
    # --------------------------------------------------------

    if submit_pipe:

        clean_tag = tag_number.strip()

        if not clean_tag:

            st.warning(
                "Please enter a Tag Number."
            )

        else:

            duplicate = False

            for index, item in enumerate(
                st.session_state.pipe_items
            ):

                if (
                    item["tag_number"].lower()
                    == clean_tag.lower()
                ):

                    if (
                        not editing
                        or index
                        != st.session_state.editing_index
                    ):
                        duplicate = True
                        break

            if duplicate:

                st.warning(
                    f"Tag Number '{clean_tag}' "
                    "has already been added."
                )

            else:

                new_item = {
                    "tag_number":
                        clean_tag,

                    "outside_diameter_mm":
                        float(outside_diameter),

                    "pipe_length_m":
                        float(pipe_length),

                    "pipe_quantity":
                        int(pipe_quantity),

                    "dft_um":
                        float(dft),

                    "volume_solids_pct":
                        float(volume_solids)
                }

                if editing:

                    st.session_state.pipe_items[
                        st.session_state.editing_index
                    ] = new_item

                    st.session_state.editing_index = None

                else:

                    st.session_state.pipe_items.append(
                        new_item
                    )

                # Any change means previous results
                # need to be recalculated.
                st.session_state.calculation_results = []

                st.rerun()

    # --------------------------------------------------------
    # CANCEL EDIT
    # --------------------------------------------------------

    if editing:

        if st.button(
            "Cancel Editing",
            use_container_width=True
        ):
            st.session_state.editing_index = None
            st.rerun()

    st.divider()

    # --------------------------------------------------------
    # ADDED PIPE TAGS
    # --------------------------------------------------------

    st.subheader(
        f"Added Pipe Tags "
        f"({len(st.session_state.pipe_items)})"
    )

    if not st.session_state.pipe_items:

        st.info(
            "No pipe tags have been added yet."
        )

    else:

        for index, item in enumerate(
            st.session_state.pipe_items
        ):

            with st.container(border=True):

                col1, col2, col3, col4 = (
                    st.columns(
                        [2.5, 4, 1, 1]
                    )
                )

                with col1:

                    st.write(
                        f"**{index + 1}. "
                        f"{item['tag_number']}**"
                    )

                    st.caption(
                        f"OD: "
                        f"{item['outside_diameter_mm']:.2f} mm"
                    )

                with col2:

                    st.write(
                        f"Length: "
                        f"**{item['pipe_length_m']:.2f} m** "
                        f"  |  Qty: "
                        f"**{item['pipe_quantity']}**"
                    )

                    st.caption(
                        f"DFT: {item['dft_um']:.1f} µm "
                        f"• Volume Solids: "
                        f"{item['volume_solids_pct']:.1f}%"
                    )

                with col3:

                    if st.button(
                        "✏️ Edit",
                        key=f"edit_{index}",
                        use_container_width=True
                    ):
                        st.session_state.editing_index = (
                            index
                        )
                        st.rerun()

                with col4:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{index}",
                        use_container_width=True
                    ):

                        st.session_state.pipe_items.pop(
                            index
                        )

                        st.session_state.calculation_results = []

                        if (
                            st.session_state.editing_index
                            is not None
                        ):
                            st.session_state.editing_index = None

                        st.rerun()

    # --------------------------------------------------------
    # NAVIGATION / CALCULATE
    # --------------------------------------------------------

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "← Edit Job Information",
            use_container_width=True
        ):
            st.session_state.editing_index = None
            st.session_state.page = "New Job"
            st.rerun()

    with col2:

        if st.button(
            "🧮 Calculate All Pipe Tags",
            type="primary",
            use_container_width=True,
            disabled=(
                len(
                    st.session_state.pipe_items
                ) == 0
            )
        ):

            recalculate_all()
            st.rerun()

    # --------------------------------------------------------
    # CALCULATION RESULTS
    # --------------------------------------------------------

    if st.session_state.calculation_results:

        results = (
            st.session_state.calculation_results
        )

        st.divider()

        st.subheader(
            "📐 Engineering Estimation Results"
        )

        table_data = []

        for item in results:

            table_data.append({
                "Tag Number":
                    item["tag_number"],

                "OD (mm)":
                    round(
                        item["outside_diameter_mm"],
                        2
                    ),

                "Length (m)":
                    round(
                        item["pipe_length_m"],
                        2
                    ),

                "Qty":
                    item["pipe_quantity"],

                "DFT (µm)":
                    round(
                        item["dft_um"],
                        1
                    ),

                "VS (%)":
                    round(
                        item["volume_solids_pct"],
                        1
                    ),

                "Surface Area (m²)":
                    round(
                        item["surface_area_m2"],
                        2
                    ),

                "WFT (µm)":
                    round(
                        item["wft_um"],
                        1
                    ),

                "Theoretical Coating (L)":
                    round(
                        item[
                            "theoretical_coating_l"
                        ],
                        2
                    )
            })

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # TOTALS
        # ----------------------------------------------------

        total_tags = len(results)

        total_pipe_quantity = sum(
            item["pipe_quantity"]
            for item in results
        )

        total_length = sum(
            item["pipe_length_m"]
            * item["pipe_quantity"]
            for item in results
        )

        total_area = sum(
            item["surface_area_m2"]
            for item in results
        )

        total_coating = sum(
            item["theoretical_coating_l"]
            for item in results
        )

        st.subheader("Overall Job Summary")

        col1, col2, col3, col4, col5 = (
            st.columns(5)
        )

        with col1:

            st.metric(
                "Pipe Tags",
                total_tags
            )

        with col2:

            st.metric(
                "Pipe Quantity",
                total_pipe_quantity
            )

        with col3:

            st.metric(
                "Total Length",
                f"{total_length:.2f} m"
            )

        with col4:

            st.metric(
                "Surface Area",
                f"{total_area:.2f} m²"
            )

        with col5:

            st.metric(
                "Theoretical Coating",
                f"{total_coating:.2f} L"
            )

        # ----------------------------------------------------
        # CALCULATION METHOD
        # ----------------------------------------------------

        with st.expander(
            "View Engineering Calculation Method"
        ):

            st.write(
                "**External Pipe Surface Area**"
            )

            st.latex(
                r"A = \pi D L N"
            )

            st.write(
                "D = outside diameter (m)"
            )

            st.write(
                "L = pipe length (m)"
            )

            st.write(
                "N = quantity"
            )

            st.write("---")

            st.write(
                "**Wet Film Thickness**"
            )

            st.latex(
                r"WFT = \frac{DFT}{VS/100}"
            )

            st.write(
                "VS = coating volume solids (%)"
            )

            st.write("---")

            st.write(
                "**Theoretical Coating Quantity**"
            )

            st.latex(
                r"Q = \frac{A \times WFT}{1000}"
            )

        st.warning(
            "The coating quantity is a theoretical "
            "engineering value. Actual material consumption "
            "may be higher due to application losses, "
            "surface condition, overspray and other "
            "project-specific factors."
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        st.divider()

        if st.session_state.job_saved:

            st.success(
                "✅ This job has already been saved."
            )

            st.write(
                f"Database Job ID: "
                f"**{st.session_state.saved_job_id}**"
            )

            if st.button(
                "📋 Go to Job Records",
                type="primary",
                use_container_width=True
            ):
                reset_job()
                st.session_state.page = "Job Records"
                st.rerun()

        else:

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

                    # Legacy column from the old design.
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

                job_success, saved_job = (
                    save_job(database_job)
                )

                if not job_success:

                    st.error(
                        "Unable to save the job."
                    )

                    st.error(saved_job)

                else:

                    new_job_id = saved_job["id"]

                    database_items = []

                    for result in results:

                        database_items.append({
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
                            database_items
                        )
                    )

                    if pipe_success:

                        st.session_state.job_saved = True
                        st.session_state.saved_job_id = (
                            new_job_id
                        )

                        st.rerun()

                    else:

                        st.error(
                            "The job was created, but the "
                            "pipe tags could not be saved."
                        )

                        st.error(pipe_response)

                        st.warning(
                            f"Job ID {new_job_id} was created. "
                            "Do not press Save repeatedly."
                        )


# ============================================================
# PIPE INSULATION
# ============================================================

elif st.session_state.page == "Insulation Placeholder":

    st.title("🧱 Pipe Insulation")

    st.info(
        "The Pipe Insulation engineering estimation "
        "module will be developed next."
    )

    if st.button(
        "← Back to Job Information"
    ):
        st.session_state.page = "New Job"
        st.rerun()


# ============================================================
# INSULATION REPLACEMENT
# ============================================================

elif st.session_state.page == "Replacement Placeholder":

    st.title("🔄 Insulation Replacement")

    st.info(
        "The Insulation Replacement engineering "
        "estimation module will be developed next."
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

        search = st.text_input(
            "🔍 Search Jobs",
            placeholder=(
                "Job reference, location, "
                "supervisor or work type..."
            )
        )

        filtered_jobs = jobs

        if search:

            query = search.lower()

            filtered_jobs = [
                job
                for job in jobs
                if (
                    query in str(
                        job.get(
                            "job_reference",
                            ""
                        )
                    ).lower()
                    or
                    query in str(
                        job.get(
                            "location",
                            ""
                        )
                    ).lower()
                    or
                    query in str(
                        job.get(
                            "supervisor",
                            ""
                        )
                    ).lower()
                    or
                    query in str(
                        job.get(
                            "work_type",
                            ""
                        )
                    ).lower()
                )
            ]

        st.caption(
            f"{len(filtered_jobs)} "
            "job record(s) shown"
        )

        for job_record in filtered_jobs:

            job_id = job_record["id"]

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
                            "-"
                        )
                    )

                    st.write(
                        f"**Work Type:** "
                        f"{job_record.get('work_type', '-')}"
                    )

                    st.write(
                        f"**Location:** "
                        f"{job_record.get('location') or '-'}"
                    )

                with col2:

                    st.write(
                        f"**Site Visit Date:** "
                        f"{job_record.get('inspection_date', '-')}"
                    )

                    st.write(
                        f"**Supervisor:** "
                        f"{job_record.get('supervisor') or '-'}"
                    )

                    st.write(
                        f"**Prepared By:** "
                        f"{job_record.get('prepared_by') or '-'}"
                    )

                with col3:

                    status = job_record.get(
                        "status",
                        "Draft"
                    )

                    st.write("**Status**")

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
                                "Total Surface Area",
                                f"{total_area:.2f} m²"
                            )

                        with col_c:

                            st.metric(
                                "Theoretical Coating",
                                f"{total_coating:.2f} L"
                            )

                        table = []

                        for item in pipe_records:

                            table.append({
                                "Tag":
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
                            table,
                            use_container_width=True,
                            hide_index=True
                        )

                        if job_record.get(
                            "description"
                        ):

                            st.write(
                                "**Job Description / Scope**"
                            )

                            st.write(
                                job_record[
                                    "description"
                                ]
                            )

                else:

                    st.caption(
                        "No pipe tag estimation data "
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

    try:

        response = (
            supabase
            .table("pipe_items")
            .select("*")
            .execute()
        )

        all_items = response.data or []

    except Exception as e:

        all_items = []

        st.warning(
            f"Unable to retrieve pipe item data: {e}"
        )

    total_jobs = len(jobs)
    total_tags = len(all_items)

    total_area = sum(
        item.get(
            "surface_area_m2",
            0
        ) or 0
        for item in all_items
    )

    total_coating = sum(
        item.get(
            "theoretical_coating_l",
            0
        ) or 0
        for item in all_items
    )

    painting_jobs = sum(
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
            "Painting Jobs",
            painting_jobs
        )

    with col3:
        st.metric(
            "Total Pipe Tags",
            total_tags
        )

    with col4:
        st.metric(
            "Total Surface Area",
            f"{total_area:.2f} m²"
        )

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
        "Detailed reports and insulation engineering "
        "results will be added in later development stages."
    )
