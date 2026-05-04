"""
Seed Script — Creates default teacher account and sample data for testing.

Usage:
  cd backend
  python seed.py

This will create:
  1. A teacher account (teacher@ams.edu / teacher123)
  2. A teacher profile
  3. Sample subjects
  4. A student account (student@ams.edu / student123)
  5. Sample attendance records
"""

import os
import sys
from datetime import date, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from app.database import SessionLocal, engine, Base
from app.models import User, UserRole, TeacherProfile, Subject, Attendance, AttendanceStatus, Feedback
from app.auth import hash_password


def seed():
    """Insert seed data into the database."""

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ── CHECK IF ALREADY SEEDED ──
        existing_teacher = db.query(User).filter(User.email == "teacher@ams.edu").first()
        if existing_teacher:
            print("⚠️  Seed data already exists. Skipping...")
            print(f"   Teacher: teacher@ams.edu / teacher123")
            existing_student = db.query(User).filter(User.email == "student@ams.edu").first()
            if existing_student:
                print(f"   Student: student@ams.edu / student123")
            return

        print("🌱 Seeding database...")

        # ── 1. CREATE TEACHER ──
        teacher = User(
            name="Mr. Ali Hassan",
            email="teacher@ams.edu",
            password_hash=hash_password("teacher123"),
            role=UserRole.teacher,
            semester=6,
            department="Computer Science",
        )
        db.add(teacher)
        db.flush()  # Get teacher.id

        # ── 2. CREATE TEACHER PROFILE ──
        teacher_profile = TeacherProfile(
            user_id=teacher.id,
            subject="Data Structures",
            class_name="BS-CS",
            profile_complete=True,
        )
        db.add(teacher_profile)

        print(f"   ✓ Teacher created: {teacher.email} (password: teacher123)")

        # ── 3. CREATE STUDENT ──
        student = User(
            name="Ayesha Siddiqui",
            email="student@ams.edu",
            password_hash=hash_password("student123"),
            role=UserRole.student,
            semester=6,
            department="Computer Science",
        )
        db.add(student)
        db.flush()

        # Additional students
        students_data = [
            ("Bilal Ahmed", "bilal@student.edu", "Software Engineering"),
            ("Fatima Malik", "fatima@student.edu", "Computer Science"),
            ("Hassan Raza", "hassan@student.edu", "Information Technology"),
            ("Zainab Qureshi", "zainab@student.edu", "Computer Science"),
            ("Omar Farooq", "omar@student.edu", "Computer Science"),
        ]

        all_students = [student]
        for name, email, dept in students_data:
            s = User(
                name=name,
                email=email,
                password_hash=hash_password("student123"),
                role=UserRole.student,
                semester=6,
                department=dept,
            )
            db.add(s)
            db.flush()
            all_students.append(s)

        print(f"   ✓ {len(all_students)} students created (password: student123)")

        # ── 4. CREATE SUBJECTS ──
        subjects_data = ["Data Structures", "Database Systems", "Web Engineering", "Algorithms", "Operating Systems"]
        subjects = []
        for name in subjects_data:
            subj = Subject(
                name=name,
                teacher_id=teacher.id,
                semester=6,
            )
            db.add(subj)
            db.flush()
            subjects.append(subj)

        print(f"   ✓ {len(subjects)} subjects created")

        # ── 5. CREATE SAMPLE ATTENDANCE ──
        import random
        random.seed(42)

        today = date.today()
        attendance_count = 0

        for subj in subjects:
            # Generate dates for the past 22 days (excluding weekends)
            dates = []
            d = today - timedelta(days=30)
            while d <= today and len(dates) < 22:
                if d.weekday() < 5:  # Mon-Fri
                    dates.append(d)
                d += timedelta(days=1)

            for s in all_students:
                for d in dates:
                    # Random status with 80% present rate (varied by subject/student)
                    present_chance = random.uniform(0.35, 0.95)
                    status = AttendanceStatus.PRESENT if random.random() < present_chance else AttendanceStatus.ABSENT

                    att = Attendance(
                        student_id=s.id,
                        subject_id=subj.id,
                        teacher_id=teacher.id,
                        semester=6,
                        date=d,
                        status=status,
                    )
                    db.add(att)
                    attendance_count += 1

        print(f"   ✓ {attendance_count} attendance records created")

        # ── 6. SAMPLE FEEDBACK ──
        feedback1 = Feedback(
            student_id=student.id,
            teacher_id=teacher.id,
            rating=5,
            comment="Excellent teaching methodology. Concepts are explained clearly with great examples. Very supportive and approachable.",
        )
        db.add(feedback1)
        print(f"   ✓ 1 sample feedback created")

        # ── COMMIT ──
        db.commit()

        print("\n✅ Seed complete!")
        print("=" * 50)
        print("  🔐 Teacher Login:")
        print("     Email: teacher@ams.edu")
        print("     Password: teacher123")
        print("")
        print("  🎓 Student Login:")
        print("     Email: student@ams.edu")
        print("     Password: student123")
        print("")
        print("  📊 Sample data includes:")
        print(f"     {len(all_students)} students in Semester 6")
        print(f"     {len(subjects)} subjects")
        print(f"     {attendance_count} attendance records")
        print("=" * 50)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
