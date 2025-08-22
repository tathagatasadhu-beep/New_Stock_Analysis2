def dcf_valuation(
    start_fcf_per_share: float,
    growth_rate: float = 5.0,
    discount_rate: float = 10.0,
    terminal_growth: float = 2.5,
    years: int = 5,
) -> float:
    """
    Simple per-share DCF: projects starting FCF/share at growth_rate for `years`,
    discounts at discount_rate, adds terminal value (Gordon Growth).
    """
    if discount_rate <= terminal_growth:
        # avoid division by zero in terminal formula; nudge if needed
        terminal_growth = max(0.0, min(terminal_growth, discount_rate - 0.1))

    dr = discount_rate / 100.0
    gr = growth_rate / 100.0
    tg = terminal_growth / 100.0

    pv = 0.0
    cf = float(start_fcf_per_share)
    for t in range(1, years + 1):
        cf *= (1 + gr)
        pv += cf / ((1 + dr) ** t)

    # Terminal value at end of year N
    terminal = (cf * (1 + tg)) / (dr - tg)
    pv += terminal / ((1 + dr) ** years)

    return max(pv, 0.0)
