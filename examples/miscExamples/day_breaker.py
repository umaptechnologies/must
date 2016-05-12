from must import must_list_objects


class DayBreaker:
    '''Breaks items into chunks, based on their day.'''
    def __init__(self):
        pass

    def break_by_day(self, list_to_break, day_transitions):
        must_list_objects(list_to_break).that_must_have('time')  # and must be sorted by time
        must_list_objects(day_transitions).that_must_have('time')  # and must be sorted by time

        results = []
        today = []
        for x in list_to_break:
            while len(results) < len(day_transitions) and x.time > day_transitions[len(results)].time:
                results.append(today)
                today = []
            today.append(x)
        results.append(today)
        while len(results) < len(day_transitions)+1:
            results.append([])
        return results
