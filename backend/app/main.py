from __future__ import annotations
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .database import engine
from .schemas import EnrollmentCreate

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CourseHub API",
    version="0.5.0",
    description="API thuc hanh Buoi 4 & 5 - CourseHub fullstack",
)

# Cau hinh CORS cho phep React Frontend goi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to CourseHub API"}

@app.get("/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection error")

@app.get("/courses")
def get_courses():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT code, name, credits FROM courses ORDER BY code;"))
        return [dict(row._mapping) for row in result]

@app.get("/sections")
def get_sections():
    query = """
        SELECT class_id, course_code, capacity, enrolled, remaining
        FROM v_section_summary
        ORDER BY class_id;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return [dict(row._mapping) for row in result]

@app.get("/students/{student_id}/enrollments")
def get_student_enrollments(student_id: str):
    query = """
        SELECT e.class_section_id, cs.course_code, c.name AS course_name, e.enrolled_at
        FROM enrollments e
        JOIN class_sections cs ON e.class_section_id = cs.id
        JOIN courses c ON cs.course_code = c.code
        WHERE e.student_id = :student_id
        ORDER BY e.class_section_id;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), {"student_id": student_id})
        return [dict(row._mapping) for row in result]

@app.post("/enrollments", status_code=status.HTTP_201_CREATED)
def create_enrollment(data: EnrollmentCreate):
    with engine.begin() as conn:
        student_check = conn.execute(
            text("SELECT id FROM students WHERE id = :sid"),
            {"sid": data.student_id}
        ).fetchone()
        if not student_check:
            raise HTTPException(status_code=404, detail="Student not found")

        section = conn.execute(
            text("""
                SELECT id, capacity, enrolled 
                FROM class_sections 
                WHERE id = :cid 
                FOR UPDATE
            """),
            {"cid": data.class_section_id}
        ).fetchone()
        if not section:
            raise HTTPException(status_code=404, detail="Class section not found")

        if section.enrolled >= section.capacity:
            raise HTTPException(status_code=409, detail="Lop hoc phan da het cho")

        existing = conn.execute(
            text("""
                SELECT 1 FROM enrollments 
                WHERE student_id = :sid AND class_section_id = :cid
            """),
            {"sid": data.student_id, "cid": data.class_section_id}
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Sinh vien da dang ky lop nay")

        conn.execute(
            text("""
                INSERT INTO enrollments (student_id, class_section_id)
                VALUES (:sid, :cid)
            """),
            {"sid": data.student_id, "cid": data.class_section_id}
        )

        conn.execute(
            text("""
                UPDATE class_sections 
                SET enrolled = enrolled + 1 
                WHERE id = :cid
            """),
            {"cid": data.class_section_id}
        )

        conn.execute(
            text("""
                INSERT INTO enrollment_events (student_id, class_section_id, event_type, dataset)
                VALUES (:sid, :cid, 'CREATED', 'demo')
            """),
            {"sid": data.student_id, "cid": data.class_section_id}
        )

    return {"message": "Enrollment successful"}

@app.delete("/enrollments/{student_id}/{class_section_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_enrollment(student_id: str, class_section_id: str):
    with engine.begin() as conn:
        conn.execute(
            text("SELECT id FROM class_sections WHERE id = :cid FOR UPDATE"),
            {"cid": class_section_id}
        )

        existing = conn.execute(
            text("""
                SELECT 1 FROM enrollments 
                WHERE student_id = :sid AND class_section_id = :cid
            """),
            {"sid": student_id, "cid": class_section_id}
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        conn.execute(
            text("""
                DELETE FROM enrollments 
                WHERE student_id = :sid AND class_section_id = :cid
            """),
            {"sid": student_id, "cid": class_section_id}
        )

        conn.execute(
            text("""
                UPDATE class_sections 
                SET enrolled = GREATEST(0, enrolled - 1) 
                WHERE id = :cid
            """),
            {"cid": class_section_id}
        )

        conn.execute(
            text("""
                INSERT INTO enrollment_events (student_id, class_section_id, event_type, dataset)
                VALUES (:sid, :cid, 'CANCELLED', 'demo')
            """),
            {"sid": student_id, "cid": class_section_id}
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- TU THUC HANH BUOI 4 & 5 ---
@app.get("/enrollment-events", tags=["enrollment-events"])
def get_enrollment_events(
    student_id: Optional[str] = Query(None, description="Loc theo ma sinh vien"),
    event_type: Optional[str] = Query(None, description="Loc theo loai su kien"),
    skip: int = Query(0, ge=0, description="So ban ghi bo qua"),
    limit: int = Query(20, ge=1, le=100, description="So ban ghi toi da"),
):
    query = """
        SELECT id, student_id, class_section_id, event_type, occurred_at, dataset
        FROM enrollment_events
        WHERE 1=1
    """
    params = {"skip": skip, "limit": limit}

    if student_id:
        query += " AND student_id = :student_id"
        params["student_id"] = student_id
    if event_type:
        query += " AND event_type = :event_type"
        params["event_type"] = event_type

    query += " ORDER BY occurred_at DESC, id DESC LIMIT :limit OFFSET :skip;"

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            return [dict(row._mapping) for row in result]
    except SQLAlchemyError as err:
        logger.error(f"Loi truy van enrollment_events: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Loi he thong khi lay nhat ky dang ky",
        )

@app.post("/demo/test-rollback-fail", tags=["demo"])
def test_rollback_fail(data: EnrollmentCreate):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO enrollments (student_id, class_section_id) VALUES (:sid, :cid)"),
            {"sid": data.student_id, "cid": data.class_section_id}
        )
        # Co y vi pham CHECK constraint de rollback
        conn.execute(
            text("INSERT INTO enrollment_events (student_id, class_section_id, event_type, dataset) VALUES (:sid, :cid, 'INVALID_TYPE', 'demo')"),
            {"sid": data.student_id, "cid": data.class_section_id}
        )
    return {"message": "Success"}