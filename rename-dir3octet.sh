#!/bin/bash
# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2023 Niels Bijleveld

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


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
