from flask import Flask
from flask import render_template, request, redirect, url_for, flash

from flaskext.mysql import MySQL

from flask import send_from_directory

from datetime import datetime #Nos permitirá darle el nombre a la foto

import os

app = Flask(__name__)
app.secret_key="ClaveSecreta"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_BD']='sistema'
mysql.init_app(app)

CARPETA= os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/')
def index():
    sql = "SELECT s.*, ifnull(SUM(m.cantidad),0) AS cant FROM stock.stock s LEFT JOIN stock.movimientos m ON s.id=m.codProd GROUP BY m.Codprod ORDER BY s.id"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    productos=cursor.fetchall() #genera tupla de datos
    conn.commit()
    return render_template('productos/index.html', productos=productos)

@app.route('/create')
def create():
    return render_template('productos/create.html')

@app.route('/storeProducto', methods=['POST'])
def storage():
    _denominacion=request.form['txtDenominacion']
    _rubro=request.form['txtRubro']
    _descripcion=request.form['txtDescripcion']
    _foto=request.files['txtFoto']

    if _denominacion == '' or _rubro == '' or _descripcion == '' or _foto =='':
            flash('Recuerda llenar los datos de los campos')
            return redirect(url_for('create'))

    now= datetime.now()
    tiempo= now.strftime("%Y%H%M%S")
    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
    sql = "INSERT INTO `stock`.`stock` (`id`, `denominacion`, `rubro`, `descripcion`, `foto`) VALUES (NULL, %s, %s, %s, %s);"
    datos=(_denominacion, _rubro, _descripcion, nuevoNombreFoto)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')

@app.route('/compra/<int:id>')
def compra(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `stock`.`stock` WHERE id=%s", (id
    ))
    productos=cursor.fetchall()
    conn.commit()
    return render_template('productos/compra.html', productos=productos)

@app.route('/storeCompra', methods=['POST'])
def storeCompra():
    _codigo=request.form['txtID']
    _cantidad=request.form['txtCantidad']
    
    if _codigo == '' or _cantidad == '':
            flash('Recuerda llenar los datos de los campos')
            return redirect(url_for('create'))

    sql = "INSERT INTO `stock`.`movimientos` (`id`, `codProd`, `cantidad`) VALUES (NULL, %s, %s);"
    datos=(_codigo, _cantidad)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')
  
@app.route('/venta/<int:id>')
def venta(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `stock`.`stock` WHERE id=%s", (id
    ))
    productos=cursor.fetchall()
    conn.commit()
    return render_template('productos/venta.html', productos=productos)

@app.route('/storeVenta', methods=['POST'])
def storeVenta():
    _codigo=request.form['txtID']
    _cantidad=request.form['txtCantidad']
    
    if _codigo == '' or _cantidad == '':
            flash('Recuerda llenar los datos de los campos')
            return redirect(url_for('create'))

    sql = "INSERT INTO `stock`.`movimientos` (`id`, `codProd`, `cantidad`) VALUES (NULL, %s, %s);"
    datos=(_codigo, "-" + _cantidad)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')


@app.route('/listCompras')
def listCompras():
    sql = "SELECT m.id, s.foto, s.denominacion, s.rubro, s.descripcion, m.cantidad FROM stock.movimientos m INNER JOIN stock.stock s ON s.id=m.codProd WHERE cantidad >0 ORDER BY id"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    compras=cursor.fetchall() #genera tupla de datos
    conn.commit()
    return render_template('productos/listCompras.html', compras=compras)    

@app.route('/listVentas')
def listVentas():
    sql = "SELECT m.id, s.foto, s.denominacion, s.rubro, s.descripcion, m.cantidad FROM stock.movimientos m INNER JOIN stock.stock s ON s.id=m.codProd WHERE cantidad <0 ORDER BY id"    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    ventas=cursor.fetchall() #genera tupla de datos
    conn.commit()
    return render_template('productos/listVentas.html', ventas=ventas)    

if __name__=='__main__':
    app.run(debug=True)
