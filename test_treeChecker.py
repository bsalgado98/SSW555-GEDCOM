import unittest
import treeChecker
import datetime

class TestTreeChecker(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_birthBeforeMarriage(self):
        # HUSB BIRT < MARR is true?
        # WIFE BIRT < MARR is true?
        birthdays = {'I1' : datetime.datetime.strptime('12Sep2012', '%d%b%Y'), 'I2' : datetime.datetime.strptime('10Sep2012', '%d%b%Y')}
        marriages = {('I1', 'I2') : datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeMarriage(birthdays, marriages), invalid)
        
        # HUSB BIRT > MARR is false?
        # WIFE BIRT < MARR is true?
        birthdays = {'I1' : datetime.datetime.strptime('17Sep2012', '%d%b%Y'), 'I2' : datetime.datetime.strptime('10Sep2012', '%d%b%Y')}
        marriages = {('I1', 'I2') : datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        invalid = ['I1']
        self.assertEqual(treeChecker.birthBeforeMarriage(birthdays, marriages), invalid)
        
        # HUSB BIRT < MARR is true?
        # WIFE BIRT > MARR is false?
        birthdays = {'I1' : datetime.datetime.strptime('10Sep2012', '%d%b%Y'), 'I2' : datetime.datetime.strptime('20Sep2012', '%d%b%Y')}
        marriages = {('I1', 'I2') : datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        invalid = ['I2']
        self.assertEqual(treeChecker.birthBeforeMarriage(birthdays, marriages), invalid)
        
        # HUSB BIRT > MARR is false?
        # WIFE BIRT > MARR is false?
        birthdays = {'I1' : datetime.datetime.strptime('30Sep2012', '%d%b%Y'), 'I2' : datetime.datetime.strptime('30Sep2012', '%d%b%Y')}
        marriages = {('I1', 'I2') : datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        invalid = ['I1', 'I2']
        self.assertEqual(treeChecker.birthBeforeMarriage(birthdays, marriages), invalid)
        
        # HUSB BIRT = MARR is true? (betrothed to marriage before birth)
        # WIFE BIRT = MARR is true? (https://www.worldvision.org/blog/child-marriage-betrothed-birth)
        birthdays = {'I1' : datetime.datetime.strptime('16Sep2012', '%d%b%Y'), 'I2' : datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        marriages = {('I1', 'I2') : datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeMarriage(birthdays, marriages), invalid)
        
    def test_birthBeforeDeath(self):
        # BIRT < DEAT is true?
        birthdays = {'I1' : datetime.datetime.strptime('16Sep2012', '%d%b%Y')}
        deaths = {'I1' : datetime.datetime.strptime('17Sep2012', '%d%b%Y')}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeDeath(birthdays, deaths), invalid)
        
        # BIRT > DEAT is false?
        birthdays = {'I1' : datetime.datetime.strptime('18Sep2012', '%d%b%Y')}
        deaths = {'I1' : datetime.datetime.strptime('17Sep2012', '%d%b%Y')}
        invalid = ['I1']
        self.assertEqual(treeChecker.birthBeforeDeath(birthdays, deaths), invalid)
        
        # BIRT = DEAT is true?
        birthdays = {'I2' : datetime.datetime.strptime('17Sep2012', '%d%b%Y')}
        deaths = {'I2' : datetime.datetime.strptime('17Sep2012', '%d%b%Y')}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeDeath(birthdays, deaths), invalid)

    def testBirthBeforeCurrentDate(self):
        # BIRT < Current Date True?
        birthday = {'I1' : datetime.datetime.strptime('1Jan1997', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeCurrentDate(birthday), invalid)

        birthday = {'I1': datetime.datetime.strptime('29Sep1996', '%d%b%Y').date()}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeCurrentDate(birthday), invalid)

        # BIRT = Current Date True?
        birthday = {'I1': datetime.datetime.today().date()}
        invalid = []
        self.assertEqual(treeChecker.birthBeforeCurrentDate(birthday), invalid)

        # BIRT > Current Date False?
        birthday = {'I1' : datetime.datetime.strptime('12Dec2077', '%d%b%Y').date()}
        invalid = ['I1']
        self.assertEqual(treeChecker.birthBeforeCurrentDate(birthday), invalid)

        birthday = {'I2': datetime.datetime.strptime('3May2022', '%d%b%Y').date()}
        invalid = ['I2']
        self.assertEqual(treeChecker.birthBeforeCurrentDate(birthday), invalid)

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
        self.assertEqual(treeChecker.divorceBeforeDeath(treeList, individualList), True)

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
        self.assertEqual(treeChecker.divorceBeforeDeath(treeList, individualList), True)

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
        self.assertEqual(treeChecker.divorceBeforeDeath(treeList, individualList), True)

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
        self.assertEqual(treeChecker.divorceBeforeDeath(treeList, individualList), False)

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
        self.assertEqual(treeChecker.divorceBeforeDeath(treeList, individualList), False)

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
        self.assertEqual(treeChecker.bigamy(treeList, individualList), True)

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
        self.assertEqual(treeChecker.bigamy(treeList, individualList), False)

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
        self.assertEqual(treeChecker.bigamy(treeList, individualList), False)

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
        self.assertEqual(treeChecker.bigamy(treeList, individualList), False)

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
        self.assertEqual(treeChecker.bigamy(treeList, individualList), False)

if __name__ == '__main__':
    print('Running Unit Tests')
    unittest.main()
