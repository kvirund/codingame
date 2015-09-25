# Author: Anton Gorev aka Veei
# Date: 2015/09/24

# N: Number of elements which make up the association table.
read N
# Q: Number Q of file names to be analyzed.
read Q
declare -A exts
for (( i=0; i<N; i++ )); do
    # EXT: file extension
    # MT: MIME type.
    read EXT MT
    exts["${EXT^^}"z]="$MT"
done

for (( i=0; i<Q; i++ )); do
    # FNAME: One file name per line.
    read FNAME
    if [[ "${FNAME##*.}" == "$FNAME" ]]; then
        ext=""
    else
        ext=${FNAME##*.}
    fi
    echo ${exts[${ext^^}z]:-UNKNOWN}
done
