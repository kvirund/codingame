# Author: Anton Gorev aka Veei
# Date: 2015/09/24

# game loop
last=100500
while true; do
    read spaceX spaceY
    max=-1
    for (( i=0; i<8; i++ )); do
        # mountainH: represents the height of one mountain, from 9 to 0. Mountain heights are provided from left to right.
        read mountainH
        if (( max < mountainH )); then
            max=$mountainH
            maxX=$i
        fi
    done

    # Write an action using echo
    # To debug: echo "Debug messages..." >&2
    if (( last != spaceY && maxX == spaceX )); then
        echo "FIRE"
        last=$spaceY
    else
        echo "HOLD"
    fi
done
