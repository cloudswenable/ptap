import os
import subprocess
import re

def isOPS(ops):
    if ops in ['+','-','*','/']:
        return True
    return False

def higher(next, pre):
    if (next == '+' or next == '-') and (pre == '*' or pre == '/'):
        return False
    return True

class Calculater:

    def operate(
        self,
        num1,
        num2,
        op,
        ):
        if op == '+':
            return num1 + num2
        if op == '-':
            return num1 - num2
        if op == '*':
            return num1 * num2
        if op == '/' and num2 > 0:
            return num1 / num2
	return None

    def popAndOp(self, datas, ops):
        if not ops:
            return ''
        num2 = datas.pop()
        num1 = datas.pop()
        op = ops.pop()
        tmpNum = self.operate(float(num1), float(num2), op)
        datas.append(tmpNum)
        if not ops:
            return ''
        return ops[-1]

    def toSuffixCodes(self, formula):
        in_stack = []
        out_stack = []
        index = 0
        while index < len(formula):
            if formula[index].isdigit() or formula[index] == '.':
                length = 0
                while index + length < len(formula) and (formula[index+length].isdigit() or formula[index+length] == '.'):
                    length = length+1
                out_stack.append(formula[index:index+length])
                index += length
            elif formula[index] == '(':
                in_stack.append(formula[index])
                index += 1
            elif formula[index] == ')':
                while len(in_stack) > 0:
                    stack_top = in_stack.pop()
                    if stack_top == '(':
                        break
                    elif stack_top == None:
                        print "Error for parse formula"
                        return None
                    else:
                        out_stack.append(stack_top)
                index += 1
            elif isOPS(formula[index]) and ( len(in_stack) == 0 or higher(formula[index], in_stack[len(in_stack)-1])):
                in_stack.append(formula[index])
                index += 1
            elif isOPS(formula[index]):
                out_stack.append(in_stack.pop())
                in_stack.append(formula[index])
                index += 1
	    else:
		return None

        while len(in_stack) > 0:
            out_stack.append(in_stack.pop())
        return out_stack

    def calculate(self, formula):
        suffix_expression = self.toSuffixCodes(formula)
        if suffix_expression:
            data_stack = []
            for i in range(0, len(suffix_expression)):
                if isOPS(suffix_expression[i]):
                    right = float(data_stack.pop())
                    left = float(data_stack.pop())
                    number = self.operate(left, right, suffix_expression[i])
		    if number:
                        data_stack.append(number)
		    else:
			return -1
                else:
                    data_stack.append(suffix_expression[i])
            return data_stack[0]
        return -1

def createPaths(base, rPath):
        tmp = base + '/'
        if not os.path.isdir(base): os.mkdir(tmp)
        items = []
        for item in rPath.split('/'):
                if item:
                        items.append(item)
        for item in items:
                tmp += item + '/'
                if not os.path.isdir(tmp): os.mkdir(tmp)
        return tmp

def killCommand(items):
	c = subprocess.Popen('ps auxww', shell=True, stdout=subprocess.PIPE)
	s = c.communicate()
	commands = s[0].split('\n')
	pa = re.compile('\\d{1,6}')
	print '++++++++++++++++++++++ items = ', items
	for command in commands:
		if command.find('perf-monitor-platform')<0: continue
		wantKill = True
		print 
		print '+++++++++++++command = ', command
		for item in items:
			print '+++++++++++++++++++++++ item = ', item, '        find(item) = ', command.find(item)
			if command.find(item)<0:
				wantKill = False
				break
		
		if wantKill:
			gs = pa.search(command)
			pid = gs.group(0)
			print 'kill : ', pid
			subprocess.call(['sudo', 'kill', '-s', '9', pid]) 

def main():
	#items = ['perf', 'record', ]
	#killCommand(items)
    cal = Calculater()
    print cal.calculate('(10+3)/2')
    #print cal.calculate('10+3/2')

if __name__ == '__main__':
    main()
