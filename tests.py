import pytest
import epood2 as epood


def test_add_item():
    shop = epood.Shop()
    item = epood.Item("Apple", 1.0, 10, shop)
    assert item.name == "Apple"
    assert item.price == 1.0
    assert shop.items["Apple"].amount == 10
    assert shop.items["Apple"] is item


def test_create_cart():
    shop = epood.Shop()
    item = epood.Item('book', 20.99, 5, shop)
    client = epood.Client(12, 51.25)
    cart = epood.Cart(shop, client)
    cart.update_cart(item, 2)
    assert shop.clients[client.id] == client
    assert shop.carts[client.id] == cart


def test_check_amount():  # NotEnoughItems(), check_amount()
    shop = epood.Shop()
    item = epood.Item("Banana", 2.0, 5, shop)
    assert item.check_amount(3) is True
    with pytest.raises(epood.NotEnoughItems):
        item.check_amount(10)


def test_update_balance():  # OutOfBalance(), update_balance()
    client = epood.Client(1, 50)
    client.update_balance(20)
    assert client.balance == 30
    with pytest.raises(epood.OutOfBalance):
        client.update_balance(40)


def test_deletion_from_cart():  # Deletion
    shop = epood.Shop()
    item = epood.Item('book', 20.99, 5, shop)
    client = epood.Client(12, 51.25)
    cart = epood.Cart(shop, client)
    cart.update_cart(item, 2)
    cart.update_cart(item, 3, False)
    assert cart.contents == {}


def test_subtract_from_empty_cart():  # NoSuchItemInCart()
    shop = epood.Shop()
    item = epood.Item('book', 20.99, 5, shop)
    client = epood.Client(12, 51.25)
    cart = epood.Cart(shop, client)
    with pytest.raises(epood.NoSuchItemInCart):
        cart.update_cart(item, 3, False)
    assert cart.contents == {}


def test_multiple_shops_transactions():  # Multiple Shops, Addition
    shop1 = epood.Shop()
    shop2 = epood.Shop()
    item1 = epood.Item("banaan", 2, 10, shop1)
    item2 = epood.Item("banaan", 3, 6, shop2)
    client = epood.Client(21, 28)
    cart1 = epood.Cart(shop1, client)
    cart2 = epood.Cart(shop2, client)
    cart1.update_cart(item1, 6)
    cart2.update_cart(item2, 5)
    cart1.check_out()
    cart2.check_out()
    assert client.balance == 1
    assert shop1.transactions[client.id][0][1] == {item1: 6}
    assert shop2.transactions[client.id][0][1] == {item2: 5}


def test_multiple_clients_transactions():  # Multiple Clients, MissingStock(), Subtraction
    client1 = epood.Client(1, 2)
    client2 = epood.Client(2, 4)
    shop = epood.Shop()
    item = epood.Item("banaan", 1, 3, shop)
    cart1 = epood.Cart(shop, client1)
    cart2 = epood.Cart(shop, client2)
    cart1.update_cart(item, 2)
    cart2.update_cart(item, 2)
    cart1.check_out()
    with pytest.raises(epood.MissingStock):
        cart2.check_out()
    cart2.update_cart(item, 1, False)
    cart2.check_out()
    assert shop.transactions[client1.id][0][1] == {item: 2}
    assert shop.transactions[client2.id][0][1] == {item: 1}


def test_multiple_products():  # Multiple Products, random_date(), update_cart(), check_amount()
    shop = epood.Shop()
    item1 = epood.Item('Harry Potter', 20.99, 5, shop)
    item2 = epood.Item('Lord of the Rings', 21.99, 3, shop)
    client = epood.Client(12, 68.97)
    cart = epood.Cart(shop, client)
    cart.update_cart(item1, 1)
    cart.update_cart(item2, 2)
    cart.check_out()
    assert client.balance == 4
    assert shop.transactions[client.id][0][1] == {item1: 1, item2: 2}


def test_multiple_transactions_sorting():  # view_cart(), Transaction Sorting
    shop = epood.Shop()
    client = epood.Client(12, 68.97)
    shop.add_transaction('13.01', {'some_item': 10}, client)
    shop.add_transaction('02.01', {'some_item': 5}, client)
    shop.add_transaction('01.12', {'some_item': 66}, client)
    shop.add_transaction('16.02', {'some_item': 1}, client)
    shop.add_transaction('02.12', {'some_item': 2}, client)
    shop.add_transaction('17.12', {'some_item': 3, 'some_item2': 4}, client)
    transactions = client.view_cart(shop)
    for i in range(len(transactions) - 1):
        date = transactions[i][0].split('.')[::-1]
        date2 = transactions[i+1][0].split('.')[::-1]
        if date[0] == date2[0]:
            assert date[1] > date2[1]
        else:
            assert date[0] > date2[0]


def test_gold_client():  # Gold Client, Shop(), Item(), Client(), Cart(), check_out(), get_cost()
    shop = epood.Shop()
    item1 = epood.Item('RAM DDR5 6200MT/s CL36 16GB x2', 114.99, 15, shop)
    item2 = epood.Item('Ryzen 7 7800x3D', 389.99, 30, shop)
    client = epood.Client(12, 610.97, True)
    cart = epood.Cart(shop, client)
    cart.update_cart(item1, 2)
    cart.update_cart(item2, 1)
    cart.check_out()
    assert client.balance == 53


"""
Gold Client  # CHECK
Transaction Sorting  # CHECK
Multiple Products  # CHECK
Multiple Clients  # CHECK
Multiple Shops  # CHECK


epood.Shop()  # CHECK
    epood.Shop.add_transaction()

epood.Item()   # CHECK
    epood.NotEnoughItems()  # CHECK
    
epood.Cart()   # CHECK
    epood.Cart.update_cart()   # CHECK
        epood.Item.check_amount()  # CHECK
    epood.Cart.check_out()   # CHECK
        epood.Cart.get_cost()  # CHECK
        epood.random_date()  # CHECK
    epood.NoSuchItemInCart()  # CHECK
    epood.MissingStock()  # CHECK
    #Subtraction  # CHECK
    #Addition  # CHECK
    #Deletion  # CHECK
    
epood.Client()  # CHECK
    epood.Client.view_cart()  # CHECK
    epood.Client.update_balance()  # CHECK
    epood.OutOfBalance()  # CHECK
"""
