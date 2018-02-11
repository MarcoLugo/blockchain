# blockchain
Simple blockchain implementation in Python with the goal of gaining a practical understanding of how blockchain works.

## Run A Node

python3 run.py port

Ports can be found in node_list inside run.py.

## Interacting With The Blockchain

You can interact via HTTP requests with the node. For example, if you are running a node on port 1331:

### Mine

http://127.0.0.1:1331/mine

### View Chain

http://127.0.0.1:1331/get_chain

### View Balances

http://127.0.0.1:1331/get_balances

### Make Transaction

This operation takes two parameters passed via GET: destination and amount. The transaction will be rejected if the amount is not strictly positive or if the origin node (i.e. sender) does not have enough funds.

http://127.0.0.1:1331/add_transaction?destination=1332&amount=2

### Apply Consensus Algorithm

http://127.0.0.1:1331/consensus

The consensus algorithm is what will reconciliate the blockchain accross the different nodes. It will take the longest valid chain available.

You can have a look at run.py to learn more.

