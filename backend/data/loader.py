from data.seed import ACCOUNTS, ORDERS, TICKETS


class DataFrames:
    def __init__(self) -> None:
        try:
            import pandas as pd

            self.accounts = pd.DataFrame(ACCOUNTS)
            self.orders = pd.DataFrame(ORDERS)
            self.tickets = pd.DataFrame(TICKETS)
        except Exception:
            self.accounts = ACCOUNTS
            self.orders = ORDERS
            self.tickets = TICKETS


DATA = DataFrames()
