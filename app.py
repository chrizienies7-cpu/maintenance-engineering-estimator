
import math
import streamlit as st
from datetime import date
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
# UPPERCASE INPUT STYLING
# ============================================================

st.markdown(
    """
    <style>
    /* Show typed text in uppercase */
    div[data-testid="stTextInput"] input {
        text-transform: uppercase !important;
    }

    div[data-testid="stTextArea"] textarea {
        text-transform: uppercase !important;
    }

    /* Uppercase placeholders */
    div[data-testid="stTextInput"] input::placeholder {
        text-transform: uppercase;
    }

    div[data-testid="stTextArea"] textarea::placeholder {
        text-transform: uppercase;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def uppercase(value):
    """Normalize user-entered text to uppercase."""
    return str(value or "").strip().upper()


# ============================================================
# SUPABASE CONNECTION
# ============================================================

@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


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
    "pending_job_id": None,
    "form_version": 0,
    "save_message": ""
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
            supabase.table("jobs")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []

    except Exception as error:
        st.error(f"Unable to retrieve jobs: {error}")
        return []


def get_pipe_items(job_id):
    try:
        response = (
            supabase.table("pipe_items")
            .select("*")
            .eq("job_id", job_id)
            .order("id")
            .execute()
        )
        return response.data or []

    except Exception as error:
        st.error(f"Unable to retrieve pipe tags: {error}")
        return []


def save_job(data):
    try:
        response = (
            supabase.table("jobs")
            .insert(data)
            .execute()
        )

        if response.data:
            return True, response.data[0]

        return False, "No job ID returned."

    except Exception as error:
        return False, str(error)


def save_pipe_items(items):
    try:
        supabase.table("pipe_items").insert(items).execute()
        return True, None

    except Exception as error:
        return False, str(error)


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
    st.session_state.pending_job_id = None
    st.session_state.save_message = ""
    st.session_state.form_version += 1


def calculate_pipe(item):
    diameter_m = item["outside_diameter_mm"] / 1000

    area = (
        math.pi
        * diameter_m
        * item["pipe_length_m"]
        * item["pipe_quantity"]
    )

    wft = item["dft_um"] / (
        item["volume_solids_pct"] / 100
    )

    coating = area * wft / 1000

    result = item.copy()
    result["surface_area_m2"] = area
    result["wft_um"] = wft
    result["theoretical_coating_l"] = coating

    return result


def calculate_all():
    st.session_state.calculation_results = [
        calculate_pipe(item)
        for item in st.session_state.pipe_items
    ]


def go_to(page):
    st.session_state.page = page
    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("🔧 KHAL")
    st.caption("MAINTENANCE ENGINEERING")
    st.divider()

    if st.button("🏠 Dashboard", use_container_width=True):
        go_to("Dashboard")

    if st.button("➕ New Job", use_container_width=True):
        reset_job()
        go_to("New Job")

    if st.button("📋 Job Records", use_container_width=True):
        go_to("Job Records")

    if st.button("📊 Reports", use_container_width=True):
        go_to("Reports")

    st.divider()
    st.caption("ENGINEERING ESTIMATION SYSTEM")
    st.caption("FYP PROTOTYPE • 2026")


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
        job.get("status") == "Draft" for job in jobs
    )
    completed_jobs = sum(
        job.get("status") == "Completed" for job in jobs
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Jobs", total_jobs)
    col2.metric("Draft Jobs", draft_jobs)
    col3.metric("Completed Jobs", completed_jobs)
    col4.metric("Work Modules", 3)

    st.write("")

    with st.container(border=True):
        st.subheader("🔧 New Engineering Estimation")

        st.write(
            "Create a maintenance job, record site visit "
            "information and calculate engineering quantities "
            "for multiple pipe tags."
        )

        if st.button(
            "➕ CREATE NEW JOB",
            type="primary",
            use_container_width=True
        ):
            reset_job()
            go_to("New Job")

    st.subheader("Recent Jobs")

    if not jobs:
        st.info("No job records available.")

    for job in jobs[:5]:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.write(
                    f"**{uppercase(job.get('job_reference'))}**"
                )
                st.caption(job.get("work_type", "-"))

            with col2:
                st.write(uppercase(job.get("location")) or "-")
                st.caption(
                    "Supervisor: "
                    + (uppercase(job.get("supervisor")) or "-")
                )

            with col3:
                st.write(job.get("status", "Draft"))


# ============================================================
# NEW JOB
# ============================================================

elif st.session_state.page == "New Job":

    st.title("➕ Create New Job")
    st.write("Enter the job and site visit information.")
    st.divider()

    old_job = st.session_state.job_data

    work_options = [
        "Select Work Type",
        "Pipe Painting / Coating",
        "Pipe Insulation",
        "Insulation Replacement"
    ]

    old_work_type = old_job.get(
        "work_type", "Select Work Type"
    )

    work_index = (
        work_options.index(old_work_type)
        if old_work_type in work_options
        else 0
    )

    old_date = old_job.get("inspection_date")

    try:
        default_date = (
            date.fromisoformat(old_date)
            if old_date
            else date.today()
        )
    except ValueError:
        default_date = date.today()

    with st.form("job_information_form"):

        st.subheader("1. Job Information")

        col1, col2 = st.columns(2)

        with col1:
            job_reference = st.text_input(
                "Job Reference / Work Order *",
                value=old_job.get("job_reference", ""),
                placeholder="KH-2026-001"
            )

            location = st.text_input(
                "Work Location / Area",
                value=old_job.get("location", ""),
                placeholder="AREA 5"
            )

            work_type = st.selectbox(
                "Work Type *",
                work_options,
                index=work_index
            )

        with col2:
            inspection_date = st.date_input(
                "Inspection / Site Visit Date",
                value=default_date
            )

            supervisor = st.text_input(
                "Supervisor / Site Visit By *",
                value=old_job.get("supervisor", ""),
                placeholder="SUPERVISOR NAME"
            )

            prepared_by = st.text_input(
                "Prepared By",
                value=old_job.get("prepared_by", ""),
                placeholder="ESTIMATOR NAME"
            )

        st.subheader("2. Job Description")

        description = st.text_area(
            "Scope / Description of Work",
            value=old_job.get("description", ""),
            placeholder="EXTERNAL PIPE PAINTING WORK",
            height=130
        )

        st.info(
            "Pipe tags are entered on the next page. "
            "One job can contain multiple pipe tags."
        )

        submitted = st.form_submit_button(
            "Continue to Pipe Tags →",
            type="primary",
            use_container_width=True
        )

    if submitted:

        if not uppercase(job_reference):
            st.warning("Please enter the Job Reference.")

        elif work_type == "Select Work Type":
            st.warning("Please select a Work Type.")

        elif not uppercase(supervisor):
            st.warning("Please enter the Supervisor.")

        else:
            new_job_data = {
                "job_reference": uppercase(job_reference),
                "location": uppercase(location),
                "work_type": work_type,
                "inspection_date": str(inspection_date),
                "supervisor": uppercase(supervisor),
                "prepared_by": uppercase(prepared_by),
                "description": uppercase(description)
            }

            if (
                st.session_state.job_data
                and new_job_data != st.session_state.job_data
            ):
                st.session_state.calculation_results = []

            st.session_state.job_data = new_job_data

            if work_type == "Pipe Painting / Coating":
                go_to("Pipe Tags")
            elif work_type == "Pipe Insulation":
                go_to("Insulation Placeholder")
            else:
                go_to("Replacement Placeholder")


# ============================================================
# PIPE TAG INPUT
# ============================================================

elif st.session_state.page == "Pipe Tags":

    job = st.session_state.job_data

    if not job:
        st.warning("Create a job first.")
        if st.button("Go to New Job"):
            go_to("New Job")
        st.stop()

    st.title("🎨 Pipe Painting / Coating")
    st.write("Multiple Pipe Tag Engineering Estimation")
    st.divider()

    st.subheader("Job & Site Visit Information")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Job Reference", job["job_reference"])
    col2.metric("Location", job["location"] or "-")
    col3.metric("Supervisor", job["supervisor"])
    col4.metric("Site Visit Date", job["inspection_date"])

    st.divider()

    # --------------------------------------------------------
    # ADD / EDIT PIPE TAG
    # --------------------------------------------------------

    editing_index = st.session_state.editing_index
    editing = editing_index is not None

    if editing:
        existing = st.session_state.pipe_items[editing_index]
        st.subheader(
            f"✏️ Edit Pipe Tag: {existing['tag_number']}"
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
        "Enter the pipe information and submit the form. "
        "The page will not rerun while you are typing."
    )

    form_key = (
        f"edit_pipe_{editing_index}_"
        f"{st.session_state.form_version}"
        if editing
        else f"add_pipe_{st.session_state.form_version}"
    )

    with st.form(
        form_key,
        clear_on_submit=not editing
    ):

        col1, col2, col3 = st.columns(3)

        with col1:
            tag_number = st.text_input(
                "Tag Number *",
                value=existing["tag_number"],
                placeholder="4720-P-001"
            )

            outside_diameter = st.number_input(
                "Outside Diameter (mm) *",
                min_value=0.01,
                value=float(
                    existing["outside_diameter_mm"]
                ),
                step=1.0,
                format="%.2f"
            )

        with col2:
            pipe_length = st.number_input(
                "Pipe Length (m) *",
                min_value=0.01,
                value=float(existing["pipe_length_m"]),
                step=0.5,
                format="%.2f"
            )

            pipe_quantity = st.number_input(
                "Pipe Quantity *",
                min_value=1,
                value=int(existing["pipe_quantity"]),
                step=1
            )

        with col3:
            dft = st.number_input(
                "Required DFT (µm) *",
                min_value=0.1,
                value=float(existing["dft_um"]),
                step=10.0,
                format="%.1f"
            )

            volume_solids = st.number_input(
                "Volume Solids (%) *",
                min_value=0.1,
                max_value=100.0,
                value=float(
                    existing["volume_solids_pct"]
                ),
                step=1.0,
                format="%.1f"
            )

        submit_pipe = st.form_submit_button(
            "💾 Update Pipe Tag"
            if editing
            else "➕ Add Pipe Tag",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.job_saved
        )

    # --------------------------------------------------------
    # PROCESS FORM
    # --------------------------------------------------------

    if submit_pipe:

        clean_tag = uppercase(tag_number)

        if not clean_tag:
            st.warning("Please enter a Tag Number.")

        else:
            duplicate = any(
                item["tag_number"].upper() == clean_tag
                and (
                    not editing
                    or index != editing_index
                )
                for index, item in enumerate(
                    st.session_state.pipe_items
                )
            )

            if duplicate:
                st.warning(
                    f"Tag {clean_tag} already exists "
                    "in this job."
                )

            else:
                new_item = {
                    "tag_number": clean_tag,
                    "outside_diameter_mm": float(
                        outside_diameter
                    ),
                    "pipe_length_m": float(pipe_length),
                    "pipe_quantity": int(pipe_quantity),
                    "dft_um": float(dft),
                    "volume_solids_pct": float(
                        volume_solids
                    )
                }

                if editing:
                    st.session_state.pipe_items[
                        editing_index
                    ] = new_item
                    st.session_state.editing_index = None

                else:
                    st.session_state.pipe_items.append(
                        new_item
                    )

                st.session_state.calculation_results = []
                st.session_state.form_version += 1
                st.rerun()

    if editing:
        if st.button("Cancel Editing"):
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
        st.info("No pipe tags added yet.")

    else:
        for index, item in enumerate(
            st.session_state.pipe_items
        ):

            with st.container(border=True):

                col1, col2, col3, col4 = st.columns(
                    [2.5, 4, 1, 1]
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
                        f"| Qty: "
                        f"**{item['pipe_quantity']}**"
                    )

                    st.caption(
                        f"DFT: {item['dft_um']:.1f} µm "
                        f"• VS: "
                        f"{item['volume_solids_pct']:.1f}%"
                    )

                with col3:
                    if st.button(
                        "✏️ Edit",
                        key=f"edit_{index}",
                        disabled=st.session_state.job_saved,
                        use_container_width=True
                    ):
                        st.session_state.editing_index = index
                        st.rerun()

                with col4:
                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{index}",
                        disabled=st.session_state.job_saved,
                        use_container_width=True
                    ):
                        st.session_state.pipe_items.pop(index)
                        st.session_state.calculation_results = []
                        st.session_state.editing_index = None
                        st.rerun()

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "← Edit Job Information",
            use_container_width=True,
            disabled=st.session_state.job_saved
        ):
            st.session_state.editing_index = None
            go_to("New Job")

    with col2:
        if st.button(
            "🧮 Calculate All Pipe Tags",
            type="primary",
            use_container_width=True,
            disabled=(
                not st.session_state.pipe_items
                or st.session_state.job_saved
            )
        ):
            calculate_all()
            st.rerun()

    # --------------------------------------------------------
    # CALCULATION RESULTS
    # --------------------------------------------------------

    results = st.session_state.calculation_results

    if results:
        st.divider()
        st.subheader("📐 Engineering Estimation Results")

        result_table = []

        for item in results:
            result_table.append({
                "Tag Number": item["tag_number"],
                "OD (mm)": round(
                    item["outside_diameter_mm"], 2
                ),
                "Length (m)": round(
                    item["pipe_length_m"], 2
                ),
                "Qty": item["pipe_quantity"],
                "DFT (µm)": round(item["dft_um"], 1),
                "VS (%)": round(
                    item["volume_solids_pct"], 1
                ),
                "Surface Area (m²)": round(
                    item["surface_area_m2"], 2
                ),
                "WFT (µm)": round(item["wft_um"], 1),
                "Theoretical Coating (L)": round(
                    item["theoretical_coating_l"], 2
                )
            })

        st.dataframe(
            result_table,
            use_container_width=True,
            hide_index=True
        )

        total_tags = len(results)

        total_quantity = sum(
            item["pipe_quantity"] for item in results
        )

        total_length = sum(
            item["pipe_length_m"] * item["pipe_quantity"]
            for item in results
        )

        total_area = sum(
            item["surface_area_m2"] for item in results
        )

        total_coating = sum(
            item["theoretical_coating_l"]
            for item in results
        )

        st.subheader("Overall Job Summary")

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Pipe Tags", total_tags)
        col2.metric("Pipe Quantity", total_quantity)
        col3.metric(
            "Total Length", f"{total_length:.2f} m"
        )
        col4.metric(
            "Surface Area", f"{total_area:.2f} m²"
        )
        col5.metric(
            "Theoretical Coating",
            f"{total_coating:.2f} L"
        )

        with st.expander(
            "📐 View Engineering Calculation Method"
        ):
            st.write("**External Pipe Surface Area**")
            st.latex(r"A = \pi D L N")

            st.write(
                "D = outside diameter (m), "
                "L = length (m), N = quantity"
            )

            st.write("**Wet Film Thickness**")
            st.latex(r"WFT = \frac{DFT}{VS/100}")

            st.write("**Theoretical Coating Quantity**")
            st.latex(r"Q = \frac{A \times WFT}{1000}")

        st.warning(
            "Coating quantities are theoretical and "
            "exclude application losses, overspray and "
            "other project-specific allowances."
        )

        st.divider()

        # ----------------------------------------------------
        # SAVE JOB AND PIPE ITEMS
        # ----------------------------------------------------

        if st.session_state.job_saved:

            st.success(
                "✅ Job and pipe tags saved successfully."
            )

            st.write(
                "Database Job ID: "
                f"**{st.session_state.saved_job_id}**"
            )

            if st.button(
                "📋 Go to Job Records",
                type="primary",
                use_container_width=True
            ):
                reset_job()
                go_to("Job Records")

        else:

            if st.session_state.pending_job_id:
                st.warning(
                    "The job record was created earlier, "
                    "but the pipe tags were not confirmed "
                    "as saved. Retry will use the existing "
                    "job ID rather than creating another job."
                )

            if st.button(
                "💾 Save Job & Engineering Estimation",
                type="primary",
                use_container_width=True
            ):

                job_id = st.session_state.pending_job_id

                if job_id is None:

                    database_job = {
                        "job_reference": job["job_reference"],
                        "location": job["location"],
                        "equipment": None,
                        "work_type": job["work_type"],
                        "inspection_date": job[
                            "inspection_date"
                        ],
                        "supervisor": job["supervisor"],
                        "prepared_by": job["prepared_by"],
                        "description": job["description"],
                        "status": "Draft"
                    }

                    success, saved_job = save_job(
                        database_job
                    )

                    if not success:
                        st.error(
                            f"Unable to save job: {saved_job}"
                        )
                        st.stop()

                    job_id = saved_job["id"]

                    st.session_state.pending_job_id = job_id

                database_items = []

                for item in results:
                    database_items.append({
                        "job_id": job_id,
                        "tag_number": item["tag_number"],
                        "outside_diameter_mm": item[
                            "outside_diameter_mm"
                        ],
                        "pipe_length_m": item[
                            "pipe_length_m"
                        ],
                        "pipe_quantity": item[
                            "pipe_quantity"
                        ],
                        "dft_um": item["dft_um"],
                        "volume_solids_pct": item[
                            "volume_solids_pct"
                        ],
                        "surface_area_m2": item[
                            "surface_area_m2"
                        ],
                        "wft_um": item["wft_um"],
                        "theoretical_coating_l": item[
                            "theoretical_coating_l"
                        ]
                    })

                # Check for existing tags in case an earlier
                # database response was interrupted.
                existing_items = get_pipe_items(job_id)

                if existing_items:
                    st.warning(
                        "Pipe records already exist for "
                        "this job. Automatic retry has been "
                        "stopped to avoid duplicate entries."
                    )

                else:
                    pipe_success, pipe_error = (
                        save_pipe_items(database_items)
                    )

                    if pipe_success:
                        st.session_state.job_saved = True
                        st.session_state.saved_job_id = job_id
                        st.session_state.pending_job_id = None
                        st.rerun()

                    else:
                        st.error(
                            "The job was created, but pipe "
                            "items could not be saved."
                        )
                        st.error(pipe_error)


# ============================================================
# INSULATION PLACEHOLDERS
# ============================================================

elif st.session_state.page == "Insulation Placeholder":

    st.title("🧱 Pipe Insulation")
    st.info(
        "Pipe Insulation calculations will be "
        "added in the next development stage."
    )

    if st.button("← Back to Job Information"):
        go_to("New Job")


elif st.session_state.page == "Replacement Placeholder":

    st.title("🔄 Insulation Replacement")
    st.info(
        "Insulation Replacement calculations will "
        "be added in the next development stage."
    )

    if st.button("← Back to Job Information"):
        go_to("New Job")


# ============================================================
# JOB RECORDS
# ============================================================

elif st.session_state.page == "Job Records":

    st.title("📋 Job Records")
    st.write(
        "Saved maintenance jobs and pipe estimations."
    )
    st.divider()

    jobs = get_jobs()

    if not jobs:
        st.info("No job records found.")

    else:
        search = st.text_input(
            "🔍 Search Jobs",
            placeholder=(
                "JOB REFERENCE, LOCATION, "
                "SUPERVISOR OR WORK TYPE"
            )
        )

        query = uppercase(search)

        filtered_jobs = [
            job for job in jobs
            if not query or any(
                query in uppercase(job.get(field))
                for field in [
                    "job_reference",
                    "location",
                    "supervisor",
                    "work_type"
                ]
            )
        ]

        st.caption(
            f"{len(filtered_jobs)} job record(s) shown"
        )

        for job in filtered_jobs:

            pipe_records = get_pipe_items(job["id"])

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [2, 2, 1]
                )

                with col1:
                    st.subheader(
                        uppercase(job.get("job_reference"))
                    )
                    st.write(
                        f"**Work Type:** "
                        f"{job.get('work_type', '-')}"
                    )
                    st.write(
                        f"**Location:** "
                        f"{uppercase(job.get('location')) or '-'}"
                    )

                with col2:
                    st.write(
                        f"**Site Visit Date:** "
                        f"{job.get('inspection_date', '-')}"
                    )
                    st.write(
                        f"**Supervisor:** "
                        f"{uppercase(job.get('supervisor')) or '-'}"
                    )
                    st.write(
                        f"**Prepared By:** "
                        f"{uppercase(job.get('prepared_by')) or '-'}"
                    )

                with col3:
                    st.write("**Status**")
                    st.write(job.get("status", "Draft"))
                    st.metric(
                        "Pipe Tags",
                        len(pipe_records)
                    )

                if pipe_records:

                    total_area = sum(
                        item.get("surface_area_m2") or 0
                        for item in pipe_records
                    )

                    total_coating = sum(
                        item.get("theoretical_coating_l") or 0
                        for item in pipe_records
                    )

                    with st.expander(
                        "View Engineering Estimation"
                    ):

                        col_a, col_b, col_c = st.columns(3)

                        col_a.metric(
                            "Pipe Tags",
                            len(pipe_records)
                        )
                        col_b.metric(
                            "Surface Area",
                            f"{total_area:.2f} m²"
                        )
                        col_c.metric(
                            "Theoretical Coating",
                            f"{total_coating:.2f} L"
                        )

                        table = []

                        for item in pipe_records:
                            table.append({
                                "Tag": uppercase(
                                    item.get("tag_number")
                                ),
                                "OD (mm)": item.get(
                                    "outside_diameter_mm"
                                ),
                                "Length (m)": item.get(
                                    "pipe_length_m"
                                ),
                                "Qty": item.get(
                                    "pipe_quantity"
                                ),
                                "DFT (µm)": item.get(
                                    "dft_um"
                                ),
                                "VS (%)": item.get(
                                    "volume_solids_pct"
                                ),
                                "Area (m²)": round(
                                    item.get(
                                        "surface_area_m2"
                                    ) or 0, 2
                                ),
                                "WFT (µm)": round(
                                    item.get("wft_um") or 0, 1
                                ),
                                "Coating (L)": round(
                                    item.get(
                                        "theoretical_coating_l"
                                    ) or 0, 2
                                )
                            })

                        st.dataframe(
                            table,
                            use_container_width=True,
                            hide_index=True
                        )

                        if job.get("description"):
                            st.write("**Job Description / Scope**")
                            st.write(
                                uppercase(job["description"])
                            )

                else:
                    st.caption(
                        "No pipe tag estimation stored "
                        "for this job."
                    )


# ============================================================
# REPORTS
# ============================================================

elif st.session_state.page == "Reports":

    st.title("📊 Reports")
    st.write("Maintenance Engineering Estimation Summary")
    st.divider()

    jobs = get_jobs()

    try:
        response = (
            supabase.table("pipe_items")
            .select("*")
            .execute()
        )
        all_items = response.data or []

    except Exception as error:
        st.warning(
            f"Unable to retrieve report data: {error}"
        )
        all_items = []

    total_area = sum(
        item.get("surface_area_m2") or 0
        for item in all_items
    )

    total_coating = sum(
        item.get("theoretical_coating_l") or 0
        for item in all_items
    )

    painting_jobs = sum(
        job.get("work_type") == "Pipe Painting / Coating"
        for job in jobs
    )

    insulation_jobs = sum(
        job.get("work_type") == "Pipe Insulation"
        for job in jobs
    )

    replacement_jobs = sum(
        job.get("work_type") == "Insulation Replacement"
        for job in jobs
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Jobs", len(jobs))
    col2.metric("Painting Jobs", painting_jobs)
    col3.metric("Total Pipe Tags", len(all_items))
    col4.metric(
        "Total Surface Area",
        f"{total_area:.2f} m²"
    )

    col5, col6, col7 = st.columns(3)

    col5.metric(
        "Theoretical Coating",
        f"{total_coating:.2f} L"
    )
    col6.metric("Insulation Jobs", insulation_jobs)
    col7.metric("Replacement Jobs", replacement_jobs)

    st.info(
        "Additional reporting and insulation "
        "calculations will be developed later."
    )
