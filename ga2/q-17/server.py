from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    # Serve JSON with your email
    return jsonify({"email": "23f3003994@ds.study.iitm.ac.in"})

if __name__ == "__main__":
    app.run(port=5000)
