import boundary_to_trace_v4 as bt
import trace_to_boundary as tb
import matplotlib.pyplot as plt
import random
import z3

# random.seed(708)

def invert(boundary, param_boundaries):
    """
    Takes a boundary, and rotates it by 180 degrees in parameter space

    Arguments:
    boundary -- a boundary
    param_boundaries -- list of lists giving upper and lower bounds for possible
                        parameter values. Specifically, should be of the form
                        [[lower_bound_x, upper_bound_x], 
                         [lower_bound_y, upper_bound_y]]

    Note that a 180 degree rotation is the same as flipping vertically and then
    horizontally, which is what we will actually do
    """
    new_boundary = []
    for point in boundary:
        new_x = param_boundaries[0][0] + param_boundaries[0][1] - point[0]
        new_y = param_boundaries[1][0] + param_boundaries[1][1] - point[1]
        new_boundary.append([new_x, new_y])
    return new_boundary[::-1]

def plot(data):
    """
    Convert a trace or a boundary to two lists, x and y axis. And plot it.
    """

    x_axis = [data[i][0] for i in range(len(data))]
    y_axis = [data[i][1] for i in range(len(data))]
    plt.plot(x_axis, y_axis)
    plt.show()

def label(boundary, should_invert=False, param_boundaries=[[0.0, 20.0],
                                                           [0, 1.0]],
          epsilon=0.01, num_points=200, lipschitz_param=0.05):
    """
    Takes a boundary, and returns its proper label, which is True or False.

    Correct implementation will depend on context, and in the extreme case will
    require computation done by the human.
    """
    # TODO: add type assertions
    if should_invert:
        my_boundary = invert(boundary, param_boundaries)
    else:
        my_boundary = boundary
    # plot(my_boundary)
    print("in the label function")
    
    # print("in the label function, should_invert is", should_invert)
    # print("boundary that label is synthesising", my_boundary)
    # print(num_points)
    
    xs = [z3.Real('x%d' % i) for i in range(num_points)]
    us = [z3.Real('u%d' % i) for i in range(num_points)]

    def make_phi(xs, us):
        # this basically makes a formula encoding dynamics of a system xs
        # controlled by us
        formula = True
        for i in range(num_points - 1):
            formula = z3.And(formula, xs[i+1] == xs[i] + us[i],
                             # xs[i+1] - xs[i] <= lipschitz_param,
                             # xs[i] - xs[i+1] <= lipschitz_param,
                             xs[i] >= 0, xs[i+1] >= 0, xs[i] <= 1, xs[i+1] <= 1)
        return formula

    trace = bt.trace(my_boundary, epsilon, num_points, xs,
                     param_boundaries[0][1], make_phi(xs, us))

    print("trace that is being labelled is", trace)
    plot(trace)

    # in this labelling function, we demand that the trace's velocity be inside a polygon with points
    # (0,1), (8, 0.9), (14, 0.6), (20, 0.2), (0,0.5), (5, 0.3), (12, 0.2), (20, 0.1).
    
    class_val = True
    
    for point in trace:
        if point[0] <= 8:
            class_val = class_val and (point[1] <= point[0]/(-80.0) + 1.0)
        if point[0] <= 14 and point[0] >= 8:
            class_val = class_val and (point[1] <= point[0]/(-20.0) + 13.0/10)
        if point[0] >= 14:
            class_val = class_val and (point[1] <= point[0]/(-15.0) + 23.0/15)
        if point[0] <= 5:
            class_val = class_val and (point[1] >= point[0]/(-25.0) + 0.5)
        if point[0] >=5 and point[0] <= 12:
            class_val = class_val and (point[1] >= point[0]/(-70.0) + 13.0/35)
        if point[0] >= 12:
            class_val = class_val and (point[1] >= point[0]/(-80.0) + 7.0/20)

    return class_val

def get_positive_example(param_boundaries):
    """Randomly samples a boundary that should be classified positively.

    This will be specific to one particular hypothesis.
    """
    print("We are now inside get_positive_example")

    pos_trace = []
    for i in range(201):
        x_val = ((param_boundaries[0][1] - param_boundaries[0][0])*(i/200.0)
                 + param_boundaries[0][0])
        m = -0.03
        b = 0.75
        y_val = m*x_val + b
        pos_trace.append([x_val, y_val])

    plot(pos_trace)
    boundary = tb.boundary(pos_trace)
    nice_boundary = [point for point in boundary
                     if (point[0] >= param_boundaries[0][0]
                         and point[0] <= param_boundaries[0][1]
                         and point[1] >= param_boundaries[1][0]
                         and point[1] <= param_boundaries[1][1])]

    plot(nice_boundary)
    print(nice_boundary)

    true_label = True
    
    for point in pos_trace:
        if point[0] <= 8:
            true_label = true_label and (point[1] <= point[0]/(-80.0) + 1.0)
        if point[0] <= 14 and point[0] >= 8:
            true_label = true_label and (point[1] <= point[0]/(-20.0) + 13.0/10)
        if point[0] >= 14:
            true_label = true_label and (point[1] <= point[0]/(-15.0) + 23.0/15)
        if point[0] <= 5:
            true_label = true_label and (point[1] >= point[0]/(-25.0) + 0.5)
        if point[0] >=5 and point[0] <= 12:
            true_label = true_label and (point[1] >= point[0]/(-70.0) + 13.0/35)
        if point[0] >= 12:
            true_label = true_label and (point[1] >= point[0]/(-80.0) + 7.0/20)

    # print("positive trace we generate is", pos_trace)
            
    print("true classification of your trace is", true_label)

    # print("boundary we generate is", nice_boundary)
    
    assert label(nice_boundary), "the positive example you generated isn't actually labelled positive!"
    return nice_boundary

# my_bound = get_positive_example([[0, 20], [0,1]])
# print(my_bound)