#!/usr/bin/env python3

################################################################################
# Simple blockchain implementation in Python with the goal of gaining
# a practical understanding of how blockchain works.
#
# Author: Marco Lugo
################################################################################

from blockchain import Blockchain
import sys
from flask import Flask, jsonify, request

flask_port = int(sys.argv[1]) # required argument for port
myself = str(flask_port)

##########################################################################################################
node_list = [1331,1332,1333] # ports of all (possible) nodes; temporary until distributed solution is implemented (TODO)
assert flask_port in node_list
##########################################################################################################

# create our blockchain
dchain = Blockchain(node_list)
# create Flask instance
app = Flask(__name__)

dchain.get_consensus(node_list)

@app.route('/get_chain')
def get_chain():
    list_chain = []
    chain_size = len(dchain.chain)
    for i in range(chain_size):
        block = dchain.chain[i]
        list_chain.append({'index':block.index, 'timestamp':block.timestamp,
                            'content':block.content, 'previous_hash':block.previous_hash,
                            'hash':block.hash})
    response = {'chain': list_chain}
    return jsonify(response), 200

@app.route('/mine')
def mine():
    dchain.mine_block(myself)
    return 'Mining...'

@app.route('/get_balances')
def balances():
    response = {'balances': dchain.get_balances()}
    return jsonify(response), 200

@app.route('/consensus')
def consensus():
    dchain.get_consensus(node_list)
    return 'Applying consensus algorithm... use get_chain to see resulting chain'

@app.route('/add_transaction')
def add_transaction():
    destination = request.args.get('destination')
    amount = request.args.get('amount')
    dchain.add_transaction(myself, destination, amount)
    return 'Attempting transaction...'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=flask_port)
