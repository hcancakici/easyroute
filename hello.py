from flask import Flask, request
import json


app = Flask(__name__)

global index_add_counter

index_add_counter = 0


@app.route('/create', methods=('GET', 'POST'))
def create():
    global index_add_counter
    kk = request.args.keys()
    data = []
    for k in kk:
        data.append(k)
    data = data[1]
    data = data.split("],[")
    data_len = len(data)
    data[0] = data[0].replace("]", "")
    data[data_len-1] = data[data_len-1].replace("]", "")
    data[data_len-1] = data[data_len-1].replace("[", "")
    data[0] = data[0].replace("[", "")
    index_add_counter += 1
    with open('data/loc_data_{}.txt'.format(str(index_add_counter)), 'w') as filehandle:
        json.dump(data, filehandle)
    return {}
