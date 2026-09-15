import unittest
from contextlib import redirect_stdout
from io import StringIO


class Person:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def printInfo(self):
        print("id: {0}, name: {1}".format(self.id, self.name))


class Manager(Person):
    def __init__(self, id, name, title):
        super().__init__(id, name)
        self.title = title

    def printInfo(self):
        print("id: {0}, name: {1}, title: {2}".format(
            self.id, self.name, self.title))


class Employee(Person):
    def __init__(self, id, name, skill):
        super().__init__(id, name)
        self.skill = skill

    def printInfo(self):
        print("id: {0}, name: {1}, skill: {2}".format(
            self.id, self.name, self.skill))


class TestPerson(unittest.TestCase):
    def test_person_id(self):
        self.assertEqual(Person(1, "Kim").id, 1)

    def test_person_name(self):
        self.assertEqual(Person(1, "Kim").name, "Kim")

    def test_person_print_info(self):
        output = StringIO()
        with redirect_stdout(output):
            Person(1, "Kim").printInfo()
        self.assertEqual(output.getvalue(), "id: 1, name: Kim\n")

    def test_manager_is_person(self):
        self.assertIsInstance(Manager(2, "Lee", "Team Leader"), Person)

    def test_manager_title(self):
        self.assertEqual(Manager(2, "Lee", "Team Leader").title, "Team Leader")

    def test_manager_print_info(self):
        output = StringIO()
        with redirect_stdout(output):
            Manager(2, "Lee", "Team Leader").printInfo()
        self.assertEqual(output.getvalue(),
                         "id: 2, name: Lee, title: Team Leader\n")

    def test_employee_is_person(self):
        self.assertIsInstance(Employee(3, "Park", "Python"), Person)

    def test_employee_skill(self):
        self.assertEqual(Employee(3, "Park", "Python").skill, "Python")

    def test_employee_print_info(self):
        output = StringIO()
        with redirect_stdout(output):
            Employee(3, "Park", "Python").printInfo()
        self.assertEqual(output.getvalue(), "id: 3, name: Park, skill: Python\n")

    def test_each_class_has_expected_members(self):
        manager = Manager(2, "Lee", "Team Leader")
        employee = Employee(3, "Park", "Python")
        self.assertEqual(manager.__dict__, {
            "id": 2, "name": "Lee", "title": "Team Leader"})
        self.assertEqual(employee.__dict__, {
            "id": 3, "name": "Park", "skill": "Python"})


if __name__ == "__main__":
    unittest.main()