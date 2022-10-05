import costco_api
import raleys_api
import target_api
import pyrebase
import asyncio


firebaseConfig = {
    "apiKey": "AIzaSyAdjEwdx-NqPxn3PcS7Eq1TvPPnF0igy1U",
    "authDomain": "ucentials-dev.firebaseapp.com",
    "databaseURL": "https://ucentials-dev-default-rtdb.firebaseio.com",
    "projectId": "ucentials-dev",
    "storageBucket": "ucentials-dev.appspot.com",
    "messagingSenderId": "469291886700",
    "appId": "1:469291886700:web:bb200805573c7cd2ed5049",
    "measurementId": "G-631JFGRJ1B"
}
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
