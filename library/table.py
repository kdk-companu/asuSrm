import datetime

from dateutil.relativedelta import relativedelta


class Table:

    def calendar_up(month: int, yer: int, lasting=2, weekends_holidays=None):
        """Функция выводит дни. Для отрисовки верхней шапки
        Структура данных:
        {'Февраль':[date(Дата),count(Кол-во дней),text,color]
        """
        MONTH_SELECT = {1: 'Январь', 2: 'Февраль', 3: 'Март',
                        4: 'Апрель', 5: 'Май', 6: 'Июнь', 7: 'Июль',
                        8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
        date_begin = datetime.date(yer, month, 1)
        # Запрос к базе данных с праздниками
        if weekends_holidays:
            WeekendsHolidays_lists = [(d.date, d.work) for d in weekends_holidays]
        calendar = dict()
        for i in range(0, lasting):
            calendar_days = list()
            # Проходим по календарным дням
            for d in range(0, ((date_begin + relativedelta(months=1)) - date_begin).days):
                day_d = date_begin + datetime.timedelta(days=d)
                # Добавляем выходные по календарю
                day_not_working = '#b0b7c6' if day_d.weekday() == 6 or day_d.weekday() == 5 else '#ffffff'
                # Устанавливаем праздники
                if weekends_holidays:
                    if len(WeekendsHolidays_lists) > 0:
                        for schedule_base in WeekendsHolidays_lists:
                            if day_d == schedule_base[0]:
                                day_not_working = '#ffffff' if schedule_base[1] else '#b0b7c6'
                                WeekendsHolidays_lists.remove(schedule_base)
                                break
                calendar_days.append([day_d, 1, '', day_not_working])
            calendar[MONTH_SELECT[date_begin.month]] = calendar_days
            date_begin += relativedelta(months=1)
        return calendar

    def planing(month: int, yers: int, calendar: dict, workers=None, missings=None, missions=None, lasting=2):
        """Список дней для пользователя"""
        date_begin = datetime.date(yers, month, 1)
        date_final = (datetime.date(yers, month, 1) + relativedelta(months=lasting)) - relativedelta(days=1)
        workers_calendar_list = list()
        for i, j in calendar.items():
            workers_calendar_list.extend(j)
        """Заполняется словарь датами для сотрудников"""
        workers_calendar = dict()
        for worker in workers:
            workers_calendar[worker] = workers_calendar_list.copy()
        """ Заполняем отсутствие сотрудников"""
        if missings:
            for missing in missings:
                d_in = date_begin
                d_out = date_final
                d_len = 0
                if not missing.date_end < date_begin or not missing.date_start < date_begin:
                    if missing.date_start > date_begin:
                        d_in = missing.date_start
                    if missing.date_end < date_final:
                        d_out = missing.date_end
                    d_len = (d_out - d_in).days + 1
                    '''Замена в списке'''
                    for i in range(len(workers_calendar[missing.user])):
                        if workers_calendar[missing.user][i][0] == d_in:
                            n_date_start = workers_calendar[missing.user][0:i]
                            n_date_update = [[d_in, d_len, '', missing.information_missing.color], ]
                            n_date_end = workers_calendar[missing.user][
                                         i + d_len:len(workers_calendar[missing.user])]
                            workers_calendar[missing.user] = n_date_start + n_date_update + n_date_end
                            break
        """ Заполняем Командировки """
        if missions:
            for mission in missions:
                d_in = date_begin
                d_out = date_final
                d_len = 0
                if not mission.date_arrival < date_begin or not mission.date_departure < date_begin:
                    if mission.date_departure > date_begin:
                        d_in = mission.date_departure
                    if mission.date_arrival < date_final:
                        d_out = mission.date_arrival
                    d_len = (d_out - d_in).days + 1
                    """Замена в списке"""
                    for i in range(len(workers_calendar[mission.user])):
                        if workers_calendar[mission.user][i][0] == d_in:
                            n_date_start = workers_calendar[mission.user][0:i]
                            color = '#E75A67' if mission.status == 'FINAL' else '#ffff66'
                            n_date_update = [[d_in, d_len, mission.organizations_objects.name_tables, color], ]
                            n_date_end = workers_calendar[mission.user][
                                         i + d_len:len(workers_calendar[mission.user])]
                            workers_calendar[mission.user] = n_date_start + n_date_update + n_date_end
                            break

        return workers_calendar
