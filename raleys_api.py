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
blacklisted_categories = ["Baby Store"]
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

    if category in blacklisted_categories:
        return

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
        "Cookie": "_gcl_au=1.1.1022822.1665018196; _gcl_aw=GCL.1665018196.Cj0KCQjw1vSZBhDuARIsAKZlijRAAiO4TSaG_0F5p_F0M682lefiCm63jbD-Skc3Wl-hw3oABXnUkk0aAqA8EALw_wcB; _gid=GA1.2.1285164275.1665018196; _gac_UA-72342337-4=1.1665018196.Cj0KCQjw1vSZBhDuARIsAKZlijRAAiO4TSaG_0F5p_F0M682lefiCm63jbD-Skc3Wl-hw3oABXnUkk0aAqA8EALw_wcB; _fbp=fb.1.1665018195971.232443667; gig_bootstrap_3_GKrrAPXlGczVrnHfPGZmmUeR7ANOjp5s_fPs142vSSeUf_SVNfdAA11jS5mhdWKo=login_ver4; _clck=1vlxaw0^|1^|f5h^|0; notice_behavior=implied,eu; _clsk=1m72k9o^|1665018196931^|1^|1^|e.clarity.ms/collect; TS01363ad3=01c609ed7bc192131887e9d6ed8165a7d8d6a86cc1ee63a88a38151f0f8dd1f60f770f200b1ffe382352720b34ea6e77efcccf23e6; ajs_anonymous_id=7d74f9c0-6395-4a72-adcd-f4e8c8362153; _dd_r=1; _dd=0e97a5f3-fa1f-40af-8991-4be472d6c615; gig_canary=false; gig_canary_ver=13406-3-27750285; _uetsid=a9cfda10451211ed98c3af3eddc8052d; _uetvid=a9d019a0451211eda98369590a111f4f; session-ray=.eJxNjMtSgzAARf8l69qBTGEIOyVTG5TgYCvQDcMjLeERkEADdfx3cdy4OJtzH18guQxMlsC-pI1kG5D0bGhTwcQI7HGYViOZlLwTydjVTAAbsMUts-ec-9wlpzvRKXfRdpV6Dj-WlXsOm1vWoP7sENOrCKTVdaY4Vq_OXyeCTU2qTvdwvFIbvqN4HAZjGhr_8n4qwlmumzJr0cRC_VZEHvdFsBThSZK2KYvf_2MM6fFx9jFR3kHbvmDzKqI33Hvwfe_sdxGqlHoqd4N-tuSnGA9GTANNPWBqgQ2YJBsSXgDb0ExDQ8j6_gHg9VrI.Fh-65w.JtV9Zxk_VjaQLB4LO6sk0U9zgwg; TS014dd9f8=01c609ed7b84e90ebabed7d9b6d882d4ccce668626ee63a88a38151f0f8dd1f60f770f200bfc2a2aacfb7313484e6f86e1b516a2803986a30052d012c5cfa6d6548f62f56b; __adroll_fpc=5f51c75caf9f356f75e49954597413ad-1665018215185; __ar_v4=^%^7CFARJQKXGQ5FMVA2Y5EDNQ7^%^3A20221005^%^3A1^%^7CAA4HHHFBZVHRNCRWD6UMK2^%^3A20221005^%^3A1^%^7CDB6KNLYDXVASPHFNWFWEX3^%^3A20221005^%^3A1; gig_bootstrap_3_Tikef4yXIbKNr4dyPwM27hHXXPJDmg2vn3kJgkBOG8WpYu9P_rGd6tz883airYyj=login_ver4; liveagent_oref=https://www.raleys.com/; liveagent_ptid=39be19e8-cd74-4a3e-aef9-1c6b1e579678; _ga=GA1.2.1971745481.1665018196; _gat_UA-72342337-4=1; _br_uid_2=uid^%^3D5478923515559^%^3Av^%^3D15.0^%^3Ats^%^3D1665018216528^%^3Ahc^%^3D2; liveagent_sid=338d0055-fc75-4f76-9647-509cad149374; liveagent_vc=4; _ga_MXYSWRDLRL=GS1.1.1665018216.1.1.1665018257.0.0.0; _gat=1",
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
