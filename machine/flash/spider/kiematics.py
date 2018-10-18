coxa = 26.5  # lenght of 1st leg section
femur = 48  # lenght of 2nd leg section
tiba = 67  # lenght of 3rd leg section
right_angle = pi/2  # this is used because the zero of my robot is at 90 degrees
t1_part = tiba**2 - femur**2  # this only needs to be caluated once
reach = femur + tiba  # calucate the max reach


def cal_angles(x, y, z):
    coxa_angle = atan(y/x)
    x = hypot(x, y) - coxa
    l = hypot(x, z)
    if l < reach:  # error check if in reach before calucation
        t1 = (l**2 - t1_part) / (2 * l)
        t2 = l - t1
        femur_angle = acos(t1/femur) - atan(z/x)
        # minus off the offset for my zero point
        tiba_angle = asin(t1/femur) + asin(t2/tiba) - right_angle
    else:  # if out of reach
        # this is leg streched out stright due to my zero point at 90 degrees
        tiba_angle = right_angle
        femur_angle = - atan(z/x)  # point at target coordinate
    return (coxa_angle, femur_angle, tiba_angle)
