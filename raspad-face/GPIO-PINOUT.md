# Raspberry Pi GPIO Pinout Reference

## Quick Answer: We're Using GPIO 17

The **Magic Screen button uses GPIO pin 17** (BCM numbering).

This is **Pin 11** on the physical Raspberry Pi GPIO header.

## Full GPIO Header Layout

```
Physical Raspberry Pi GPIO Header (40-pin):

       3V3 Power    [ 1]  [ 2]  5V Power
   GPIO 2 (SDA)     [ 3]  [ 4]  5V Power
   GPIO 3 (SCL)     [ 5]  [ 6]  GND ← USE THIS FOR BUTTON
   GPIO 4           [ 7]  [ 8]  GPIO 14 (TXD)
            GND     [ 9]  [10]  GPIO 15 (RXD)
   GPIO 17          [11]  [12]  GPIO 18 ← USE THIS FOR BUTTON
   GPIO 27          [13]  [14]  GND ← OR THIS FOR GROUND
   GPIO 22          [15]  [16]  GPIO 23
       3V3 Power    [17]  [18]  GPIO 24
   GPIO 10 (MOSI)   [19]  [20]  GND
   GPIO 9 (MISO)    [21]  [22]  GPIO 25
   GPIO 11 (SCLK)   [23]  [24]  GPIO 8 (CE0)
            GND     [25]  [26]  GPIO 7 (CE1)
   GPIO 0 (SDA)     [27]  [28]  GPIO 1 (SCL)
   GPIO 5           [29]  [30]  GND
   GPIO 6           [31]  [32]  GPIO 12
   GPIO 13          [33]  [34]  GND
   GPIO 19          [35]  [36]  GPIO 16
   GPIO 26          [37]  [38]  GPIO 20
            GND     [39]  [40]  GPIO 21
```

## For the Magic Screen Button

**Connect your button like this:**

```
Button Wire 1 → GPIO 17 (Pin 11)
Button Wire 2 → GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
```

When you press the button, it connects GPIO 17 to ground.
The code detects this as a button press.

## Why GPIO 17?

- ✅ Not used by RasPad touchscreen
- ✅ Easy to access on header
- ✅ Has internal pull-up (no resistor needed)
- ✅ No conflicts with other functions

## If You Want to Change It

Edit `orchestrator.py`:
```python
button_bridge.setup_button(pin=17)  # Change 17 to any GPIO number
```

Available safe GPIO pins for buttons:
- GPIO 17 (Pin 11) ← **We use this one**
- GPIO 22 (Pin 15)
- GPIO 23 (Pin 16)
- GPIO 24 (Pin 18)
- GPIO 25 (Pin 22)
- GPIO 26 (Pin 37)
- GPIO 27 (Pin 13)

Avoid:
- GPIO 2, 3 (I2C - used by many devices)
- GPIO 14, 15 (Serial TX/RX)
- GPIO 10, 9, 11 (SPI - used for SD card)

## Visualizing Your RasPad

When you look at the RasPad's GPIO header from above:

```
Looking at the Pi from above, USB ports point away from you:

         ┌─── USB Ports (point this way) ───┐
         │                                    │
         │                                    │
   View │  [GPIO Header]                      │
   from │  40 pins in 2 rows of 20            │
  this  │  ┌──────────────────────────────┐   │
  angle │  │ ●●●●●●●●●●●●●●●●●●●●       │   │  Pin 1 (top-left)
         │  │ ●●●●●●●●●●●●●●●●●●●●       │   │  is 3V3 power
         │  └──────────────────────────────┘   │
         │                                    │
         │                                    │
         └───────────────────────────────────┘

Pin 11 (GPIO 17) is in the 6th position from the top, left column.
```

## Testing Which Pin

```bash
# See all GPIO pins in use:
gpio readall

# Should show you which pins are available
```

That's it! Your button goes on **GPIO 17 (Pin 11) to any GND pin**.
