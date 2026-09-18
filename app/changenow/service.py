from app.changenow.client import ChangeNOWClient


class ChangeNOWService:
    def __init__(self):
        self.client = ChangeNOWClient()

    # ========================================================
    # GET AVAILABLE CURRENCIES
    # ========================================================

    def get_currencies(self) -> list:
        return self.client.get_available_currencies()

    # ========================================================
    # VALIDATE CURRENCY PAIR
    # ========================================================

    def validate_currency_pair(
        self,
        *,
        from_currency: str,
        to_currency: str,
        from_network: str | None = None,
        to_network: str | None = None,
    ) -> dict:
        currencies = self.get_currencies()

        from_currency = from_currency.lower().strip()
        to_currency = to_currency.lower().strip()

        from_matches = [
            currency
            for currency in currencies
            if currency.get("ticker", "").lower()
            == from_currency
            and currency.get("sell") is True
            and (
                not from_network
                or currency.get("network", "").lower()
                == from_network.lower().strip()
            )
        ]

        to_matches = [
            currency
            for currency in currencies
            if currency.get("ticker", "").lower()
            == to_currency
            and currency.get("buy") is True
            and (
                not to_network
                or currency.get("network", "").lower()
                == to_network.lower().strip()
            )
        ]

        if not from_matches:
            raise ValueError(
                "Unsupported source currency/network: "
                f"{from_currency}/"
                f"{from_network or 'default'}"
            )

        if not to_matches:
            raise ValueError(
                "Unsupported destination currency/network: "
                f"{to_currency}/"
                f"{to_network or 'default'}"
            )

        return {
            "valid": True,
            "from": from_matches[0],
            "to": to_matches[0],
        }

    # ========================================================
    # CREATE EXCHANGE
    # ========================================================

    def create_exchange(
        self,
        *,
        from_currency: str,
        to_currency: str,
        from_amount: str,
        address: str,
        from_network: str | None = None,
        to_network: str | None = None,
        extra_id: str | None = None,
        refund_address: str | None = None,
        refund_extra_id: str | None = None,
        user_id: str | None = None,
        contact_email: str | None = None,
        source: str | None = None,
        flow: str = "standard",
        exchange_type: str = "direct",
        rate_id: str | None = None,
    ) -> dict:
        self.validate_currency_pair(
            from_currency=from_currency,
            to_currency=to_currency,
            from_network=from_network,
            to_network=to_network,
        )

        return self.client.create_exchange(
            from_currency=from_currency,
            to_currency=to_currency,
            from_amount=from_amount,
            address=address,
            from_network=from_network,
            to_network=to_network,
            extra_id=extra_id,
            refund_address=refund_address,
            refund_extra_id=refund_extra_id,
            user_id=user_id,
            contact_email=contact_email,
            source=source,
            flow=flow,
            exchange_type=exchange_type,
            rate_id=rate_id,
        )

    # ========================================================
    # GET EXCHANGE STATUS
    # ========================================================

    def get_exchange_status(
        self,
        transaction_id: str,
    ) -> dict:
        return self.client.get_exchange_status(
            transaction_id
        )

    # ========================================================
    # NORMALIZE STATUS
    # ========================================================

    def normalize_status(
        self,
        status: str | None,
    ) -> str:
        if not status:
            return "unknown"

        normalized = status.lower().strip()

        status_map = {
            "waiting": "waiting",
            "confirming": "confirming",
            "exchanging": "exchanging",
            "sending": "sending",
            "finished": "finished",
            "failed": "failed",
            "refunded": "refunded",
            "expired": "expired",
            "hold": "hold",
        }

        return status_map.get(
            normalized,
            normalized,
        )

    # ========================================================
    # VALIDATE STATUS TRANSITION
    # ========================================================

    def is_valid_status_transition(
        self,
        current_status: str | None,
        new_status: str | None,
    ) -> bool:
        """
        Prevent exchange statuses from moving backwards.

        Normal flow:

            waiting
                ↓
            confirming
                ↓
            exchanging
                ↓
            sending
                ↓
            finished

        Terminal states cannot be changed again.
        """

        if not new_status:
            return False

        new_status = self.normalize_status(
            new_status
        )

        if not current_status:
            return True

        current_status = self.normalize_status(
            current_status
        )

        # Same status is always safe.
        if current_status == new_status:
            return True

        # These statuses are terminal.
        terminal_statuses = {
            "finished",
            "failed",
            "refunded",
            "expired",
        }

        # Never allow a terminal transaction to move
        # to another state.
        if current_status in terminal_statuses:
            return False

        # Normal ChangeNOW progression.
        status_order = {
            "waiting": 0,
            "confirming": 1,
            "exchanging": 2,
            "sending": 3,
            "finished": 4,
        }

        # Normal forward transition.
        if (
            current_status in status_order
            and new_status in status_order
        ):
            return (
                status_order[new_status]
                >= status_order[current_status]
            )

        # A transaction can move into a failure,
        # refund, or expiration state.
        if new_status in {
            "failed",
            "refunded",
            "expired",
        }:
            return True

        # Unknown transitions are rejected.
        return False