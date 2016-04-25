from must import MustHavePatterns
from day_breaker import DayBreaker


class TestDayBreaker:
    @classmethod
    def setup_class(cls):
        cls.test_patterns = MustHavePatterns(DayBreaker)

    def test_break_by_day(self):

        class Time:
            def __init__(self,time):
                self.time = time

        day_breaker = self.test_patterns.create(DayBreaker)
        to_break = map(Time, [0.1, 0.2, 1, 1.2, 2.5, 4])
        day_transitions = map(Time, range(6))

        results = day_breaker.break_by_day(to_break, day_transitions)
        result_times = map(lambda a:[b.time for b in a], results)

        day_transition_times = map(lambda a:a.time, day_transitions)
        print day_transition_times
        print result_times

        assert result_times[0] == []
        assert result_times[1] == [0.1, 0.2, 1]
        assert result_times[2] == [1.2]
        assert result_times[3] == [2.5]
        assert result_times[4] == [4]
        assert result_times[5] == []
        assert result_times[6] == []
