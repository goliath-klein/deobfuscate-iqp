#!/bin/bash

WRONG=$1-wrong.tmp
echo "Extracting wrong records to $WRONG"
grep -v pattern $1 | grep -A 1 -B 7 wrong > $WRONG

echo
echo -n "Number of attempts: "
grep Attack $1 | wc -l
echo -n "Number of failures: "
grep Attack $WRONG | wc -l

echo

echo -n "Mean of n - g - m2 overall: "
grep "n - g - m2" $1 | cut -d " " -f 7 | awk '{ total += $1 } END { print total/NR }'
echo -n "Mean of n - g - m2 among failures: "
grep "n - g - m2" $WRONG | cut -d " " -f 7 | awk '{ total += $1 } END { print total/NR }'

echo
echo "Cases where dim ker G was strictly larger than n−g-m2:" 
echo "---"
grep -A5 -B4 "bound= [^0]" $1
echo "---"
echo 

echo -n "Number of times sample_D would have returned corrupted data: "
grep Failed $1 | wc -l

echo

echo "Removing $WRONG"
rm $WRONG
