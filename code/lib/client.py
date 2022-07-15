import logging

import json
from web3 import Web3

logger = logging.getLogger(__name__)


class Client():
    """
    build client to access infura public node
    """

    def __init__(self, provider: str, private_key: str, contract_conf: dict):
        """
        :param provider: str
        :param private_key: test
        :param contract_conf: contract_conf is a dict that contains contract info
        """

        self._logger = logger

        self._provider = provider
        self._web3 = Web3(Web3.HTTPProvider(self._provider))
        assert self._web3.isConnected()

        self._private_key = private_key
        self._account = self._web3.eth.account.from_key(self._private_key)
        assert self._web3.isAddress(self._account.address)

        assert (contract_conf['abi_path'] is not None) and (contract_conf['bin_path'] is not None)
        self._contract = self.init_contract(contract_conf)

        self._transaction = None

        print('cur account:{}, isConnected:{}'.format(self._account.address, self._web3.isConnected()))



    def get_balance(self, unit):
        """
        unit: return self balance
        """
        return self._web3.fromWei(self._web3.eth.get_balance(self._account), unit)

    def init_contract(self, contract_conf):
        with open(contract_conf['abi_path'], 'r') as f:
            _abi = json.load(f)

        with open(contract_conf['bin_path'], 'r') as f:
            _bin = f.readline()

        contract = self._web3.eth.contract(abi=_abi, bytecode=_bin) # 合约对象
        construct_txn = contract.constructor().buildTransaction({
            'from': self._account.address,
            'nonce': self._web3.eth.getTransactionCount(self._account.address),
            'gas': 5000000,
            'gasPrice': self._web3.toWei('21', 'gwei')
        })

        signed = self._account.signTransaction(construct_txn)
        tx_id = self._web3.eth.sendRawTransaction(signed.rawTransaction)
        contract_addr = self._web3.eth.waitForTransactionReceipt(tx_id.hex()).contractAddress
        c = self._web3.eth.contract(address=contract_addr, abi=_abi)
        print('cur contract address :{}, functions set :{}'.format(c.address, c.all_functions()))
        return c

    def transact(self, transaction):
        """
        make a transaction with web3.py
        """
        assert self._web3.isChecksumAddress(transaction['to'])
        self._transaction = transaction

        signed = self._web3.eth.account.sign_transaction(self._transaction, self._private_key)
        tx = self._web3.eth.send_raw_transaction(signed.rawTransaction)
        return tx

