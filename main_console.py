from fetch_data_and_signal import backtest_coins_by_params,backtest_coin_with_param
from analysis import full_analysis
import asyncio
import json

def read_data():
    try:
        with open('config.json', 'r') as f:
            data=json.load(f)
    except:
        data={}
    return data


async def main():
    data=read_data()
    while True:

        command = input("Введите команду (run, coin, analysis): ").strip().lower()
        if command == "run":
            await backtest_coins_by_params(data)
            print('Сбор данных завершен')
        elif command == "coin":
            data=read_data()

            await backtest_coin_with_param(data)
            print("Сбор данных завершен")

        elif command == "analysis":
            data=read_data()


            full_analysis(data)
            print("Анализ завершен")
        else:
            print("Неизвестная команда. Попробуйте снова.")

if __name__ == "__main__":
    asyncio.run(main())