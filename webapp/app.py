from flask import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save():
    dic = {"laser":"off", "mode":"manual", "x":"0", "y":"0"}
    try:
        dic["laser"] = request.form["laser"]
        dic["mode"] = request.form["mode"]
        dic["x"] = request.form["x"]
        dic["y"] = request.form["y"]
        with open('control_mode.txt', 'w') as f:
            f.write(str(dic))
    except:        
        with open('control_mode.txt', 'w') as f:
            f.write(str(dic))
        
    return dic["laser"]

if __name__ == '__main__':
    app.run(debug=True, host='172.20.1.191')

