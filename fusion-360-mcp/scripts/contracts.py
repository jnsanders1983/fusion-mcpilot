"""Host-side validation for optional live geometry acceptance metrics."""
import math


def geometry_expectations(expected,prefix=''):
    if not isinstance(expected,dict):raise ValueError('Geometry expectations must be an object.')
    count=prefix+'body_count';size=prefix+'size_mm';volume=prefix+'volume_mm3'
    if set(expected)-{count,size,volume}:raise ValueError('Unknown geometry expectation.')
    if count in expected and (type(expected[count]) is not int or expected[count]<0):raise ValueError('Body count must be a nonnegative integer.')
    if size in expected and (not isinstance(expected[size],(list,tuple)) or len(expected[size])!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in expected[size])):raise ValueError('Expected dimensions must be three positive finite millimeter values.')
    if volume in expected and (type(expected[volume]) not in (int,float) or not math.isfinite(expected[volume]) or expected[volume]<0):raise ValueError('Expected volume must be nonnegative and finite.')
    return expected
