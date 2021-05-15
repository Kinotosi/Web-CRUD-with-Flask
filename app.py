from operator import le
import re
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import url
from sqlalchemy.orm import query

app = Flask(__name__)
app.secret_key = "ejofhfiuewhuowhofwiuaufdoufjfshihsfibu"

# Database connect
userpass = 'mysql+pymysql://root:@'
basedir = '127.0.0.1'
dbname = '/sekolah'

app.config["SQLALCHEMY_DATABASE_URI"] = userpass + basedir + dbname
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

class Siswa(db.Model):
    nis = db.Column(db.Integer, primary_key=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    tempat_lahir = db.Column(db.String(100), nullable=False)
    tanggal_lahir = db.Column(db.String(20), nullable=False)
    alamat = db.Column(db.String(255), nullable=False)

    def __init__(self, nis, nama, tempat_lahir, tanggal_lahir, alamat):
        self.nis = nis
        self.nama = nama
        self.tempat_lahir = tempat_lahir
        self.tanggal_lahir = tanggal_lahir
        self.alamat = alamat

class Guru(db.Model):
    nip = db.Column(db.String(10), primary_key=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    tanggal_lahir = db.Column(db.String(30), nullable=False)
    alamat = db.Column(db.String(255), nullable=False)
    Mapels = db.relationship('Mapel', backref='guru', lazy=True)

    def __init__(self, nip, nama, tanggal_lahir, alamat):
        self.nip = nip
        self.nama = nama
        self.tanggal_lahir = tanggal_lahir
        self.alamat = alamat


class Mapel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_pel = db.Column(db.String(255), nullable=False)
    jumlah_jam = db.Column(db.Integer, nullable=False)
    guru_nip = db.Column(db.String(10), db.ForeignKey('guru.nip'), nullable=False)
    ruangan = db.Column(db.String(50), nullable=False)

    def __init__(self, nama_pel, jumlah_jam, guru_nip, ruangan):
        self.nama_pel = nama_pel
        self.jumlah_jam = jumlah_jam
        self.guru_nip = guru_nip
        self.ruangan = ruangan

# Dashboard Page
@app.route('/')
def index():
    data_siswa = len(Siswa.query.all())
    data_guru = len(Guru.query.all())
    return render_template('index.html', jum_siswa=data_siswa, jum_guru=data_guru)

# Siswa Page
@app.route('/siswa')
def siswa():
    data_siswa = db.session.query(Siswa)
    return render_template('siswa/index.html', data_siswa=data_siswa)

# Add Data Siswa
@app.route('/siswa/tambah', methods=['POST', 'GET'])
def siswaTambah():
    cek_data = len(Siswa.query.all())
    if request.method == 'POST':
        nis = request.form['nis']
        nama = request.form['nama']
        tempat_lahir = request.form['tempat_lahir']
        tanggal_lahir = request.form['tanggal_lahir']
        alamat = request.form['alamat']

        add_siswa = Siswa(nis, nama, tempat_lahir, tanggal_lahir, alamat)
        db.session.add(add_siswa)
        db.session.commit()

        new_data = len(Siswa.query.all())
        if new_data == cek_data:
            flash('Data Gagal Ditambahkan', 'danger')
            return redirect(url_for('siswa'))
        else:
            flash('Data Berhasil Ditambahkan', 'success')
            return redirect(url_for('siswa'))

    return render_template('siswa/tambah.html')

# Edit Data Siswa
@app.route('/siswa/ubah/<nis>')
def ubah(nis):
    data_siswa = Siswa.query.get(nis)
    return render_template("siswa/ubah.html", data=data_siswa)

# Proses Edit Data Siswa
@app.route('/siswa/ubah_siswa', methods=['GET', 'POST'])
def ubah_siswa():
    data_siswa = Siswa.query.get(request.form.get('id'))

    data_siswa.nis = request.form['nis']
    data_siswa.nama = request.form['nama']
    data_siswa.tempat_lahir = request.form['tempat_lahir']
    data_siswa.tanggal_lahir = request.form['tanggal_lahir']
    data_siswa.alamat = request.form['alamat']

    db.session.commit()

    flash('Data Berhasil Dirubah', 'success')
    return redirect(url_for('siswa'))

# Delete Data Siswa
@app.route('/siswa/hapus/<nis>', methods=['GET', 'POST'])
def hapusSiswa(nis):
    cek_data = len(Siswa.query.all())
    data_siswa = Siswa.query.get(nis)
    db.session.delete(data_siswa)
    db.session.commit()

    konfirm_data = len(Siswa.query.all())
    if cek_data == konfirm_data:
        flash("Data Gagal Dihapus", "danger")
        return redirect(url_for("siswa"))
    else:
        flash("Data Berhasil Dihapus", "success")
        return redirect(url_for("siswa"))
 

# Mata Pelajaran Page
@app.route('/mapel')
def mapel():
    data_mapel = db.session.query(Guru, Mapel).join(Mapel).all()
    return render_template('mapel/index.html', data_mapel=data_mapel)

# Add New Mata Pelajaran
@app.route('/mapel/tambah', methods=["GET", "POST"])
def mapelTambah():
    cek_data = len(Mapel.query.all())
    if request.method == "POST":
        nama_mapel = request.form["nama_mapel"]
        jumlah_jam = request.form["jumlah_jam"]
        nip_guru = request.form["guru_pengampu"]
        ruangan = request.form["ruangan"]

        add_mapel = Mapel(nama_mapel, jumlah_jam, nip_guru, ruangan)
        db.session.add(add_mapel)
        db.session.commit()

        jum_data = len(Mapel.query.all())
        if jum_data == cek_data:
            flash("Data Gagal Ditambahkan", "danger")
            return redirect(url_for("mapel"))
        else :
            flash("Data Berhasil Ditambahkan", "success")
            return redirect(url_for("mapel"))

    return render_template('mapel/tambah.html')

# Edit Data Mata Pelajaran
@app.route('/mapel/ubah/<id>')
def mapelUbah(id):
    data_mapel = Mapel.query.get(id)
    return render_template('mapel/ubah.html', data_mapel=data_mapel)

# Proses Edit Data Mata Pelajaran
@app.route('/mapel/ubah_mapel', methods=['GET', 'POST'])
def ubahMapel() :
    dataMapel = Mapel.query.get(request.form.get('id'))

    dataMapel.nama_pel = request.form['nama_mapel']
    dataMapel.jumlah_jam = request.form['jumlah_jam']
    dataMapel.guru_nip = request.form['guru_pengampu']
    dataMapel.ruangan = request.form['ruangan']

    db.session.commit()

    flash("Data Berhasil Dirubah", "success")

    return redirect(url_for('mapel'))

# Delete Data Mata Pelajaran
@app.route('/mapel/hapus/<id>', methods=['GET', 'POST'])
def hapusMapel(id):
    cek_data = len(Mapel.query.all())
    data_mapel = Mapel.query.get(id)
    db.session.delete(data_mapel)
    db.session.commit()

    konfirm_data = len(Mapel.query.all())
    if cek_data == konfirm_data:
        flash("Data Gagal Dihapus", "danger")
        return redirect(url_for('mapel'))
    else:
        flash("Data Berhasil Dihapus", "success")
        return redirect(url_for('mapel'))

# Guru Page
@app.route('/guru')
def guru():
    data_guru = db.session.query(Guru)
    return render_template('guru/index.html', data_guru=data_guru)

# Add New Data Guru
@app.route('/guru/tambah', methods=['GET', 'POST'])
def guruTambah():
    cek_data = len(Guru.query.all())
    if request.method == 'POST':
        nip = request.form['nip']
        nama = request.form['nama']
        tanggal_lahir = request.form['tanggal_lahir']
        alamat = request.form['alamat']

        add_guru = Guru(nip, nama, tanggal_lahir, alamat)
        db.session.add(add_guru)
        db.session.commit()

        konfirm_data = len(Guru.query.all())
        if cek_data == konfirm_data:
            flash("Data Gagal Ditambahkan", "danger")
            return redirect(url_for('guru'))
        else:
            flash("Data Berhasil Ditambahkab", "success")
            return redirect(url_for('guru'))

    return render_template('guru/tambah.html')

# Edit Data Guru
@app.route('/guru/ubah/<nip>')
def guruUbah(nip):
    data_guru = Guru.query.get(nip)
    return render_template('guru/ubah.html', data_guru=data_guru)

# Proses Edit Data Guru
@app.route('/guru/ubah_guru', methods=['GET', 'POST'])
def prosesTambahGuru():
    data_guru = Guru.query.get(request.form.get('id'))

    data_guru.nip = request.form['nip']
    data_guru.nama = request.form['nama']
    data_guru.tanggal_lahir = request.form['tanggal_lahir']
    data_guru.alamat = request.form['alamat']

    db.session.commit()

    flash("Data Berhasil Dirubah", "success")
    return redirect(url_for('guru'))

# Delete Data Guru
@app.route('/guru/hapus/<nip>')
def hapusGuru(nip):
    cek_data = len(Guru.query.all())
    data_guru = Guru.query.get(nip)
    db.session.delete(data_guru)
    db.session.commit()

    konfirm_data = len(Guru.query.all())
    if konfirm_data == cek_data:
        flash("Data Gagal Dihapus", "danger")
        return redirect(url_for('guru'))
    else:
        flash("Data Berhasil Dihapus", "success")
        return redirect(url_for("guru"))

