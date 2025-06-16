import unittest


def search(number: int, search_list: list[int]) -> bool:
    left, right = 0, len(search_list) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if search_list[mid] == number:
            return True
        elif search_list[mid] < number:
            left = mid + 1
        else:
            right = mid - 1
    return False


class TestSearchInSortedList(unittest.TestCase):
    def setUp(self):
        self.sorted_list = [1, 2, 3, 45, 356, 569, 600, 705, 923]
        self.large_list = list(range(1, 1000001))
        self.empty_list = []
        self.single_element_list = [42]
        self.duplicate_list = [1, 2, 2, 2, 3, 4, 4, 5]

    def test_element_exists(self):
        test_cases = [
            (45, True),
            (923, True),
            (1, True),
            (600, True),
            (356, True),
        ]

        for number, expected in test_cases:
            with self.subTest(number=number, expected=expected):
                self.assertEqual(search(number, self.sorted_list), expected)

    def test_element_does_not_exist(self):
        test_cases = [0, 4, 700, 1000, -5, 924, 355]

        for number in test_cases:
            with self.subTest(number=number):
                self.assertFalse(search(number, self.sorted_list))

    def test_edge_cases(self):
        test_cases = [
            (self.empty_list, 1, False),
            (self.single_element_list, 42, True),
            (self.single_element_list, 41, False),
            (self.single_element_list, 43, False),
            (self.duplicate_list, 2, True),
            (self.duplicate_list, 4, True),
            (self.duplicate_list, 6, False),
        ]

        for lst, number, expected in test_cases:
            with self.subTest(lst=lst[:5], number=number, expected=expected):
                self.assertEqual(search(number, lst), expected)

    def test_large_list(self):
        test_cases = [
            (1, True),
            (500000, True),
            (999999, True),
            (1000000, True),
            (0, False),
            (1000001, False),
        ]

        for number, expected in test_cases:
            with self.subTest(number=number, expected=expected):
                self.assertEqual(search(number, self.large_list), expected)

    def test_first_last_elements(self):
        test_lists = [
            self.sorted_list,
            self.large_list,
            self.duplicate_list,
            [10, 20, 30],
            [-5, 0, 5],
        ]

        for lst in test_lists:
            with self.subTest(lst=lst[:5]):
                self.assertTrue(search(lst[0], lst))
                self.assertTrue(search(lst[-1], lst))
                self.assertFalse(search(lst[-1] + 1, lst))


if __name__ == "__main__":
    unittest.main()
