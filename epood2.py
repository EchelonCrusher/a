from datetime import datetime
import random


class Item:  # Müüdav ese
    """
    Sellel on nimi, hind.

    Igat eset on e-poes kindel kogus.

    Klient saab osta e-poes eset seni, kuniks kaupa jätkub.
    """
    def __init__(self, name: str, price: float, amount: int, shop: 'Shop'):
        self.name = name
        self.price = price
        self.amount = amount
        shop.items[self.name] = self

    def check_amount(self, amount: int):
        if amount > self.amount:
            raise NotEnoughItems(amount, self)  # NotEnoughItems
        return True


class Shop:  # E-pood
    """
    Teab toodete koguste kohta

    Teab kõikide toimunud ostude kohta

    Teab kõiki e-poodi registreeritud kliente.
    """
    def __init__(self):
        self.items = {}  # {item_name: item: Item, ...}
        self.clients = {}  # {client.id: client: Client, ...}
        self.transactions = {}  # {client_id: [(date, {item: count, ...}), ...], ...}
        self.carts = {}  # {item: count, ...}

    def add_transaction(self, date: str, cart: dict, client: 'Client'):
        new_transaction = (date, cart)
        if client.id not in self.transactions:
            self.transactions[client.id] = []
        self.transactions[client.id].append(new_transaction)


class Client:  # Klient
    """
    Tal on id, korv, tüüp (kuldklient, tava klient) ja ostude ajalugu

    Klient saab vaadata ostude ajalugu (näiteks näeb, et ostis 10.04 saia ja piima, 4.04 leiba, piima ja nutellat)

    Klient näeb ajalugu selliselt, et kõige hiljutisem ost on esimene. (10.04 ..., 4.04...., 27.03....)

    Klient ei saa sooritada ostu, kui ta arvel on ostukorvi maksumusest madalam summa - visata veateade.

    Kuldkilent saab 10% soodustust toodetelt
    """

    def __init__(self, client_id: int, balance: float = 0, gold_client: bool = False, shop: Shop = None):
        self.id = client_id
        self.balance = balance
        self.gold = gold_client
        if shop:
            shop.clients[self.id] = self

    def update_balance(self, value: float):
        """
        Subtract value from balance.
        Negative value adds balance.

        :param value:
        :return:
        """
        if value > self.balance:
            raise OutOfBalance(value, self.balance)  # OutOfBalance
        self.balance -= value

    def view_cart(self, shop: Shop):
        transactions = shop.transactions[self.id]
        sorted_cart = sorted(transactions, key=lambda x: x[0].split('.')[::-1], reverse=True)  # Sort transactions
        # Nice way of printing
        for transaction in sorted_cart:
            print(f'\n---------------------------------------\n{transaction[0]}')
            for item, amount in transaction[1].items():
                print(f'{item} x {amount}')
        print('\n---------------------------------------')
        return sorted_cart


class Cart:  # Ostukorv
    """
    Saab lisada ja eemaldada esemeid

    Saab suurendada või vähendada esemete hulka
    """
    def __init__(self, shop: Shop, client: Client):
        self.contents = {}
        self.shop = shop
        self.client = client
        if client not in shop.clients:
            shop.clients[client.id] = client
        shop.carts[client.id] = self

    def update_cart(self, item: Item, amount: int, addition: bool = True):
        if addition:
            if item.check_amount(amount):
                self.contents[item] = self.contents.get(item, 0) + amount  # Addition
        elif item in self.contents:
            if self.contents[item] <= amount:  # Deletion
                del self.contents[item]
            else:
                self.contents[item] -= amount  # Subtraction
        else:
            raise NoSuchItemInCart  # NoSuchItemInCart

    def check_out(self):
        cost = self.get_cost()  # Get Cost
        if cost > self.client.balance:
            raise OutOfBalance(cost, self.client.balance)  # OutOfBalance
        for item, amount in self.contents.items():
            if item.amount < amount:
                raise MissingStock(amount, item)  # MissingStock
            item.amount -= amount
        if self.client.id not in self.shop.transactions:
            self.shop.transactions[self.client.id] = []
        self.shop.transactions[self.client.id].append((random_date(), self.contents))  # Random date
        self.client.update_balance(cost)
        self.contents = {}
    
    def get_cost(self) -> float:
        total_cost = 0
        for item, amount in self.contents.items():
            total_cost += item.price * amount
        return round(total_cost - self.client.gold * total_cost * 0.1, 2)  # Gold Client
        

def random_date():
    random_day = random.randint(1, 365)
    date = datetime.strptime(str(random_day), '%j')
    return date.strftime('%d.%m')


class OutOfBalance(Exception):
    def __init__(self, cost, balance):
        print(f'Insufficient funds. You need {cost}€, but have {balance}€.')


class NotEnoughItems(Exception):
    def __init__(self, amount: int, item: Item):
        print(f'Unable to add {item.name} x {amount} to the cart. '
              f'The stock currently contains {item.name} x {item.amount}.')


class MissingStock(Exception):
    def __init__(self, amount: int, item: Item):
        print(f'Unable to purchase {item.name} x {amount} The stock currently contains {item.name} x {item.amount}.')


class NoSuchItemInCart(Exception):
    def __init__(self):
        print('No such item in cart.')
