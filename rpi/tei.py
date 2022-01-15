import bluetooth
import uuid
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread
import sys
import os

# Constants
MY_UUID = "00001101-0000-1000-8000-00805F9B34FB"
IMAGES = {
    1: "/home/pi/Desktop/redycler/rpi/assets/1.png",
    2: "/home/pi/Desktop/redycler/rpi/assets/4.png",
    3: "/home/pi/Desktop/redycler/rpi/assets/3.png"
}

# Starting code to connect to Android
host = ""
port = bluetooth.PORT_ANY # RPi Port 1 = BLE

# Creating Socket bluetooth RFCOMM communication
server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

print("Bluetooth Socket Created")
try:
    server.bind((host,port))
    print("Bluetooth Binding Completed")
except:
    print("Bluetooth Binding Failed")

server.listen(1) # One connection at a time

print("Server UUID:", MY_UUID)
bluetooth.advertise_service(server, "RedyclerService", MY_UUID)

# Server accepts the client requests and assigns a MAC address
client, address = server.accept()
print("Connected To", address)
print("Client:", client)

# Create a thread to receive Bluetooth messages and put it on the queue
def bluetoothThread(q):
    try:
        while True:
            # Receiving data
            data = client.recv(1024) # 1024 is buffer size
            selection = int.from_bytes(data, "little")
            q.append(selection)
    except:
        # Close the client and server connection
        q.put(0)
        client.close()
        server.close()

# Select correct image
def getPilImage(selection):
    pilImage = None
    if selection in IMAGES:
        pilImage = Image.open(os.path.abspath(IMAGES[selection]))
    return pilImage

# Queue to communicate between threads
queue = []

# Callback function and process first item in queue
def processQueue(q, root):
    print("Checking Queue...")
    if not q:
        root.after(2000, processQueue, q, root)
        return
    # Pop everything off the queue
    selection = q.pop(0)
    while q:
        q.pop(0)
    print("Found item:", selection)
    root.destroy()
    setupRoot(selection)

# Setup root for new image
def setupRoot(selection):
    pilImage = getPilImage(selection)
    if not pilImage:
        sys.exit("ERROR")
    root = tk.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()
    root.bind("<Escape>", lambda e: root.destroy())
    canvas = tk.Canvas(root,width=w,height=h)
    canvas.pack()
    canvas.configure(background='black')
    pilImage = pilImage.resize((w,h), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(0,0,image=image, anchor="nw")
    root.after(2000, processQueue, queue, root)
    root.mainloop()

bleThread = Thread(target=bluetoothThread, args=(queue, ))
bleThread.start()
setupRoot(2)
