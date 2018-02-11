#!/usr/bin/env python3

################################################################################
# Simple blockchain implementation in Python with the goal of gaining
# a practical understanding of how blockchain works.
#
# Author: Marco Lugo
################################################################################

import time # for obtaining the timestamp
import sha3 # for cryptographic hashing functions
import json # for using json objects as block contents
import math # for the proof-of-work
import requests # for consensus algorithm

# class to hold the blocks that will come together to form the blockchain
class Block:
    def __init__(self, index, timestamp, content, previous_hash, hash=None):
        self.index = index # block index
        self.timestamp = timestamp # block timestamp
        self.content = content # block content (transaction data)
        self.previous_hash = previous_hash # hash of the previous block
        if hash == None:
            self.hash = self.get_hash() # hash for this block (built upon the hash of the previous block among other things)
        else:
            self.hash = hash

    def get_hash(self):
        string_to_hash = str(self.index) + str(self.timestamp) + str(self.content) + str(self.previous_hash)
        hash_string = sha3.sha3_512(string_to_hash.encode('utf-8')).hexdigest()
        return hash_string

# class to hold the chain itself
class Blockchain:
    def __init__(self, node_list=[]):
        self.chain = [] # list to contain our blockchain
        self.create_block() # instantiate the class with the initial block
        self.node_list = node_list

    # creates a block for the chain; if no arguments are passed, it creates the initial block
    def create_block(self, previous_block=None, content=''):
        timestamp = time.time()
        if previous_block == None: # create the first block
            block = Block(0, timestamp, {'proof':'404'}, 'B0')
        else: # create a new block to append, it uses the hash from the previous block as input
            index = previous_block.index + 1
            block_hash = previous_block.get_hash()
            block = Block(index, timestamp, content, block_hash)
        self.chain.append(block)

    # recreates the hash given all inputs, used for validatin the chain
    def recreate_hash(self, index, timestamp, content, previous_hash):
        string_to_hash = str(index) + str(timestamp) + str(content) + str(previous_hash)
        hash_string = sha3.sha3_512(string_to_hash.encode('utf-8')).hexdigest()
        return hash_string

    # adds a transaction to the chain (creating a block)
    def add_transaction(self, origin, destination, amount):
        amount = float(amount)
        if amount <= 0 or self.get_balances()[origin] < amount: # if amount is not strictly positive or not enough balance in account, ignore
            return
        transaction = {}
        transaction['from'] = origin
        transaction['to'] = destination
        transaction['amount'] = amount
        json_data = json.dumps(transaction, sort_keys=True)
        self.create_block(previous_block=self.chain[-1], content=json_data)

    def mine_block(self, destination):
        transaction = {}
        transaction['from'] = ''
        transaction['to'] = destination
        transaction['amount'] = 1
        transaction['proof'] = self.proof_of_work(self.chain[-1].hash, self.chain[-1].index)
        transaction_json = json.dumps(transaction, sort_keys=True) # dict order is not kept but is of paramount importance for hash validation
        self.create_block(previous_block=self.chain[-1], content=transaction_json)

    # determines how many leading zeros are required for proof-of-work.
    def how_many_leading_zeros(self, block_index):
        n_leading_zeros = 2 + math.floor((block_index*block_index)/1000) # guarantees increasing marginal cost of mining
        return n_leading_zeros

    # increases until the resulting hash contaings n_leading_zeros leading zeros
    def proof_of_work(self, previous_hash, block_index):
        proof = 0
        n_leading_zeros = self.how_many_leading_zeros(block_index)
        while self.validate_proof(proof, previous_hash) != n_leading_zeros:
            proof += 1 #
        return proof

    def validate_proof(self, proof, previous_hash):
        hash_string = (str(previous_hash) + str(proof)).encode('utf-8')
        hash_out = sha3.sha3_512(hash_string).hexdigest()
        n_leading_zeros = len(hash_out) - len(hash_out.lstrip('0'))
        return n_leading_zeros

    # loops through whole chain validating proofs and hashes
    def validate_chain(self, chain):
        is_chain_valid = True
        chain_size = len(chain)
        for i in range(chain_size):
            if i > 0:
                content_dict = json.loads(chain[i]['content'])
                n_leading_zeros = self.how_many_leading_zeros(i)
                if 'proof' in content_dict: # if the block has a proof (i.e. was mined)
                    if self.validate_proof(content_dict['proof'], chain[i]['previous_hash']) != n_leading_zeros:
                        is_chain_valid = False
                        break
                if chain[i]['hash'] != self.recreate_hash(chain[i]['index'], chain[i]['timestamp'], chain[i]['content'], chain[i]['previous_hash']):
                    is_chain_valid = False
                    break
        return is_chain_valid

    def get_consensus(self, node_list):
        for port in node_list:
            try:
                response = requests.get('http://127.0.0.1:'+str(port)+'/get_chain', timeout=2)
                if response.status_code == 200: # request was successful
                    chain = response.json()['chain']
                    if len(chain) > len(self.chain) and self.validate_chain(chain): # another node holds a longer valid chain
                        self.chain = [] # reset current chain
                        for i,c in enumerate(chain):
                            self.chain.append(Block(i, chain[i]['timestamp'], chain[i]['content'], chain[i]['previous_hash'], chain[i]['hash']))
            except:
                pass


    # prints contents of a specific block given an index
    def show_block(self, block_index):
        block = self.chain[block_index]
        print('-'*40)
        print('Block index: ' + str(block.index))
        print('Block timestamp: ' + str(block.timestamp))
        print('Block content: ' + str(block.content))
        print('Block previous hash: ' + str(block.previous_hash))
        print('Block hash: ' + str(block.hash))
        print('-'*40)

    # prints contents of a specific block given an index
    def inspect_whole_chain(self):
        chain_size = len(self.chain)
        for i in range(chain_size):
            self.show_block(i)

    # gets all balances, useful for informational purposes but also for validating that a transaction can be done
    def get_balances(self):
        node_accounts = {}
        for index,block in enumerate(self.chain[1:]):
            content = json.loads(block.content)
            dest = content['to']
            if dest not in node_accounts: # account has not been created yet
                node_accounts[dest] = node_account(dest)
            if 'proof' in content: # block was mined
                node_accounts[dest].credit(float(content['amount']))
            elif 'proof' not in content: # transaction
                node_accounts[dest].credit(float(content['amount']))
                node_accounts[content['from']].debit(float(content['amount']))
        # transform accounts into a single dict with node_name keys and balance values
        balances = {}
        for key in node_accounts:
            balances[key] = node_accounts[key].get_balance()
        return balances

# class to hold blockchain accounting
class node_account:
    def __init__(self, node_name, node_balance=0):
        self.node_name = node_name
        self.node_balance = node_balance

    def credit(self, amount):
        self.node_balance += amount

    def debit(self, amount):
        self.node_balance -= amount

    def get_balance(self):
        return self.node_balance
