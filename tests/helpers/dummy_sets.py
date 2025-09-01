import itertools

SET_1 = {"1", "2", "3"}
SET_2 = {"3", "4", "5"}
SET_3 = {"5", "6", "7"}

combinations = list(itertools.combinations([SET_1, SET_2, SET_3], 2))
combinations_with_flag = list(itertools.product([False, True], combinations))
combinations_with_flag_syncasync = list(
    itertools.product([False, True], [False, True], combinations)
)
