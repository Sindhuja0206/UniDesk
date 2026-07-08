import sqlite3
import pandas as pd
import os

DB_PATH = "./data/chat_history.db"
EXCEL_PATH = "./data/students.xlsx"
SUBJECTS = ["ANN", "OOSE", "Deep Learning"]


def init_marks_table():
    """Create the marks table if it doesn't exist."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            roll_no    INTEGER PRIMARY KEY,
            name       TEXT NOT NULL,
            ann        REAL,
            oose       REAL,
            deep_learning REAL,
            attendance REAL
        )
    """)
    conn.commit()
    conn.close()


def load_excel_to_db(excel_path: str = EXCEL_PATH):
    """Read the students.xlsx file and load it into the SQLite marks table."""
    if not os.path.exists(excel_path):
        return f"❌ Excel file not found at {excel_path}"

    df = pd.read_excel(excel_path, sheet_name="Marks")
    # Drop the "Class Average" summary row (it has no Roll No)
    df = df.dropna(subset=["Roll No"])

    init_marks_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM marks")  # refresh on each load

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO marks (roll_no, name, ann, oose, deep_learning, attendance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            int(row["Roll No"]),
            row["Name"],
            float(row["ANN"]),
            float(row["OOSE"]),
            float(row["Deep Learning"]),
            float(row["Attendance (%)"])
        ))

    conn.commit()
    count = cursor.execute("SELECT COUNT(*) FROM marks").fetchone()[0]
    conn.close()
    return f"✅ Loaded {count} student records into the database."


def get_all_students() -> pd.DataFrame:
    """Return all students with computed total/average via SQL."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT
            roll_no AS "Roll No",
            name AS "Name",
            ann AS "ANN",
            oose AS "OOSE",
            deep_learning AS "Deep Learning",
            (ann + oose + deep_learning) AS "Total",
            ROUND((ann + oose + deep_learning) / 3.0, 2) AS "Average",
            attendance AS "Attendance (%)",
            CASE WHEN attendance >= 75 THEN 'Good Standing' ELSE 'Low Attendance' END AS "Status"
        FROM marks
        ORDER BY roll_no
    """, conn)
    conn.close()
    return df


def get_student_by_roll(roll_no: int) -> dict:
    """Return one student's full record + average via SQL."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            roll_no, name, ann, oose, deep_learning,
            (ann + oose + deep_learning) AS total,
            ROUND((ann + oose + deep_learning) / 3.0, 2) AS average,
            attendance
        FROM marks
        WHERE roll_no = ?
    """, (roll_no,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "roll_no": row[0],
        "name": row[1],
        "ann": row[2],
        "oose": row[3],
        "deep_learning": row[4],
        "total": row[5],
        "average": row[6],
        "attendance": row[7],
        "status": "Good Standing" if row[7] >= 75 else "Low Attendance"
    }


def get_student_rank(roll_no: int) -> dict:
    """Return a student's rank in class based on average marks, via SQL window-style ranking."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT
            roll_no,
            name,
            ROUND((ann + oose + deep_learning) / 3.0, 2) AS average
        FROM marks
        ORDER BY average DESC
    """, conn)
    conn.close()

    df["rank"] = df["average"].rank(method="min", ascending=False).astype(int)
    total = len(df)
    row = df[df["roll_no"] == roll_no]

    if row.empty:
        return None

    return {
        "rank": int(row["rank"].values[0]),
        "total_students": total
    }


def get_class_summary() -> dict:
    """Class-wide stats via SQL aggregate functions."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) AS total_students,
            ROUND(AVG(ann), 2) AS avg_ann,
            ROUND(AVG(oose), 2) AS avg_oose,
            ROUND(AVG(deep_learning), 2) AS avg_dl,
            ROUND(AVG((ann + oose + deep_learning) / 3.0), 2) AS class_average,
            ROUND(AVG(attendance), 2) AS avg_attendance,
            SUM(CASE WHEN attendance < 75 THEN 1 ELSE 0 END) AS low_attendance_count
        FROM marks
    """)
    row = cursor.fetchone()
    conn.close()

    return {
        "total_students": row[0],
        "avg_ann": row[1],
        "avg_oose": row[2],
        "avg_deep_learning": row[3],
        "class_average": row[4],
        "avg_attendance": row[5],
        "low_attendance_count": row[6]
    }


def get_top_students(n: int = 3) -> pd.DataFrame:
    """Top N students by average marks, via SQL ORDER BY + LIMIT."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT
            name AS "Name",
            roll_no AS "Roll No",
            ROUND((ann + oose + deep_learning) / 3.0, 2) AS "Average"
        FROM marks
        ORDER BY "Average" DESC
        LIMIT ?
    """, conn, params=(n,))
    conn.close()
    return df


def get_student_by_name(name: str) -> dict:
    """Return one student's full record + average via SQL, looked up by name (case-insensitive)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            roll_no, name, ann, oose, deep_learning,
            (ann + oose + deep_learning) AS total,
            ROUND((ann + oose + deep_learning) / 3.0, 2) AS average,
            attendance
        FROM marks
        WHERE LOWER(name) = LOWER(?)
    """, (name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "roll_no": row[0],
        "name": row[1],
        "ann": row[2],
        "oose": row[3],
        "deep_learning": row[4],
        "total": row[5],
        "average": row[6],
        "attendance": row[7],
        "status": "Good Standing" if row[7] >= 75 else "Low Attendance"
    }


def get_low_attendance_students(threshold: int = 75) -> pd.DataFrame:
    """Students below attendance threshold, via SQL WHERE clause."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT
            roll_no AS "Roll No",
            name AS "Name",
            attendance AS "Attendance (%)"
        FROM marks
        WHERE attendance < ?
        ORDER BY attendance ASC
    """, conn, params=(threshold,))
    conn.close()
    return df