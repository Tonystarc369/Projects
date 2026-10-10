import numpy as np

class IRSContract:
    def __init__(self, notional=50e6, maturity=5.0, fixed_rate=0.04, pay_fixed=True):
        self.notional = notional
        self.maturity = maturity
        self.fixed_rate = fixed_rate
        self.pay_fixed = pay_fixed
        
    def value(self, r, t):
        if t >= self.maturity:
            return 0.0
        remaining_t = self.maturity - t
        df = np.exp(-r * remaining_t)
        annuity = (1.0 - df) / np.maximum(r, 1e-5)
        val = self.notional * (r - self.fixed_rate) * annuity
        return val if self.pay_fixed else -val

class FXForwardContract:
    def __init__(self, notional_usd=30e6, strike_fx=83.5, maturity=2.0):
        self.notional_usd = notional_usd
        self.strike_fx = strike_fx
        self.maturity = maturity
        
    def value(self, r, fx, t):
        if t >= self.maturity:
            return 0.0
        remaining_t = self.maturity - t
        df = np.exp(-r * remaining_t)
        val = self.notional_usd * (fx - self.strike_fx) * df
        return val

class CDSContract:
    def __init__(self, notional=20e6, coupon=0.015, maturity=3.0, lgd=0.6):
        self.notional = notional
        self.coupon = coupon
        self.maturity = maturity
        self.lgd = lgd
        
    def value(self, r, cs, t):
        if t >= self.maturity:
            return 0.0
        remaining_t = self.maturity - t
        df = np.exp(-r * remaining_t)
        risky_annuity = (1.0 - np.exp(-(r + cs/self.lgd) * remaining_t)) / np.maximum(r + cs/self.lgd, 1e-5)
        val = self.notional * (cs - self.coupon) * risky_annuity
        return val