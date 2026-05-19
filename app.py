from flask import Flask, request, render_template_string, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "idecreative_saas"

# ================= DB =================
def db():
    conn = sqlite3.connect("booking.db")
    return conn

def init():
    conn = db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            telepon TEXT,
            tanggal TEXT,
            event TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()

init()

# ================= LOGIN ADMIN =================
ADMIN_USER = "admin"
ADMIN_PASS = "123"

# ================= HOME =================
@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Ide Creative SaaS</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body{
    font-family:Segoe UI;
    background: linear-gradient(135deg,#ff9a9e,#fad0c4);
}

.card{
    border-radius:20px;
    box-shadow:0 10px 30px rgba(0,0,0,0.15);
    animation:fade 0.7s ease-in-out;
}

@keyframes fade{
    from{opacity:0;transform:translateY(20px)}
    to{opacity:1;transform:translateY(0)}
}

.title{
    font-size:30px;
    font-weight:900;
    color:#d63384;
}
</style>
</head>

<body>

<div class="container text-center mt-5">

<div class="title">IDE CREATIVE SAAS</div>
<p>Booking System Profesional</p>

<div class="row mt-4">

    <!-- BOOKING -->
    <div class="col-md-6">
        <div class="card p-4">

            <h5>📅 Booking Event</h5>

            <input id="nama" class="form-control mb-2" placeholder="Nama">
            <input id="telp" class="form-control mb-2" placeholder="No HP">
            <input id="tanggal" type="date" class="form-control mb-2">

            <select id="event" class="form-control mb-3">
                <option>Wedding</option>
                <option>Birthday</option>
                <option>Seminar</option>
                <option>Concert</option>
                <option>Corporate</option>
            </select>

            <button class="btn btn-success w-100" onclick="book()">🚀 Booking</button>

        </div>
    </div>

    <!-- LOGIN -->
    <div class="col-md-6">
        <div class="card p-4">

            <h5>🔐 Admin Login</h5>

            <form method="POST" action="/login">
                <input class="form-control mb-2" name="user" placeholder="username">
                <input class="form-control mb-3" name="pass" type="password" placeholder="password">
                <button class="btn btn-dark w-100">Login</button>
            </form>

        </div>
    </div>

</div>

</div>

<script>
function book(){

    let nama = document.getElementById("nama").value;
    let telp = document.getElementById("telp").value;
    let tanggal = document.getElementById("tanggal").value;
    let event = document.getElementById("event").value;

    fetch("/book",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({nama,telp,tanggal,event})
    })

    let msg =
`🔥 BOOKING IDE CREATIVE\n\n` +
`Nama: ${nama}\n` +
`Telp: ${telp}\n` +
`Tanggal: ${tanggal}\n` +
`Event: ${event}`;

    window.open("https://wa.me/6281342527108?text=" + encodeURIComponent(msg));
}
</script>

</body>
</html>
""")

# ================= BOOK =================
@app.route("/book", methods=["POST"])
def book():
    data = request.json

    conn = db()
    c = conn.cursor()

    c.execute("""
        INSERT INTO bookings VALUES (NULL,?,?,?,?,?)
    """, (data["nama"], data["telp"], data["tanggal"], data["event"], "pending"))

    conn.commit()
    conn.close()

    return {"status":"ok"}

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    if request.form["user"] == ADMIN_USER and request.form["pass"] == ADMIN_PASS:
        session["admin"] = True
        return redirect("/admin")
    return redirect("/")

# ================= ADMIN DASHBOARD =================
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/")

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Admin Dashboard</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>

<body>

<div class="container mt-5">

<h2>📊 Dashboard Admin</h2>

<canvas id="chart"></canvas>

<hr>

<table class="table table-bordered mt-3">
<tr>
<th>ID</th><th>Nama</th><th>Telp</th><th>Tanggal</th><th>Event</th><th>Status</th><th>Aksi</th>
</tr>

{% for b in data %}
<tr>
<td>{{b[0]}}</td>
<td>{{b[1]}}</td>
<td>{{b[2]}}</td>
<td>{{b[3]}}</td>
<td>{{b[4]}}</td>
<td>
<span class="badge bg-warning">{{b[5]}}</span>
</td>
<td>
<a href="/update/{{b[0]}}/confirmed" class="btn btn-success btn-sm">✔</a>
<a href="/update/{{b[0]}}/cancel" class="btn btn-danger btn-sm">✖</a>
</td>
</tr>
{% endfor %}

</table>

<a href="/logout" class="btn btn-dark">Logout</a>

</div>

<script>
async function load(){

let res = await fetch("/chart");
let data = await res.json();

new Chart(document.getElementById("chart"),{
    type:"bar",
    data:{
        labels:data.map(x=>x.event),
        datasets:[{
            label:"Booking",
            data:data.map(x=>x.total),
            backgroundColor:"#ff4d6d"
        }]
    }
});

}
load();
</script>

</body>
</html>
""", data=get_all())

# ================= DATA =================
def get_all():
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM bookings ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

# ================= CHART API =================
@app.route("/chart")
def chart():
    conn = db()
    c = conn.cursor()

    c.execute("SELECT event, COUNT(*) FROM bookings GROUP BY event")
    data = c.fetchall()

    conn.close()

    return jsonify([{"event":d[0],"total":d[1]} for d in data])

# ================= UPDATE STATUS =================
@app.route("/update/<int:id>/<status>")
def update(id, status):
    conn = db()
    c = conn.cursor()

    c.execute("UPDATE bookings SET status=? WHERE id=?", (status, id))

    conn.commit()
    conn.close()

    return redirect("/admin")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)