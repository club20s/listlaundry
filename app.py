import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify,redirect,url_for,make_response
from pymongo import MongoClient
from datetime import datetime


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)

db = client[DB_NAME]

app = Flask(__name__)

# homes
@app.route('/')
def home():
   return render_template('index.html')

@app.route("/bucket/done", methods=["POST"])
def bucket_done():
    num_receive = request.form["num_give"]
    db.bucket.update_one(
        {'num': int(num_receive)},
        {'$set': {'done': 1}}
    )
    return jsonify({'msg': 'Update done!'})

@app.route("/bucket", methods=["GET"])
def bucket_get():
    buckets_list = list(db.bucket.find({},{'_id':False}))
    return jsonify({'buckets':buckets_list})

@app.route("/bucket", methods=["POST"])
def bucket_post():  
    bucket_receive = request.form["bucket_give"]
    description = request.form.get('description_give')

    today =datetime.now()
    time = today.strftime('%d-%M-%Y')

    count = db.bucket.count_documents({})
    num = count + 1
    doc = {
        'num':num,
        'bucket': bucket_receive,
        "description": description,
        'time' :time,
        'done':0
    }
    db.bucket.insert_one(doc)
    return jsonify({'msg':'data saved!'})

@app.route('/delete_done', methods=["DELETE"])
def delete_done_data():
    # Pastikan Anda memiliki akses ke database dan mendapatkan koleksi yang sesuai (misalnya db.bucket)
    db.bucket.delete_many({'done': 1})  # Hapus semua dokumen dari koleksi 'bucket' yang sudah selesai (done=1)
    return jsonify({'msg': 'All done data deleted!'})


@app.route("/bucket/<int:num>", methods=["DELETE"])
def delete_bucket_by_num(num):
    # Pastikan Anda memiliki akses ke database dan mendapatkan koleksi yang sesuai (misalnya db.bucket)
    result = db.bucket.delete_one({'num': num})
    if result.deleted_count > 0:
        return jsonify({'msg': f'Data with num {num} deleted successfully!'})
    else:
        return jsonify({'msg': f'Data with num {num} not found or already deleted!'})


if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)