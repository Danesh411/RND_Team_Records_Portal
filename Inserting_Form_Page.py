from config import *

def insert_page():


    def convert_dates(obj):
        if isinstance(obj, dict):
            return {k: convert_dates(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_dates(elem) for elem in obj]
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        else:
            return obj

    def ensure_list_from_string(value):
        """Convert comma-separated string to list, strip spaces."""
        if isinstance(value, str):
            return [c.strip() for c in value.split(",") if c.strip()]
        elif isinstance(value, list):
            return value
        else:
            return []

    st.set_page_config(page_title="R&D Team – Site/App Completion Status", layout="wide")
    st.title("🔍 R&D Team – Site/App Completion Status")

    # Initialize session state
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}


    st.header("R&D Team Form")

    # --- Platform, User Login ---
    platform = st.text_input(
        "Platform",
        placeholder="Please enter the site name",
        value=st.session_state.form_data.get("platform", ""),
        key="platform"
    )

    is_user_login = st.checkbox(
        "Is User Login",
        value=st.session_state.form_data.get("is_user_login", False),
        key="is_user_login"
    )

    # --- Country, Feasible For, Domain, Approx Volume ---
    col1, col2 = st.columns(2)

    with col1:

        # ✅ Convert default country to list before passing to multiselect
        default_country = ensure_list_from_string(st.session_state.form_data.get("country", []))

        country = st.multiselect(
            "Country",
            options=clean_countries,
            default=default_country,
            placeholder="Select one or more countries",
            key="country"
        )

        feasible_for = st.selectbox(
            "Feasible For",
            options=platform_type_options,
            index=platform_type_options.index(
                st.session_state.form_data.get("feasible_for", "Web")
            ),
            key="feasible_for"
        )

    with col2:
        domain = st.text_input(
            "Domain",
            placeholder="https://example.com",
            value=st.session_state.form_data.get("domain", ""),
            key="domain"
        )

        approx_volume = st.number_input(
            "Approx Volume",
            min_value=0,
            value=int(st.session_state.form_data.get("approx_volume", 0)),
            step=1,
            key="approx_volume"
        )

    # --- Method ---
    method = st.selectbox(
        "Method",
        options=Request_type_option,
        index=Request_type_option.index(
            st.session_state.form_data.get("method", "Direct Request")
        ),
        key="method"
    )

    # --- Proxy Usage ---
    is_proxy_used = st.checkbox(
        "Is Proxy Used",
        value=st.session_state.form_data.get("is_proxy_used", False),
        key="is_proxy_used"
    )

    proxy_name = ""
    credits_val = 0

    if is_proxy_used:
        proxy_col1, proxy_col2 = st.columns(2)
        with proxy_col1:
            proxy_name = st.selectbox(
                "Proxy Name",
                options=proxy_options,
                index=0,
                key="proxy_name"
            )
        with proxy_col2:
            per_request_credit = st.number_input(
                "Per Request Credit",
                min_value=1,
                value=int(st.session_state.form_data.get("perrequestcredit", 1)),
                step=1,
                key="perrequestcredit"
            )

        total_req_col1, total_req_col2 = st.columns(2)
        with total_req_col1:
            total_request = st.number_input(
                "Total Request",
                min_value=1,
                value=int(st.session_state.form_data.get("totalrequest", 1)),
                step=1,
                key="totalrequest"
            )
        with total_req_col2:
            final_credit = per_request_credit * total_request
            st.text_input("Total Credit", value=str(final_credit), disabled=True)
            credits_val = final_credit
    else:
        for key in ["proxy_name", "perrequestcredit", "totalrequest"]:
            st.session_state.form_data.pop(key, None)

    # --- Complexity, GitHub, Last Checked, File Upload ---
    col3, col4 = st.columns(2)

    with col3:
        if feasible_for == "Not Checked":
            complexity = st.selectbox(
                "Complexity",
                options=["Not Checked"],
                index=0,
                disabled=True,
                key="complexity"
            )
        else:
            complexity = st.selectbox(
                "Complexity",
                options=Complexity_option,
                index=Complexity_option.index(
                    st.session_state.form_data.get("complexity", "Low")
                ),
                key="complexity"
            )

        if complexity == "Not Checked":
            github_link = st.text_input(
                "GitHub Code Link",
                value="",
                disabled=True,
                key="github_link"
            )
        else:
            github_link = st.text_input(
                "GitHub Code Link",
                placeholder="https://github.com/user/repo",
                value=st.session_state.form_data.get("github_link", ""),
                key="github_link"
            )

    with col4:
        last_checked_date = datetime.now().strftime("%Y-%m-%d")
        st.text_input("Last Checked Date", value=str(last_checked_date), disabled=True)

        sow_doc = st.file_uploader(
            "Upload SOW Document(s)",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt", "xlsx"],
            key="sow_doc"
        )
        if sow_doc:
            st.write("📁 Uploaded:", ", ".join([f.name for f in sow_doc]))

    # ========================
    # Validation & Submit
    # ========================
    st.markdown("---")

    if st.button("✅ Submit"):
        is_valid = True

        # Validate Platform
        if not platform.strip():
            st.error("❌ **Platform** is required.")
            is_valid = False

        # Validate Domain URL
        if domain.strip() and not (domain.startswith("http://") or domain.startswith("https://")):
            st.error("❌ **Domain** must start with `http://` or `https://`.")
            is_valid = False

        # Validate Country
        if not country:
            st.error("❌ **Country** selection is required.")
            is_valid = False

        # Validate GitHub link
        if github_link.strip() and ("github.com" not in github_link or not github_link.startswith("http")):
            st.error("❌ **GitHub Code Link** must be a valid GitHub URL.")
            is_valid = False

        if not is_valid:
            st.warning("⚠️ Please correct the errors above before submitting.")
        else:
            # Prepare data
            is_user_login_status = bool(is_user_login)
            unique_string = f"{is_user_login_status}-{domain}"
            unique_hashID = hashlib.sha256(unique_string.encode()).hexdigest()

            # Convert list to string for DB
            country_str = ", ".join(country) if country else ""

            submitted_data = {
                "platform": platform.strip(),
                "row_hash_Id": unique_hashID,
                "domain": domain.strip() if method != "Browser Automation" and feasible_for != "Not Checked" else "",
                "is_user_login": is_user_login_status,
                "country": country_str,
                "feasible_for": feasible_for,
                "approx_volume": int(approx_volume) if feasible_for != "Not Checked" else 0,
                "method": method if feasible_for != "Not Checked" else "",
                "is_proxy_used": 1 if (is_proxy_used and feasible_for != "Not Checked") else 0,
                "proxy_name": proxy_name if is_proxy_used and feasible_for != "Not Checked" else "",
                "credits": credits_val if is_proxy_used and feasible_for != "Not Checked" else 0,
                "complexity": complexity if feasible_for != "Not Checked" else "Not Checked",
                "last_checked_date": last_checked_date,
                "gitHub_code_link": github_link.strip() if complexity != "Not Checked" else "",
                "sow_doc": ", ".join([f.name for f in sow_doc]) if sow_doc else ""
            }

            # Save to session state (but keep country as list for UI)
            st.session_state.form_data.update({
                **submitted_data,
                "country": country,  # keep list form for UI
                "sow_doc": [f.name for f in sow_doc] if sow_doc else []
            })

            # Insert into MySQL
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()

                insert_query = """
                    INSERT INTO inserting_completion_records
                    (platform, row_hash_Id, domain, is_user_login, country, feasible_for, approx_volume, method, is_proxy_used, proxy_name, credits, complexity, last_checked_date, gitHub_code_link, sow_doc)
                    VALUES (%(platform)s, %(row_hash_Id)s, %(domain)s, %(is_user_login)s, %(country)s, %(feasible_for)s, %(approx_volume)s, %(method)s, %(is_proxy_used)s, %(proxy_name)s, %(credits)s, %(complexity)s, %(last_checked_date)s, %(gitHub_code_link)s, %(sow_doc)s)
                """

                cursor.execute(insert_query, submitted_data)
                conn.commit()
                st.success("✅ Data successfully inserted into MySQL!")
                st.toast("Submission successful! 🎉", icon="✅")

            except mysql.connector.Error as err:
                st.error(f"❌ MySQL Error: {err}")
                st.code(str(err))

            except Exception as e:
                st.error("❌ Unexpected error during submission.")
                st.exception(e)

            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals() and conn.is_connected():
                    conn.close()