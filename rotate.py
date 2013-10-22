# CC0 Licensed. http://creativecommons.org/publicdomain/zero/1.0/legalcode

import datetime
import unittest

def to_delete(dates, now=datetime.datetime.now()):
    # We never want to delete the most recent backup.
    possible_dates = sorted(dates)[:-1]

    # Approximate ages of backups we'd like to have, oldest to newest.
    dividers = [
            now - datetime.timedelta(days=28, hours=1),
            now - datetime.timedelta(days=7, hours=1),
            now - datetime.timedelta(days=1, hours=1),
            now
    ]

    # Pair up dividers as boundary conditions for the partitions we
    # create below. [(oldest, 2nd oldest), (2nd oldest, 3rd oldest), ...]
    divider_pairs = zip(dividers, dividers[1:])

    # Partitions is a list of lists. Each list inside partitions will
    # contain the dates between a pair of dividers.
    partitions = []
    for first, second in divider_pairs:
        partition = []
        for date in possible_dates:
            if date > first and date < second:
                partition.append(date)
        partitions.append(partition)

    # Of items older than the oldest divider we want to delete all but the youngest.
    to_delete = [date for date in possible_dates if date < dividers[0]][:-1]

    # And all but the oldest and youngest items within each partition.
    for partition in partitions:
        to_delete.extend(sorted(partition)[1:-1])

    # But we don't want to delete every single backup, as we might
    # otherwise if say the only backups present are all older than
    # the oldest divider.
    if not len(to_delete) < len(possible_dates):
        return set([]) 

    return set(to_delete)

class TestRotate(unittest.TestCase):
    def test_many_in_day(self):
        now      = datetime.datetime(2013, 02, 20, 23, 59, 59)
        earlier  = datetime.datetime(2013, 02, 20, 22, 59, 59)
        earlier2 = datetime.datetime(2013, 02, 20, 21, 59, 59)
        earlier3 = datetime.datetime(2013, 02, 20, 20, 59, 59)
        delete = to_delete([now, earlier, earlier2, earlier3], now)
        self.assertEqual(delete, set([earlier2]))

    def test_many_in_first_week(self):
        now                 = datetime.datetime(2013, 02, 20, 23, 59, 59)
        earlier_today       = datetime.datetime(2013, 02, 20, 20, 59, 59)
        earlier_this_week   = datetime.datetime(2013, 02, 18, 20, 59, 59)
        delete = to_delete([now, earlier_today, earlier_this_week], now)
        self.assertEqual(delete, set([]))

    def test_single(self):
        now = datetime.datetime(2013, 02, 20, 23, 59, 59)
        delete = to_delete([now],now)
        self.assertEqual(delete, set([]))

    def test_many_in_first_and_second_week(self):
        now                 = datetime.datetime(2013, 02, 20, 23, 59, 59)
        earlier_today       = datetime.datetime(2013, 02, 20, 22, 59, 59)
        earlier_today2      = datetime.datetime(2013, 02, 20, 21, 59, 59)
        earlier_today3      = datetime.datetime(2013, 02, 20, 20, 59, 59)
        earlier_this_week   = datetime.datetime(2013, 02, 15, 22, 59, 59)
        earlier_this_week2  = datetime.datetime(2013, 02, 15, 21, 59, 59)
        earlier_this_week3  = datetime.datetime(2013, 02, 15, 20, 59, 59)
        earlier_last_week   = datetime.datetime(2013, 02, 10, 22, 59, 59)
        earlier_last_week2  = datetime.datetime(2013, 02, 10, 21, 59, 59)
        earlier_last_week3  = datetime.datetime(2013, 02, 10, 20, 59, 59)
        delete = to_delete(
                [now, earlier_today, earlier_today2, earlier_today3,
                 earlier_this_week, earlier_this_week2, earlier_this_week3,
                 earlier_last_week, earlier_last_week2, earlier_last_week3],
                now)

        self.assertEqual(delete, set([earlier_today2, earlier_this_week2, earlier_last_week2]))

    def test_one_older_than_two_weeks(self):
        now                 = datetime.datetime(2013, 01, 20, 23, 59, 59)
        earlier_old         = datetime.datetime(2012, 01, 20, 23, 59, 59)
        delete = to_delete([now, earlier_old], now)
        self.assertEqual(delete, set([]))

    def test_only_one_old(self):
        now                 = datetime.datetime(2013, 01, 20, 23, 59, 59)
        earlier_old         = datetime.datetime(2012, 01, 20, 23, 59, 59)
        delete = to_delete([earlier_old], now)
        self.assertEqual(delete, set([]))

    def test_truncation(self):
        now                 = datetime.datetime(2013, 01, 20, 23, 59, 59)
        now_backup          = datetime.datetime(2013, 01, 20, 23, 59, 00)
        old                 = datetime.datetime(2013, 01, 20, 23, 40, 00)
        delete = to_delete([now_backup, old], now)
        self.assertEqual(delete, set([]))

    def test_cycle(self):
        now = datetime.datetime(2013, 1, 1, 1, 1, 1)
        current_set = set([])

        while now <= datetime.datetime(2013, 4, 1, 1, 1, 1):
            current_set.add(now)
            current_set = current_set.difference(to_delete(current_set, now))

            if now > datetime.datetime(2013, 2, 1, 1, 1, 1):
                self.assertGreaterEqual(len(current_set), 7)

                s = sorted(current_set)
                self.assertGreater(now - s[0], datetime.timedelta(weeks=4))

            now += datetime.timedelta(hours=1)


if __name__ == '__main__':
    unittest.main()
