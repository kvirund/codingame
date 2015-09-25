# Author: Anton Gorev aka Veei
# Date: 2015/09/24

# ---
# Hint: You can use the debug stream to print initialTX and initialTY, if Thor seems not follow your orders.

# lightX: the X position of the light of power
# lightY: the Y position of the light of power
# initialTX: Thor's starting X position
# initialTY: Thor's starting Y position
read lightX lightY initialTX initialTY

# game loop
while true; do
    read remainingTurns
    if (( 0 < $lightY - $initialTY )); then
        echo -n "S"
        lightY=$((lightY - 1))
    elif ((0 > $lightY - $initialTY)); then
        echo -n "N"
        lightY=$((lightY + 1))
    fi
    if (( 0 < $lightX - $initialTX )); then
        echo -n "E"
        lightX=$((lightX - 1))
    elif ((0 > $lightX - $initialTX)); then
        echo -n "W"
        lightX=$((lightX + 1))
    fi
    echo 
done
