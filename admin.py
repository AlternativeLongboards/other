import serial
import time
import datetime
from pymongo import MongoClient


client = MongoClient('mongodb://213.32.89.50:27017/')

db = client['production']
staff = db['staff']


MasterModule = serial.Serial('/dev/ttyUSB0', 115200)
time.sleep(3)

class comm():
    def serial_write(data_to_send):
        MasterModule.write(str(data_to_send).encode('utf-8'))
        MasterModule.flush()
        time.sleep(0.01)

    def serial_clear():
        if (MasterModule.inWaiting() > 0):
            MasterModule.read(MasterModule.inWaiting())
            MasterModule.flush()

    def serial_read():
        myData = MasterModule.read(MasterModule.inWaiting())
        return myData


def ask_data():

    readData = ""
    sendConfirmation = ""
    readConfirmation = ""
    counter = 0

    while (readConfirmation[0:4] != 'AC2E' or counter < 3):
        readData = ""
        sendConfirmation = ""
        readConfirmation = ""
        comm.serial_clear()
        comm.serial_write('AC1E')
        time.sleep(0.01)
        readData= comm.serial_read().decode()
        if (readData[0:1] != '0'):
            sendConfirmation = 'AD' + str(readData[8:17]) + 'E'
            comm.serial_clear()
            comm.serial_write(sendConfirmation)
            time.sleep(0.01)
            readConfirmation = comm.serial_read().decode()
            if (readConfirmation[0:4] == 'AC2E'):
                return readData[1:17]
                break
            else:
                counter = counter + 1
                if (counter == 3):
                    return -1
                    break
        else:
            return 0
            break

def find_worker_name():

    worker_code = ""
    worker_name = ""


    while (len(worker_name) == 0):
        worker_code = ask_data()
        if (worker_code == 0 or worker_code == -1):
            worker_code = ""
        worker_name = list(staff.find({"code": worker_code[3:16]}, {"name": 1, "_id": 0}))
        worker_name = str(worker_name)
        worker_name = worker_name[11:len(worker_name) - 3]

        if (worker_name != ""):
            return worker_name
        elif (worker_code != ""):
            print("ZŁA KARTA CWELU")
            worker_code = ""

def add_worker():

    worker_code = ""
    worker_name = input('Podaj imię pracownika i zeskanuj kartę \n' )

    while(len(worker_code) == 0):
        worker_code = ask_data()
        if (worker_code == 0 or worker_code == -1):
            worker_code = ""

    is_present = list(staff.find({"code": worker_code[3:16]}, {"name": 1, "_id":0}))
    is_present = str(is_present)
    if (len(is_present) == 2):
        new_worker = {


            "name": worker_name,
            "code": worker_code[3:16]

        }
        staff.insert_one(new_worker)
        print('Dodano pracownika')
    else:
        print('Pracownik jest juz w bazie')

def main_handling():
    while (True):
        data = ask_data()
        if (data != 0 and data != -1):

            if (collection_02.find({"code": str(data[3:16])}).count() == 0):

                new_data = {

                    "minute": str(datetime.datetime.now().strftime('%M')),
                    "model": data[5:7],
                    "code": data[3:16],
                    "worker": worker,
                    "operation": "02",
                    "month": str(datetime.datetime.now().strftime('%m')),
                    "second": str(datetime.datetime.now().strftime('%S')),
                    "day": str(datetime.datetime.now().strftime('%d')),
                    "hour": str(datetime.datetime.now().strftime('%H')),
                    "year": str(datetime.datetime.now().strftime('%Y')),

                }

                collection_02.insert_one(new_data)
                print(data + " " + str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')))
            else:
                print('ELEMENT JEST W BAZIE')



print(MasterModule.name)

print("ZESKANUJ KARTE PRACOWNIKA")

add_worker()


