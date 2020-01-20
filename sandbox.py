from pyIB.ib.ibfunc import ibfunc



def main():
    print("Starting")
    ibf=ibfunc()
    try:
        print(ibf.ibc.isConnected())
    except AttributeError:
        print("Attribute Error!")

    print("TIME TO MAKE SOME BENJAMINS!!!!!")

if __name__ == '__main__':
    main()

