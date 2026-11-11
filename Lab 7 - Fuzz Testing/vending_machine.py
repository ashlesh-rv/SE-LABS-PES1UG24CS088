
def parse_coins(coins_csv):
    if not isinstance(coins_csv, str) or not coins_csv.strip():
        return []

    try:
        coins = [int(c.strip()) for c in coins_csv.split(',')]

        if any(c < 0 for c in coins):
            return []

        return coins
    except ValueError:
        return []


def slot_position(code):
    if not isinstance(code, str):
        return None

    code = code.strip()

    if len(code) < 2:
        return None

    if not code[0].isalpha() or not code[1:].isdigit():
        return None

    row = ord(code[0].upper()) - ord('A')
    column = int(code[1:]) - 1

    if column < 0:
        return None

    return row, column


def change_due(payment):
    if not isinstance(payment, str):
        return "0 five-coins"

    parts = payment.split('/')

    if len(parts) != 2:
        return "0 five-coins"

    try:
        paid = int(parts[0].strip())
        price = int(parts[1].strip())

        if paid < 0 or price < 0 or paid < price:
            return "0 five-coins"

        change = paid - price
        return str(change // 5) + ' five-coins'

    except ValueError:
        return "0 five-coins"


def main():
    print("==== Running parse_coins ====")
    user_input = input("Enter coin values as CSV (e.g. 5,10,25): ")
    result = parse_coins(user_input)
    print("Coins:", result)

    print("\n==== Running slot_position ====")
    user_input = input("Enter a slot code (e.g. B7): ")
    result = slot_position(user_input)
    print("Row and Column:", result)

    print("\n==== Running change_due ====")
    user_input = input("Enter paid/price (e.g. 200/150): ")
    result = change_due(user_input)
    print("Change Due:", result)


if __name__ == "__main__":
    main()
