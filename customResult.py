import unittest
from sty import fg
import time
import json
SEVERITY = {"Minor": 1, "Normal": 2, "Major": 4, "Critical": 6}


class CustomResults(unittest.TestResult):
    def __init__(self, stream=None, descriptions=None, verbosity=None):
        super().__init__(stream, descriptions, verbosity)
        self.success = 0
        self.verbosity = verbosity
        self.failed = 0
        self.tests = 0
        self.start = 0
        self.total = 0
        self.severity = 0
        self.stop = 0
        self.entry = {}
        self.time = {}

    def startTest(self, test):
        self.tests += 1
        if self.verbosity:
            print('Starting test: ' + str(test).split("__")[0].split('_')[1] + ' with ' + fg.blue + str(test).split("__")[1][0:-2].capitalize() + fg.rs + " severity")
        self.start = time.time()
        self.severity = SEVERITY[str(test).split("__")[1][0:-2].capitalize()]

    def stopTest(self, test):
        self.stop = round(time.time() - self.start, 4)
        if self.verbosity:
            print("Test duration: {:.4f} s \n".format(self.stop))
        self.total += self.stop
        self.addTimeResult(test)

    def addFailure(self, test, err):
        if self.verbosity:
            print(fg.da_red + "Test failed: " + fg.rs + str(test).split("__")[0])
        self.failed += 1
        self.addResult(test)

    def addSuccess(self, test):
        if self.verbosity:
            print(fg.da_green + "Test passed: " + fg.rs + str(test).split("__")[0])
        self.success += 1
        self.severity = 0
        self.addResult(test)

    def generateSummary(self):
        p1 = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n{} tests finished. Summary:\n".format(self.failed+self.success) + fg.da_green + "PASSED: {}\n".format(self.success) + fg.rs
        p2 = fg.da_red + "FAIL: {}\n".format(self.failed) + fg.rs
        p3 = "SUCCESS RATE: {:.2%}\n".format(self.success / self.tests) + fg.rs
        p4 = "TOTAL RUNTIME: {:.4f} s".format(self.total) + fg.rs
        return p1+p2+p3+p4

    def generateEntry(self):
        return self.entry

    def generateTime(self):
        return self.time

    def generateCounts(self):
        try:
            with open('counts.json') as json_file:
                data = json.load(json_file)
                json_file.close()
        except:
            data = {}
        for item in self.entry.items():
            try:
                data[item[0]] = data[item[0]] + 1
            except:
                data[item[0]] = 1

        return data

    def addResult(self, test):
        try:
            self.entry[str(test).split("__.")[1][:-1]] = self.entry[str(test).split("__.")[1][:-1]] + self.severity
        except:
            self.entry[str(test).split("__.")[1][:-1]] = self.severity

    def addTimeResult(self, test):
        try:
            self.time[str(test).split("__.")[1][:-1]] = self.time[str(test).split("__.")[1][:-1]] + self.stop
        except:
            self.time[str(test).split("__.")[1][:-1]] = self.stop