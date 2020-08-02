import unittest
import ocsuite

chapters_example = {  # repeated_chapters = ['OP', 'ED']
    '01': {
        'Part A': 0,
        'Title Card': 3771,
        'Part B': 3861,
        'Middle Card': 20884,
        'Part C': (21004, 29696),
        'OP': 30042,
        'Part D': 32201,
        'Preview': (33686, 34045)
    },
    '02': {
        'Part A': 34070,
        'OP': 35748,
        'Part B': 37907,
        'Middle Card': 51309,
        'Part C': 51429,
        'ED': 65048,
        'Part D': 67181,
        'Preview': (67733, 68092)
    },
    '03': {
        'Part A': 70000,
        'Part B': 80000,
        'Part C': (90000, 100000)
    }
}

small_test = {  # repeated_chapters = ['OP', 'ED']
    '01': {
        'Part A': 0,
        'OP': 10,
        'Part B': 15,
        'Part C': 25,
        'ED': 35,
        'Part D': (40, 50)
    }
}

full_test = {  # repeated_chapters = ['OP', 'ED']
    '01':
        {
        'Part A': 10,
        'OP': 20,
        'Part B': 25,
        'Part C': 35,
        'ED': 45,
        'Part D': (50, 59)
        },
    '02': {
        'OP': 75,
        'Part A': 80,
        'Part B': 90,
        'Part C': (100, 109)
    },
    '03': {
        'OP': 110,
        'Part A': (115, 124),
        'Part B': 135,
        'Part C': 145,
        'ED': (155, 159)
    },
    '04': {
        'Part A': 160,
        'Part B': 170,
        'Part C': 180,
        'OP': (190, 194)
    },
    'OVA': {
        'Part A': (200, 219),
        'Part B': (231, 250),
    },
    'OVA 2': {
        'Part A': (270, 299)
    }
}

repeated_chapters = ['OP', 'ED']
remuxed_bdmv = '/path/to/remuxed.mkv'


class OCsuiteTests(unittest.TestCase):
    pass
    # TODO: add testing for all helper functions
    # TODO: add testing for main function


if __name__ == '__main__':
    unittest.main()
