from flask import Flask
from source import BeerAgenda
from source.professionals import ProType

app = Flask(__name__)

ba = BeerAgenda(force_get_event=False, all_professionals=True)


@app.route('/professionals', methods=['GET'])
def professionals():
    return [pro.to_dict(True, keys=["name",
                                    "relative_url",
                                    "display_name",
                                    "email",
                                    "phone",
                                    "address",
                                    "urls",
                                    "types",
                                    "subscribed"
                                    ])
            for pro in ba.professionals]


@app.route('/professionals/types', methods=['GET'])
def proTypes():
    return [pt.name for pt in ProType]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
