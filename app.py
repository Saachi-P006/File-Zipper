from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from zipper import compress_file, decompress_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/compress", methods=["POST"])
def compress():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    output_filename = os.path.splitext(file.filename)[0] + ".huff"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    compress_file(input_path, output_path)

    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)

    return jsonify({
        "file_url": f"/uploads/{output_filename}",
        "original_size": original_size,
        "compressed_size": compressed_size
    })

@app.route("/decompress", methods=["POST"])
def decompress():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    output_filename = os.path.splitext(file.filename)[0] + "_decompressed"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    decompress_file(input_path, output_path)

    compressed_size = os.path.getsize(input_path)
    decompressed_size = os.path.getsize(output_path)

    return jsonify({
        "file_url": f"/uploads/{output_filename}",
        "compressed_size": compressed_size,
        "decompressed_size": decompressed_size
    })

if __name__ == "__main__":
    app.run(debug=True)
