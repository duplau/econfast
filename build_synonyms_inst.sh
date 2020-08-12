#!/usr/bin/sh

awk 'BEGIN{ FS=" " } { if ($NF~ /\([A-Z]+\)/) { acro = substr($NF, 2, length($NF)-2); $NF=""; NF-=1; print acro " => " $0 } else if ($(NF-1) == "-") { acro = $NF; $NF=""; $(NF-1)=""; NF-=2; print acro " => ", $0 } }' < registered_institutions | sort | uniq > synonyms_inst
