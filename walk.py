AssertionError#! /usr/bin/python

import csv
from optparse import OptionParser

# how many acceleration values per window for smoothing purposes
VALUES_PER_WINDOW = 15

THRESHOLD_SHOE = 8
TIME_THRESHOLD_SHOE = 300

THRESHOLD_WALK = 2.8
TIME_THRESHOLD_WALK = 300

def run(filename):
    """
    Read the trace file, skip the header,
    smooth the values over a 300ms window,
    find the peaks, remove local peaks, print results
    """
    fh = open(filename, 'r')
    reader = csv.reader(fh)

    # skip header row
    reader.next()

    smooth_vals = smoothValues(reader)

    peaks = findPeaks(smooth_vals)
    #print peaks
    #print len(peaks)

    peaks = removeFalsePositives(peaks)

    printResults(peaks)

def smoothValues(reader):
    """
    Smooth the values by using 300 ms averages instead of the raw values
    """
    window = []
    values = []

    for line in reader:
        if len(window) < VALUES_PER_WINDOW:
            window.append(float(line[ACCEL_DIRECTION_INDEX]))
            continue

        values.append( (int(line[0]), average(window)) )
        window = window[1:] + [float(line[ACCEL_DIRECTION_INDEX])]

    return values
    
def findPeaks(vals):
    """
    Find all values over the threshold
    """
    peaks = []
    lastVal = 0.0
    localMax = 0.0
    localMaxTime = 0

    for i, (time, val) in enumerate(vals):
        if val >= localMax:
            localMax = val
            localMaxTime = time

        # if the value is over the threshold
        # and is smaller than the localMax
        # AND the next value is also smaller than the local max
        # then consider this to be a peak and reset local max
        if localMax > THRESHOLD and val < lastVal \
           and i + 1 < len(vals) - 1 and vals[i][1] > vals[i+1][1]:
            # Found a peak
            peaks.append( (localMaxTime, localMax) )
            localMax = 0.0

        lastVal = val

    return peaks

def removeFalsePositives(peaks):
    """
    If there are multiple local peaks within 300 ms of each other,
    only keep the larger one since that is too short of time for a step
    """
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


def printResults(peaks):
    """
    Print each peak and the total number of steps
    """
    print "time, average acceleration:"
    for peak in peaks:
        print peak
    print
    print "Total steps:"
    print len(peaks)


def average(ls):
    return sum(ls) / len(ls)


if __name__ == '__main__':
    parser = OptionParser()

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
