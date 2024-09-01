import datetime 
from datetime import timezone, datetime



def main():
    now = datetime.now(timezone.utc).strftime("%H:%M:%S %m.%d.%Y")
    print(now)
    




if __name__ == "__main__":
    main()