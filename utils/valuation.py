def dcf_valuation(data, discount_rate=10, growth_rate=5, years=5):
    prices = data.get("c", [])
    if not prices:
        return 0
    last_price = prices[-1]
    cash_flow = last_price*0.1
    value = 0
    for i in range(1, years+1):
        value += cash_flow*((1+growth_rate/100)**i)/((1+discount_rate/100)**i)
    return value
