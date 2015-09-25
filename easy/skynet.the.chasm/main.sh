# Author: Anton Gorev aka Veei
# Date: 2015/09/24

# road: the length of the road before the gap.
read r
# gap: the length of the gap.
read g
# platform: the length of the landing platform.
read p

function solve
{
    local road=$1
    local gap=$2
    local platform=$3
    local speed=$4
    local coordX=$5

    if [[ ${m["$speed $coordX"]:-0} == 1 ]]; then
        return 1
    fi
    if (( 0 == $speed && $coordX > $gap + $road )); then
        return 0
    elif (( $coordX >= $road + $gap + $platform)); then  # out of road
        return 1
    else
        if (( $coordX >= $road + $gap )); then
            solve $road $gap $platform $((speed-1)) $((coordX+speed-1))
            if ((0 == $?)); then
                solution="SLOW $solution"
                return 0
            fi
        elif (($coordX + $speed < $road )); then # try to increase/decrease speed
            if (($coordX + $speed + 1 < $road)); then
                solve $road $gap $platform $((speed+1)) $((coordX+speed+1))
                if ((0 == $?)); then
                    solution="SPEED $solution"
                    return 0
                fi
            fi
            if ((0 < $speed && $coordX + $speed - 1 < $road)); then
                solve $road $gap $platform $((speed-1)) $((coordX+speed-1))
                if ((0 == $?)); then
                    solution="SLOW $solution"
                    return 0
                fi
            fi
            if (( 0 < $speed )); then
                solve $road $gap $platform $((speed)) $((coordX+speed))
                if ((0 == $?)); then
                    solution="WAIT $solution"
                    return 0
                fi
            fi
        elif (( $coordX >= $road - $speed )); then
            if ((0 < $speed && $coordX + $speed - 1 < $road)); then
                solve $road $gap $platform $((speed-1)) $((coordX+speed-1))
                if ((0 == $?)); then
                    solution="SLOW $solution"
                    return 0
                fi
            fi
            if (( $coordX < $road && ($coordX + $speed) >= ($road + $gap) && 0 < $speed)); then  # try jump
                solve $road $gap $platform $((speed)) $((coordX+speed))
                if ((0 == $?)); then
                    solution="JUMP $solution"
                    return 0
                fi
            fi
        fi
        m["${speed} ${coordX}"]="1"
        return 1
    fi
}

declare -A m
# game loop
while true; do
    # speed: the motorbike's speed.
    read speed
    # coordX: the position on the road of the motorbike.
    read coordX

    # Write an action using echo
    # To debug: echo "Debug messages..." >&2

    if [[ ${solved:-0} == "0" ]]; then
        solution=""
        solve $r $g $p $speed $coordX

        if ((0 == $?)); then
            for i in $solution; do
                echo $i
            done
            exit
            solved=1
        else
            echo "solution has not been found">&2
        fi
    fi
done
