from app.bigisub.client import BigisubClient


class BigisubService:
    def __init__(self):
        self.client = BigisubClient()

    def login(
        self,
        email_or_username: str,
        password: str,
    ) -> dict:
        return self.client.login(
            email_or_username=email_or_username,
            password=password,
        )

    def get_wallet_balance(self) -> dict:
        return self.client.get_wallet_balance()

    def purchase_airtime(
        self,
        network: int,
        phone_number: str,
        amount: str,
        airtime_type: str,
        pin: str,
    ) -> dict:
        return self.client.purchase_airtime(
            network=network,
            phone_number=phone_number,
            amount=amount,
            airtime_type=airtime_type,
            pin=pin,
        )

    def get_data_plans(self) -> dict:
        return self.client.get_data_plans()

    def get_cable_plans(self) -> dict:
        return self.client.get_cable_plans()

    def get_recharge_pin_plans(self) -> dict:
        return self.client.get_recharge_pin_plans()

    def get_result_checker_prices(self) -> dict:
        return self.client.get_result_checker_prices()

    def get_smile_plans(self) -> dict:
        return self.client.get_smile_plans()

    def get_betting_billers(self) -> dict:
        return self.client.get_betting_billers()
    def purchase_electricity(
    self,
    disco: str,
    meter_number: str,
    meter_type: str,
    amount: str,  
    ) -> dict:
     return self.client.purchase_electricity(
        disco=disco,
        meter_number=meter_number,
        meter_type=meter_type,
        amount=amount,
    )