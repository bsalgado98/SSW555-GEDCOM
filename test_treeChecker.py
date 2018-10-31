import datetime
import sqlite3
import unittest
from datetime import timedelta
from os import mkdir, path
from shutil import rmtree
import io
import sys

import Salgado_parseGEDCOM
import treeChecker
import printTable

def dictToGEDCOM(zeroName, dictionary):
    lines = []
    for ident, tags in dictionary.items():
        lines.append("0 " + ident + " " + zeroName)
        for tag, value in tags.items():
            if isinstance(value, datetime.date):
                lines.append("1 " + tag + " " + value.strftime("%d %b %Y"))
            elif isinstance(value, list):
                for item in value:
                    lines.append("1 " + tag + " " + item)
            else:
                lines.append("1 " + tag + " " + value)
    return lines


def setupTestDB(dbFile, famDict=None, indiDict=None):
    if not path.exists("temp"):
        mkdir("temp")
    if famDict is None:
        famDict = {}
    if indiDict is None:
        indiDict = {}
    gedcom = dictToGEDCOM("FAM", famDict) + dictToGEDCOM("INDI", indiDict)
    Salgado_parseGEDCOM.parse(gedcom, "file:temp/" + dbFile)
    return sqlite3.connect("file:temp/" + dbFile, uri=True).cursor()


class TestTreeChecker(unittest.TestCase):

    def setUp(self):
        if not path.exists("temp"):
            mkdir("temp")

    def tearDown(self):
        rmtree("temp")

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
            }
        }
        cursor = setupTestDB("divorceBeforeDeath01.db", famDict=treeList)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        divorces = treeChecker.getDivorces(cursor)
        self.assertEqual(treeChecker.divorceBeforeDeath(cursor, individualDeaths, divorces), [])

    def test_divorceBeforeDeath02(self):
        # Test if returns True when no deaths but a valid divorce is found
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": datetime.date(1, 1, 1)
            }
        }
        cursor = setupTestDB("divorceBeforeDeath02.db", famDict=treeList)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        divorces = treeChecker.getDivorces(cursor)
        self.assertEqual(treeChecker.divorceBeforeDeath(cursor, individualDeaths, divorces), [])

    def test_divorceBeforeDeath03(self):
        # Test if returns True when valid deaths and divorces are found
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "DIV": datetime.date(1, 1, 1)
            }
        }
        cursor = setupTestDB("divorceBeforeDeath03.db", famDict=treeList)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        divorces = treeChecker.getDivorces(cursor)
        self.assertEqual(treeChecker.divorceBeforeDeath(cursor, individualDeaths, divorces), [])

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
            "I1": {
                "DEAT": datetime.date(1, 1, 1)
            }
        }
        cursor = setupTestDB("divorceBeforeDeath04.db", treeList, individualList)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        divorces = treeChecker.getDivorces(cursor)
        self.assertEqual(treeChecker.divorceBeforeDeath(cursor, individualDeaths, divorces), ["F1"])

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
            "I2": {
                "DEAT": datetime.date(1, 1, 1)
            }
        }
        cursor = setupTestDB("divorceBeforeDeath05.db", treeList, individualList)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        divorces = treeChecker.getDivorces(cursor)
        self.assertEqual(treeChecker.divorceBeforeDeath(cursor, individualDeaths, divorces), ["F1"])

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
            }
        }
        individualList = {
            "I1": {"FAMS": "F1"},
            "I2": {"FAMS": "F1"}
        }
        cursor = setupTestDB("bigamy01.db", treeList, individualList)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        divorces = treeChecker.getDivorces(cursor)
        self.assertEqual(treeChecker.bigamy(cursor, individualDeaths, divorces), [])

    def test_bigamy02(self):
        # Test if returns False when bigamy with no divorces is found
        treeList = {
            "F1": {
                "MARR": datetime.date(1, 1, 1),
                "HUSB": "I1",
                "WIFE": "I2",
            },
            "F2": {
                "MARR": datetime.date(1, 1, 2),
                "HUSB": "I1",
                "WIFE": "I3",
            }
        }
        individualList = {
            "I1": {
                "SEX": "M",
                "FAMS": ["F1", "F2"],
            },
            "I2": {
                "SEX": "F",
                "FAMS": "F1",
            },
            "I3": {
                "SEX": "F",
                "FAMS": "F2",
            }
        }
        cursor = setupTestDB("bigamy02.db", treeList, individualList)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        divorces = treeChecker.getDivorces(cursor)
        self.assertEqual(treeChecker.bigamy(cursor, individualDeaths, divorces), ["I1"])

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
            }
        }
        individualList = {
            "I1": {
                "SEX": "M",
                "FAMS": ["F1", "F2"],
            },
            "I2": {
                "SEX": "F",
                "FAMS": "F1",
            },
            "I3": {
                "SEX": "F",
                "FAMS": "F2",
            }
        }
        cursor = setupTestDB("bigamy03.db", treeList, individualList)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        divorces = treeChecker.getDivorces(cursor)
        self.assertEqual(treeChecker.bigamy(cursor, individualDeaths, divorces), ["I1"])

    def test_bigamy04(self):
        # Test if returns False when bigamy with deaths is found
        treeList = {
            "F1": {
                "MARR": datetime.date(1, 1, 1),
                "HUSB": "I1",
                "WIFE": "I2",
            },
            "F2": {
                "MARR": datetime.date(1, 1, 2),
                "HUSB": "I1",
                "WIFE": "I3",
            }
        }
        individualList = {
            "I1": {
                "SEX": "M",
                "FAMS": ["F1", "F2"],
            },
            "I2": {
                "SEX": "F",
                "DEAT": datetime.date(1, 1, 3),
                "FAMS": "F1",
            },
            "I3": {
                "SEX": "F",
                "FAMS": "F2",
            }
        }
        cursor = setupTestDB("bigamy04.db", treeList, individualList)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        divorces = treeChecker.getDivorces(cursor)
        self.assertEqual(treeChecker.bigamy(cursor, individualDeaths, divorces), ["I1"])

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
            }
        }
        individualList = {
            "I1": {
                "SEX": "M",
                "FAMS": ["F1", "F2"],
            },
            "I2": {
                "SEX": "F",
                "DEAT": datetime.date(1, 1, 4),
                "FAMS": "F1",
            },
            "I3": {
                "SEX": "F",
                "FAMS": "F2",
            }
        }
        cursor = setupTestDB("bigamy05.db", treeList, individualList)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        divorces = treeChecker.getDivorces(cursor)
        self.assertEqual(treeChecker.bigamy(cursor, individualDeaths, divorces), ["I1"])

    def test_childbirth_beforeparentmarriage01(self):
        # Test Child born before parents marriage = True
        treeList = {
            "F1": {
                "MARR": datetime.date(1990, 12, 15),
                "HUSB": "I1",
                "WIFE": "I2",
                "CHIL": "I3"
            }
        }
        individualList = {
            "I3": {"BIRT": datetime.date(1985, 12, 20)}
        }
        cursor = setupTestDB("beforeparentmarriage01.db", treeList, individualList)
        individualBirthdays = treeChecker.getIndividualBirthdays(cursor)
        self.assertEqual(treeChecker.birthBeforeParentsMarriage(cursor, individualBirthdays), ["I3"])

    def test_childbirth_beforeparentmarriage02(self):
        # Test Child born before parents marriage = False
        treeList = {
            "F1": {
                "MARR": datetime.date(1990, 12, 15),
                "HUSB": "I1",
                "WIFE": "I2",
                "CHIL": "I3"
            }
        }
        individualList = {
            "I3": {"BIRT": datetime.date(2000, 12, 20)}
        }
        cursor = setupTestDB("beforeparentmarriage02.db", treeList, individualList)
        individualBirthdays = treeChecker.getIndividualBirthdays(cursor)
        self.assertEqual(treeChecker.birthBeforeParentsMarriage(cursor, individualBirthdays), [])

    def test_childbirth_afterparentdeath01(self):
        # Test Child born more than 9 months after Father death
        treeList = {
            "F1": {
                "MARR": datetime.date(1990, 12, 15),
                "HUSB": "I1",
                "WIFE": "I2",
                "CHIL": "I3"
            }
        }
        individualList = {
            "I1": {"DEAT": datetime.date(1980, 4, 13)},
            "I2": {},
            "I3": {"BIRT": datetime.date(1985, 12, 20)}
        }
        cursor = setupTestDB("afterparentdeath01.db", treeList, individualList)
        individualBirthdays = treeChecker.getIndividualBirthdays(cursor)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        self.assertEqual(treeChecker.birthBeforeParentsDeath(cursor, individualBirthdays, individualDeaths), ["I3"])

    def test_childbirth_afterparentdeath02(self):
        # Test Child born less than 9 months after Father death
        treeList = {
            "F1": {
                "MARR": datetime.date(1990, 12, 15),
                "HUSB": "I1",
                "WIFE": "I2",
                "CHIL": "I3"
            }
        }
        individualList = {
            "I1": {"DEAT": datetime.date(1985, 5, 13)},
            "I3": {"BIRT": datetime.date(1985, 4, 20)}
        }
        cursor = setupTestDB("afterparentdeath02.db", treeList, individualList)
        individualBirthdays = treeChecker.getIndividualBirthdays(cursor)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        self.assertEqual(treeChecker.birthBeforeParentsDeath(cursor, individualBirthdays, individualDeaths), [])

    def test_childbirth_afterparentdeath03(self):
        # Test Child born after Mother death
        treeList = {
            "F1": {
                "MARR": datetime.date(1990, 12, 15),
                "HUSB": "I1",
                "WIFE": "I2",
                "CHIL": "I3"
            }
        }
        individualList = {
            "I2": {"DEAT": datetime.date(2000, 5, 13)},
            "I3": {"BIRT": datetime.date(2000, 4, 20)}
        }
        cursor = setupTestDB("afterparentdeath03.db", treeList, individualList)
        individualBirthdays = treeChecker.getIndividualBirthdays(cursor)
        individualDeaths = treeChecker.getIndividualDeaths(cursor)
        self.assertEqual(treeChecker.birthBeforeParentsDeath(cursor, individualBirthdays, individualDeaths), [])

    def test_childrenLimit01(self):
        # Test if childrenLimit returns the invalid family when a family has 15 or more children
        treeList = {
            "F1": {
                "CHIL": ["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9", "I10", "I11", "I12", "I13", "I14", "I15"]
            }
        }
        cursor = setupTestDB("childrenLimit01.db", famDict=treeList)
        self.assertEqual(treeChecker.childrenLimit(cursor), ["F1"])

    def test_childrenLimit02(self):
        # Test if childrenLimit returns an empty list when a family does not have 15 or more children
        treeList = {
            "F1": {
                "CHIL": "I1"
            }
        }
        cursor = setupTestDB("childrenLimit02.db", famDict=treeList)
        self.assertEqual(treeChecker.childrenLimit(cursor), [])

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
        cursor = setupTestDB("consistentLastNames01.db", treeList, individualList)
        self.assertEqual(treeChecker.consistentLastNames(cursor), ["F1"])

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
        cursor = setupTestDB("consistentLastNames02.db", treeList, individualList)
        self.assertEqual(treeChecker.consistentLastNames(cursor), [])

    def test_parentsNotTooOld(self):
        # Test if marriageAfter14 returns an empty list when checking correct family ages
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
                "SEX": "F",
                "BIRT": datetime.date(1990, 12, 15)
            },
            "I2": {
                "NAME": "John /Doe/",
                "SEX": "M",
                "BIRT": datetime.date(1990, 12, 15)
            },
            "I3": {
                "NAME": "Tom /Doe/",
                "SEX": "M",
                "BIRT": datetime.date(1990, 12, 15)
            }
        }
        cursor = setupTestDB("parentsNotTooOld.db", treeList, individualList)
        individualBirthdays = treeChecker.getIndividualBirthdays(cursor)
        self.assertEqual(treeChecker.parentsNotTooOld(cursor, individualBirthdays), ['I1', 'I2'])

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
        cursor = setupTestDB("marriageAfter14.db", treeList, individualList)
        marriages = treeChecker.getMarriages(cursor)
        individualBirthdays = treeChecker.getIndividualBirthdays(cursor)
        self.assertEqual(treeChecker.marriageAfter14(individualBirthdays, marriages), [])

    def test_siblingsSpacing(self):
        treeList = {"TEST_FAMILY1": {"CHIL": ["A", "B"]}, "TEST_FAMILY2": {"CHIL": ["C", "D", "E"]}}
        individualBirthdays = {"A": datetime.date(1, 1, 1), "B": datetime.date(1, 1, 2), "C": datetime.date(1, 1, 1),
                               "D": datetime.date(1, 1, 6), "E": datetime.date(1, 1, 10)}
        cursor = setupTestDB("siblingSpacing.db", famDict=treeList)
        self.assertEqual(treeChecker.siblingsSpacing(cursor, individualBirthdays), ['C and D', 'C and E', 'D and E'])

    def test_multipleBirths(self):
        treeList = {"TEST_FAMILY1": {"CHIL": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]}}
        individualBirthdays = {"1": datetime.date(1, 1, 1), "2": datetime.date(1, 1, 1), "3": datetime.date(1, 1, 1),
                               "4": datetime.date(1, 1, 1), "5": datetime.date(1, 1, 1), "6": datetime.date(1, 1, 1),
                               "7": datetime.date(2, 2, 2), "8": datetime.date(3, 3, 3), "9": datetime.date(3, 3, 3),
                               "10": datetime.date(3, 3, 3), "11": datetime.date(3, 3, 3), "12": datetime.date(3, 3, 3),
                               "13": datetime.date(3, 3, 3)}
        cursor = setupTestDB("multipleBirths", famDict=treeList)
        self.assertEqual(treeChecker.multipleBirths(cursor, individualBirthdays),
                         ["Invalid siblings: ['1', '2', '3', '4', '5', '6']",
                          "Invalid siblings: ['8', '9', '10', '11', '12', '13']"])

    def test_uniqueIDs(self):
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2"
            },
            "F2": {
                "HUSB": "I3",
                "WIFE": "I4"
            }
        }
        individualList = {
            "I1": {
                "NAME": "John /Doe/",
            },
            "I2": {
                "NAME": "Jessica /Doe/",
            },
            "I3": {
                "NAME": "John /Dang/"
            },
            "I4": {
                "NAME": "Jessica /Dang/"
            }
        }
        cursor = setupTestDB("uniqueIDs.db", treeList, individualList)
        self.assertEqual(treeChecker.uniqueIDs(cursor), ([], []))

    def test_uniqueNameAndBirthDate01(self):
        individualList = {
            "I1": {
                "NAME": "John /Doe/",
                "BIRT": datetime.date(1, 1, 1)
            },
            "I2": {
                "NAME": "John /Doe/",
                "BIRT": datetime.date(1, 1, 1)
            }
        }
        cursor = setupTestDB("uniqueNameAndBirthDate01.db", individualList)
        self.assertEqual(treeChecker.uniqueIDs(cursor), ([], []))

    def test_uniqueNameAndBirthDate02(self):
        individualList = {
            "I1": {
                "NAME": "John /Damn/",
                "BIRT": datetime.date(1, 1, 1)
            },
            "I2": {
                "NAME": "John /Doe/",
                "BIRT": datetime.date(1, 1, 1)
            },
            "I3": {
                "NAME": "John /Doe/",
                "BIRT": datetime.date(1, 2, 1)
            }
        }
        cursor = setupTestDB("uniqueNameAndBirthDate02.db", individualList)
        self.assertEqual(treeChecker.uniqueIDs(cursor), ([], []))

    def test_allUniqueSpousePairs01(self):
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2"
            },
            "F2": {
                "HUSB": "I1",
                "WIFE": "I2"
            }
        }
        cursor = setupTestDB("allUniqueSpousePairs01.db", famDict=treeList)
        self.assertEqual(treeChecker.allUniqueSpousePairs(cursor), [("I1", "I2")])

    def test_allUniqueSpousePairs02(self):
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2"
            },
            "F2": {
                "HUSB": "I2",
                "WIFE": "I3"
            }
        }
        cursor = setupTestDB("allUniqueSpousePairs02.db", famDict=treeList)
        self.assertEqual(treeChecker.allUniqueSpousePairs(cursor), [])

    def test_uniqueFirstNames01(self):
        treeList = {
            "F1": {
                "CHIL": ["I1", "I2"]
            }
        }
        individualList = {
            "I1": {
                "NAME": "John /Doe/",
                "BIRT": datetime.date(1, 1, 1)
            },
            "I2": {
                "NAME": "John /Doe/",
                "BIRT": datetime.date(1, 1, 1)
            }
        }
        cursor = setupTestDB("uniqueFirstNames01.db", treeList, individualList)
        self.assertEqual(treeChecker.uniqueFirstNames(cursor), ["John /Doe/"])

    def test_uniqueFirstNames02(self):
        treeList = {
            "F1": {
                "CHIL": ["I1", "I2"]
            }
        }
        individualList = {
            "I1": {
                "NAME": "John /Doe/",
                "BIRT": datetime.date(1, 1, 1)
            },
            "I2": {
                "NAME": "John /Doe/",
                "BIRT": datetime.date(1, 1, 2)
            }
        }
        cursor = setupTestDB("uniqueFirstNames02.db", treeList, individualList)
        self.assertEqual(treeChecker.uniqueFirstNames(cursor), [])


    def test_siblingsShouldNotMarry(self):
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
                "SEX": "M"
            },
            "I4": {
                "NAME": "Sally /Doe/",
                "SEX": "F"
            }
        }

        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "CHIL": ["I3","I4"]
            },
            "F2": {
                "HUSB": "I3",
                "WIFE": "I4",
                "CHIL": "I3"
            }
        }
        cursor = setupTestDB("siblingsShouldNotMarry.db", treeList, individualList)
        marriages = treeChecker.getMarriages(cursor)
        self.assertEqual(treeChecker.siblingsShouldNotMarry(cursor, marriages), [])



    def test_correctGenderForRole(self):
        treeList = {
            "F1": {
                "HUSB": "I1",
                "WIFE": "I2",
                "CHIL": ["I3","I4"]
            }
        }
        individualList = { 
            "I1": {
                    "NAME": "John /Doe/",
                    "SEX": "F"
                },
            "I2": {
                "NAME": "Mary /Doe/",
                "SEX": "F"
            }
        }
        cursor = setupTestDB("correctGenderForRole.db", treeList, individualList)
        self.assertEqual(treeChecker.correctGenderForRole(cursor), ["I1"])

    def test_correspondingEntries(self):
        treeList = {
            "F1": ['I1', 'I2', ['I3', 'I4']],
            "F2": ['I5', 'I6', ['I7', 'I8']]
        }
        indiList = {
            "I1": ['M', None, ['F1']],
            "I2": ['F', None, ['F1']],
            "I3": ['M', 'F1', [None]],
            "I4": ['F', 'F1', [None]],
            "I5": ['F', None, ['F2']],
            "I6": ['F', None, ['F1']],
            "I7": ['M', 'F1', [None]],
            "I8": ['F', 'F1', [None]]
        }
        self.assertEqual(treeChecker.correspondingEntries(treeList, indiList), [
            'Misgendered wife in family: F1',
            'Misgendered husband in family: F2',
            'Missing wife: I6 in family: F2',
            'Missing child: I7 in family: F2',
            'Missing child: I8 in family: F2'
        ])
        
    def test_orderSiblingsByAge(self):
        self.maxDiff = None
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        printTable.printTree()
        sys.stdout = sys.__stdout__
        self.assertEqual(capturedOutput.getvalue(), capturedOutput.getValue())
        
if __name__ == '__main__':
    print('Running Unit Tests')
    unittest.main()
