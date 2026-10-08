
import math
from datetime import date

import streamlit as st
from supabase import create_client


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Maintenance Engineering Estimator",
    page_icon="🔧",
    layout="wide"
)

st.markdown(
    """
    <style>
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        text-transform: uppercase !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def up(value):
    return str(value or "").strip().upper()


# ============================================================
# SUPABASE CONNECTION
# ============================================================

@st.cache_resource
def db():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


S = db()


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = dict(
    page="Dashboard",
    job={},
    pipes=[],
    editing=None,
    form_version=0,
    results=[],
    saved_id=None,
    pending_id=None,
    save_error=""
)

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset():
    st.session_state.job = {}
    st.session_state.pipes = []
    st.session_state.editing = None
    st.session_state.form_version += 1
    st.session_state.results = []
    st.session_state.saved_id = None
    st.session_state.pending_id = None
    st.session_state.save_error = ""


def nav(page):
    st.session_state.page = page
    st.rerun()


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def rows(table, **filters):
    q = S.table(table).select("*")

    for k, v in filters.items():
        q = q.eq(k, v)

    return q.execute().data or []


def coating_systems():
    data = rows("coating_systems")
    result = {}

    for r in data:
        result.setdefault(
            r["system_id"], []
        ).append(r)

    for key in result:
        result[key].sort(
            key=lambda r: r["coat_number"]
        )

    return dict(sorted(result.items()))


# ============================================================
# ENGINEERING CALCULATIONS
# ============================================================

def area_for(pipe):

    if pipe["area_method"] == "Whole Pipe":

        return (
            math.pi
            * pipe["outside_diameter_mm"]
            / 1000
            * pipe["pipe_length_m"]
            * pipe["pipe_quantity"]
        )

    return sum(
        spot["length_m"]
        * spot["width_m"]
        * spot["quantity"]
        for spot in pipe["spots"]
    )


def calc_pipe(pipe, specs):

    area = area_for(pipe)
    coats = []

    if pipe["work_type"] == "Pipe Painting / Coating":

        for row in specs[pipe["system_id"]]:

            coat_no = int(row["coat_number"])

            vs = pipe["volume_solids"][coat_no]

            dft = float(row["nominal_dft_um"])

            wft = dft / (vs / 100)

            coating_l = area * wft / 1000

            coats.append({
                "coat_number": coat_no,
                "coating_description":
                    row["coating_description"],
                "dft_um": dft,
                "volume_solids_pct": vs,
                "wft_um": wft,
                "theoretical_coating_l": coating_l
            })

    return {
        "pipe": pipe,
        "area": area,
        "coats": coats,
        "total_dft": sum(
            c["dft_um"] for c in coats
        ),
        "litres": sum(
            c["theoretical_coating_l"]
            for c in coats
        )
    }


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🔧 KHAL")

    st.caption(
        "MAINTENANCE ENGINEERING • FYP PROTOTYPE"
    )

    for title, page in [
        ("🏠 Dashboard", "Dashboard"),
        ("➕ New Job", "New Job"),
        ("📋 Job Records", "Job Records"),
        ("📊 Reports", "Reports")
    ]:

        if st.button(
            title,
            use_container_width=True
        ):

            if page == "New Job":
                reset()

            nav(page)

    st.divider()

    st.caption(
        "Use fictional data only. "
        "Anonymous prototype database access is enabled."
    )


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":

    st.title("Maintenance Engineering Estimator")

    st.write(
        "Job planning and quantity estimation "
        "for piping coating and insulation maintenance."
    )

    try:

        jobs = rows("jobs")

        st.metric(
            "Saved Jobs",
            len(jobs)
        )

        if jobs:

            st.dataframe(
                [
                    {
                        "Reference":
                            j.get("job_reference"),
                        "Work Type":
                            j.get("work_type"),
                        "Activity":
                            j.get("work_activity"),
                        "Location":
                            j.get("location")
                    }
                    for j in jobs[-15:]
                ],
                hide_index=True,
                use_container_width=True
            )

    except Exception as exc:

        st.error(
            f"Database connection error: {exc}"
        )

    if st.button(
        "Create New Job",
        type="primary"
    ):
        reset()
        nav("New Job")


# ============================================================
# NEW JOB
# ============================================================

elif st.session_state.page == "New Job":

    st.title("New Job / Site Visit")

    job = st.session_state.job

    types = [
        "Pipe Painting / Coating",
        "Pipe Insulation"
    ]

    activities = [
        "New",
        "Replacement",
        "Spot Repair",
        "Whole Area"
    ]

    with st.form("job_form"):

        a, b = st.columns(2)

        with a:

            reference = st.text_input(
                "Job Reference *",
                value=job.get(
                    "job_reference", ""
                ),
                placeholder="DEMO-001"
            )

            location = st.text_input(
                "Work Location",
                value=job.get(
                    "location", ""
                )
            )

            work_type = st.selectbox(
                "Work Type",
                types,
                index=(
                    types.index(job["work_type"])
                    if job.get("work_type") in types
                    else 0
                )
            )

            activity = st.selectbox(
                "Work Activity",
                activities,
                index=(
                    activities.index(
                        job["work_activity"]
                    )
                    if job.get("work_activity")
                    in activities
                    else 0
                )
            )

        with b:

            try:
                initial_date = date.fromisoformat(
                    job["inspection_date"]
                )

            except (KeyError, ValueError):
                initial_date = date.today()

            visit_date = st.date_input(
                "Site Visit Date",
                value=initial_date
            )

            supervisor = st.text_input(
                "Supervisor / Site Visit By *",
                value=job.get(
                    "supervisor", ""
                )
            )

            prepared = st.text_input(
                "Prepared By",
                value=job.get(
                    "prepared_by", ""
                )
            )

        description = st.text_area(
            "Description / Scope",
            value=job.get(
                "description", ""
            )
        )

        submit = st.form_submit_button(
            "Continue to Pipe Tags →",
            type="primary",
            use_container_width=True
        )

    if submit:

        if not up(reference) or not up(supervisor):

            st.error(
                "Job reference and supervisor are required."
            )

        else:

            new_job = {
                "job_reference": up(reference),
                "location": up(location),
                "work_type": work_type,
                "work_activity": activity,
                "inspection_date": str(visit_date),
                "supervisor": up(supervisor),
                "prepared_by": up(prepared),
                "description": up(description)
            }

            if (
                job
                and job["work_type"] != work_type
            ):
                st.session_state.pipes = []

            st.session_state.job = new_job

            st.session_state.results = []

            nav("Pipe Tags")


# ============================================================
# PIPE TAG INPUT
# ============================================================

elif st.session_state.page == "Pipe Tags":

    job = st.session_state.job

    if not job:
        nav("New Job")

    st.title(job["work_type"])

    st.caption(
        f"{job['job_reference']} • "
        f"{job['work_activity']} • "
        f"{job['location']} • "
        f"Supervisor: {job['supervisor']}"
    )

    # --------------------------------------------------------
    # INSULATION MODULE
    # --------------------------------------------------------

    if job["work_type"] == "Pipe Insulation":

        st.info(
            "Insulation measurement and quantity "
            "calculation will be implemented in the "
            "next module. This version does not save "
            "insulation estimations."
        )

        if st.button("← Edit Job"):
            nav("New Job")

        st.stop()

    # --------------------------------------------------------
    # LOAD COATING SYSTEMS
    # --------------------------------------------------------

    try:
        specs = coating_systems()

    except Exception as exc:

        st.error(
            f"Cannot read coating specifications: {exc}"
        )

        st.stop()

    if not specs:

        st.error(
            "No coating systems found in Supabase. "
            "Please load your coating reference table."
        )

        st.stop()

    # --------------------------------------------------------
    # SAVE STATUS
    # --------------------------------------------------------

    if st.session_state.saved_id is not None:

        st.success(
            "Job saved successfully. "
            f"Job ID: {st.session_state.saved_id}"
        )

        if st.button(
            "View Job Records",
            type="primary"
        ):
            nav("Job Records")

        st.stop()

    if st.session_state.pending_id is not None:

        st.warning(
            "A job record was already created "
            f"(ID {st.session_state.pending_id}). "
            "Editing is disabled until its save issue "
            "is resolved to prevent inconsistent records."
        )

        st.error(
            st.session_state.save_error
        )

        st.stop()

    # --------------------------------------------------------
    # ADD OR EDIT PIPE
    # --------------------------------------------------------

    idx = st.session_state.editing

    editing = idx is not None

    if editing:

        existing = st.session_state.pipes[idx]

    else:

        existing = {
            "tag_number": "",
            "outside_diameter_mm": 114.3,
            "pipe_length_m": 1.0,
            "pipe_quantity": 1,
            "area_method": (
                "Spot Repair"
                if job["work_activity"] == "Spot Repair"
                else "Whole Pipe"
            ),
            "system_id": list(specs)[0],
            "volume_solids": {},
            "spots": []
        }

    st.subheader(
        "Edit Pipe Tag"
        if editing
        else "Add Pipe Tag"
    )

    method_options = [
        "Whole Pipe",
        "Spot Repair"
    ]

    systems = list(specs)

    choice_a, choice_b = st.columns(2)

    method = choice_a.selectbox(
        "Measurement Method",
        method_options,
        index=method_options.index(
            existing["area_method"]
        ),
        key=(
            f"method_"
            f"{st.session_state.form_version}_{idx}"
        )
    )

    system_id = choice_b.selectbox(
        "Coating System ID",
        systems,
        index=(
            systems.index(existing["system_id"])
            if existing["system_id"] in systems
            else 0
        ),
        key=(
            f"system_"
            f"{st.session_state.form_version}_{idx}"
        )
    )

    # Number of spot groups is outside the form,
    # allowing the required input rows to be generated.

    if method == "Spot Repair":

        count = st.number_input(
            "Number of spot groups on this pipe tag",
            min_value=1,
            max_value=100,
            value=max(
                1,
                len(existing["spots"])
            ),
            step=1,
            key=(
                f"count_"
                f"{st.session_state.form_version}_{idx}"
            )
        )

    else:
        count = 0

    # --------------------------------------------------------
    # PIPE INPUT FORM
    # --------------------------------------------------------

    with st.form(
        f"pipe_form_"
        f"{st.session_state.form_version}_{idx}",
        clear_on_submit=False
    ):

        a, b, c = st.columns(3)

        with a:

            tag = st.text_input(
                "Tag Number *",
                value=existing["tag_number"]
            )

            od = st.number_input(
                "Pipe Outside Diameter (mm)",
                min_value=0.01,
                value=float(
                    existing["outside_diameter_mm"]
                ),
                format="%.2f"
            )

        with b:

            length = st.number_input(
                "Painted Pipe Length (m)",
                min_value=0.01,
                value=float(
                    existing["pipe_length_m"]
                ),
                format="%.2f",
                help=(
                    "Used for whole-pipe calculation"
                )
            )

            qty = st.number_input(
                "Number of Pipes",
                min_value=1,
                value=int(
                    existing["pipe_quantity"]
                )
            )

        with c:

            total_dft = sum(
                float(r["nominal_dft_um"])
                for r in specs[system_id]
            )

            st.metric(
                "Total Nominal DFT",
                f"{total_dft:g} µm"
            )

        # ----------------------------------------------------
        # COATING LAYERS
        # ----------------------------------------------------

        st.markdown(
            "**Coating layers — DFT from reference, "
            "volume solids from manufacturer TDS**"
        )

        volume_solids = {}

        for coat in specs[system_id]:

            no = int(coat["coat_number"])

            ca, cb = st.columns([3, 1])

            ca.write(
                f"Coat {no}: "
                f"{coat['coating_description']} "
                f"— **{coat['nominal_dft_um']:g} "
                "µm DFT**"
            )

            if existing["system_id"] == system_id:

                previous_vs = (
                    existing["volume_solids"].get(
                        no,
                        75.0
                    )
                )

            else:
                previous_vs = 75.0

            volume_solids[no] = cb.number_input(
                f"Coat {no} Volume Solids (%)",
                min_value=0.1,
                max_value=100.0,
                value=float(previous_vs),
                format="%.1f",
                key=(
                    f"vs_"
                    f"{st.session_state.form_version}_"
                    f"{idx}_{system_id}_{no}"
                )
            )

        st.caption(
            "Volume solids defaults to 75% for "
            "demonstration ONLY. Replace every value "
            "with the relevant paint TDS value before "
            "using results."
        )

        # ----------------------------------------------------
        # MULTIPLE REPAIR SPOTS
        # ----------------------------------------------------

        spot_rows = []

        if method == "Spot Repair":

            st.markdown("**Repair Spots**")

            st.caption(
                "Enter the actual measured surface "
                "length and circumferential width of "
                "each repair spot. Multiple identical "
                "spots can be entered using quantity."
            )

            for i in range(int(count)):

                if i < len(existing["spots"]):

                    prior = existing["spots"][i]

                else:

                    prior = {
                        "spot_number": f"SP-{i+1:02}",
                        "length_m": 0.5,
                        "width_m": 0.3,
                        "quantity": 1
                    }

                st.write(
                    f"**Spot Group {i+1}**"
                )

                x, y, z, w = st.columns(4)

                spot_no = x.text_input(
                    "Spot ID",
                    value=prior["spot_number"],
                    key=(
                        f"sn_"
                        f"{st.session_state.form_version}_"
                        f"{idx}_{i}"
                    )
                )

                sl = y.number_input(
                    "Length (m)",
                    min_value=0.001,
                    value=float(
                        prior["length_m"]
                    ),
                    format="%.3f",
                    key=(
                        f"sl_"
                        f"{st.session_state.form_version}_"
                        f"{idx}_{i}"
                    )
                )

                sw = z.number_input(
                    "Surface Width (m)",
                    min_value=0.001,
                    value=float(
                        prior["width_m"]
                    ),
                    format="%.3f",
                    key=(
                        f"sw_"
                        f"{st.session_state.form_version}_"
                        f"{idx}_{i}"
                    )
                )

                sq = w.number_input(
                    "Spot Quantity",
                    min_value=1,
                    value=int(
                        prior["quantity"]
                    ),
                    key=(
                        f"sq_"
                        f"{st.session_state.form_version}_"
                        f"{idx}_{i}"
                    )
                )

                spot_rows.append({
                    "spot_number": (
                        up(spot_no)
                        or f"SP-{i+1:02}"
                    ),
                    "length_m": float(sl),
                    "width_m": float(sw),
                    "quantity": int(sq)
                })

        submit = st.form_submit_button(
            "💾 Update Pipe Tag"
            if editing
            else "➕ Add Pipe Tag",
            type="primary",
            use_container_width=True
        )

    # --------------------------------------------------------
    # PROCESS PIPE FORM
    # --------------------------------------------------------

    if submit:

        clean = up(tag)

        if not clean:

            st.error(
                "Enter a tag number."
            )

        elif any(
            p["tag_number"] == clean
            and i != idx
            for i, p in enumerate(
                st.session_state.pipes
            )
        ):

            st.error(
                "This tag number already exists "
                "in the job."
            )

        elif (
            method == "Spot Repair"
            and any(
                s["width_m"] > math.pi * od / 1000
                for s in spot_rows
            )
        ):

            st.error(
                "A spot surface width cannot exceed "
                "the pipe circumference. Split "
                "unusually large or overlapping "
                "patches, or use Whole Pipe."
            )

        else:

            item = {
                "tag_number": clean,
                "outside_diameter_mm": float(od),
                "pipe_length_m": float(length),
                "pipe_quantity": int(qty),
                "area_method": method,
                "system_id": system_id,
                "volume_solids": volume_solids,
                "spots": spot_rows,
                "work_type": job["work_type"]
            }

            if editing:

                st.session_state.pipes[idx] = item

            else:

                st.session_state.pipes.append(item)

            st.session_state.editing = None
            st.session_state.results = []
            st.session_state.form_version += 1

            st.rerun()

    if editing:

        if st.button("Cancel Editing"):

            st.session_state.editing = None
            st.session_state.form_version += 1

            st.rerun()

    # --------------------------------------------------------
    # ADDED PIPE TAGS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Added Pipe Tags "
        f"({len(st.session_state.pipes)})"
    )

    for i, pipe in enumerate(
        st.session_state.pipes
    ):

        a, b, c, d = st.columns(
            [3, 3, 1, 1]
        )

        a.write(
            f"**{i+1}. {pipe['tag_number']}**"
        )

        b.write(
            f"{pipe['system_id']} • "
            f"{pipe['area_method']} • "
            f"{area_for(pipe):.3f} m²"
        )

        if c.button(
            "Edit",
            key=f"edit_{i}"
        ):

            st.session_state.editing = i
            st.session_state.form_version += 1

            st.rerun()

        if d.button(
            "Delete",
            key=f"del_{i}"
        ):

            st.session_state.pipes.pop(i)
            st.session_state.editing = None
            st.session_state.results = []
            st.session_state.form_version += 1

            st.rerun()

    # --------------------------------------------------------
    # CALCULATE
    # --------------------------------------------------------

    a, b = st.columns(2)

    if a.button(
        "← Edit Job Information",
        use_container_width=True
    ):
        nav("New Job")

    if b.button(
        "🧮 Calculate All Pipe Tags",
        type="primary",
        disabled=not st.session_state.pipes,
        use_container_width=True
    ):

        st.session_state.results = [
            calc_pipe(p, specs)
            for p in st.session_state.pipes
        ]

        st.rerun()

    # --------------------------------------------------------
    # CALCULATION RESULTS
    # --------------------------------------------------------

    if st.session_state.results:

        st.divider()

        st.subheader(
            "Engineering Estimation Results"
        )

        summaries = []
        layers = []

        for result in st.session_state.results:

            pipe = result["pipe"]

            summaries.append({
                "Tag": pipe["tag_number"],
                "System": pipe["system_id"],
                "Method": pipe["area_method"],
                "Spot Groups": len(
                    pipe["spots"]
                ),
                "Area (m²)": round(
                    result["area"], 3
                ),
                "Total DFT (µm)":
                    result["total_dft"],
                "Theoretical Total (L)": round(
                    result["litres"], 3
                )
            })

            for coat in result["coats"]:

                layers.append({
                    "Tag": pipe["tag_number"],
                    "Coat": coat["coat_number"],
                    "Coating":
                        coat["coating_description"],
                    "DFT (µm)": coat["dft_um"],
                    "Volume Solids (%)":
                        coat["volume_solids_pct"],
                    "WFT (µm)": round(
                        coat["wft_um"], 2
                    ),
                    "Theoretical (L)": round(
                        coat["theoretical_coating_l"],
                        3
                    )
                })

        st.dataframe(
            summaries,
            use_container_width=True,
            hide_index=True
        )

        st.subheader(
            "Coat-by-Coat Calculation"
        )

        st.dataframe(
            layers,
            use_container_width=True,
            hide_index=True
        )

        total_area = sum(
            r["area"]
            for r in st.session_state.results
        )

        total_l = sum(
            r["litres"]
            for r in st.session_state.results
        )

        a, b, c = st.columns(3)

        a.metric(
            "Pipe Tags",
            len(st.session_state.results)
        )

        b.metric(
            "Total Coating Area",
            f"{total_area:.3f} m²"
        )

        c.metric(
            "Total Theoretical Coating",
            f"{total_l:.3f} L"
        )

        with st.expander(
            "Calculation Formulas"
        ):

            st.latex(
                r"A_{whole}=\pi D L N"
            )

            st.latex(
                r"A_{spots}=\sum (l_i w_i n_i)"
            )

            st.latex(
                r"WFT_i=\frac{DFT_i}{VS_i/100}"
            )

            st.latex(
                r"Q_i=\frac{A\times WFT_i}{1000}"
            )

        st.warning(
            "Theoretical wet paint quantity only. "
            "No wastage or overspray allowance. "
            "Confirm the applicable PETRONAS "
            "specification revision and project "
            "requirements. Volume solids defaults "
            "are illustrative, not verified "
            "manufacturer values."
        )

        # ----------------------------------------------------
        # SAVE JOB
        # ----------------------------------------------------

        if st.button(
            "💾 Save Job & Estimation",
            type="primary",
            use_container_width=True
        ):

            try:

                if st.session_state.pending_id is None:

                    job_row = dict(
                        st.session_state.job
                    )

                    job_row["status"] = "Draft"

                    response = (
                        S.table("jobs")
                        .insert(job_row)
                        .execute()
                    )

                    st.session_state.pending_id = (
                        response.data[0]["id"]
                    )

                job_id = st.session_state.pending_id

                # Save each pipe, then its spots
                # and coating layers.

                for result in st.session_state.results:

                    pipe = result["pipe"]

                    parent = {
                        "job_id": job_id,
                        "tag_number":
                            pipe["tag_number"],
                        "outside_diameter_mm":
                            pipe["outside_diameter_mm"],
                        "pipe_length_m":
                            pipe["pipe_length_m"],
                        "pipe_quantity":
                            pipe["pipe_quantity"],
                        "dft_um":
                            result["total_dft"],
                        "volume_solids_pct": None,
                        "surface_area_m2":
                            result["area"],
                        "wft_um": None,
                        "theoretical_coating_l":
                            result["litres"],
                        "coating_system_id":
                            pipe["system_id"],
                        "area_method":
                            pipe["area_method"]
                    }

                    response = (
                        S.table("pipe_items")
                        .insert(parent)
                        .execute()
                    )

                    pipe_id = response.data[0]["id"]

                    # Save repair spots

                    if pipe["spots"]:

                        spot_payload = []

                        for spot in pipe["spots"]:

                            spot_payload.append({
                                "pipe_item_id": pipe_id,
                                "spot_number":
                                    spot["spot_number"],
                                "spot_length_m":
                                    spot["length_m"],
                                "spot_width_m":
                                    spot["width_m"],
                                "spot_quantity":
                                    spot["quantity"],
                                "spot_area_m2":
                                    spot["length_m"]
                                    * spot["width_m"]
                                    * spot["quantity"]
                            })

                        (
                            S.table("pipe_spots")
                            .insert(spot_payload)
                            .execute()
                        )

                    # Save coating layers

                    coat_payload = [
                        {
                            "pipe_item_id": pipe_id,
                            **coat
                        }
                        for coat in result["coats"]
                    ]

                    (
                        S.table("coating_estimations")
                        .insert(coat_payload)
                        .execute()
                    )

                st.session_state.saved_id = job_id
                st.session_state.pending_id = None

                st.rerun()

            except Exception as exc:

                st.session_state.save_error = (
                    f"{exc}. Some records may have "
                    "been saved. Do not press Save "
                    "again; inspect Supabase first."
                )

                st.error(
                    st.session_state.save_error
                )


# ============================================================
# JOB RECORDS
# ============================================================

elif st.session_state.page == "Job Records":

    st.title("Job Records")

    try:

        jobs = sorted(
            rows("jobs"),
            key=lambda j: j.get("id", 0),
            reverse=True
        )

        query = up(
            st.text_input("Search Jobs")
        )

        for job in jobs:

            if query and not any(
                query in up(job.get(k))
                for k in (
                    "job_reference",
                    "location",
                    "supervisor",
                    "work_type"
                )
            ):
                continue

            with st.expander(
                f"{up(job.get('job_reference')) or 'UNTITLED'} "
                f"• {job.get('work_type') or '-'} "
                f"• {job.get('work_activity') or '-'}"
            ):

                st.write(
                    f"**Location:** "
                    f"{up(job.get('location')) or '-'} "
                    f"| **Supervisor:** "
                    f"{up(job.get('supervisor')) or '-'} "
                    f"| **Status:** "
                    f"{job.get('status') or '-'}"
                )

                pipes = rows(
                    "pipe_items",
                    job_id=job["id"]
                )

                if not pipes:

                    st.info(
                        "No pipe estimation data saved "
                        "for this job."
                    )

                else:

                    st.dataframe(
                        [
                            {
                                "Tag":
                                    up(p.get("tag_number")),
                                "System":
                                    p.get("coating_system_id"),
                                "Area Method":
                                    p.get("area_method"),
                                "Area (m²)":
                                    p.get("surface_area_m2"),
                                "Total DFT (µm)":
                                    p.get("dft_um"),
                                "Total Coating (L)":
                                    p.get(
                                        "theoretical_coating_l"
                                    )
                            }
                            for p in pipes
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                    for p in pipes:

                        spots = rows(
                            "pipe_spots",
                            pipe_item_id=p["id"]
                        )

                        coats = rows(
                            "coating_estimations",
                            pipe_item_id=p["id"]
                        )

                        if spots or coats:

                            st.markdown(
                                f"**{up(p.get('tag_number'))} "
                                "— Detail**"
                            )

                            if spots:

                                st.caption(
                                    "Spot Repair Measurements"
                                )

                                st.dataframe(
                                    [
                                        {
                                            "Spot":
                                                up(s["spot_number"]),
                                            "Length (m)":
                                                s["spot_length_m"],
                                            "Width (m)":
                                                s["spot_width_m"],
                                            "Quantity":
                                                s["spot_quantity"],
                                            "Area (m²)":
                                                s["spot_area_m2"]
                                        }
                                        for s in spots
                                    ],
                                    hide_index=True,
                                    use_container_width=True
                                )

                            if coats:

                                st.caption(
                                    "Individual Coating Layers"
                                )

                                st.dataframe(
                                    [
                                        {
                                            "Coat":
                                                c["coat_number"],
                                            "Coating":
                                                c["coating_description"],
                                            "DFT (µm)":
                                                c["dft_um"],
                                            "Volume Solids (%)":
                                                c["volume_solids_pct"],
                                            "WFT (µm)":
                                                c["wft_um"],
                                            "Theoretical (L)":
                                                c["theoretical_coating_l"]
                                        }
                                        for c in sorted(
                                            coats,
                                            key=lambda c:
                                                c["coat_number"]
                                        )
                                    ],
                                    hide_index=True,
                                    use_container_width=True
                                )

    except Exception as exc:

        st.error(
            f"Unable to retrieve job records: {exc}"
        )


# ============================================================
# REPORTS
# ============================================================

elif st.session_state.page == "Reports":

    st.title("Reports")

    try:

        jobs = rows("jobs")
        pipes = rows("pipe_items")

        a, b, c, d = st.columns(4)

        a.metric(
            "Total Jobs",
            len(jobs)
        )

        b.metric(
            "Pipe Tags",
            len(pipes)
        )

        c.metric(
            "Estimated Area",
            f"{sum(float(p.get('surface_area_m2') or 0) for p in pipes):.2f} m²"
        )

        d.metric(
            "Theoretical Coating",
            f"{sum(float(p.get('theoretical_coating_l') or 0) for p in pipes):.2f} L"
        )

        st.caption(
            "Prototype summary. Database API result "
            "limits may require pagination for "
            "larger datasets."
        )

    except Exception as exc:

        st.error(
            f"Unable to load reports: {exc}"
        )
