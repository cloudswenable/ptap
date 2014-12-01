import socket
import re
import platform
import os
import shutil
import traceback
from ClusterConfig import *

def dictToString(datas):
    ret = '{'
    for key,value in datas.items():
        ret += ('%s:%s,') % (key, value)
    ret.rstrip(',')
    ret += '}'
    return ret

def collectMachineInfo():
	name = open('/proc/sys/kernel/hostname').read().strip()
        config = AgentClientConfig()
	ip_addr = config.client_ip
	os_info = "-".join(platform.linux_distribution())

	cpuinfo = open('/proc/cpuinfo').read()
	pa = re.compile('model name.*:(.*)\n')
	ma = pa.search(cpuinfo)
	cpu_info = ma.group(1).strip()
        start = cpu_info.rfind('@')
        end = cpu_info.rfind('GHz')
        if start > 0 and end > 0:
            cpu_freq = float(cpu_info[start+1:end])
	meminfo = open('/proc/meminfo').read()
	pa = re.compile('MemTotal:(.*)\n')
	ma = pa.search(meminfo)
	mem_info = ma.group(1).strip()

	disk =  os.statvfs("/")
	disk_info = str(disk.f_bsize * disk.f_blocks / 1024) + ' kB'

        orignal = {'name': name, 'ip_addr': ip_addr, 'os_info': os_info, 'cpu_info': cpu_info,  'mem_info': mem_info, 'disk_info': disk_info}

        added = {}
        lscpu = os.popen("lscpu").readlines()
        for line in lscpu:
            key, value = line.split(':')
            added[key] = value.strip('\n').strip(' ')
        added['cpu_freq'] = cpu_freq

        return[orignal, dictToString(added)]


def createPaths(base, rPath):
	tmp = base + '/'
	if not os.path.isdir(base): os.makedirs(tmp)
	items = []
	for item in rPath.split('/'):
		if item:
			items.append(item)
	for item in items:
		tmp += item + '/'
		if not os.path.isdir(tmp): os.mkdir(tmp)
	return tmp

def deletePath(base, rPath):
	tmp = base + '/' + rPath
	try:
		shutil.rmtree(tmp)
	except:
		return 
	paths = rPath.split('/')
	cleanPaths = []
	for path in paths:
		if path: cleanPaths.append(path)
	i = len(cleanPaths)-1
	while i > 0:
		tmp = base + '/' + '/'.join(cleanPaths[:i])
		if not os.listdir(tmp):
			shutil.rmtree(tmp)
		else:
			break
		i = i - 1

def readOutputDatas(base, rPath):
	tmp = base + '/' + rPath + '/Process'
	names = []
	datas = []
	try:
		files = os.listdir(tmp)
		for file in files:
			subFiles = os.listdir(tmp+'/'+file)
			for subFile in subFiles:
				names.append(subFile + ' ' + file)
				data = []
				for line in open(tmp+'/'+file+'/'+subFile+'/report.dat'):
					if line.startswith('#'): continue
					if not line.strip(): continue
					item, itemData = line[:-1].split('\t\t')
					data.append((item, itemData))
				datas.append(data)
	except:
		traceback.print_exc()
	return names, datas


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
                while index + length < len(formula) and (formula[index+length].isdigit() or formula[index+length]=='.'):
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

def main():
    cal = Calculater()
    print cal.calculate('100-99.94')
    print collectMachineInfo() 

if __name__ == '__main__':
    main()
