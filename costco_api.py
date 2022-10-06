from datetime import date
import requests
import asyncio
import json

other_departments = {
    "Auto Accessories": 15,
    "Babies": 23,
    "Books": 188,
    "Cleaning & Laundry Products": 77,
    "Computers": 217,
    "Electronics": 30,
    "Health & Personal Care": 8,
    "Home Improvement": 200,
    "Housewares": 213,
    "Lawn & Garden": 204,
    "Office Products": 12,
    "Small Appliances": 215,
    "Sporting Goods": 196,
    "Toys & Seasonal": 198
}

departments = {
    "Alcohol": 18,
    "Bakery & Desserts": 21,
    "Bed & Bath": 211,
    "Beverages": 48,
    "Breakfast": 115,
    "Canned Goods": 27,
    "Coffee & Sweeteners": 57,
    "Dairy & Eggs": 63,
    "Deli": 1,
    "Frozen Foods": 95,
    "Kirkland Signature": 107,
    "Meat & Seafood": 4,
    "Pantry & Dry Goods": 6,
    "Paper Products & Food Storage": 36,
    "Pets": 25,
    "Produce": 45,
    "Snacks, Candy & Nuts": 40
}
units_of_measurement = ['oz', 'fl oz', 'qt', 'qts', 'lb',
                        'lbs', 'ct', 'l', 'each', 'ct', 'gal', 'pk']
blacklisted_units = ['by', 'load', 'previously', 'frozen', '"', "'"]
costco_data = {}


def parse_size_string(parsed_size_string, base_price) -> list:
    unit = parsed_size_string.pop(-1)
    if len(parsed_size_string) < 5:
        if len(parsed_size_string) == 1:
            unit_price = base_price/float(parsed_size_string[0])
            return [unit_price, unit]
        elif len(parsed_size_string) == 2:
            unit_price = base_price/float(parsed_size_string[0])
            return [unit_price, f'{parsed_size_string[1]} {unit}']
        elif len(parsed_size_string) == 3:
            unit_price = base_price / \
                (float(parsed_size_string[0])*float(parsed_size_string[2]))
            return [unit_price, unit]
        elif len(parsed_size_string) == 4:
            unit_price = base_price / \
                (float(parsed_size_string[0])*float(parsed_size_string[2]))
            return [unit_price, f'{parsed_size_string[3]} {unit}']

    return [base_price, 'each']


def calculate_unit_price(
    product_name,
    size_string,
    unit,
    base_price,
    unit_price
) -> list:
    if size_string:
        parsed_size_string = size_string.lower().split()
        unit_price, unit = parse_size_string(parsed_size_string, base_price)

    elif not unit_price:
        unit_price = base_price
        unit = 'each'
        parsed_product_name = product_name.lower().split(",")
        parsed_size_string = parsed_product_name[-1].split()
        if len(parsed_product_name) > 1 and \
           any(s in parsed_size_string for s in units_of_measurement) and not \
           any(s in parsed_size_string for s in blacklisted_units):
            unit_price, unit = parse_size_string(
                parsed_size_string, base_price)

    return [round(unit_price, 2), unit.lower()]


def update_json_object(product_data):
    department = product_data['department'].replace('/', 'and')
    category = product_data['category'].replace('/', 'and')

    try:
        costco_data[department][category].append(product_data)
    except KeyError:
        try:
            costco_data[department][category] = [product_data]
        except KeyError:
            costco_data[department] = {category: [product_data]}


def send_request(id):
    url = "https://sameday.costco.com/api/v2/store_products"
    querystring = {"category_id": f"{id}", "limit": "10000"}
    headers = {
        "authority": "sameday.costco.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "referer": f"https://sameday.costco.com/shop/categories/{id}",
        "sec-ch-ua": "^\^Google"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    return response.json()


async def retrieve_data(id):
    try:
        request = await asyncio.to_thread(send_request, id)
        main_items = request["items"]
        featured_items = request["placements"]

        for item in main_items + featured_items:
            try:
                department = item["categories"][0]["name"]
                category = item["categories"][1]["name"]
                product_name = item["name"]
                base_price = item["base_price"]
                size_string = item["size_string"]
                unit_price = item["uom_price"]["price"]
                unit = item["uom_price"]["uom"]
            except KeyError:
                department = item["product"]["categories"][0]["name"]
                category = item["product"]["categories"][1]["name"]
                product_name = item["product"]["name"]
                base_price = item["product"]["base_price"]
                size_string = item["product"]["size_string"]
                unit_price = item["product"]["uom_price"]["price"]
                unit = item["product"]["uom_price"]["uom"]

            unit_price, unit = calculate_unit_price(
                product_name, size_string, unit, base_price, unit_price)
            today = date.today().strftime("%D")
            product_data = {
                'department': department,
                'category': category,
                'product_name': product_name,
                'base_price': base_price,
                'unit_price': unit_price,
                'unit': unit,
                'date': today
            }

            update_json_object(product_data)
    except Exception:
        pass


async def main():
    print("Costco START")

    # retrieve data from each costco department concurrently
    await asyncio.gather(*[retrieve_data(id) for id in departments.values()])

    with open('data/costco_data.json', 'w') as file:
        json_string = json.dumps(costco_data, indent=2)
        file.write(json_string)
        file.close
    print("Costco DONE")


if __name__ == "__main__":
    asyncio.run(main())
