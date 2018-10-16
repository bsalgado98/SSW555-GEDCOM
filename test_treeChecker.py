import unittest
import treeChecker
import datetime
from datetime import timedelta


class TestTreeChecker(unittest.TestCase):

    def setUp(self):
        pass

    def test_birthBeforeMarriage(self):
        # HUSB BIRT < MARR is true?
        # WIFE BIRT < MARR is true?
        birthdays = {'I1': datetime.datetime.strptime('12Sep2012', '%d%b%Y'),
                     'I2': datetime.datetime.strptime('10Sep2012', '%d%b%Y')}
        marriages = {('I1', 'I2'): datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeMarriage(birthdays, marriages), invalid)

        # HUSB BIRT > MARR is false?
        # WIFE BIRT < MARR is true?
        birthdays = {'I1': datetime.datetime.strptime('17Sep2012', '%d%b%Y'),
                     'I2': datetime.datetime.strptime('10Sep2012', '%d%b%Y')}
        marriages = {('I1', 'I2'): datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        invalid = ['I1']
        self.assertEqual(treeChecker.birthBeforeMarriage(birthdays, marriages), invalid)

        # HUSB BIRT < MARR is true?
        # WIFE BIRT > MARR is false?
        birthdays = {'I1': datetime.datetime.strptime('10Sep2012', '%d%b%Y'),
                     'I2': datetime.datetime.strptime('20Sep2012', '%d%b%Y')}
        marriages = {('I1', 'I2'): datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        invalid = ['I2']
        self.assertEqual(treeChecker.birthBeforeMarriage(birthdays, marriages), invalid)

        # HUSB BIRT > MARR is false?
        # WIFE BIRT > MARR is false?
        birthdays = {'I1': datetime.datetime.strptime('30Sep2012', '%d%b%Y'),
                     'I2': datetime.datetime.strptime('30Sep2012', '%d%b%Y')}
        marriages = {('I1', 'I2'): datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        invalid = ['I1', 'I2']
        self.assertEqual(treeChecker.birthBeforeMarriage(birthdays, marriages), invalid)

        # HUSB BIRT = MARR is true? (betrothed to marriage before birth)
        # WIFE BIRT = MARR is true? (https://www.worldvision.org/blog/child-marriage-betrothed-birth)
        birthdays = {'I1': datetime.datetime.strptime('16Sep2012', '%d%b%Y'),
                     'I2': datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        marriages = {('I1', 'I2'): datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeMarriage(birthdays, marriages), invalid)

    def test_birthBeforeDeath(self):
        # BIRT < DEAT is true?
        birthdays = {'I1': datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        deaths = {'I1': datetime.datetime.strptime('17Sep2012', '%d%b%Y')}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeDeath(birthdays, deaths), invalid)

        # BIRT > DEAT is false?
        birthdays = {'I1': datetime.datetime.strptime('18Sep2012', '%d%b%Y')}
        deaths = {'I1': datetime.datetime.strptime('17Sep2012', '%d%b%Y')}
        invalid = ['I1']
        self.assertEqual(treeChecker.birthBeforeDeath(birthdays, deaths), invalid)

        # BIRT = DEAT is true?
        birthdays = {'I2': datetime.datetime.strptime('17Sep2012', '%d%b%Y')}
        deaths = {'I2': datetime.datetime.strptime('17Sep2012', '%d%b%Y')}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeDeath(birthdays, deaths), invalid)

    def testBirthBeforeCurrentDate(self):
        # BIRT < Current Date True?
        birthday = {'I1': datetime.datetime.strptime('1Jan1997', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeCurrentDate(birthday), invalid)

        birthday = {'I1': datetime.datetime.strptime('29Sep1996', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeCurrentDate(birthday), invalid)

        # BIRT = Current Date True?
        birthday = {'I1': datetime.datetime.today().date()}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeCurrentDate(birthday), invalid)

        # BIRT > Current Date True?
        birthday = {'I1': datetime.datetime.strptime('12Dec2077', '%d%b%Y').date()}
        invalid = ['I1']
        self.assertEqual(treeChecker.birthBeforeCurrentDate(birthday), invalid)

        birthday = {'I2': datetime.datetime.strptime('3May2022', '%d%b%Y').date()}
        invalid = ['I2']
        self.assertEqual(treeChecker.birthBeforeCurrentDate(birthday), invalid)

    def testDeathBeforeCurrentDate(self):
        # DEAT < Current Date True?
        death = {'D1': datetime.datetime.strptime('1Jan1996', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.deathBeforeCurrentDate(death), invalid)

        death = {'D2': datetime.datetime.strptime('14Oct1996', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.deathBeforeCurrentDate(death), invalid)

        # DEAT = Current Date True?
        death = {'D3': datetime.datetime.today().date()}
        invalid = []
        self.assertEqual(treeChecker.deathBeforeCurrentDate(death), invalid)

        # DEAT > Current Date True?
        death = {'D4': datetime.datetime.strptime('11Dec2047', '%d%b%Y').date()}
        invalid = ['D4']
        self.assertEqual(treeChecker.deathBeforeCurrentDate(death), invalid)

        death = {'D5': datetime.datetime.strptime('3Jun2022', '%d%b%Y').date()}
        invalid = ['D5']
        self.assertEqual(treeChecker.deathBeforeCurrentDate(death), invalid)

    def testMarriageBeforeCurrentDate(self):
        # MARR < Current Date True?
        marriage = {'M1': datetime.datetime.strptime('1Feb1987', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.marriageBeforeCurrentDate(marriage), invalid)

        marriage = {'M2': datetime.datetime.strptime('29Nov1996', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.marriageBeforeCurrentDate(marriage), invalid)

        # MARR = Current Date True?
        marriage = {'M3': datetime.datetime.today().date()}
        invalid = []
        self.assertEqual(treeChecker.marriageBeforeCurrentDate(marriage), invalid)

        # MARR > Current Date True?
        marriage = {'M4': datetime.datetime.strptime('12Dec2177', '%d%b%Y').date()}
        invalid = ['M4']
        self.assertEqual(treeChecker.marriageBeforeCurrentDate(marriage), invalid)

        marriage = {'M5': datetime.datetime.strptime('3May2822', '%d%b%Y').date()}
        invalid = ['M5']
        self.assertEqual(treeChecker.marriageBeforeCurrentDate(marriage), invalid)

    def testDivorceBeforeCurrentDate(self):
        # DIV < Current Date True?
        divorce = {'Dv1': datetime.datetime.strptime('16May1998', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.divorcesBeforeCurrentDate(divorce), invalid)

        divorce = {'Dv2': datetime.datetime.strptime('21Dec2012', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.divorcesBeforeCurrentDate(divorce), invalid)

        # DIV = Current Date True?
        divorce = {'Dv3': datetime.datetime.today().date()}
        invalid = []
        self.assertEqual(treeChecker.divorcesBeforeCurrentDate(divorce), invalid)

        # DIV > Current Date True?
        divorce = {'Dv4': datetime.datetime.strptime('29Apr2777', '%d%b%Y').date()}
        invalid = ['Dv4']
        self.assertEqual(treeChecker.divorcesBeforeCurrentDate(divorce), invalid)

        divorce = {'Dv5': datetime.datetime.strptime('12May2050', '%d%b%Y').date()}
        invalid = ['Dv5']
        self.assertEqual(treeChecker.divorcesBeforeCurrentDate(divorce), invalid)

    def test_divorceBeforeDeath01(self):
        # Test if returns True when no deaths or divorces found
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": "NA"
            }
        }
        individualList = {
            "I1": {"DEAT": "NA"},
            "I2": {"DEAT": "NA"}
        }
        self.assertEqual(treeChecker.divorceBeforeDeath(treeList, individualList), [])

    def test_divorceBeforeDeath02(self):
        # Test if returns True when no deaths but a valid divorce is found
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": datetime.date(1, 1, 1)
            }
        }
        individualList = {
            "I1": {"DEAT": "NA"},
            "I2": {"DEAT": "NA"}
        }
        self.assertEqual(treeChecker.divorceBeforeDeath(treeList, individualList), [])

    def test_divorceBeforeDeath03(self):
        # Test if returns True when valid deaths and divorces are found
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": datetime.date(1, 1, 1)
            }
        }
        individualList = {
            "I1": {"DEAT": datetime.date(9999, 1, 1)},
            "I2": {"DEAT": datetime.date(9999, 1, 1)}
        }
        self.assertEqual(treeChecker.divorceBeforeDeath(treeList, individualList), [])

    def test_divorceBeforeDeath04(self):
        # Test if returns False when an invalid divorce is found due to the husband's death
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": datetime.date(9999, 1, 1)
            }
        }
        individualList = {
            "I1": {"DEAT": datetime.date(1, 1, 1)},
            "I2": {"DEAT": "NA"}
        }
        self.assertEqual(treeChecker.divorceBeforeDeath(treeList, individualList), ["F1"])

    def test_divorceBeforeDeath05(self):
        # Test if returns False when an invalid divorce is found due to the wife's death
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": datetime.date(9999, 1, 1)
            }
        }
        individualList = {
            "I1": {"DEAT": "NA"},
            "I2": {"DEAT": datetime.date(1, 1, 1)}
        }
        self.assertEqual(treeChecker.divorceBeforeDeath(treeList, individualList), ["F1"])

    def testAgeLimit(self):
        # Age < 150 years True?
        birthday = {'I1': datetime.datetime.strptime('30Jan1997', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.ageLimit(birthday), invalid)

        birthday = {'I1': datetime.datetime.strptime('29Apr2006', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.ageLimit(birthday), invalid)

        # Age = 150 years True?
        birthday = {'I1': (datetime.datetime.today().date() - timedelta(days=54750))}
        invalid = []
        self.assertEqual(treeChecker.ageLimit(birthday), invalid)

        # Age > Current Date True?
        birthday = {'I1': datetime.datetime.strptime('1Jan1000', '%d%b%Y').date()}
        invalid = ['I1']
        self.assertEqual(treeChecker.ageLimit(birthday), invalid)

        birthday = {'I2': datetime.datetime.strptime('12Oct1850', '%d%b%Y').date()}
        invalid = ['I2']
        self.assertEqual(treeChecker.ageLimit(birthday), invalid)

    def test_bigamy01(self):
        # Test if returns True when no bigamy is found
        treeList = {
            "F1": {
                "MARR": datetime.date(1, 1, 1),
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": "NA"
            }
        }
        individualList = {
            "I1": {"FAMS": "F1"},
            "I2": {"FAMS": "F1"}
        }
        individualDeaths = treeChecker.getIndividualDeaths(individualList)
        divorces = treeChecker.getDivorces(treeList)
        self.assertEqual(treeChecker.bigamy(treeList, individualList, individualDeaths, divorces), [])

    def test_bigamy02(self):
        # Test if returns False when bigamy with no divorces is found
        treeList = {
            "F1": {
                "MARR": datetime.date(1, 1, 1),
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": "NA"
            },
            "F2": {
                "MARR": datetime.date(1, 1, 2),
                "HUSB": "I1",
                "WIFE": "I3",
                "DIV": "NA"
            }
        }
        individualList = {
            "I1": {
                "SEX": "M",
                "DEAT": "NA",
                "FAMS": ["F1", "F2"],
            },
            "I2": {
                "SEX": "F",
                "DEAT": "NA",
                "FAMS": "F1",
            },
            "I3": {
                "SEX": "F",
                "DEAT": "NA",
                "FAMS": "F2",
            }
        }
        individualDeaths = treeChecker.getIndividualDeaths(individualList)
        divorces = treeChecker.getDivorces(treeList)
        self.assertEqual(treeChecker.bigamy(treeList, individualList, individualDeaths, divorces), ["I1"])

    def test_bigamy03(self):
        # Test if returns False when bigamy with divorces is found
        treeList = {
            "F1": {
                "MARR": datetime.date(1, 1, 1),
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": datetime.date(1, 1, 3)
            },
            "F2": {
                "MARR": datetime.date(1, 1, 2),
                "HUSB": "I1",
                "WIFE": "I3",
                "DIV": "NA"
            }
        }
        individualList = {
            "I1": {
                "SEX": "M",
                "DEAT": "NA",
                "FAMS": ["F1", "F2"],
            },
            "I2": {
                "SEX": "F",
                "DEAT": "NA",
                "FAMS": "F1",
            },
            "I3": {
                "SEX": "F",
                "DEAT": "NA",
                "FAMS": "F2",
            }
        }
        individualDeaths = treeChecker.getIndividualDeaths(individualList)
        divorces = treeChecker.getDivorces(treeList)
        self.assertEqual(treeChecker.bigamy(treeList, individualList, individualDeaths, divorces), ["I1"])

    def test_bigamy04(self):
        # Test if returns False when bigamy with deaths is found
        treeList = {
            "F1": {
                "MARR": datetime.date(1, 1, 1),
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": "NA"
            },
            "F2": {
                "MARR": datetime.date(1, 1, 2),
                "HUSB": "I1",
                "WIFE": "I3",
                "DIV": "NA"
            }
        }
        individualList = {
            "I1": {
                "SEX": "M",
                "DEAT": "NA",
                "FAMS": ["F1", "F2"],
            },
            "I2": {
                "SEX": "F",
                "DEAT": datetime.date(1, 1, 3),
                "FAMS": "F1",
            },
            "I3": {
                "SEX": "F",
                "DEAT": "NA",
                "FAMS": "F2",
            }
        }
        individualDeaths = treeChecker.getIndividualDeaths(individualList)
        divorces = treeChecker.getDivorces(treeList)
        self.assertEqual(treeChecker.bigamy(treeList, individualList, individualDeaths, divorces), ["I1"])

    def test_bigamy05(self):
        # Test if returns False when bigamy with both divorce and death is found
        treeList = {
            "F1": {
                "MARR": datetime.date(1, 1, 1),
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": datetime.date(1, 1, 3)
            },
            "F2": {
                "MARR": datetime.date(1, 1, 2),
                "HUSB": "I1",
                "WIFE": "I3",
                "DIV": "NA"
            }
        }
        individualList = {
            "I1": {
                "SEX": "M",
                "DEAT": "NA",
                "FAMS": ["F1", "F2"],
            },
            "I2": {
                "SEX": "F",
                "DEAT": datetime.date(1, 1, 4),
                "FAMS": "F1",
            },
            "I3": {
                "SEX": "F",
                "DEAT": "NA",
                "FAMS": "F2",
            }
        }
        individualDeaths = treeChecker.getIndividualDeaths(individualList)
        divorces = treeChecker.getDivorces(treeList)
        self.assertEqual(treeChecker.bigamy(treeList, individualList, individualDeaths, divorces), ["I1"])

    def test_childrenLimit01(self):
        # Test if childrenLimit returns the invalid family when a family has 15 or more children
        treeList = {
            "F1": {
                "CHIL": ["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9", "I10", "I11", "I12", "I13", "I14", "I15"]
            }
        }
        self.assertEqual(treeChecker.childrenLimit(treeList), ["F1"])

    def test_childrenLimit02(self):
        # Test if childrenLimit returns an empty list when a family does not have 15 or more children
        treeList = {
            "F1": {
                "CHIL": "I1"
            }
        }
        self.assertEqual(treeChecker.childrenLimit(treeList), [])

    def test_consistentLastNames01(self):
        # Test if consistentLastNames returns the invalid family when a family has inconsistent last names for the males
        treeList = {
            "F1": {
                "HUSB": "I1",
                "CHIL": "I2"
            }
        }
        individualList = {
            "I1": {
                "NAME": "John /Doe/",
                "SEX": "M"
            },
            "I2": {
                "NAME": "John /Smith/",
                "SEX": "M"
            }
        }
        self.assertEqual(treeChecker.consistentLastNames(treeList, individualList), ["F1"])

    def test_consistentLastNames02(self):
        # Test if consistentLastNames returns an empty list when a family has consistent last names for the males
        treeList = {
            "F1": {
                "HUSB": "I1",
                "CHIL": "I2"
            }
        }
        individualList = {
            "I1": {
                "NAME": "John /Doe/",
                "SEX": "M"
            },
            "I2": {
                "NAME": "John /Doe/",
                "SEX": "M"
            }
        }
        self.assertEqual(treeChecker.consistentLastNames(treeList, individualList), [])


    def test_parentsNotTooOld(self):
        #Test if marriageAfter14 returns an empty list when checking correct family ages
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "CHIL": "I3"
            }
        }
        individualList = {
            "I1": {
                "NAME": "Jane /Doe/",
                "SEX": "F"
            },
            "I2": {
                "NAME": "John /Doe/",
                "SEX": "M"
            },
            "I3": {
                "NAME": "Tom /Doe/",
                "SEX": "M",
            }
        }
        individualBirthdays = treeChecker.getIndividualBirthdays(individualList)
        self.assertEqual(treeChecker.parentsNotTooOld(treeList, individualList, individualBirthdays), []) 

    def test_marriageAfter14(self):
        individualList = {
           "I1": {
                "NAME": "Jane /Doe/",
                "SEX": "F",
                "BIRT": datetime.datetime.strptime('1Jan1960', '%d%b%Y').date(),
            },
            "I2": {
                "NAME": "John /Doe/",
                "SEX": "M",
                "BIRT": datetime.datetime.strptime('1Jan1962', '%d%b%Y').date(),
            },
            "I3": {
                "NAME": "Tom /Doe/",
                "SEX": "M",
                "BIRT": datetime.datetime.strptime('1Jan1997', '%d%b%Y').date(),
            }
        }
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "CHIL": "I3",
                "MARR": datetime.datetime.strptime('1Jan1980', '%d%b%Y').date(),
            }
        }
        marriages = treeChecker.getMarriages(treeList)
        individualBirthdays = treeChecker.getIndividualBirthdays(individualList)
        self.assertEqual(treeChecker.marriageAfter14(individualBirthdays, marriages), []) 





if __name__ == '__main__':
    print('Running Unit Tests')
    unittest.main()
