import streamlit as st
import sqlite3
import os
from faker import Faker

fake = Faker()

# Datafolder (If you want another, just change the name)
DB_DIR = "databases"

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

st.title("Database Builder")

# Creating Tabs
tab1, tab2, tab3 = st.tabs(["📁 Create Database", "🎲 Add Random Data", "See your databases"])

# Tab1 - To create a Database
with tab1:

    st.header("Create Your Database")

    # Initialize column storage
    if "columns" not in st.session_state:
        st.session_state.columns = []

    # Database name and table name
    database_name = st.text_input("Database name (without extension)")
    table_name = st.text_input("Table name")

    TYPES = ["TEXT", "INTEGER", "REAL", "BLOB"]

    st.subheader("Columns")

    # Add column button
    if st.button("➕ Add Column"):
        st.session_state.columns.append({"name": "", "type": "TEXT"})

    remove_list = []
    # Add every column and type of this columns
    for i, col in enumerate(st.session_state.columns):

        with st.container():
            c1, c2, c3 = st.columns([4, 3, 1])

            with c1:
                st.session_state.columns[i]["name"] = st.text_input(
                    f"Column {i+1} name", value=col["name"], key=f"name_{i}"
                )

            with c2:
                st.session_state.columns[i]["type"] = st.selectbox(
                    f"Column {i+1} type",
                    TYPES,
                    index=TYPES.index(col["type"]),
                    key=f"type_{i}"
                )

            with c3:
                if st.button("❌", key=f"delete_{i}"):
                    remove_list.append(i)

    for idx in sorted(remove_list, reverse=True):
        del st.session_state.columns[idx]

    # Create DB button
    if st.button("Create Database"):
        if not database_name or not table_name:
            st.error("Please enter a database and table name.")
        elif len(st.session_state.columns) == 0:
            st.error("At least one column is required.")
        else:
            try:
                db_path = os.path.join(DB_DIR, f"{database_name}.db")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                col_sql = ", ".join(
                    [f"{col['name']} {col['type']}" for col in st.session_state.columns]
                )

                sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {col_sql}
                );
                """

                cursor.execute(sql)
                conn.commit()
                conn.close()

                st.success(f"Database created successfully at: {db_path}")

            except Exception as e:
                st.error(str(e))

# Tab2 - Add random Data to your Database
with tab2:
    st.header("Add Random Data to Your Database")

    db_files = [f for f in os.listdir(DB_DIR) if f.endswith(".db")]

    if len(db_files) == 0:
        st.warning("No databases found. Create one in the first tab.")
    else:
        db_choice = st.selectbox("Select a database", db_files)
        db_path = os.path.join(DB_DIR, db_choice)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]

        if len(tables) == 0:
            st.warning("This database has no tables.")
        else:
            table_choice = st.selectbox("Select a table", tables)

            # Fetch column info
            cursor.execute(f"PRAGMA table_info({table_choice})")
            table_info = cursor.fetchall()

            # All columns except "id"
            columns = [(col[1], col[2]) for col in table_info if col[1] != "id"]

            st.subheader("Table Columns and Types")
            for name, col_type in columns:
                st.write(f"**{name}** → `{col_type}`")

            st.markdown("---")

            # Amount of rows to generate
            num_rows = st.number_input(
                "Number of random rows to insert",
                min_value=1,
                max_value=100000,
                step=1
            )

            def generate_based_on_type(sql_type, name):
                """Generates faker data depending on column SQL type."""
                sql_type = sql_type.upper()

                # Try guessing by COLUMN NAME first
                n = name.lower()
                if "email" in n:
                    return fake.email()
                if "phone" in n:
                    return fake.phone_number()
                if "name" in n:
                    return fake.name()
                if "address" in n:
                    return fake.address().replace("\n", ", ")
                if "city" in n:
                    return fake.city()
                if "state" in n:
                    return fake.state()
                if "country" in n:
                    return fake.country()
                if "url" in n or "site" in n:
                    return fake.url()
                if "username" in n:
                    return fake.user_name()
                if "password" in n:
                    return fake.password()

                # If not guessed, fallback to SQL TYPE:
                if sql_type == "TEXT":
                    return fake.word()
                if sql_type == "INTEGER":
                    return fake.random_int(min=0, max=99999)
                if sql_type == "REAL":
                    return fake.pyfloat(left_digits=3, right_digits=2)
                if sql_type == "BLOB":
                    return os.urandom(8)  # simple binary dummy data

                return fake.word()

            # Insert button
            if st.button("Insert Random Data"):
                try:
                    col_names = [name for name, _ in columns]
                    placeholders = ", ".join(["?"] * len(col_names))
                    sql = f"INSERT INTO {table_choice} ({', '.join(col_names)}) VALUES ({placeholders})"

                    data = []
                    for _ in range(num_rows):
                        row = [
                            generate_based_on_type(col_type, col_name)
                            for col_name, col_type in columns
                        ]
                        data.append(row)

                    cursor.executemany(sql, data)
                    conn.commit()

                    st.success(f"Inserted {num_rows} random rows into {table_choice}")

                except Exception as e:
                    st.error(str(e))

        conn.close()

# Tab3 - View And edit your data
with tab3:

    st.header("View & Edit Databases")

    db_files = [f for f in os.listdir(DB_DIR) if f.endswith(".db")]

    if len(db_files) == 0:
        st.warning("No databases found.")
    else:
        db_choice = st.selectbox("Select a database", db_files, key="view_db")
        db_path = os.path.join(DB_DIR, db_choice)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]

        if len(tables) == 0:
            st.warning("This database has no tables.")
        else:
            table_choice = st.selectbox("Select a table", tables, key="view_table")

            # Load table data properly into DataFrame
            import pandas as pd

            df = pd.read_sql_query(f"SELECT * FROM {table_choice}", conn)

            st.subheader("Edit Table")
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                width='stretch',
                key="editor_live"
            )

            # SAVE CHANGES
            if st.button("Save Changes to Database"):
                try:
                    cursor.execute(f"DELETE FROM {table_choice}")
                    conn.commit()

                    # Insert edited data
                    edited_df.to_sql(table_choice, conn, if_exists='append', index=False)

                    st.success("Changes saved successfully!")

                except Exception as e:
                    st.error(str(e))

            # DELETE A ROW BY ID
            st.subheader("Delete a Row by ID")
            row_id_to_delete = st.number_input("Enter ID", min_value=1, step=1)

            if st.button("Delete Row"):
                try:
                    cursor.execute(f"DELETE FROM {table_choice} WHERE id = ?", (row_id_to_delete,))
                    conn.commit()
                    st.success(f"Row {row_id_to_delete} deleted!")
                except Exception as e:
                    st.error(str(e))

            conn.close()
