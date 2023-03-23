import smartpy as sp

class Lottery(sp.Contract):
    def __init__(self, max, cost):

        # storage variables
        self.init(
            players = sp.map(l = {}, tkey = sp.TNat, tvalue = sp.TAddress),
            ticket_cost = cost,
            tickets_available = sp.nat(max),
            max_tickets = sp.nat(max),
            operator = sp.test_account("admin").address,
            index = sp.nat(0)
        )

    # The following buy_ticket function doesn't work. The loops are broken.

    '''

    @sp.entry_point
    def buy_ticket(self, number):
        sp.set_type(number, sp.TNat)

        # assertions
        sp.verify(number > 0, "MUST BUY AT LEAST 1 TICKET")
        sp.verify(self.data.tickets_available >= number, "NOT ENOUGH TICKETS AVAILABLE")
        sp.verify(sp.amount >= sp.mul(self.data.ticket_cost, number), "NOT ENOUGH TEZ")

        # storage changes
        self.data.tickets_available = sp.as_nat(self.data.tickets_available - number)
        
        i = sp.nat(0)
        sp.while i < number:
            self.data.players[self.data.index + i] = sp.sender
            i += 1

        self.data.index = self.data.index + i

        # return extra tez
        extra_amount = sp.amount - sp.mul(self.data.ticket_cost, number)
        sp.if extra_amount > sp.tez(0):
            sp.send(sp.sender, extra_amount)

    '''

    @sp.entry_point
    def buy_ticket(self):

        # assertions
        sp.verify(self.data.tickets_available > 0, "NOT ENOUGH TICKETS AVAILABLE")
        sp.verify(sp.amount >= self.data.ticket_cost, "NOT ENOUGH TEZ")

        # storage changes
        self.data.tickets_available = sp.as_nat(self.data.tickets_available - 1)
        
        self.data.players[self.data.index] = sp.sender
        self.data.index = self.data.index + 1

        # return extra tez
        extra_amount = sp.amount - self.data.ticket_cost
        sp.if extra_amount > sp.tez(0):
            sp.send(sp.sender, extra_amount)

    @sp.entry_point
    def change_ticket_cost(self, new_cost):
        sp.set_type(new_cost, sp.TMutez)

        # assertions
        sp.verify(sp.sender == self.data.operator, "NOT AUTHORISED")
        sp.verify(self.data.tickets_available == self.data.max_tickets, "LOTTERY HAS ALREADY STARTED")
        sp.verify(new_cost > sp.tez(0), "TICKET COST SET TO 0")    

        # storage changes
        self.data.ticket_cost = new_cost

    @sp.entry_point
    def change_max_tickets(self, new_max):
        sp.set_type(new_max, sp.TNat)

        # assertions
        sp.verify(sp.sender == self.data.operator, "NOT AUTHORISED")
        sp.verify(self.data.tickets_available == self.data.max_tickets, "LOTTERY HAS ALREADY STARTED")
        sp.verify(new_max > 0, "MAX TICKETS SET TO 0")   

        # storage changes
        self.data.max_tickets = new_max
        self.data.tickets_available = new_max

    @sp.entry_point
    def end_game(self, random_number):
        sp.set_type(random_number, sp.TNat)

        # assertions
        sp.verify(self.data.tickets_available == 0, "TICKETS NOT SOLD OUT")
        sp.verify(sp.sender == self.data.operator, "NOT AUTHORISED")

        # generate winner 
        winner_index = random_number % self.data.max_tickets
        winner_address = self.data.players[winner_index]

        # send tez to winner
        sp.send(winner_address, sp.balance)

        # reset game
        self.data.players = {}
        self.data.tickets_available = self.data.max_tickets
        self.data.index = 0

@sp.add_test(name = "main")
def test():
    scenario = sp.test_scenario()

    # test accounts
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    john = sp.test_account("john")
    mike = sp.test_account("mike")
    charles =  sp.test_account("charles")

    #contract instance
    lottery = Lottery(5, sp.tez(1))
    scenario += lottery

    #buy ticket
    scenario += lottery.buy_ticket().run(
        amount = sp.tez(6), 
        sender = alice
    )

    scenario += lottery.buy_ticket().run(
        amount = sp.mutez(999999), 
        sender = bob,
        valid = False
    )

    #change ticket cost
    scenario += lottery.change_ticket_cost(sp.tez(2)).run(
        sender = bob,
        valid = False
    )

    scenario += lottery.change_ticket_cost(sp.tez(8)).run(
        sender = admin,
        valid = False
    )

    #change max tickets

    scenario += lottery.change_max_tickets(7).run(
        sender = bob,
        valid = False
    )

    scenario += lottery.change_max_tickets(7).run(
        sender = admin,
        valid = False
    )

    #buy ticket
    scenario += lottery.buy_ticket().run(
        amount = sp.tez(200), 
        sender = john
    )

    scenario += lottery.buy_ticket().run(
        amount = sp.mutez(1000001), 
        sender = mike
    )

    #end game
    scenario += lottery.end_game(3).run(
        sender = admin,
        valid = False
    )

    #buy ticket
    scenario += lottery.buy_ticket().run(
        amount = sp.tez(5), 
        sender = charles
    )

    scenario += lottery.buy_ticket().run(
        amount = sp.tez(1), 
        sender = alice
    )

    scenario += lottery.buy_ticket().run(
        amount = sp.tez(1), 
        sender = alice,
        valid = False
    )

    #end game
    scenario += lottery.end_game(3).run(
        sender = bob,
        valid = False
    )

    scenario += lottery.end_game(5).run(
        sender = admin
    )

    #change ticket cost
    scenario += lottery.change_ticket_cost(sp.tez(0)).run(
        sender = admin,
        valid = False
    )

    scenario += lottery.change_ticket_cost(sp.tez(2)).run(
        sender = admin
    )

    #change max tickets

    scenario += lottery.change_max_tickets(0).run(
        sender = admin,
        valid = False
    )

    scenario += lottery.change_max_tickets(7).run(
        sender = admin
    )

    