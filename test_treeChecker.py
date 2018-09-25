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


if __name__ == '__main__':
    print('Running Unit Tests')
    unittest.main()