import unittest
import ocsuite

chapters = {  # inclusive
    '01|Part A':      0,
    '01|Title Card':  3771,
    '01|Part B':      3861,
    '01|Middle Card': 20884,
    '01|Part C':      21004,
    '01|OP':          30042,
    '01|Part D':      32201,
    '01|Preview':     [33686, 34045],

    '02|Part A':      34070,
    '02|OP':          35748,
    '02|Part B':      37907,
    '02|Middle Card': 51309,
    '02|Part C':      51429,
    '02|ED':          65048,
    '02|Part D':      67181,
    '02|Preview':     [67733, 68092],

    '03|Part A':      68117,
    '03|OP':          70059,
    '03|Part B':      72218,
    '03|Middle Card': 81785,
    '03|Part C':      81905,
    '03|ED':          98591,
    '03|Part D':      100726,
    '03|Preview':     [101780, 102139],

    '04|Part A':      102164,
    '04|OP':          104730,
    '04|Part B':      106887,
    '04|Middle Card': 120888,
    '04|Part C':      121008,
    '04|ED':          133140,
    '04|Part D':      135273,
    '04|Preview':     [135825, 136184],

    '05|Part A':      136209,
    '05|OP':          137049,
    '05|Part B':      139206,
    '05|Middle Card': 151267,
    '05|Part C':      151387,
    '05|ED':          167475,
    '05|Part D':      169608,
    '05|Preview':     [169872, 170231],

    '06|Part A':      170256,
    '06|OP':          171958,
    '06|Part B':      174117,
    '06|Middle Card': 187232,
    '06|Part C':      187352,
    '06|ED':          200513,
    '06|Part D':      202648,
    '06|Preview':     [203918, 204277],

    '07|Part A':      204302,
    '07|OP':          205406,
    '07|Part B':      207563,
    '07|Middle Card': 226000,
    '07|Part C':      226120,
    '07|ED':          235520,
    '07|Part D':      237653,
    '07|Preview':     [237965, 238324],

    '08|Part A':      238349,
    '08|OP':          242282,
    '08|Part B':      244439,
    '08|Middle Card': 254893,
    '08|Part C':      255013,
    '08|ED':          268798,
    '08|Part D':      270933,
    '08|Preview':     [272011, 272370],

    '09|Part A':      272395,
    '09|OP':          273115,
    '09|Part B':      275273,
    '09|Middle Card': 283976,
    '09|Part C':      284096,
    '09|ED':          303396,
    '09|Part D':      305529,
    '09|Preview':     [306057, 306416],

    '10|Part A':      306443,
    '10|OP':          307233,
    '10|Part B':      309390,
    '10|Middle Card': 322889,
    '10|Part C':      323009,
    '10|ED':          336602,
    '10|Part D':      338737,
    '10|Preview':     [340103, 340462],

    '11|Part A':      340487,
    '11|OP':          340775,
    '11|Part B':      342933,
    '11|Middle Card': 359379,
    '11|Part C':      359499,
    '11|ED':          369569,
    '11|Part D':      371703,
    '11|Preview':     [374148, 374507],

    '12|Part A':      [374545, 408744],

    'OVA|OP':                                   408769,
    'OVA|Part 1: You Never Let Us Down':        410927,
    'OVA|Card 1':                               425143,
    'OVA|Part 2: Always Growing Closer':        425263,
    'OVA|Card 2':                               426566,
    'OVA|Part 3: Let\'s Change You Into This!': 426710,
    'OVA|Card 3':                               435940,
    'OVA|Part 4: I\'m Your Big Sister':         436060,
    'OVA|ED':                                   [439243, 441376]
}

repeated_chapters = ['OP', 'ED']
remuxed_bdmv = '/path/to/remuxed.mkv'


class OCsuiteTests(unittest.TestCase):

    def test_compress(self):
        self.assertEqual(ocsuite._compress([1, 5, 11, 13], [3, 8, 12, 15]), ([0, 3, 7, 9], [2, 6, 8, 11]))
        self.assertEqual(ocsuite._compress([1, 4, 8, 11, 14, 18, 24, 33, 36], [2, 7, 9, 13, 17, 20, 30, 35, 41]),
                         ([0, 2, 6, 8, 11, 15, 18, 25, 28], [1, 5, 7, 10, 14, 17, 24, 27, 33]))
        self.assertEqual(ocsuite._compress([5], [9]), ([0], [4]))

    def test_combine(self):
        self.assertEqual(ocsuite._combine([0, 5, 9, 12, 17, 19, 25], [2, 8, 11, 14, 18, 20, 27]),
                         ([0, 5, 17, 25], [2, 14, 20, 27]))
        self.assertEqual(
            ocsuite._combine([1, 3, 7, 10, 21, 45, 60, 72, 74, 82], [2, 5, 9, 20, 40, 50, 70, 73, 79, 90]),
            ([1, 7, 45, 60, 72, 82], [5, 40, 50, 70, 79, 90]))
        self.assertEqual(ocsuite._combine([5], [9]), ([5], [9]))

    # TODO: add testing for main function


if __name__ == '__main__':
    unittest.main()
