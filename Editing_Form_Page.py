
from config import *


def edit_page():

    def get_data():
        conn = mysql.connector.connect(**DB_CONFIG)
        query = """SELECT row_hash_Id, platform, domain, is_user_login, country, feasible_for,
                          approx_volume, method, is_proxy_used, proxy_name, credits, complexity,
                          last_checked_date, gitHub_code_link, sow_doc
                   FROM inserting_completion_records"""
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def update_data(updated_df, original_df):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for _, row in updated_df.iterrows():
            if not row.equals(original_df.loc[original_df["row_hash_Id"] == row["row_hash_Id"]].iloc[0]):
                update_query = """
                    UPDATE inserting_completion_records
                    SET platform=%s, domain=%s, is_user_login=%s, country=%s, feasible_for=%s,
                        approx_volume=%s, method=%s, is_proxy_used=%s, proxy_name=%s, credits=%s,
                        complexity=%s, last_checked_date=%s, gitHub_code_link=%s, sow_doc=%s
                    WHERE row_hash_Id=%s
                """
                cursor.execute(update_query, (
                    row["platform"], row["domain"], row["is_user_login"], row["country"],
                    row["feasible_for"], row["approx_volume"], row["method"], row["is_proxy_used"],
                    row["proxy_name"], row["credits"], row["complexity"], row["last_checked_date"],
                    row["gitHub_code_link"], row["sow_doc"], row["row_hash_Id"]
                ))

        conn.commit()
        cursor.close()
        conn.close()

    # Page config
    st.set_page_config(page_title="Edit Database Records", layout="wide")
    st.title("✏️ Edit R&D Team Records")

    # Initialize session state
    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None
    if "form_data" not in st.session_state:
        st.session_state.form_data = {"perrequestcredit": 1, "totalrequest": 1}

    # ===========================
    # Edit Mode: Show Form
    # ===========================
    if st.session_state.edit_id is not None:
        df = get_data()
        record = df[df["row_hash_Id"] == st.session_state.edit_id].iloc[0]

        st.subheader(f"Editing Record — {record['platform']}")

        platform = st.text_input("Platform", record["platform"])
        domain = st.text_input("Domain", record["domain"])
        is_user_login = st.checkbox("Is User Login", bool(record["is_user_login"]))

        country = st.multiselect(
            "Country",
            options=clean_countries,  # <-- changed here
            default=[c.strip() for c in record["country"].split(",") if c.strip() in clean_countries]
        )

        # feasible_for = st.text_input("Feasible For", record["feasible_for"])
        feasible_for = st.selectbox("Feasible For",
                                    options=platform_type_options,
                                    index=platform_type_options.index(record["feasible_for"].strip())
                                    if record["feasible_for"] and record["feasible_for"].strip() in proxy_options
                                    else 0
                                    )


        approx_volume = st.number_input("Approx Volume", value=int(record["approx_volume"]))

        method = st.selectbox("Method",
                              options=Request_type_option,
                              index=Request_type_option.index(record["method"].strip())
                              if record["method"] and record["method"].strip() in proxy_options
                              else 0
                              )

        is_proxy_used = st.checkbox("Is Proxy Used", bool(record["is_proxy_used"]))

        proxy_name = st.selectbox(
            "Proxy Name",
            options=proxy_options,
            index=proxy_options.index(record["proxy_name"].strip())
            if record["proxy_name"] and record["proxy_name"].strip() in proxy_options
            else 0
        )

        per_request_credit = st.number_input(
            "Per Request Credit",
            min_value=1,
            value=int(st.session_state.form_data.get("perrequestcredit", 1)),
            step=1,
            key="perrequestcredit"
        )
        st.session_state.form_data["perrequestcredit"] = per_request_credit

        total_request = st.number_input(
            "Total Request",
            min_value=1,
            value=int(st.session_state.form_data.get("totalrequest", 1)),
            step=1,
            key="totalrequest"
        )
        st.session_state.form_data["totalrequest"] = total_request

        final_credit = per_request_credit * total_request
        credits = st.text_input("Credits", str(final_credit), disabled=True)

        complexity = st.text_input("Complexity", record["complexity"])
        complexity = st.selectbox("Complexity",
                                  options=Complexity_option,
                                  index=Complexity_option.index(record["complexity"].strip())
                                  if record["complexity"] and record["complexity"].strip() in proxy_options
                                  else 0)

        last_checked_date_check = datetime.now().strftime("%Y-%m-%d")
        last_checked_date = st.text_input("Last Checked Date", value=str(last_checked_date_check), disabled=True)
        gitHub_code_link = st.text_input("GitHub Code Link", record["gitHub_code_link"])
        sow_doc = st.text_input("SOW Doc", record["sow_doc"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Update Record"):
                updated_record = pd.DataFrame([{
                    "row_hash_Id": record["row_hash_Id"],
                    "platform": platform,
                    "domain": domain,
                    "is_user_login": int(is_user_login),
                    "country": ",".join(country),  # <-- FIX HERE
                    "feasible_for": feasible_for,
                    "approx_volume": approx_volume,
                    "method": method,
                    "is_proxy_used": int(is_proxy_used),
                    "proxy_name": proxy_name,
                    "credits": credits,
                    "complexity": complexity,
                    "last_checked_date": last_checked_date,
                    "gitHub_code_link": gitHub_code_link,
                    "sow_doc": sow_doc
                }])

                update_data(updated_record, df)
                st.success("✅ Record updated successfully!")
                st.session_state.edit_id = None
                st.rerun()

        with col2:
            if st.button("⬅ Back"):
                st.session_state.edit_id = None
                st.rerun()

    # ===========================
    # View Mode: Table Format using st.data_editor
    # ===========================
    else:
        df_original = get_data()

        # Search
        search_term = st.text_input("🔍 Search", placeholder="Filter records...")
        if search_term:
            df_filtered = df_original[df_original.apply(
                lambda row: row.astype(str).str.contains(search_term, case=False).any(),
                axis=1
            )]
        else:
            df_filtered = df_original.copy()

        if df_filtered.empty:
            st.info("No matching records found.")
        else:
            # Add a "Modify" column (checkbox) for selection
            df_display = df_filtered.copy()
            df_display["Modify"] = False  # Will be used as checkbox

            # Reorder: Move 'Modify' to front
            cols = ["Modify"] + [col for col in df_display.columns if col != "Modify" and col != "row_hash_Id"] + ["row_hash_Id"]
            df_display = df_display[cols]

            # Hide sensitive or unnecessary columns
            hide_cols = ["row_hash_Id", "gitHub_code_link", "sow_doc", "credits", "method", "proxy_name", "complexity"]
            hide_cols = [col for col in hide_cols if col in df_display.columns]

            # Display editable table with checkbox
            edited_df = st.data_editor(
                df_display,
                hide_index=True,
                column_config={
                    "Modify": st.column_config.CheckboxColumn("Modify", help="Check to edit this row"),
                    **{col: st.column_config.Column(width="medium", required=False) for col in df_display.columns}
                },
                disabled=["platform", "domain", "is_user_login", "country", "feasible_for",
                          "approx_volume", "method", "is_proxy_used", "proxy_name",
                          "credits", "complexity", "last_checked_date",
                          "gitHub_code_link", "sow_doc"],  # disable only data cols
                key="data_editor"
            )

            # Check if user checked any "Modify" box
            modified_rows = edited_df[edited_df["Modify"]]

            if not modified_rows.empty:
                if st.button("✏️ Edit Selected Record", type="primary"):
                    # Only allow editing one row at a time
                    selected_id = modified_rows.iloc[0]["row_hash_Id"]
                    st.session_state.edit_id = selected_id
                    st.rerun()