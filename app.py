import streamlit as st

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Maintenance Engineering Estimator",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM DESIGN
# =========================================================

st.markdown("""
<style>

/* Main page */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Dashboard cards */

.dashboard-card {
    padding: 20px;
    border: 1px solid #444;
    border-radius: 12px;
    margin-bottom: 10px;
}

.card-title {
    font-size: 15px;
    opacity: 0.7;
}

.card-number {
    font-size: 32px;
    font-weight: 700;
    margin-top: 5px;
}

/* New Job box */

.new-job-box {
    padding: 25px;
    border: 1px solid #444;
    border-radius: 12px;
    margin-top: 10px;
}

.small-text {
    opacity: 0.7;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🔧 KHAL")
    st.caption("Maintenance Engineering")

    st.divider()

    st.write("### Navigation")

    st.button(
        "🏠 Dashboard",
        use_container_width=True
    )

    st.button(
        "➕ New Job",
        use_container_width=True
    )

    st.button(
        "📋 Job Records",
        use_container_width=True
    )

    st.button(
        "📊 Reports",
        use_container_width=True
    )

    st.divider()

    st.caption("Engineering Estimation System")
    st.caption("FYP Prototype • 2026")


# =========================================================
# MAIN DASHBOARD
# =========================================================

st.title("Maintenance Engineering Estimator")

st.write(
    "Industrial Maintenance Job Planning & "
    "Engineering Quantity Estimation"
)

st.divider()


# =========================================================
# =========================================================
# DASHBOARD SUMMARY
# =========================================================

st.subheader("Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Jobs",
        value="0"
    )

with col2:
    st.metric(
        label="Draft Jobs",
        value="0"
    )

with col3:
    st.metric(
        label="Completed Jobs",
        value="0"
    )

with col4:
    st.metric(
        label="Work Types",
        value="3"
    )
# =========================================================
# NEW JOB
# =========================================================

st.write("")
st.subheader("Start New Estimation")

left, right = st.columns([3, 1])

with left:

    with st.container(border=True):

        st.subheader("🔧 Engineering Job Estimation")

        st.write(
            "Create a new industrial maintenance job and "
            "calculate engineering work quantities based "
            "on site measurements."
        )

        st.write("**Current Work Modules**")

        st.write("🎨 Pipe Painting / Coating")
        st.write("🧱 Pipe Insulation")
        st.write("🔄 Insulation Replacement")


with right:

    st.write("")
    st.write("")

    new_job = st.button(
        "➕ CREATE NEW JOB",
        type="primary",
        use_container_width=True
    )
# =========================================================
# RECENT JOBS
# =========================================================

st.write("")
st.subheader("Recent Jobs")

st.info(
    "No job records available. "
    "Create your first maintenance estimation job."
)