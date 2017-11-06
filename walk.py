#! /usr/bin/python

import csv
from optparse import OptionParser

THRESHOLD_SHOE = 8
TIME_THRESHOLD_SHOE = 500

THRESHOLD_WALK = 2.8
TIME_THRESHOLD_WALK = 500

def run(filename):
    fh = open(filename, 'r')
    reader = csv.reader(fh)

    # skip header row
    reader.next()

    smooth_vals = smoothValues(reader)

    peaks = findPeaks(smooth_vals)
    print peaks
    print len(peaks)

    peaks = removeFalsePositives(peaks)

    print peaks
    print len(peaks)

def smoothValues(reader):
    window = []
    values = []

    for line in reader:
        if len(window) < 15:
            window.append(float(line[ACCEL_DIRECTION_INDEX]))
            continue

        values.append( (int(line[0]), average(window)) )
        window = window[1:] + [float(line[ACCEL_DIRECTION_INDEX])]

    return values
    
def findPeaks(vals):
    peaks = []
    lastVal = 0.0
    localMax = 0.0
    localMaxTime = 0

    for i, (time, val) in enumerate(vals):
        if val >= localMax:
            localMax = val
            localMaxTime = time

        if localMax > THRESHOLD and val < lastVal \
           and i + 1 < len(vals) - 1 and vals[i][1] > vals[i+1][1]:
            # Found a peak
            peaks.append( (localMaxTime, localMax) )
            localMax = 0.0

        lastVal = val

    return peaks

def removeFalsePositives(peaks):
    good_peaks = []
    lastTime = 0
    lastVal = 0.0
    timeDiff = 0.0
    
    for i, (time, val) in enumerate(peaks):
        if i == 0:
            lastTime = time
            lastVal = val
            continue

        timeDiff = time - lastTime
        if timeDiff > TIME_THRESHOLD:
            good_peaks.append( (lastTime, lastVal) )
            lastTime = time
            lastVal = val
        else:
            # Under time threshold, only keep one
            if val > lastVal:
                lastTime = time
                lastVal = val

    # Add the last one if necessary
    if lastTime - good_peaks[-1][0] > TIME_THRESHOLD:
        good_peaks.append( (lastTime, lastVal) )

    return good_peaks

def average(ls):
    return sum(ls) / len(ls)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")

    (options, args) = parser.parse_args()

    # set thresholds based on filenames
    if args[0].endswith('-pocket.csv'):
        THRESHOLD = THRESHOLD_WALK
        TIME_THRESHOLD = TIME_THRESHOLD_WALK
        ACCEL_DIRECTION_INDEX = 3
    else:
        THRESHOLD = THRESHOLD_SHOE
        TIME_THRESHOLD = TIME_THRESHOLD_SHOE
        ACCEL_DIRECTION_INDEX = 1
            
    run(args[0])
