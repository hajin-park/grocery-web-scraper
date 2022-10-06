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
        # "cookie": "TealeafAkaSid=Rhk979qarpurYlrCUAAraDA911NzyGRA; visitorId=0183AAD60C130201809B9F7E5460529B; sapphire=1; brwsr=5e4d42c0-4513-11ed-924b-f7fef5cd8152; UserLocation=95340^|37.330^|-120.440^|CA^|US; egsSessionId=191f190f-9ef0-4dea-acc3-dd4f538442b2; accessToken=eyJraWQiOiJlYXMyIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJkY2QwOWY4My03MjYxLTQ1NDQtOTE4YS1jMTc1ZjVmYWMwYzEiLCJpc3MiOiJNSTYiLCJleHAiOjE2NjUxMDQ5MDEsImlhdCI6MTY2NTAxODUwMSwianRpIjoiVEdULjQzMTkyNzE0N2E3YTRhMDE4ZDE3ZWM3N2YxYzVlYjgzLWwiLCJza3kiOiJlYXMyIiwic3V0IjoiRyIsImRpZCI6ImUzNTNjZmZlYzFmMzU2MGVhZjE4NDAyNTg5NTI1NGE4ODEzNTdiMTFkMWM0ZGFlMWEzNWQ0MDE3MzNmYzMwMDkiLCJzY28iOiJlY29tLm5vbmUsb3BlbmlkIiwiY2xpIjoiZWNvbS13ZWItMS4wLjAiLCJhc2wiOiJMIn0.Dllcr6AZVQwhtwljNKo68nBA3U6YRtDM6FsMvWpzk3FJiLMr-WVSK_t3XjYVo33FqFB4QWuGjRYLTljCjFUpFpDBEZeomht68jy08uzU49_95_zNA9ezq7Wh6zXR6fAO5WGpSIM_8crtAPuTcw8F7I4RLiuzSz6jOT7JxFCXv8xEO-HSE0MwNXldXGpt0cdMdTf20GJEL86VIyx98k4WzeVddgAUnYSmGZvQb7sGpw_FvskB52fOMKLUXg6Wc6xzd6VwSSfUXHf9lmXeKpteP4u4mCshy2kTT7bPtqJQSb7ChnsDNCobbsGcjEMCNzPti2MV6-8HJ0lzxHiLOAkuVA; idToken=eyJhbGciOiJub25lIn0.eyJzdWIiOiJkY2QwOWY4My03MjYxLTQ1NDQtOTE4YS1jMTc1ZjVmYWMwYzEiLCJpc3MiOiJNSTYiLCJleHAiOjE2NjUxMDQ5MDEsImlhdCI6MTY2NTAxODUwMSwiYXNzIjoiTCIsInN1dCI6IkciLCJjbGkiOiJlY29tLXdlYi0xLjAuMCIsInBybyI6eyJmbiI6bnVsbCwiZW0iOm51bGwsInBoIjpmYWxzZSwibGVkIjpudWxsLCJsdHkiOmZhbHNlfX0.; refreshToken=KzP1Ly9hbVeAlANSMRFBWUKi80ytU1KbaqoOPsip7y64GS41cDSgVHJkCfpKYgLrdDd_ldqzM4abwXB9izpoag; __gads=ID=a5a47b52677dfe9c:T=1665018502:S=ALNI_Mb0iI_coh4TzsyVvnrSNko6em5oUA; __gpi=UID=000008d4ece9a0f1:T=1665018502:RT=1665018502:S=ALNI_MZOabjkTRld4JJZ5akZodRJROLY1w; ci_ref=tgt_adv_xasd0002; ci_pixmgr=imprad; ci_clkid=5e4d42c0n451311ed924bf7fef5cd8152; _gcl_au=1.1.1167823618.1665018502; ffsession=^{^%^22sessionHash^%^22:^%^22178c916970212a1665018501108^%^22^%^2C^%^22prevPageName^%^22:^%^22grocery^%^22^%^2C^%^22prevPageType^%^22:^%^22level^%^201^%^22^%^2C^%^22prevPageUrl^%^22:^%^22https://www.target.com/c/grocery/-/N-5xt1a^%^22^%^2C^%^22sessionHit^%^22:2^%^2C^%^22prevSearchTerm^%^22:^%^22non-search^%^22^}; _uetsid=5f24db40451311ed96c8537a8a73582b; _uetvid=5f24f3e0451311ed91709957ad34e360; _mitata=ZDgzYzcyMmQ1ZWMyZGNkMjViZTU1ZDk1MjdjZjE4NDVmNzZiZDA3NDY2MWQ2MzAxNGZkYTYzNmU1ZjUxNjFhMw==_/^@^#/1665018453_/^@^#/c1E96TVVyn7AdlHZ_/^@^#/OGEwZTljYWJiNzU2NzVkMjIzMGUwOWU2MTNjNWZjYTlkYmZiNWJiYjk4NTJiOTljY2M0OTU4NTQwMDJlYTcyMw==_/^@^#/230",
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
