import random
from data import professors_info, groups, slots, weekdays

from constraints import (
    is_professor_busy,
    is_professor_assigned_to_group_on_day,
    heuristic_sort_professors,
    get_available_rooms,
)


class CSP:
    def __init__(self, groups, weekdays, slots, professors_info):
        # Змінні: всі слоти розкладу
        self.variables = [(group, weekday, slot) for group in groups for weekday in weekdays for slot in slots]
        # Домени: можливі призначення для кожного слота
        self.domains = self.initialize_domains(professors_info)
        self.schedule = {}  # Порожній розклад
        self.professors_info = professors_info

    def initialize_domains(self, professors_info):
        """Ініціалізує домени для всіх змінних."""
        domains = {}
        for variable in self.variables:
            group, weekday, slot = variable
            available_professors = [
                professor
                for professor, info in professors_info.items()
                if info["subjects"]
            ]
            domains[variable] = available_professors  # Призначення для змінної
        return domains

    def get_available_professors(self, weekday, slot, group):
        """
        Отримує список доступних викладачів для заданого дня, часу та групи.
        """
        available_professors = []
        for professor in self.domains[(group, weekday, slot)]:
            if not is_professor_busy(professor, weekday, slot, self.schedule):
                if self.professors_info[professor]["current_hours"] < self.professors_info[professor]["max_hours"]:
                    if not is_professor_assigned_to_group_on_day(professor, group, weekday, self.schedule):
                        available_professors.append(professor)
        return available_professors

    def assign_professor(self, variable):
        """
        Призначає викладача до розкладу для заданої змінної.
        """
        group, weekday, slot = variable
        available_professors = self.get_available_professors(weekday, slot, group)
        if not available_professors:
            return False

        available_professors = heuristic_sort_professors(available_professors)
        for professor in available_professors:
            subjects = self.professors_info[professor]["subjects"]
            if subjects:
                subject = random.choice(subjects)
                available_rooms = get_available_rooms(weekday, slot, self.schedule)
                if available_rooms:
                    room = random.choice(available_rooms)
                    self.schedule[variable] = (professor, subject, room)
                    self.professors_info[professor]["current_hours"] += 1
                    return True
        return False

    def solve(self):
        """
        Алгоритм CSP для створення розкладу.
        """
        for variable in self.variables:
            assigned = self.assign_professor(variable)
            if not assigned:
                self.schedule[variable] = ("Вільно", "Немає предмету", "Немає аудиторії")
        return self.schedule


def print_schedule(schedule):
    """
    Друкує розклад для кожної групи, виводячи дні тижня і відповідні пари.
    """
    for group in groups:
      
        print(f"\n{'=' * 80}")
        print(f"Розклад для групи: {group}")
        print(f"{'=' * 80}")
        print(f"{'День тижня':<15}{'Час':<10}{'Предмет':<35}{'Тип':<10}{'Викладач':<30}{'Аудиторія':<10}")
        print(f"{'-' * 80}")  
        
        for weekday in weekdays:
            print(f"\n{weekday:<15}") 
            for slot in slots:
                key = (group, weekday, slot)
                if key in schedule:
                    professor, subject, room = schedule[key]
                    if professor != "Вільно":
                        
                        subject_name = subject["subject"] if isinstance(subject, dict) else subject
                        subject_type = subject["type"] if isinstance(subject, dict) else ""

                        print(
                            f"{'':<15}{slot:<10}{subject_name:<35}{subject_type:<10}{professor:<30}{room:<10}"
                        )
                    else:
                        print(f"{'':<15}{slot:<10}{'Вікно':<35}{'':<10}{'':<30}{'':<10}")
                else:
                    print(f"{'':<15}{slot:<10}{'Немає даних':<35}{'':<10}{'':<30}{'':<10}")
        print(f"{'=' * 80}") 

if __name__ == "__main__":
    csp = CSP(groups, weekdays, slots, professors_info)
    schedule = csp.solve()
    print_schedule(schedule)
