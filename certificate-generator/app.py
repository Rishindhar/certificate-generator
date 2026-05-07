from flask import Flask, render_template, request, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import sqlite3
import os
import random

app = Flask(__name__)

# ✅ Create DB
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            event TEXT,
            date TEXT,
            cert_id TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')


# Border
def draw_border(canvas, doc):
    width, height = A4
    canvas.setStrokeColor(colors.blue)
    canvas.setLineWidth(3)
    canvas.rect(30, 30, width - 60, height - 60)


@app.route('/generate', methods=['POST'])
def generate():
    name = request.form['name']
    role = request.form['role']
    event = request.form['event']
    date = request.form['date']

    if not os.path.exists("certificates"):
        os.makedirs("certificates")

    cert_id = "CERT" + str(random.randint(10000, 99999))
    filename = f"certificates/{name}.pdf"

    # PDF
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    title = ParagraphStyle(name='title', fontSize=24, alignment=TA_CENTER)
    normal = ParagraphStyle(name='normal', fontSize=14, alignment=TA_CENTER)

    content = []
    content.append(Spacer(1, 50))
    content.append(Paragraph("CERTIFICATE OF COMPLETION", title))
    content.append(Spacer(1, 30))
    content.append(Paragraph(f"This is to certify that <b>{name}</b>", normal))
    content.append(Paragraph(f"Role: {role}", normal))
    content.append(Paragraph(f"Event: {event}", normal))
    content.append(Paragraph(f"Date: {date}", normal))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"Certificate ID: {cert_id}", normal))

    doc.build(content, onFirstPage=draw_border)

    # ✅ SAVE TO DATABASE
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO certificates (name, role, event, date, cert_id)
        VALUES (?, ?, ?, ?, ?)
    """, (name, role, event, date, cert_id))

    conn.commit()
    conn.close()

    print("Saved:", name)

    return send_file(filename, as_attachment=True)


# ✅ ADMIN PANEL
@app.route('/admin')
def admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT name, role, event, date, cert_id FROM certificates")
    data = c.fetchall()

    conn.close()

    return render_template('admin.html', records=data)


# ✅ DEBUG ROUTE (very important)
@app.route('/testdb')
def testdb():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM certificates")
    data = c.fetchall()
    conn.close()
    return str(data)


if __name__ == '__main__':
    app.run(debug=True)