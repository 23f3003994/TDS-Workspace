import ijson
from datetime import datetime

file_path = "q-json-customer-flatten.jsonl"

start_date = datetime.fromisoformat("2024-07-13T00:00:00+00:00")
end_date = datetime.fromisoformat("2024-09-10T23:59:59+00:00")

total_quantity = 0

with open(file_path, "r") as f:
    for customer in ijson.items(f, "", multiple_values=True):
        # Filter region
        if customer.get("region") != "Latin America":
            continue

        orders = customer.get("orders", [])
        for order in orders:
            # Filter order date
            order_date = datetime.fromisoformat(order["order_date"].replace("Z","+00:00"))
            if not (start_date <= order_date <= end_date):
                continue

            items = order.get("items", [])
            for item in items:
                # Filter channel and category
                if item.get("channel") != "Direct":
                    continue
                if item.get("category") != "Security":
                    continue

                # Add quantity
                total_quantity += item.get("quantity", 0)

print("Total Security items sold:", total_quantity)