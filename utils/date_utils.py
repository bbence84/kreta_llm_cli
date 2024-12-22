import datetime

class KretaDateUtils:

    def __init__(self):
        pass
    
    # Gets start date and end date of the week for the given date
    def get_week_start_enddates(self, date_of_week = datetime.date.today()):
        today = date_of_week
        if today.weekday() == 5:  # Saturday
            today += datetime.timedelta(days=2)
        elif today.weekday() == 6:  # Sunday
            today += datetime.timedelta(days=1)
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)
        return start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")    

    # Gets start date and end date of the current week. 
    # If the current day is Sunday or Saturday, it will return the start and end date of the next week.
    def get_actual_week_dates(self):
        today = datetime.date.today()
        if today.weekday() == 5:  # Saturday
            today += datetime.timedelta(days=2)
        elif today.weekday() == 6:  # Sunday
            today += datetime.timedelta(days=1)
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)
        return start_of_week, end_of_week

    # Gets the start of the school year which is the first Monday of September.
    def get_start_of_school_year(self, year):
        start_date = datetime.date(year, 9, 1)
        if start_date.weekday() != 0:  # Not Monday
            start_date += datetime.timedelta(days=(7 - start_date.weekday()))
        return start_date

    # Gets the end of the half year which is January the 17th. If the current date is after the 17th of January, it will return the 17th of January of the next year.
    def get_end_of_half_year(self, year):
        end_date = datetime.date(year, 1, 17)
        if datetime.date.today() > end_date:
            end_date = datetime.date(year + 1, 1, 17)
        return end_date

    # Gets the end of the school year which ends on the 20th of June. If the current date is after the 20th of June, it will return the 20th of June of the next year.
    def get_end_of_school_year(self, year):
        end_date = datetime.date(year, 6, 20)
        if datetime.date.today() > end_date:
            end_date = datetime.date(year + 1, 6, 20)
        return end_date    