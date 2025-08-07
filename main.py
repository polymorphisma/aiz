def multiplicatoin(value):

    multiplication_val = 0

    def new_value():
        nonlocal multiplication_val
        multiplication_val += 1
        print(value * multiplication_val)
        return value * multiplication_val

    return new_value



hund_m = multiplicatoin(324)


hund_m()
hund_m()
hund_m()
hund_m()
hund_m()
hund_m()