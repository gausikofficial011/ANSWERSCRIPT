from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

def create_alice_pdf(filepath: Path):
    c = canvas.Canvas(str(filepath), pagesize=letter)
    width, height = letter

    # Title & Metadata
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, "MIDTERM EXAMINATION ANSWER SCRIPT")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 90, "Subject: Data Structures and Algorithms (CS202)")
    c.drawString(50, height - 110, "Student Name: Alice Vance")
    c.drawString(50, height - 130, "Student Number: STU-001")
    c.drawString(50, height - 150, "Date: 2026-06-20")

    c.setLineWidth(1)
    c.line(50, height - 165, width - 50, height - 165)

    # Question 1
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 200, "Question 1:")

    c.setFont("Helvetica-Oblique", 11)
    c.drawString(70, height - 220, "Explain the difference between a Stack and a Queue data structure.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 260, "Student Response:")

    c.setFont("Helvetica", 12)
    text_lines = [
        "A Stack is a Last-In-First-Out (LIFO) linear data structure where elements are inserted",
        "and removed from the exact same end, known as the top of the stack.",
        "Common operations include push (insert at top) and pop (remove from top).",
        "",
        "In contrast, a Queue is a First-In-First-Out (FIFO) linear data structure where elements",
        "are inserted at the rear end (enqueue operation) and removed from the front end",
        "(dequeue operation).",
        "",
        "Key Difference: In a Stack, the last element added is the first to be retrieved (LIFO),",
        "while in a Queue, the first element added is the first to be served (FIFO)."
    ]

    y = height - 290
    for line in text_lines:
        c.drawString(70, y, line)
        y -= 22

    c.save()
    print(f"[OK] Generated {filepath}")

def create_bob_pdf(filepath: Path):
    c = canvas.Canvas(str(filepath), pagesize=letter)
    width, height = letter

    # Title & Metadata
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, "MIDTERM EXAMINATION ANSWER SCRIPT")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 90, "Subject: Data Structures and Algorithms (CS202)")
    c.drawString(50, height - 110, "Student Name: Bob Miller")
    c.drawString(50, height - 130, "Student Number: STU-002")
    c.drawString(50, height - 150, "Date: 2026-06-20")

    c.setLineWidth(1)
    c.line(50, height - 165, width - 50, height - 165)

    # Question 1
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 200, "Question 1:")

    c.setFont("Helvetica-Oblique", 11)
    c.drawString(70, height - 220, "Explain the difference between a Stack and a Queue data structure.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 260, "Student Response:")

    c.setFont("Helvetica", 12)
    text_lines = [
        "Stack and Queue are fundamental data structures with different access orders.",
        "",
        "1. Stack: Operates on a Last-In-First-Out (LIFO) basis. All insertions and deletions",
        "happen at the top. Think of a stack of plates.",
        "",
        "2. Queue: Operates on a First-In-First-Out (FIFO) basis. Items are added at the rear",
        "and removed from the front. Think of a line of people waiting for tickets."
    ]

    y = height - 290
    for line in text_lines:
        c.drawString(70, y, line)
        y -= 22

    c.save()
    print(f"[OK] Generated {filepath}")

if __name__ == "__main__":
    out_dir = Path("uploads")
    out_dir.mkdir(parents=True, exist_ok=True)
    create_alice_pdf(out_dir / "alice_cs202_answer_sheet.pdf")
    create_bob_pdf(out_dir / "bob_cs202_answer_sheet.pdf")
