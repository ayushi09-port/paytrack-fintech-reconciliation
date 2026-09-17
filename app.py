import sqlite3
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Import database functions from database.py
from database import (
    add_transaction,
    delete_transaction,
    get_db_connection,
    init_db,
    update_transaction,
)

# Initialize database schema
init_db()

# --- STREAMLIT UI CONFIG ---
st.set_page_config(
    page_title="PayTrack - QR Payment Reconciliation", layout="wide"
)

st.title("💳 PayTrack")
st.caption(
    "QR Payment Record & Reconciliation System | Blackbucks-NASSCOM FinTech Project"
)

# --- FLASH MESSAGE HANDLER ---
if "flash_success" in st.session_state:
    st.success(st.session_state["flash_success"])
    del st.session_state["flash_success"]

# --- SIDEBAR: NEW TRANSACTION ENTRY ---
st.sidebar.header("📥 Record New Transaction")
with st.sidebar.form("add_transaction_form", clear_on_submit=True):
    reference_id = st.text_input("Reference ID (Payment Ref Number)*").strip()
    amount = st.number_input("Amount (₹)*", min_value=0.01, step=1.0)
    payment_method = st.selectbox(
        "Payment Method*",
        ["Google Pay", "PhonePe", "Paytm", "BHIM / Other QR"],
    )
    status = st.selectbox("Status*", ["Pending", "Verified", "Mismatched"])
    customer_name = st.text_input("Customer Name / Identifier")
    order_id = st.text_input("Order ID / Service Ref")
    trans_date = st.date_input("Date", value=date.today())
    trans_time = st.time_input("Time", value=datetime.now().time())
    notes = st.text_area("Notes", placeholder="Additional details...")

    submitted = st.form_submit_button("Save Transaction")

    if submitted:
        if not reference_id:
            st.error("Reference ID is required.")
        else:
            try:
                add_transaction(
                    reference_id,
                    amount,
                    payment_method,
                    trans_date.strftime("%Y-%m-%d"),
                    trans_time.strftime("%H:%M:%S"),
                    customer_name,
                    order_id,
                    status,
                    notes,
                )
                st.session_state["flash_success"] = (
                    f"✅ Transaction '{reference_id}' recorded successfully!"
                )
                st.rerun()
            except sqlite3.IntegrityError:
                st.error(
                    f"⚠️ Duplicate Entry Detected! Reference ID '{reference_id}' already exists."
                )

# --- TABS DEFINITION ---
tab1, tab2, tab3 = st.tabs(
    [
        "📊 Reconciliation Dashboard",
        "🔍 Search & Audit Ledger",
        "📈 Visualizations & Analytics",
    ]
)

# DATA RETRIEVAL
conn = get_db_connection()
df = pd.read_sql_query(
    "SELECT * FROM transactions ORDER BY transaction_id DESC", conn
)
conn.close()

# --- TAB 1: SUMMARY & RECONCILIATION ---
with tab1:
    st.subheader("Daily Collection Summary")

    if df.empty:
        st.info("No records found. Add your first transaction in the sidebar.")
    else:
        selected_summary_date = st.date_input(
            "Select Summary Date", value=date.today()
        )
        selected_str = selected_summary_date.strftime("%Y-%m-%d")
        daily_df = df[df["date"] == selected_str]

        col1, col2, col3, col4 = st.columns(4)
        total_collected = daily_df[daily_df["status"] == "Verified"][
            "amount"
        ].sum()
        total_count = len(daily_df)
        pending_count = len(daily_df[daily_df["status"] == "Pending"])
        mismatched_count = len(daily_df[daily_df["status"] == "Mismatched"])

        col1.metric("Verified Collections", f"₹{total_collected:,.2f}")
        col2.metric("Total Today's Entries", total_count)
        col3.metric("Pending Verification", pending_count)
        col4.metric("Mismatched Entries", mismatched_count)

        st.markdown("---")
        st.write(f"**Records for {selected_str}:**")
        st.dataframe(
            daily_df[
                [
                    "transaction_id",
                    "reference_id",
                    "date",
                    "time",
                    "amount",
                    "payment_method",
                    "customer_name",
                    "order_id",
                    "status",
                    "notes",
                ]
            ],
            use_container_width=True,
        )

# --- TAB 2: SEARCH, FILTER & LEDGER MANAGEMENT ---
with tab2:
    st.subheader("Search & Audit Ledger")

    if df.empty:
        st.info("No records found.")
    else:
        col_search, col_status = st.columns([2, 1])

        with col_search:
            search_query = st.text_input(
                "Search by Ref ID, Customer Name, or Order ID:"
            ).lower()

        with col_status:
            status_filter = st.multiselect(
                "Filter by Status:",
                options=["Pending", "Verified", "Mismatched"],
                default=["Pending", "Verified", "Mismatched"],
            )

        filtered_df = df.copy()

        if search_query:
            filtered_df = filtered_df[
                filtered_df["reference_id"]
                .astype(str)
                .str.lower()
                .str.contains(search_query)
                | filtered_df["customer_name"]
                .fillna("")
                .str.lower()
                .str.contains(search_query)
                | filtered_df["order_id"]
                .fillna("")
                .str.lower()
                .str.contains(search_query)
            ]

        if status_filter:
            filtered_df = filtered_df[
                filtered_df["status"].isin(status_filter)
            ]

        st.write(f"Showing **{len(filtered_df)}** matching transaction(s):")
        st.dataframe(
            filtered_df[
                [
                    "transaction_id",
                    "reference_id",
                    "date",
                    "time",
                    "amount",
                    "payment_method",
                    "customer_name",
                    "order_id",
                    "status",
                    "notes",
                ]
            ],
            use_container_width=True,
        )

        st.markdown("---")
        st.subheader("🛠️ Manage Existing Entry")

        selected_ref = st.selectbox(
            "Select Reference ID to Modify or Delete:",
            options=df["reference_id"].unique(),
            key="selected_ref_selector",
        )

        selected_row = df[df["reference_id"] == selected_ref].iloc[0]

        manage_action = st.radio(
            "Select Action:", ["Update Entry", "Delete Entry"], horizontal=True
        )

        if manage_action == "Update Entry":
            with st.form("edit_transaction_form"):
                col_e1, col_e2, col_e3 = st.columns(3)

                with col_e1:
                    new_amount = st.number_input(
                        "Amount (₹)",
                        min_value=0.01,
                        value=float(selected_row["amount"]),
                        step=1.0,
                    )
                    new_method = st.selectbox(
                        "Payment Method",
                        ["Google Pay", "PhonePe", "Paytm", "BHIM / Other QR"],
                        index=[
                            "Google Pay",
                            "PhonePe",
                            "Paytm",
                            "BHIM / Other QR",
                        ].index(selected_row["payment_method"]),
                    )

                with col_e2:
                    new_status = st.selectbox(
                        "Status",
                        ["Pending", "Verified", "Mismatched"],
                        index=["Pending", "Verified", "Mismatched"].index(
                            selected_row["status"]
                        ),
                    )
                    new_customer = st.text_input(
                        "Customer Name",
                        value=selected_row["customer_name"] or "",
                    )

                with col_e3:
                    new_order = st.text_input(
                        "Order ID", value=selected_row["order_id"] or ""
                    )
                    new_notes = st.text_area(
                        "Notes", value=selected_row["notes"] or ""
                    )

                update_btn = st.form_submit_button("Save Changes")

                if update_btn:
                    update_transaction(
                        selected_ref,
                        new_amount,
                        new_method,
                        new_status,
                        new_customer,
                        new_order,
                        new_notes,
                    )
                    st.session_state["flash_success"] = (
                        f"✅ Transaction '{selected_ref}' updated successfully!"
                    )
                    st.rerun()

        elif manage_action == "Delete Entry":
            st.warning(
                f"⚠️ Are you sure you want to delete transaction **'{selected_ref}'**? This action cannot be undone."
            )
            if st.button("Confirm Delete", type="primary"):
                delete_transaction(selected_ref)
                st.session_state["flash_success"] = (
                    f"🗑️ Transaction '{selected_ref}' deleted successfully!"
                )
                st.rerun()

# --- TAB 3: VISUALIZATIONS & ANALYTICS ---
with tab3:
    st.subheader("📊 Payment Analytics & Trends")

    if df.empty:
        st.info("No transaction data available for visualization.")
    else:
        # Date Filter Controls
        df["date_dt"] = pd.to_datetime(df["date"])
        min_db_date = df["date_dt"].min().date()
        max_db_date = df["date_dt"].max().date()

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input(
                "Filter From Date",
                value=min_db_date,
                min_value=min_db_date,
                max_value=max_db_date,
            )
        with col_d2:
            end_date = st.date_input(
                "Filter To Date",
                value=max_db_date,
                min_value=min_db_date,
                max_value=max_db_date,
            )

        # Filtered DataFrame
        mask = (df["date_dt"].dt.date >= start_date) & (
            df["date_dt"].dt.date <= end_date
        )
        analytics_df = df[mask]

        if analytics_df.empty:
            st.warning("No records match the selected date range.")
        else:
            # 1. Daily Total Collections (Line Chart)
            st.markdown("### 1. Total Daily Collections Trend (₹)")
            daily_trend = (
                analytics_df[analytics_df["status"] == "Verified"]
                .groupby("date")["amount"]
                .sum()
                .reset_index()
            )

            if daily_trend.empty:
                st.info(
                    "No verified collection data for line graph display."
                )
            else:
                fig_line = px.line(
                    daily_trend,
                    x="date",
                    y="amount",
                    markers=True,
                    labels={"date": "Date", "amount": "Verified Amount (₹)"},
                    title="Daily Revenue Trend (Verified Transactions)",
                )
                st.plotly_chart(fig_line, use_container_width=True)

            col_c1, col_c2 = st.columns(2)

            # 2. UPI Platform Distribution (Pie Chart)
            with col_c1:
                st.markdown("### 2. Payment Gateway Distribution")
                method_dist = (
                    analytics_df.groupby("payment_method")["amount"]
                    .sum()
                    .reset_index()
                )
                fig_pie = px.pie(
                    method_dist,
                    values="amount",
                    names="payment_method",
                    hole=0.4,
                    title="Revenue Share by UPI App",
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # 3. Status Breakdown (Bar Chart)
            with col_c2:
                st.markdown("### 3. Transaction Status Breakdown")
                status_dist = analytics_df["status"].value_counts().reset_index()
                status_dist.columns = ["status", "count"]
                fig_bar = px.bar(
                    status_dist,
                    x="status",
                    y="count",
                    color="status",
                    labels={"status": "Status", "count": "Transaction Count"},
                    title="Record Volume by Reconciliation Status",
                )
                st.plotly_chart(fig_bar, use_container_width=True)
