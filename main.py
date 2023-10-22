import asyncio
import aiohttp
import argparse
import platform

from datetime import datetime, timedelta


parser = argparse.ArgumentParser(description="Currency exchange")
parser.add_argument("--days", "-d", help="Days", type=int, default=1)

args = vars(parser.parse_args())

days = int(args.get("days"))


async def date_for_fetch(days=1):
    dates = []
    end_date = datetime.now().date()

    for day in range(days):
        start_date = end_date - timedelta(day)
        formatted_date = start_date.strftime("%d.%m.%Y")
        dates.append(formatted_date)

    return dates


async def prepare_urls(dates):
    urls = []
    standart_url = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
    for date in dates:
        urls.append(standart_url + date)
    return urls


async def fetch_data(urls):
    try:
        async with aiohttp.ClientSession() as session:
            data = []
            for url in urls:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            output_data = await response.json()
                            data.append(output_data)
                        else:
                            print(
                                f"Помилка запиту. Статус код: {response.status}")
                except aiohttp.ClientConnectorError as err:
                    print(f'Connection error: {url}', str(err))
    except aiohttp.ClientConnectorError as err:
        print(f'Connection error: ', str(err))
    return data


async def parse_data(data):
    result = []
    # currency_dict = {}
    for value in data:
        date = value.get('date')
        currency_dict = {date: {}}
        exchange = value.get('exchangeRate')
        for rate in exchange:
            if rate['currency'] == 'USD':
                usd = {rate['currency']: {"sale": rate['saleRate'],
                              "purchase": rate['purchaseRate']}}
                print(usd)
                currency_dict[date].update(usd)
            if rate['currency'] == 'EUR':
                eur = {rate['currency']: {"sale": rate['saleRate'],
                                           "purchase": rate['purchaseRate']}}
                print(eur)
                currency_dict[date].update(eur)
        result.append(currency_dict)
    if not result:
        return print('На сьогоднішній день ще не має курсів валют')
    print(result)
    return result


async def main():
    dates = [await date_for_fetch(days)]
    urls = [await prepare_urls(date) for date in dates]
    data = [await fetch_data(url) for url in urls]
    result = [await parse_data(unparsed_data) for unparsed_data in data]
    # return await asyncio.gather(*result, return_exceptions=True)
    return result


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
