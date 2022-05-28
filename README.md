# airplane-boarding
airplane boarding simulator in python

## Installation

You need to have python 3 and pip installed, then run:

```
pip install -r requirements.txt
```

## Usage

### Config

Edit the config.txt to manipulate the plane dimensions, passengers distribution and passengers' variables

### GUI Version

To use the version with GUI, **run gui.py**

#### Colours meaning

Blue -> moving/idle
Red -> packing luggage - text *n left* is number of turns left to complete packing
Yellow -> barging through a filled seat - text *n left* is number of turns left to complete barging through
Green -> passenger fully boarded - text under the passenger's ticket is the passenger's idle counter - number of turns spent idle

#### Controls

Enter -> fast forward to end
Right arrow -> next turn

Space -> auto play turns
Up arrow -> faster auto turns
Down arrow -> slower auto turns

R -> restart with new passengers
7 -> restart with new passengers in *random* distribution mode
8 -> restart with new passengers in *seat* distribution mode
9 -> restart with new passengers in *section* distribution mode

Q -> quit program
