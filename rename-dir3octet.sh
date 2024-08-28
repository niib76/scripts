#!/bin/bash

# Set the original and target third octet
old_octet="240"  # The third octet you want to replace
new_octet="181"  # The new third octet you want to set

# Iterate over directories matching the pattern (e.g., 192.168.*.*)
for dir in */; do
    # Strip the trailing slash
    dir="${dir%/}"
    
    # Match the directory name with an IP address format
    if [[ $dir =~ ^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$ ]]; then
        # Extract the octets
        first_octet=${BASH_REMATCH[1]}
        second_octet=${BASH_REMATCH[2]}
        third_octet=${BASH_REMATCH[3]}
        fourth_octet=${BASH_REMATCH[4]}
        
        # Check if the third octet matches the one to replace
        if [[ "$third_octet" == "$old_octet" ]]; then
            # Construct the new directory name with the updated third octet
            new_dir="${first_octet}.${second_octet}.${new_octet}.${fourth_octet}"
            
            # Rename the directory
            mv "$dir" "$new_dir"
            echo "Renamed $dir to $new_dir"
        fi
    fi
done
