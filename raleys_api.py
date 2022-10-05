from datetime import date
import requests
import asyncio
import json

other_departments = {
    "Health & Beauty": 492,
    "Household & Pet": 902
}

departments = {
    "Beer & Wine": 401,
    "Beverages": 139,
    "Dairy": 121,
    "Deli & Bakery": 638,
    "Frozen": 202,
    "Meat & Seafood": 52,
    "Produce": 1,
    "Pantry": 685,
}
units_of_measurement = ['oz', 'fl oz', 'qt', 'qts', 'lb',
                        'lbs', 'ct', 'l', 'each', 'ct', 'gal', 'pk']
blacklisted_units = ['by', 'load', 'previously', 'frozen', '"', "'"]
raleys_data = {}


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
        raleys_data[department][category].append(product_data)
    except KeyError:
        try:
            raleys_data[department][category] = [product_data]
        except KeyError:
            raleys_data[department] = {category: [product_data]}


def send_request(id):
    url = "https://shop.raleys.com/api/v2/store_products"
    querystring = {"category_id": f"{id}", "limit": "10000"}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "gig_bootstrap_3_GKrrAPXlGczVrnHfPGZmmUeR7ANOjp5s_fPs142vSSeUf_SVNfdAA11jS5mhdWKo=login_ver4; gig_canary=false; gig_bootstrap_3_Tikef4yXIbKNr4dyPwM27hHXXPJDmg2vn3kJgkBOG8WpYu9P_rGd6tz883airYyj=login_ver4; _dd_r=1; _dd=5123d3cb-afa1-4e01-a9fe-d530a081e810; TS01363ad3=01bcf4b49ffee783169be68db584d4889d00987523807b0429f985265f593dc4979c0470a8c0471c28dbb3faa98b8285c0ed70802d; gig_canary_ver=13394-3-27719925; session-ray=.eJxNjMlugzAARP_F5zQyDokEN0QralITlUAgvVgsjmwWgzBOg6v-e6l66WEub97MF6C3iSkO3FvRKbYBdGRTX0gmZ-DOk16JYkqJQdJ5aJkELmBLyMugEicR4tRgKxKhs12hVaHLssZUqLuXnTN--PhAGmyiJl2IwfDN_3Ny1LW4GSzy7BmSYEiWT3HN4rnI9v_6UdfZQ60bXvaOZpl1r3MiTjJe6ixVuO94_fufXBFpKpsYD0YSbrlvbNSH-RnGR3rWQTu3ATuwxHul748XrX1O7BAVxyeCwQZoxSYqauDuIdxZyN59_wAwXFt1.FgPutQ.b8q-WJQgs2h-FThnJagt3Nz2jI0; TS014dd9f8=01bcf4b49f895b5f47bec798699889a5c77c80528e0f113bd1be3f90a4ac398a0f2a4db80cf3f9d2036bc936a9ddc4fa77402d2c8b67d5a9eacfb0017c623b486133969675",
        "Referer": f"https://shop.raleys.com/shop/categories/{id}",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "User-Context": "eyJTdG9yZUlkIjoiMTAzIiwiRnVsZmlsbG1lbnRUeXBlIjoiaW5zdG9yZSJ9",
        "X-Unata-Mode": "grocery",
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
                try:
                    category = item["categories"][1]["name"]
                except IndexError:
                    category = "Counter"
                product_name = item["name"]
                base_price = item["base_price"]
                size_string = item["size_string"]
                unit_price = item["uom_price"]["price"]
                unit = item["uom_price"]["uom"]
            except KeyError:
                department = item["product"]["categories"][0]["name"]
                try:
                    category = item["product"]["categories"][1]["name"]
                except IndexError:
                    category = "Counter"
                product_name = item["product"]["name"]
                base_price = item["product"]["base_price"]
                size_string = item["product"]["size_string"]
                unit_price = item["product"]["uom_price"]["price"]
                unit = item["product"]["uom_price"]["uom"]

            unit_price, unit = calculate_unit_price(
                product_name, size_string, unit, base_price, unit_price)
            today = date.today().strftime("%B %D, %Y")
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
    print("Raleys START")

    # retrieve data from each raleys department concurrently
    await asyncio.gather(*[retrieve_data(id) for id in departments.values()])

    with open('data/raleys_data.json', 'w') as file:
        json_string = json.dumps(raleys_data, indent=2)
        file.write(json_string)
        file.close
    print("Raleys DONE")


if __name__ == "__main__":
    asyncio.run(main())
