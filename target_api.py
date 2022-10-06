from datetime import date
import requests
import asyncio
import json


departments = {
    "Bakery & Bread": "5xt19",
    "Beverages": "5xt0r",
    "Breakfast & Cereal": "wo2mp",
    "Candy": "5xt0d",
    "Dairy": "5xszm",
    "Deli": "5hp74",
    "Frozen Foods": "5xszd",
    "Meat & Seafood": "5xsyh",
    "Pantry": "5xt13",
    "Produce": "u7fty",
    "Snacks": "5xsy9",
    "Wine, Beer & Liquor": "5n5q6"
}
units_of_measurement = ['oz', 'fl oz', 'qt', 'qts', 'lb',
                        'lbs', 'ct', 'l', 'each', 'ct', 'gal', 'pk']
blacklisted_units = ['by', 'load', 'previously', 'frozen', '"', "'"]
target_data = {}


def update_json_object(product_data):
    department = product_data['department'].replace('/', 'and')
    category = product_data['category'].replace('/', 'and')

    try:
        target_data[department][category].append(product_data)
    except KeyError:
        try:
            target_data[department][category] = [product_data]
        except KeyError:
            target_data[department] = {category: [product_data]}


def send_request(id, offset):
    url = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
    querystring = {
        "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96",
        "category": f"{id}",
        "channel": "WEB",
        "count": "28",
        "offset": f"{offset}",
        "page": f"/c/{id}",
        "platform": "desktop",
        "pricing_store_id": "641",
        "scheduled_delivery_store_id": "641",
        "store_ids": "641",
        "useragent": "Mozilla^%^2F5.0 ^%^28Windows NT 10.0^%^3B Win64^%^3B x64^%^29 AppleWebKit^%^2F537.36 ^%^28KHTML^%^2C like Gecko^%^29 Chrome^%^2F106.0.0.0 Safari^%^2F537.36",
        "visitor_id": "0183912A1E1C02018675F83B12A8EA93",
        "zip": "95340"}
    headers = {
        "authority": "redsky.target.com",
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "origin": "https://www.target.com",
        "sec-ch-ua": "^\^Chromium^^;v=^\^106^^, ^\^Google"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    return response.json()


async def retrieve_data(id):
    offset = 0
    while True:
        try:
            request = await asyncio.to_thread(send_request, id, offset)
            offset += 28
            products = request["data"]["search"]["products"]
            department = request["data"]["search"]["search_response"]["bread_crumb_list"][0]["values"][2]["label"]
            category = request["data"]["search"]["search_response"]["bread_crumb_list"][0]["values"][3]["label"]

            if not products:
                break

            for product in products:
                product_name = product["item"]["product_description"]["title"]
                base_price = float(
                    product["price"]["formatted_current_price"][1:])
                today = date.today().strftime("%D")

                product_data = {
                    'department': department,
                    'category': category,
                    'product_name': product_name,
                    'base_price': base_price,
                    'date': today
                }

                update_json_object(product_data)
        except Exception:
            print(f"Skipping {id}: {offset}-{offset+28}")


async def retrieve_categories(id):
    try:
        request = await asyncio.to_thread(send_request, id, 0)
        facet_list = request["data"]["search"]["search_response"]["facet_list"]
        for list in facet_list:
            if list["facet_id"] == "d_categorytaxonomy":
                options = list["options"]
                break
        ids = [option["value"] for option in options]
        await asyncio.gather(*[retrieve_data(id) for id in ids])
    except Exception:
        print(f"Skipping {id}")


async def main():
    print("Target START")

    # retrieve data from each target grocery department concurrently
    await asyncio.gather(*[retrieve_categories(id) for id in departments.values()])

    with open('data/target_data.json', 'w') as file:
        json_string = json.dumps(target_data, indent=2)
        file.write(json_string)
        file.close

    print("Target DONE")


if __name__ == "__main__":
    asyncio.run(main())
