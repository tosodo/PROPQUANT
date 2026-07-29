#!/usr/bin/env python3
"""
Unit tests for the PROPQUANT risk-compliance engine. Pure stdlib (unittest).
Worked numbers for the $50,000 2-Step Flex account. Run:

    python3 Src/research/test_pq_risk.py
"""
import unittest
from pq_risk import (FlexRules, risk_amount, position_size_lots,
                     daily_loss_headroom, order_allowed)

R = FlexRules()  # $50K defaults


class TestHardBreaches(unittest.TestCase):
    def test_max_loss_floor_is_44000(self):
        self.assertEqual(R.max_loss_floor(), 44_000.0)

    def test_max_loss_breach_boundary(self):
        self.assertTrue(R.max_loss_breached(44_000.0))     # touching = breach
        self.assertTrue(R.max_loss_breached(43_999.0))
        self.assertFalse(R.max_loss_breached(44_000.01))

    def test_daily_baseline_takes_higher(self):
        self.assertEqual(R.daily_baseline(50_000, 50_800), 50_800)
        self.assertEqual(R.daily_baseline(51_000, 50_200), 51_000)

    def test_daily_loss_floor_and_breach(self):
        base = 50_000.0
        self.assertEqual(R.daily_loss_floor(base), 48_000.0)   # 4% of 50k = 2k
        self.assertTrue(R.daily_loss_breached(48_000.0, base))
        self.assertFalse(R.daily_loss_breached(48_000.01, base))

    def test_daily_baseline_uses_higher_of_bal_equity(self):
        # if account is up, the 4% is measured off the higher figure
        base = R.daily_baseline(50_000, 51_000)
        self.assertEqual(R.daily_loss_floor(base), 48_960.0)   # 51k * 0.96

    def test_per_trade_idea_limit_is_1000(self):
        self.assertEqual(R.per_trade_idea_limit(), 1_000.0)
        self.assertTrue(R.trade_idea_breached(1_000.0))
        self.assertFalse(R.trade_idea_breached(999.99))


class TestPhaseTargets(unittest.TestCase):
    def test_targets(self):
        self.assertEqual(R.phase_target(1), 5_000.0)
        self.assertEqual(R.phase_target(2), 3_000.0)

    def test_phase_pass_needs_realized(self):
        self.assertTrue(R.phase_passed(5_000.0, 1))
        self.assertFalse(R.phase_passed(4_999.0, 1))
        self.assertTrue(R.phase_passed(3_000.0, 2))

    def test_concentration_flag_60pct(self):
        # phase1 target 5000 -> 60% = 3000
        self.assertTrue(R.concentration_flagged(3_000.01, 1))
        self.assertFalse(R.concentration_flagged(3_000.0, 1))


class TestInactivity(unittest.TestCase):
    def test_breach_at_30(self):
        self.assertTrue(R.inactivity_breached(30))
        self.assertFalse(R.inactivity_breached(29))

    def test_force_at_25(self):
        self.assertTrue(R.should_force_trade(25))
        self.assertFalse(R.should_force_trade(24))
        # forcing (25) happens strictly before breach (30) — the safety buffer
        self.assertLess(R.inactivity_force_days, R.inactivity_limit_days)


class TestSizing(unittest.TestCase):
    def test_risk_amount(self):
        self.assertEqual(risk_amount(R, 0.0075), 375.0)   # 0.75% of 50k

    def test_eurusd_sizing(self):
        # EURUSD: $10 per 1.0-pip... value per 1.0 PRICE per lot = $100,000.
        # risk $375, stop 0.0050 (50 pips): lots = 375 / (0.0050 * 100000) = 0.75
        lots = position_size_lots(375.0, 0.0050, 100_000.0, R.max_lots)
        self.assertAlmostEqual(lots, 0.75, places=6)

    def test_xauusd_sizing_not_hardcoded(self):
        # XAUUSD: $1 per $1 price move per 1.0 lot = $100 per lot per $1? Contract=100oz.
        # value per 1.0 price per lot = 100. risk $375, stop $15 -> 375/(15*100)=0.25 lots
        lots = position_size_lots(375.0, 15.0, 100.0, R.max_lots)
        self.assertAlmostEqual(lots, 0.25, places=6)

    def test_lot_cap(self):
        lots = position_size_lots(1_000_000.0, 0.0001, 100_000.0, R.max_lots)
        self.assertEqual(lots, 20.0)

    def test_zero_on_bad_inputs(self):
        self.assertEqual(position_size_lots(375.0, 0.0, 100_000.0, 20.0), 0.0)
        self.assertEqual(position_size_lots(-1.0, 0.005, 100_000.0, 20.0), 0.0)


class TestOrderGate(unittest.TestCase):
    def test_headroom(self):
        # baseline 50k, equity 49k -> floor 48k -> 1k headroom
        self.assertEqual(daily_loss_headroom(R, 49_000.0, 50_000.0), 1_000.0)
        self.assertEqual(daily_loss_headroom(R, 47_000.0, 50_000.0), 0.0)  # already under

    def test_blocks_when_risk_exceeds_headroom(self):
        # only $300 headroom, order risks $375 -> blocked
        self.assertFalse(order_allowed(R, equity=48_300.0, baseline=50_000.0,
                                       intended_risk_dollars=375.0,
                                       idea_loss_so_far=0.0, is_master=False))

    def test_allows_within_headroom(self):
        self.assertTrue(order_allowed(R, equity=49_500.0, baseline=50_000.0,
                                      intended_risk_dollars=375.0,
                                      idea_loss_so_far=0.0, is_master=False))

    def test_per_idea_blocks_on_master_only(self):
        # idea already down $700, new order risks $375 -> 1075 >= 1000 -> blocked on master
        self.assertFalse(order_allowed(R, equity=49_500.0, baseline=50_000.0,
                                       intended_risk_dollars=375.0,
                                       idea_loss_so_far=700.0, is_master=True))
        # same situation NOT on master (evaluation phase) -> idea cap doesn't apply
        self.assertTrue(order_allowed(R, equity=49_500.0, baseline=50_000.0,
                                      intended_risk_dollars=375.0,
                                      idea_loss_so_far=700.0, is_master=False))

    def test_blocks_when_already_breached(self):
        self.assertFalse(order_allowed(R, equity=44_000.0, baseline=50_000.0,
                                       intended_risk_dollars=10.0,
                                       idea_loss_so_far=0.0, is_master=False))


if __name__ == "__main__":
    unittest.main(verbosity=2)
