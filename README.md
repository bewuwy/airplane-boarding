# airplane-boarding
airplane boarding simulator in python

## Installation

You need to have **Python 3** and **pip** installed, then run:

```
pip install -r requirements.txt
```

## Usage

### Config

Edit the config.txt to manipulate the plane dimensions, passengers distribution and passengers' variables

#### Tests config

Edit the tests.txt to change types of tests and number of each of them.

The *tests* variable can bet set to list of test types (*separated by commas*).
For example:
```
tests = "random", "seat", ["section", {"section_width": 3}]
```

**Test types**:
- **random** - random passenger distribution
- **seat** - seat (distance from corridor) based distribution
- **section** - random passenger distribution by sections of given width
  - This test type can be set with a *section_width* variable.

### Tests version

To use the version without display, **run tests.py**

```
python tests.py
```

But first, make sure to set up tests in **tests.txt**.

### GUI version

To use the version with GUI, **run gui.py**

```
python gui.py
```

#### Colours meaning

- Blue -> moving/idle
- Red -> packing luggage - text *n left* is number of turns left to complete packing
- Yellow -> barging through a filled seat - text *n left* is number of turns left to complete barging through
- Green -> passenger fully boarded - text under the passenger's ticket is the passenger's idle counter - number of turns spent idle

#### Controls

- Enter -> fast forward to end
- Right arrow -> next turn

- Space -> auto play turns
- Up arrow -> faster auto turns
- Down arrow -> slower auto turns

- R -> restart with new passengers
- 7 -> restart with new passengers in *random* distribution mode
- 8 -> restart with new passengers in *seat* distribution mode
- 9 -> restart with new passengers in *section* distribution mode

- Q -> quit program
