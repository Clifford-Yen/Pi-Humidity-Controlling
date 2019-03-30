# Introduction

With the help of DHT22, one can set up a cron job on Raspberry Pi to build a database storing temperature and humidity data continuously. By analyzing these data in real time, we can also set up a cron job to determine the most efficient time to turn on the air conditioner running in dehumidifier mode to control the humidity in a closed space.

## BOM (Bill of Materials)

To complete this project, you will need all of the following materials.

- Raspberry Pi [1]
- DHT22, a temperature and humidity sensor
- IR Receiver Module (3.3V type) - TSOP38238
- IR LED (generic)
- 2N2222A NPN Transistor [2]
- 1/4W Resistors [3]
- Breadboard and jumper wires [4]

Note:

1. Pick whichever model you like. But it's much easier for beginners to use Model B or Model A.  
If you decide to go Model B, then it might be a good idea to also pick an official power supply since model B is more power-hungry. For Model A, a spare phone charger with a micro USB cable should be fine.
2. Be sure to check the full name of this transistor before you use it since there are some variants of 2N2222. But even if you bought a different variant, you can still use it. All you need to notice is the pinout of the collector and emitter.  
(Don't be afraid if you don't know what are the collector and emitter. I didn't know they at first either. And you can complete this project without knowing what it really is.)
3. Two 10K Ohm resistors are a must. If you are going to use 2N2222A, a 680 Ohm is also a correct choice. The third resistor depends on the spec of the IR LED you choose to use. For example, if you choose to use TSAL6200, then you should pick a resistor around 36 Ohm.  
For more information, please refer to [this great tutorial](https://www.instructables.com/id/Raspberry-Pi-Zero-Universal-Remote/ "Raspberry Pi Zero Universal Remote: 27 Steps (with Pictures)"). Step 4 of this tutorial will show you how these resistor values are chosen.
4. I used 10 female to male jumper wires in this project. You can also pick some male to male jumper wires if you prefer to make a more serious arrangement on the breadboard.  
On the other hand, for advanced makers, you might be capable of welding something and want to go Model Zero without using breadboard and jumper wires.

## Webpage Screenshot

![Webpage Screenshot](/Webpage_Screenshot.jpg?raw=true "Webpage Screenshot")