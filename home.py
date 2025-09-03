from Inserting_Form_Page import *
from Editing_Form_Page import *

st.set_page_config(page_title="R&D Team Records", layout="wide")

st.title("🏠 R&D Team Records Portal")

# Sidebar navigation
menu = st.sidebar.radio(
    "Choose an option:",
    ["Insert New Record", "Edit Existing Records"]
)

if menu == "Insert New Record":
    # st.subheader("➕ Insert New Record")
    insert_page()

elif menu == "Edit Existing Records":
    # st.subheader("✏️ Edit Records")
    edit_page()
