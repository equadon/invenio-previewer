#!/bin/bash
# Generate zip files with a single file inside in different sizes.
# File sizes to generate in MiB
SIZES="20000"

for size in $SIZES
do
    filename="file_${size}M"
    echo "- generating $filename.zip..."
    CMD="dd if=/dev/urandom of=$filename.bin bs=1048576 count=$size"
    $CMD > /dev/null 2>&1
    zip $filename $filename.bin > /dev/null 2>&1
done

echo "Done!"
