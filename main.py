import unittest
from unittest.suite import TestSuite
from customResult import CustomResults
from operator import itemgetter
from myrequests import *
import sys


class GetTest(unittest.TestCase):
    def test_getTestsAG__critical(self):
        self.assertTrue(getTest(critical=True, type="AG"))

    def test_getTestsPCR__critical(self):
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
            if entry not in ['Passed', 'Failed', 'Runtime']:
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
    mode = int(input("Please choose a mode in which the tool should operate:\n1, Run all test cases\n2, Run only high priority test cases\n3, Run test cases in a certain time limit using prioritization\n"))
    if mode == 1:
        print("Running all of the available test cases....\n")
        next, sort, data = prioritize()
        testcases = TEST_SUITE
        toTest = createSuite(testcases=testcases, first=first)
    elif mode == 2:
        minscore = int(input('Lowest test case score to be executed: '))
        next, sort, data = prioritize()
        procTimes = processTime()
        testcases = []
        output = []
        for i in range(1, len(list(TEST_SUITE.keys())) + 1):
            if sort[-i][1] >= minscore:
                output.append(sort[-i][0])
                testcases.append(TEST_SUITE[sort[-i][0]])
        print('The following test cases have been selected by the prioritization algorithm: ', output, '\n')
        toTest = createSuite(testcases=testcases, first=False)
    elif mode == 3:
        limit = int(input("Time limit (in seconds): "))
        core = input("Would you like to add test cases that WILL be executed? ")
        if core[0] == 'y':
            user = True
            must = []
            print(SELECTION)
            selection = input("Please select the corresponding numbers to the test cases shown above(divided by a comma) ")
            selections = selection.split(',')
            for i in range(0, len(selections)):
                if SELECTION[selections[i]] not in must:
                    must.append(SELECTION[selections[i]])
        exclude = input("Would you like to exclude test cases with low scores from the prioritization? ")
        exclude = True if exclude[0] == 'y' else False
        try:
            next, sort, data = prioritize()
            procTimes = processTime()
            first = False
            testcases = []
            total = 0
            output = []
            if user:
                print('The test cases selected by the user will be executed, their runtime WILL be calculated into the threshold.')
                for case in must:
                    total += procTimes[case]
                    testcases.append(TEST_SUITE[case])
            for i in range(1, len(list(TEST_SUITE.keys())) + 1):
                if user:
                    if sort[-i][0] not in must:
                        if procTimes[sort[-i][0]] + total <= limit:
                            if exclude:
                                if sort[-i][1] >= 3:
                                    output.append(sort[-i][0])
                                    total += procTimes[sort[-i][0]]
                                    testcases.append(TEST_SUITE[sort[-i][0]])
                            else:
                                output.append(sort[-i][0])
                                total += procTimes[sort[-i][0]]
                                testcases.append(TEST_SUITE[sort[-i][0]])
                        elif procTimes[sort[-i][0]] + total <= limit * 1.1:
                            if exclude:
                                if sort[-i][1] >= 3:
                                    print("The " + str(sort[-i][
                                                           0]) + " test case with the next best score has a runtime that would require <15% more of the time that you defined.\nAdding this test to the list would stop the prioritization algorithm.\nNot adding it will let the algorithm work further, but a test case with lower score may be added instead.")
                                    choice = input('Do you wish to add ' + str(sort[-i][0]) + '? ')
                                else:
                                    choice = "no"
                            else:
                                print("The " + str(sort[-i][
                                                       0]) + " test case with the next best score has a runtime that would require <15% more of the time that you defined.\nAdding this test to the list would stop the prioritization algorithm.\nNot adding it will let the algorithm work further, but a test case with lower score may be added instead.")
                                choice = input('Do you wish to add ' + str(sort[-i][0]) + '? ')
                            if choice[0] == 'y':
                                output.append(sort[-i][0])
                                testcases.append(TEST_SUITE[sort[-i][0]])
                                break
                else:
                    if procTimes[sort[-i][0]] + total <= limit:
                        if exclude:
                            if sort[-i][1] >= 3:
                                output.append(sort[-i][0])
                                total += procTimes[sort[-i][0]]
                                testcases.append(TEST_SUITE[sort[-i][0]])
                        else:
                            output.append(sort[-i][0])
                            total += procTimes[sort[-i][0]]
                            testcases.append(TEST_SUITE[sort[-i][0]])
                    elif procTimes[sort[-i][0]] + total <= limit * 1.1:
                        if exclude:
                            if sort[-i][1] >= 3:
                                print("The " + str(sort[-i][0]) + " test case with the next best score has a runtime that would require <15% more of the time that you defined.\nAdding this test to the list would stop the prioritization algorithm.\nNot adding it will let the algorithm work further, but a test case with lower score may be added instead.")
                                choice = input('Do you wish to add ' + str(sort[-i][0]) + '? ')
                            else:
                                choice = "no"
                        else:
                            print("The " + str(sort[-i][0]) + " test case with the next best score has a runtime that would require <15% more of the time that you defined.\nAdding this test to the list would stop the prioritization algorithm.\nNot adding it will let the algorithm work further, but a test case with lower score may be added instead.")
                            choice = input('Do you wish to add ' + str(sort[-i][0]) + '? ')
                        if choice[0] == 'y':
                            output.append(sort[-i][0])
                            testcases.append(TEST_SUITE[sort[-i][0]])
                            break
            print('The following test cases have been selected by the prioritization algorithm: ', output, '\n')
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
                print('The test cases selected by the user will be executed, their runtime WILL be calculated into the threshold.')
                for case in must:
                    total += procTimes[case]
                    testcases.append(TEST_SUITE[case])
            for i in range(1, len(list(TEST_SUITE.keys())) + 1):
                if user:
                    if sort[-i][0] not in must:
                        if procTimes[sort[-i][0]] + total <= limit:
                            output.append(sort[-i][0])
                            total += procTimes[sort[-i][0]]
                            testcases.append(TEST_SUITE[sort[-i][0]])
                        elif procTimes[sort[-i][0]] + total <= limit * 1.1:
                            print("The " + str(sort[-i][0]) + " test case with the next best score has a runtime that would require <15% more of the time that you defined.\nAdding this test to the list would stop the prioritization algorithm.\nNot adding it will let the algorithm work further, but a testcase with lower score may be added instead.")
                            choice = input('Do you wish to add ' + str(sort[-i][0]) + '? ')
                            if choice[0] == 'y':
                                output.append(sort[-i][0])
                                testcases.append(TEST_SUITE[sort[-i][0]])
                                break
                else:
                    if procTimes[sort[-i][0]] + total <= limit:
                        output.append(sort[-i][0])
                        total += procTimes[sort[-i][0]]
                        testcases.append(TEST_SUITE[sort[-i][0]])
                    elif procTimes[sort[-i][0]] + total <= limit * 1.1:
                        print("The " + str(sort[-i][0]) + " test case with the next best score has a runtime that would require <15% more of the time that you defined.\nAdding this test to the list would stop the prioritization algorithm.\nNot adding it will let the algorithm work further, but a test case with lower score may be added instead.")
                        choice = input('Do you wish to add ' + str(sort[-i][0]) + '? ')
                        if choice[0] == 'y':
                            output.append(sort[-i][0])
                            testcases.append(TEST_SUITE[sort[-i][0]])
                            break
            print('The following test cases have been selected by the prioritization algorithm: ', output)
            first = False
            toTest = createSuite(testcases=testcases, first=first)
    else:
        sys.exit("Invalid input")
    result = CustomResults(verbosity=True)
    suite = TestSuite(toTest)
    suite.run(result)
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Test run #' + next.split('run')[1] + '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n')
    summ, succ, fail, runtime, total = result.generateSummary()

    print(summ)
    time = fetchTimes()
    generateOutput(result=result, data=data, time=time, next=next)
    comp = input('Would you like to compare this test run to a previous one? ')
    if comp[0] == 'y':
        compare = int(input('Number of the run to compare: '))
        if compare < int(next.split('run')[1]):
            with open('results.json') as json_file:
                results = json.load(json_file)
                json_file.close()
            print('\n                      #'+next.split('run')[1]+'        #'+str(compare))
            print('Total # of tests:      '+str(total)+'          '+str(results['run'+str(compare)]['Passed'] + results['run'+str(compare)]['Failed']))
            print('# of tests passed:     ' + str(succ) + '          ' + str(results['run' + str(compare)]['Passed']))
            print('# of tests failed:     ' + str(fail) + '          ' + str(results['run' + str(compare)]['Failed']))
            print('Succes rate:         {:.2%}'.format(succ/total) + '     {:.2%}'.format(results['run'+str(compare)]['Passed'] / (results['run'+str(compare)]['Passed'] + results['run'+str(compare)]['Failed'])))
            print('Runtime:             {:.4f}'.format(runtime) + '     {:.4f}'.format(results['run' + str(compare)]['Runtime']))