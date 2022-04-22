import time
import unittest
import json
from unittest.suite import TestSuite
from customResult import CustomResults
from operator import itemgetter
from myrequests import *


class GetTest(unittest.TestCase):
    def test_getTests__critical(self):
        self.assertTrue(getTest(critical=True, type="AG"))
        self.assertTrue(getTest(critical=True, type="PCR"))


class TestCount(unittest.TestCase):
    def test_getCount__minor(self):
        self.assertAlmostEqual(getTest(type="PCR"), 3, delta=1)
        self.assertAlmostEqual(getTest(type="PCR"), -1, delta=1)

    def test_getCount__normal(self):
        self.assertAlmostEqual(getTest(type="AG"), 3, delta=3)
        self.assertAlmostEqual(getTest(type="AG"), 1, delta=3)


class TestTypes(unittest.TestCase):
    def test_checkType__minor(self):
        self.assertTrue(checkTestTypes())


class CreateTest(unittest.TestCase):
    def test_put__major(self):
        self.assertTrue(createTest(id=10, type="AG"))


class DeleteTest(unittest.TestCase):
    def test_delete__major(self):
        self.assertTrue(deleteTest(56))

    def test_handleDelete__normal(self):
        self.assertRaises(AssertionError, deleteTest, 0)


class EditTest(unittest.TestCase):
    def test_post__major(self):
        self.assertTrue(editTest(id=20, type="AG"))
        self.assertFalse(editTest(id=20, type="invalid type"))


def fetchResults():
    with open('results.json') as json_file:
        data = json.load(json_file)
        json_file.close()
        return data


def fetchTimes():
    with open('runtimes.json') as json_file:
        data = json.load(json_file)
        json_file.close()
        return data


def generateOutput(result=None, data=None, time=None, next=None):
    data[next] = result.generateEntry()
    with open('results.json', 'w') as json_file:
        json.dump(data, json_file)
    time[next] = result.generateTime()
    with open('runtimes.json', 'w') as json_file:
        json.dump(time, json_file)
    counts = result.generateCounts()
    with open('counts.json', 'w') as json_file:
        json.dump(counts, json_file)


def createSuite(testcases=None, first=None):
    toTest = []
    if first:
        for test in testcases.items():
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(test[1])
            toTest.append(suite)
    else:
        for test in testcases:
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(test)
            toTest.append(suite)
    return toTest


def processStats(data=None, keys=None, round=True):
    stats = {}
    for key in keys:
        run = data[key]
        entries = list(run.keys())
        for entry in entries:
            try:
                stats[entry] = stats[entry] + run[entry]
            except:
                stats[entry] = run[entry]
    with open('counts.json') as json_file:
        counts = json.load(json_file)
        json_file.close()
    for item in list(stats.keys()):
        if round:
            stats[item] = int(stats[item] / counts[item])
        else:
            stats[item] = float(stats[item] / counts[item])
    return stats


def processTime():
    time = fetchTimes()
    times = list(time.keys())
    avgTime = processStats(data=time, keys=times, round=False)
    return avgTime


def prioritize():
    data = fetchResults()
    tests = list(data.keys())
    last = int(tests[-1].split("run")[1])
    next = "run" + str(last + 1)
    stats = processStats(data=data, keys=tests)
    sort = sorted(stats.items(), key=itemgetter(1))
    return next, sort, data


TEST_SUITE = {'GetTest': GetTest, 'TestCount': TestCount, 'TestTypes': TestTypes, 'CreateTest': CreateTest,
              'DeleteTest': DeleteTest, 'EditTest': EditTest}
SELECTION = {'0': 'GetTest', '1': 'TestCount', '2': 'TestTypes', '3': 'CreateTest', '4': 'DeleteTest', '5': 'EditTest'}

if __name__ == '__main__':
    first = True
    user = False
    must = None
    limit = int(input("Time threshold (in seconds): "))
    if limit == 0:
        print("Running all of the available test cases....\n")
        next, sort, data = prioritize()
        testcases = TEST_SUITE
        toTest = createSuite(testcases=testcases, first=first)
    else:
        core = input("Would you like to add testcases that WILL be executed?")
        if core[0] == 'y':
            user = True
            must = []
            print(SELECTION)
            selection = input("Please select the corresponding numbers to the testcases shown above(divided by a comma)")
            selections = selection.split(',')
            for i in range(0, len(selections)):
                if SELECTION[selections[i]] not in must:
                    must.append(SELECTION[selections[i]])
        try:
            next, sort, data = prioritize()
            procTimes = processTime()
            first = False
            testcases = []
            total = 0
            output = []
            if user:
                print('The testcases selected by the user will be executed, their runtime WILL be calculated into the threshold.')
                for case in must:
                    total += procTimes[case]
                    testcases.append(TEST_SUITE[case])
            for i in range(1, len(list(TEST_SUITE.keys())) + 1):
                if user and sort[-i][0] not in must:
                    if procTimes[sort[-i][0]] + total <= limit:
                        output.append(sort[-i][0])
                        total += procTimes[sort[-i][0]]
                        testcases.append(TEST_SUITE[sort[-i][0]])
                    elif procTimes[sort[-i][0]] + total <= limit * 1.1:
                        print("The " + str(sort[-i][0]) + " testcase with the next best score has a runtime that would require <10% more of the time that you defined.\nAdding this test to the list would stop the prioritization algorithm.\nNot adding it will let the algorithm work further, but a testcase with lower score may be added instead.")
                        choice = input('Do you wish to add ' + str(sort[-i][0]) + '? ')
                        if choice[0] == 'y':
                            output.append(sort[-i][0])
                            testcases.append(TEST_SUITE[sort[-i][0]])
                            break
            print('The following testcases have been selected by the prioritization algorithm: ', output, '\n')
            toTest = createSuite(testcases=testcases, first=first)
        except json.decoder.JSONDecodeError:
            print("Since this is the first run, the tool will now run all of the available tests.\nFor run #2 it will appply the prioritization and time threshold.\n")
            data = {}
            time = {}
            next = "run1"
            testcases = TEST_SUITE
            toTest = createSuite(testcases=testcases, first=first)
            result = CustomResults(verbosity=False)
            suite = TestSuite(toTest)
            suite.run(result)
            generateOutput(result=result, data=data, time=time, next=next)
            next, sort, data = prioritize()
            procTimes = processTime()
            testcases = []
            total = 0
            output = []
            if user:
                print('The testcases selected by the user will be executed, their runtime WILL be calculated into the threshold.')
                for case in must:
                    total += procTimes[case]
                    testcases.append(TEST_SUITE[case])
            for i in range(1, len(list(TEST_SUITE.keys())) + 1):
                if user and sort[-i][0] not in must:
                    if procTimes[sort[-i][0]] + total <= limit:
                        output.append(sort[-i][0])
                        total += procTimes[sort[-i][0]]
                        testcases.append(TEST_SUITE[sort[-i][0]])
                    elif procTimes[sort[-i][0]] + total <= limit * 1.1:
                        print("The " + str(sort[-i][0]) + " testcase with the next best score has a runtime that would require <10% more of the time that you defined.\nAdding this test to the list would stop the prioritization algorithm.\nNot adding it will let the algorithm work further, but a testcase with lower score may be added instead.")
                        choice = input('Do you wish to add ' + str(sort[-i][0]) + '? ')
                        if choice[0] == 'y':
                            output.append(sort[-i][0])
                            testcases.append(TEST_SUITE[sort[-i][0]])
                            break
            print('The following testcases have been selected by the prioritization algorithm: ', output)
            first = False
            toTest = createSuite(testcases=testcases, first=first)

    result = CustomResults(verbosity=True)
    suite = TestSuite(toTest)
    suite.run(result)
    print(result.generateSummary())
    time = fetchTimes()
    generateOutput(result=result, data=data, time=time, next=next)



