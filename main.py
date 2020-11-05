from rate_processing import RateProcessing as RPClass
from exchange_bot import ExchangeBot as EBClass


def main():
    rpclass = RPClass(300)
    rpclass.execute()
    EBClass(rpclass).execute()


if __name__ == '__main__':
    main()
