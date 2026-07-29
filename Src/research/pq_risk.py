#!/usr/bin/env python3
"""
PROPQUANT — risk-compliance engine (pure, deterministic, correct-by-construction).

This is the "safety cage" from Design/system_design.md. It does NOT try to make money;
it makes sure no strategy can breach the FundingPips 2-Step Flex rules. Every function is
PURE — it takes explicit numbers and returns a decision — so it can be unit-tested offline
(no live account needed) and mirrored line-for-line in the MQL5 EA later.

All limits below are the 2-Step Flex rules for the $50,000 account (see Brief/brief.md).
Numbers are stated, not hidden, so a reviewer can check them against the firm's page.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class FlexRules:
    """2-Step Flex limits. Defaults are the $50K account."""
    account_size: float = 50_000.0
    max_loss_pct: float = 0.12          # hard floor = start * (1 - 0.12) = 44,000
    daily_loss_pct: float = 0.04        # daily floor = baseline * (1 - 0.04)
    per_trade_idea_pct: float = 0.02    # >$25k accounts: 2% = $1,000 (Master only)
    phase1_target_pct: float = 0.10     # +10% = $5,000
    phase2_target_pct: float = 0.06     # +6%  = $3,000
    concentration_frac: float = 0.60    # single idea > 60% of phase target -> flag
    inactivity_limit_days: int = 30     # no fully-closed trade in 30 days = breach
    inactivity_force_days: int = 25     # force a closed trade by day 25 (safety buffer)
    max_lots: float = 20.0              # platform cap (1.0 for crypto)

    # ----- hard breaches -----
    def max_loss_floor(self) -> float:
        return self.account_size * (1.0 - self.max_loss_pct)

    def max_loss_breached(self, equity: float) -> bool:
        """Equity (incl. floating P&L) at or below the static 12% floor -> breach."""
        return equity <= self.max_loss_floor()

    @staticmethod
    def daily_baseline(open_balance: float, open_equity: float) -> float:
        """Baseline set at 00:00 server time = the HIGHER of opening balance / equity."""
        return max(open_balance, open_equity)

    def daily_loss_floor(self, baseline: float) -> float:
        return baseline * (1.0 - self.daily_loss_pct)

    def daily_loss_breached(self, equity: float, baseline: float) -> bool:
        return equity <= self.daily_loss_floor(baseline)

    def per_trade_idea_limit(self) -> float:
        return self.account_size * self.per_trade_idea_pct

    def trade_idea_breached(self, idea_loss: float) -> bool:
        """idea_loss = combined realized + floating LOSS for one idea (positive number)."""
        return idea_loss >= self.per_trade_idea_limit()

    # ----- phase targets -----
    def phase_target(self, phase: int) -> float:
        pct = self.phase1_target_pct if phase == 1 else self.phase2_target_pct
        return self.account_size * pct

    def phase_passed(self, realized_profit: float, phase: int) -> bool:
        """Only CLOSED-trade (realized) profit counts toward a target."""
        return realized_profit >= self.phase_target(phase)

    # ----- soft breaches -----
    def concentration_flagged(self, idea_profit: float, phase: int) -> bool:
        return idea_profit > self.concentration_frac * self.phase_target(phase)

    def inactivity_breached(self, days_since_last_close: float) -> bool:
        return days_since_last_close >= self.inactivity_limit_days

    def should_force_trade(self, days_since_last_close: float) -> bool:
        return days_since_last_close >= self.inactivity_force_days


def risk_amount(rules: FlexRules, risk_pct: float) -> float:
    """Dollar risk for one trade, e.g. 0.75% of $50K = $375."""
    return rules.account_size * risk_pct


def position_size_lots(risk_dollars: float, stop_distance_price: float,
                       value_per_price_per_lot: float, max_lots: float) -> float:
    """
    Lots such that hitting the stop loses ~risk_dollars.

      loss_if_stopped = lots * stop_distance_price * value_per_price_per_lot
      => lots = risk_dollars / (stop_distance_price * value_per_price_per_lot)

    `value_per_price_per_lot` is money lost per 1.0 of price movement per 1.0 lot for THIS
    instrument (NOT a hard-coded $10/pip — that is only EURUSD and was a bug in the seed code).
    Capped at max_lots. Returns 0.0 if inputs are non-positive.
    """
    denom = stop_distance_price * value_per_price_per_lot
    if denom <= 0 or risk_dollars <= 0:
        return 0.0
    return min(risk_dollars / denom, max_lots)


def daily_loss_headroom(rules: FlexRules, equity: float, baseline: float) -> float:
    """Dollars of loss still allowed today before the 4% daily breach. Never negative."""
    return max(0.0, equity - rules.daily_loss_floor(baseline))


def order_allowed(rules: FlexRules, equity: float, baseline: float,
                  intended_risk_dollars: float, idea_loss_so_far: float,
                  is_master: bool) -> bool:
    """
    Pre-trade gate: refuse an order that could, at its own stop, breach a cap.
    Conservative: uses the intended risk as the worst case for the new order.
    """
    if rules.max_loss_breached(equity):
        return False
    if rules.daily_loss_breached(equity, baseline):
        return False
    # would this order's worst case blow the remaining daily headroom?
    if intended_risk_dollars > daily_loss_headroom(rules, equity, baseline):
        return False
    # per-trade-idea cap (Master account only)
    if is_master and (idea_loss_so_far + intended_risk_dollars) >= rules.per_trade_idea_limit():
        return False
    return True
