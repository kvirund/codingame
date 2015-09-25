# Author: Anton Gorev aka Veei
# Date: 2015/09/24

# n: the number of temperatures to analyse
read n
# temps: the n temperatures expressed as integers ranging from -273 to 5526
read temps

# Write an action using echo
# To debug: echo "Debug messages..." >&2

result=-1
for i in $temps; do
#    echo $i
    ai=${i/#-/}
    if (( -1 == $result )); then
        result=$i
        ar=$ai
    elif (( $ai < $ar )); then
        result=$i
        ar=$ai
    elif (( $ai == $ar && $i > $result)); then
        result=$i
        ar=$ai
    fi
done;

if (( -1 == $result)); then
    echo "0";
else
    echo $result
fi
