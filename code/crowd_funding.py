import logging
import time

from lib.client import Client


logger = logging.getLogger(__name__)


class crowd_funding(Client):
    """
    crowd_funding_cli
    """

    def __init__(self, provider, private_key, contract_conf, context, **kwargs):

        self._context = context

        super(crowd_funding, self).__init__(**kwargs)


    def sync_contract_info(self, context):
        """
        当前用户的上下文配置，与去中心化的上下文
        """
        self._context['total'] = self._web3.fromWei(self._web3.eth.get_balance(self._contract.functions.author().call), 'ether')

        if self._account.address in self._contract.functions.joined().call():
            self._context['joined'] = True
            self._context['joinPrice'] = self._web3.fromWei(self._contract.functions.joined().call()[self._account.address], 'ether')
        self._context['closed'] = self._contract.functions.closed().call()
        self._context['price'] = self._web3.fromWei(self._contract.functions.price().call(), 'ether')
        self._context['endTime'] = self._contract.functions.endTime().call()

        cur_time = time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time()))
        self._context['out_of_date'] = cur_time < self._contract.functions.endTime().call()

        if self._contract.functions.author().call == self._account.address:
            self._context['isAuthor'] = True
        else:
            self._context['isAuthor'] = False
        # TODO: overwrite cur_context
        context = self._context


    def join(self, context):
        """
        读者点击参与众筹时调用
        """
        transaction = {
            'from': self._account.address,
            'to': self._contract.functions.author().call(),
            'value': self._web3.toWei(context['price'], 'ether')
        }
        tx = self.transact(transaction)
        self.sync_contract_info(context)


    def withdraw(self, context):
        """
        赎回
        """
        transaction = {
          'from': self._account.address
        }
        self._contract.functions.withdraw(transaction)
        self.sync_contract_info(context)


    def withdrawFund(self, context):
        """
        提取资金
        """
        transaction = {
            'from': self._contract.functions.author().call()
        }
        self._contract.functions.withdrawFund(transaction)
        self.sync_contract_info(context)


