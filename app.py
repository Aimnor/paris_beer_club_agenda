from flask import Flask
from requests import request
from source import BeerAgenda

app = Flask(__name__)

ba = BeerAgenda(force_get_event=False, all_professionals=True)


@app.route('/professionals', methods=['GET'])
def professionals():
    return [pro.to_dict(True) for pro in ba.professionals]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
