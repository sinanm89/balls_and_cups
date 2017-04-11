#!/usr/local/bin/python
"""
Pindrop interview question.

Sinan,

Here is the question, it was nice talking to you:

You are a magician, and as such, love to hide balls under cups.  You have
exactly 10,000 balls and 10,000 cups, each with a different diameter drawn from
 a random distribution. (You may choose any distribution of diameters, as long
 as it is the same distribution for both balls and cups).

At each iteration, you randomly pair up all balls with cups.
(A pair consists of a single ball and single cup, and each ball/cup can only
belong to a single pair). For each pair, if the diameter of the ball is less
than the diameter of the cup, the ball gets hidden and you set the pair aside
for your show later. Repeat this process until it is impossible for any more
balls to be hidden under cups.

On average, what percentage of balls/cups are used?

Please send code with comments describing your thought process, what your code
is doing, etc. If you get stuck just explain why, or what you intended to do
next.

Thanks,
John

Short Answer: around 0.6 - 1.0%
"""
import numpy as np
import logging

DEBUG = False

logger = logging.getLogger('pindrop')
logging.basicConfig()
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logger.setLevel(LOG_LEVEL)

NUMBER_OF_BALLS = 10000
# number_of_threads = 3
MAX_DIAMETER = 10

SMALLEST_CUP_SIZE = 0
SMALLEST_BALL_SIZE = 0

# The Ball/Cup pairs are always in the same structure in the list
BALL_AXIS = 0
CUP_AXIS = 1

ORDER_BY_CUPS_DESC = ['f{0}'.format(BALL_AXIS)]
ORDER_BY_BALLS_DESC = ['f{0}'.format(CUP_AXIS)]


def get_random_diameter():
    """Return a random diameter value."""
    return np.random.random_integers(1, MAX_DIAMETER)


def calculate_usage_percentage(used_pairs, unused_pairs):
    """Calculate how many of the balls are paired in an iteration."""
    total = len(used_pairs) + len(unused_pairs)
    logger.debug('used: {0}\ntotal :{1}'.format(len(used_pairs), total))
    percentage = float(len(used_pairs)) * 100.0 / float(total)
    logger.info('percentage: {0}'.format(percentage))
    return percentage


def calculate_impossibility(pairs):
    """
    Calculate if its impossible to still match balls with cups.

    Parameters
    ----------
    pairs : List. A list of (Ball, Cup) tuples.

    Returns
    -------
    Boolean
        Impossibility value.

    """
    if not pairs or len(pairs) < 2:
        return True
    _np_pairs_array = np.array(pairs)

    # Sort the pairs with respect to the ball/cup colon
    # By sorting the arrays we can get the smallest and largest diameter
    # We need to look at the largest and smallest one to make a conclusion
    min_ball_diameter_array = np.sort(
        _np_pairs_array.view('i8,i8'), order=ORDER_BY_BALLS_DESC, axis=0
    ).view(np.int)
    max_cup_diameter_array = np.sort(
        _np_pairs_array.view('i8,i8'), order=ORDER_BY_CUPS_DESC, axis=0
    ).view(np.int)

    # first element of the sorted ball/cup array
    min_ball_size = min_ball_diameter_array[0][BALL_AXIS]
    max_cup_size = max_cup_diameter_array[-1][CUP_AXIS]

    impossibility_reached = False
    if max_cup_size <= min_ball_size:
        impossibility_reached = True
    return impossibility_reached


def randomly_match_cup_ball_pairs(pairs, max_range=None):
    """
    Randomly match the cups and balls.

    If max_range is given, create the cups and balls.

    Parameters
    ----------
    pairs : List. A list of (Ball, Cup) tuples.

    max_range : Integer. The maximum number of ball/cup objects to create.

    Returns
    -------
    dict
        the used and unused pair lists with the matching metadata.

    """
    unused_pairs = []
    used_pairs = []

    count = max_range if max_range is not None else len(pairs)
    # This loop can be divided into smaller chunks to be threaded or
    # made into async jobs for both creation and sorting.
    for i in range(0, count):
        if max_range:
            ball = get_random_diameter()
            cup = get_random_diameter()
        else:
            if len(pairs) <= 2:
                # Edge case, when left with 2 pairs we need to be careful
                impossibility_reached = calculate_impossibility(pairs)
                if impossibility_reached:
                    unused_pairs.extend(pairs)
                    return {
                        'used_pairs': used_pairs,
                        'unused_pairs': unused_pairs
                    }
            # take a random pair from each batch
            random_index = np.random.random_integers(0, len(pairs) - 1)
            pair = pairs.pop(random_index)
            ball = pair[BALL_AXIS]

            random_index = np.random.random_integers(0, len(pairs) - 1)
            pair = pairs.pop(random_index)
            cup = pair[CUP_AXIS]
            # when we pop a ball and a cup (to use)there is also an unused pair
            unused_pairs.append((pair[BALL_AXIS], pair[CUP_AXIS]))

        if ball < cup:
            used_pairs.append((ball, cup))
        else:
            unused_pairs.append((ball, cup))

    # make sure unused pairs is always a list and not None
    return {
        'used_pairs': used_pairs,
        'unused_pairs': unused_pairs if unused_pairs else []
    }


def main():
    """Main program."""
    percent_used = []
    matched_pairs = []
    # Create the initial ball/cup sets with random diameters.
    # This function also randomly pairs balls with cups
    # From now on we will always work with pairs (balls, cup)
    result = randomly_match_cup_ball_pairs([], NUMBER_OF_BALLS)
    matched_pairs.extend(result.get('used_pairs'))
    # calculate the initial usage percentage
    percent_used.append(calculate_usage_percentage(
        result.get('used_pairs'),
        result.get('unused_pairs')
    ))
    impossibility_reached = False
    while not impossibility_reached:
        # We do a check initially for impossibilities
        impossibility_reached = calculate_impossibility(
            result.get('unused_pairs'))
        if impossibility_reached:
            break
        # we match every unused pair of ball cups until we cant anymore
        result = randomly_match_cup_ball_pairs(result.get('unused_pairs'))
        matched_pairs.extend(result.get('used_pairs'))

        # can be async
        if not impossibility_reached:
            percent_used.append(calculate_usage_percentage(
                result.get('used_pairs'),
                result.get('unused_pairs')
            ))

    logger.debug('Percentage of hidden balls at each iteration: {0}'.format(
        percent_used))
    average_ball_cup_usage = np.average(percent_used)
    logger.info('Average percentage of ball/cup usage: {0}'.format(
        average_ball_cup_usage))


if __name__ == '__main__':
    main()
