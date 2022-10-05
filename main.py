import costco_api
import raleys_api
import target_api
import pyrebase
import asyncio
import json


with open('keys.json', 'r') as file:
    data = file.read()
    keys = json.loads(data)
    firebaseConfig = keys["firebaseConfig"]
    file.close


firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()


async def main():

    # retrieve data from every store concurrently
    total_data = await asyncio.gather(
        costco_api.main(),
        raleys_api.main(),
        target_api.main()
    )

    # upload data to firebase
    for data in total_data:
        pass

if __name__ == "__main__":
    asyncio.run(main())
