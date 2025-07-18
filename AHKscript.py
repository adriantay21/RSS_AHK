from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass
import time
from ahk import AHK

ahk = AHK()

# --------------------------------------------------------------------------- #
class Side(Enum):
    BUY = auto()
    SELL = auto()

class OrderType(Enum):
    LIMIT = auto()
    MARKET = auto()


# --------------------------------------------------------------------------- #
DELAY_PROFILES: dict[str, dict[str, float]] = {
    'Fast':   dict(short=0.75, long=1.5, tab=0.05),
    'Medium': dict(short=1.0, long=2.0, tab=0.06),
    'Slow':   dict(short=1.5, long=3.0, tab=0.10),
    'Slower': dict(short=2.0, long=4.0, tab=0.15),
}

# --------------------------------------------------------------------------- #
@dataclass
class OrderEnv:
    side: Side
    order_type: OrderType
    extended: bool

    def tabs_to_price_field(self) -> int:
        base = 15
        if self.order_type is OrderType.MARKET:
            base -= 2
        return base


# --------------------------------------------------------------------------- #
def ahk_script(
    num_accounts: int,
    extended_hours: bool,
    start_from: int,
    stop_event,
    market_limit: str,
    buy_sell: str,
    delay_speed: str,
    update_status,
    price: float,
) -> None:
    
    # set delays based on the selected profile

    delays = DELAY_PROFILES.get(delay_speed, DELAY_PROFILES['Medium'])
    short_delay, long_delay, tab_delay = (
        delays['short'],
        delays['long'],
        delays['tab'],
    )

    env = OrderEnv(
        side=Side.BUY if buy_sell == 'Buy' else Side.SELL,
        order_type=OrderType.LIMIT if market_limit == 'Limit' else OrderType.MARKET,
        extended=extended_hours,
    )

    # helpers --------------------------------------------------------------- #
    def safe_send(cmd: str) -> None:
        if not stop_event.is_set():
            ahk.send(cmd)

    def safe_click() -> None:
        if not stop_event.is_set():
            ahk.click()

    def sleep_with_stop(sec: float) -> None:
        end = time.monotonic() + sec
        while time.monotonic() < end and not stop_event.is_set():
            time.sleep(min(0.1, end - time.monotonic()))

    def tab_n(n: int) -> None:
        for _ in range(n):
            safe_send('{Tab}')
            sleep_with_stop(tab_delay)

    # ----------------------------------------------------------------------- #
    for i in range(start_from, num_accounts):
        if stop_event.is_set():
            break

        acct = i + 1
        update_status(acct)

        # account selection
        safe_click()
        sleep_with_stop(0.5)
        safe_send('{Tab}{Tab}{Enter}')
        sleep_with_stop(0.5)
        safe_send('{Down}' * (acct - 2))
        sleep_with_stop(0.5)
        safe_send('{Enter}')
        sleep_with_stop(short_delay)

        # market/limit order selection
        if env.order_type is OrderType.LIMIT:
            tab_n(env.tabs_to_price_field() - (4 if env.side is Side.BUY else 3))
            if env.extended:
                safe_send(str(price))
                tab_n(2 if env.side is Side.BUY else 3)
            else:
                safe_send('{Space}{Right}{Tab}')
                safe_send(str(price))
                tab_n(3 if env.side is Side.BUY else 4)
        else:  # MARKET
            tab_n(env.tabs_to_price_field() - (1 if env.side is Side.SELL else 3))
            safe_send('{Space}')
            tab_n(3)

        # confirm & close
        sleep_with_stop(0.5)
        safe_send('{Enter}')
        sleep_with_stop(long_delay)
        safe_send('{Enter}')
        sleep_with_stop(short_delay)
        safe_click()
