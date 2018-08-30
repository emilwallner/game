import numpy as np
from collections import deque
import struct

#DON'T CHANGE THESE THREE VALUES UNLESS YOU WANT TO GET AN UNUSABLE MESS
IND_SIZE = 2
REG_SIZE = 4
DIR_SIZE = REG_SIZE

REG_CODE = 1
DIR_CODE = 2
IND_CODE = 3

#define MAX_ARGS_NUMBER			4
#define MAX_PLAYERS				4
MEM_SIZE = (4*1024)
IDX_MOD = MEM_SIZE // 8
#define CHAMP_MAX_SIZE			(MEM_SIZE / 6)

#define COMMENT_CHAR			'#'
#define LABEL_CHAR				':'
#define DIRECT_CHAR				'%'
#define SEPARATOR_CHAR			','

#define LABEL_CHARS				"abcdefghijklmnopqrstuvwxyz_0123456789"

#define NAME_CMD_STRING			".name"
#define COMMENT_CMD_STRING		".comment"

REG_NUMBER = 16

#define CYCLE_TO_DIE			1536
#define CYCLE_DELTA				50
#define NBR_LIVE				21
#define MAX_CHECKS				10

T_REG = 1
T_DIR = 2
T_IND = 4
#define T_LAB					8

# define PROG_NAME_LENGTH		(128)
# define COMMENT_LENGTH			(2048)
# define COREWAR_EXEC_MAGIC		0xea83f3

'''
t_op    op_tab[17] =
{
	{"live", 1, {T_DIR}, 1, 10, "alive", 0, 0},
	{"ld", 2, {T_DIR | T_IND, T_REG}, 2, 5, "load", 1, 0},
	{"st", 2, {T_REG, T_IND | T_REG}, 3, 5, "store", 1, 0},
	{"add", 3, {T_REG, T_REG, T_REG}, 4, 10, "addition", 1, 0},
	{"sub", 3, {T_REG, T_REG, T_REG}, 5, 10, "soustraction", 1, 0},
	{"and", 3, {T_REG | T_DIR | T_IND, T_REG | T_IND | T_DIR, T_REG}, 6, 6,
		"et (and  r1, r2, r3   r1&r2 -> r3", 1, 0},
	{"or", 3, {T_REG | T_IND | T_DIR, T_REG | T_IND | T_DIR, T_REG}, 7, 6,
		"ou  (or   r1, r2, r3   r1 | r2 -> r3", 1, 0},
	{"xor", 3, {T_REG | T_IND | T_DIR, T_REG | T_IND | T_DIR, T_REG}, 8, 6,
		"ou (xor  r1, r2, r3   r1^r2 -> r3", 1, 0},
	{"zjmp", 1, {T_DIR}, 9, 20, "jump if zero", 0, 1},
	{"ldi", 3, {T_REG | T_DIR | T_IND, T_DIR | T_REG, T_REG}, 10, 25,
		"load index", 1, 1},
	{"sti", 3, {T_REG, T_REG | T_DIR | T_IND, T_DIR | T_REG}, 11, 25,
		"store index", 1, 1},
	{"fork", 1, {T_DIR}, 12, 800, "fork", 0, 1},
	{"lld", 2, {T_DIR | T_IND, T_REG}, 13, 10, "long load", 1, 0},
	{"lldi", 3, {T_REG | T_DIR | T_IND, T_DIR | T_REG, T_REG}, 14, 50,
		"long load index", 1, 1},
	{"lfork", 1, {T_DIR}, 15, 1000, "long fork", 0, 1},
	{"aff", 1, {T_REG}, 16, 2, "aff", 1, 0},
	{0, 0, {0}, 0, 0, 0, 0, 0}
};
'''

def get_val(proc, arg, idx = True, short = False):
	if arg[0] == T_REG:
		return proc.registers[arg[1] - 1]
	elif arg[0] == T_DIR:
		return arg[1]
	elif arg[0] == T_IND:
		if idx:
			pos = (proc.PC + arg[1] % IDX_MOD) % MEM_SIZE
		else:
			pos = (proc.PC + arg[1]) % MEM_SIZE
		memory = proc.mars.memory
		if short:
			val = struct.unpack(">H", memory.take(
					range(pos, pos + IND_SIZE), mode = 'wrap'))[0]
		else:
			val = struct.unpack(">I", memory.take(
					range(pos, pos + REG_SIZE), mode = 'wrap'))[0]
		return val

def set_val(proc, arg, val):
	if arg[0] == T_REG:
		proc.registers[arg[1] - 1] = val
	elif arg[0] == T_IND:
		data = bytearray(struct.pack(">I", val))
		pos = (proc.PC + arg[1] % IDX_MOD) % MEM_SIZE
		if (pos + REG_SIZE < MEM_SIZE):
			memory[pos:pos + REG_SIZE] = data
		else:
			wrap = MEM_SIZE - pos
			memory[pos:MEM_SIZE] = data[0:wrap]
			memory[0:REG_SIZE - wrap] = data[wrap: REG_SIZE]

def op_live(proc):
	champ = get_val(proc, proc.args[0])
	print("Champion {} lives!".format(champ))

def op_ld(proc):
	val = get_val(proc, proc.args[0])
	set_val(proc, proc.args[1], val)
	proc.carry = (val == 0)

def op_st(proc):
	set_val(proc, proc.args[1], get_val(proc, proc, args[0]))

def op_add(proc):
	res = np.uint32(get_val(proc, proc.args[0])) + np.uint32(get_val(proc, proc.args[1]))
	set_val(proc, proc.args[2], res.item())
	proc.carry = (res.item() == 0)

def op_sub(proc):
	res = np.uint32(get_val(proc, proc.args[0])) - np.uint32(get_val(proc, proc.args[1]))
	set_val(proc, proc.args[2], res.item())
	proc.carry = (res.item() == 0)

def op_and(proc):
	res = np.uint32(get_val(proc, proc.args[0])) & np.uint32(get_val(proc, proc.args[1]))
	set_val(proc, proc.args[2], res.item())
	proc.carry = (res.item() == 0)

def op_or(proc):
	res = np.uint32(get_val(proc, proc.args[0])) | np.uint32(get_val(proc, proc.args[1]))
	set_val(proc, proc.args[2], res.item())
	proc.carry = (res.item() == 0)

def op_xor(proc):
	res = np.uint32(get_val(proc, proc.args[0])) ^ np.uint32(get_val(proc, proc.args[1]))
	set_val(proc, proc.args[2], res.item())
	proc.carry = (res.item() == 0)

def op_zjmp(proc):
	if proc.carry:
		proc.PC += proc.args[0][1] % IDX_MOD

def op_ldi(proc):
	addr = (np.uint16(get_val(proc, proc.args[0], True, True)) % IDX_MOD) + \
										np.uint16(get_val(proc, proc.args[1], True, True))
	addr = (T_IND, addr.item() % IDX_MOD)
	set_val(proc, proc.args[2], get_val(proc, addr))

def op_sti(proc):
	addr = (np.uint32(get_val(proc, proc.args[1])) % IDX_MOD) + \
						np.uint32(get_val(proc, proc.args[2]))
	addr = (T_IND, addr.item())
	set_val(proc, proc.args[0], get_val(proc, addr))

def op_fork(proc):
	addr = get_val(proc, proc.args[0]) % IDX_MOD
	addr = (proc.PC + addr) % MEM_SIZE
	p = Process(proc.parent, proc.mars, addr)
	p.registers = list(proc.registers)
	p.carry = proc.carry
	proc.mars.processes.append(p)

def op_lld(proc):
	val = get_val(proc, proc.args[0], False)
	set_val(proc, proc.args[1], val)
	proc.carry = (val == 0)

def op_lldi(proc):
	addr = (np.uint16(get_val(proc, proc.args[0], False, True))) + \
										np.uint16(get_val(proc, proc.args[1], False, True))
	addr = (T_IND, addr.item())
	set_val(proc, proc.args[2], get_val(proc, addr))

def op_lfork(proc):
	addr = get_val(proc, proc.args[0])
	addr = (proc.PC + addr) % MEM_SIZE
	p = Process(proc.parent, proc.mars, addr)
	p.registers = list(proc.registers)
	p.carry = proc.carry
	proc.mars.processes.append(p)

class Operator:
	def __init__(self, name, argc, argtypes, opcode, cycles, text, encoding, index, func = None):
		self.name = name
		self.argc = argc
		self.argtypes = argtypes
		self.opcode = opcode
		self.cycles = cycles
		self.text = text
		self.encoding = encoding
		self.index = index
		self.func = func

OP_TAB = {
	0x01: Operator("live", 1, (T_DIR,), 1, 10, "alive", False, False, op_live),
	0x02: Operator("ld", 2, (T_DIR | T_IND, T_REG), 2, 5, "load", True, False, op_ld),
	0x03: Operator("st", 2, (T_REG, T_IND | T_REG), 3, 5, "store", True, False, op_st),
	0x04: Operator("add", 3, (T_REG, T_REG, T_REG), 4, 10, "addition", True, False, op_add),
	0x05: Operator("sub", 3, (T_REG, T_REG, T_REG), 5, 10, "soustraction", True, False, op_sub),
	0x06: Operator("and", 3, (T_REG | T_DIR | T_IND, T_REG | T_IND | T_DIR, T_REG), 6, 6,
		"et (and  r1, r2, r3   r1&r2 -> r3", True, False, op_and),
	0x07: Operator("or", 3, (T_REG | T_IND | T_DIR, T_REG | T_IND | T_DIR, T_REG), 7, 6,
		"ou  (or   r1, r2, r3   r1 | r2 -> r3", True, False, op_or),
	0x08: Operator("xor", 3, (T_REG | T_IND | T_DIR, T_REG | T_IND | T_DIR, T_REG), 8, 6,
		"ou (xor  r1, r2, r3   r1^r2 -> r3", True, False, op_xor),
	0x09: Operator("zjmp", 1, (T_DIR), 9, 20, "jump if zero", False, True, op_zjmp),
	0x0a: Operator("ldi", 3, (T_REG | T_DIR | T_IND, T_DIR | T_REG, T_REG), 10, 25,
		"load index", True, True, op_ldi),
	0x0b: Operator("sti", 3, (T_REG, T_REG | T_DIR | T_IND, T_DIR | T_REG), 11, 25,
		"store index", True, True, op_sti),
	0x0c: Operator("fork", 1, (T_DIR), 12, 800, "fork", False, True, op_fork),
	0x0d: Operator("lld", 2, (T_DIR | T_IND, T_REG), 13, 10, "long load", True, False, op_lld),
	0x0e: Operator("lldi", 3, (T_REG | T_DIR | T_IND, T_DIR | T_REG, T_REG), 14, 50,
		"long load index", True, True, op_lldi),
	0x0f: Operator("lfork", 1, (T_DIR), 15, 1000, "long fork", False, True, op_lfork),
	#0x10: Operator("aff", 1, (T_REG), 16, 2, "aff", True, False, op_aff)
}

class Process:
	PID = 0

	def __init__(self, parent, mars, position):
		Process.PID += 1
		self.PID = Process.PID
		self.parent = parent
		self.mars = mars

		self.registers = [0 for r in range(REG_NUMBER)]
		self.PC = position
		self.carry = False
		self.op = None
		self.countdown = 0

		self.args = ()

	def step(self):
		current_pc = self.PC
		if self.op is None:
			self.op = self.mars.memory[self.PC]

			if self.op in OP_TAB:
				self.countdown = OP_TAB[self.op].cycles - 1
			else:
				self.op = None
				self.PC = (self.PC + 1) % self.mars.size
		else:
			self.countdown -= 1
			if self.countdown == 0:
				self.mars.events.append(self)

		print("Proc: {}, PC: {}, op: {}, cd:{}".format(self.PID, current_pc, self.op, self.countdown))

	def exec(self):
		offset = self.arg_parse()
		def validate_args():
			operator = OP_TAB[self.op]
			for i in range(len(self.args)):
				if operator.argtypes[i] & self.args[i][0] == 0:
					return False
				if self.args[i][0] == T_REG and \
					(self.args[i][1] > REG_NUMBER or self.args[i][1] == 0):
					return False
			return True

		if validate_args():
			OP_TAB[self.op].func(self)
			print("process {}: event({}: {})".format(self.PID, self.op, OP_TAB[self.op].text))
		else:
			print("process {} invalid event({})".format(self.PID, self.op))

		self.op = None
		self.countdown = 0
		print("Skipping {} bytes".format(offset))
		self.PC += 1 + offset
		self.PC %= MEM_SIZE

	def arg_parse(self):
		op = OP_TAB[self.op]
		position = self.PC + 1
		arg_offset = 0
		memory = self.mars.memory

		if op.encoding:
			self.args = []
			code = struct.unpack(">B",
					memory.take(range(position, position + 1), mode = 'wrap'))[0]
			arg_offset += 1
			position += 1
			for i in range(op.argc):
				a = (code >> (6 - 2 * i)) & 0b11
				print("arg: ", a)
				if a == REG_CODE:
					size = 1
					self.args.append((T_REG, struct.unpack(">B",
					memory.take(range(position, position + size), mode = 'wrap'))[0]))
				elif a == DIR_CODE:
					if op.index:
						size = IND_SIZE
						self.args.append((T_DIR, struct.unpack(">H",
						memory.take(range(position, position + size), mode = 'wrap'))[0]))
					else:
						size = DIR_SIZE
						self.args.append((T_DIR, struct.unpack(">I",
						memory.take(range(position, position + size), mode = 'wrap'))[0]))
				elif a == IND_CODE:
					size = IND_SIZE
					self.args.append((T_IND, struct.unpack(">H",
					memory.take(range(position, position + size), mode = 'wrap'))[0]))
				arg_offset += size
				position += size
		else:
			if op.index:
				size = IND_SIZE
				self.args = [(T_IND, struct.unpack(">H",
					memory.take(range(position, position + size), mode = 'wrap'))[0])]
			else:
				size = DIR_SIZE
				self.args = [(T_DIR, struct.unpack(">I",
					memory.take(range(position, position + size), mode = 'wrap'))[0])]
			arg_offset += size
		return arg_offset


class Champion:
	ID = 0xffffffff
	def __init__(self, data, name = ""):
		self.ID = Champion.ID
		Champion.ID -= 1
		self.name = name
		self.data = data

	def __str__(self):
		return ("Champion: {}".format(self.name))

	def make_process(self, mars, position = 0):
		p = Process(self, mars, position)
		p.registers[0] = self.ID
		return p

class MARS:
	def __init__(self):
		Process.PID = 0
		self.size = MEM_SIZE
		self.memory = np.zeros((self.size,), dtype = np.ubyte)
		self.champions = []
		self.processes = [] #make a linked list!
		self.events = deque()

	def add_champion(self, champion, offset = 0):
		self.champions.append(champion)
		self.memory[offset:offset + champion.data.shape[0]] = champion.data
		self.processes.append(champion.make_process(self, offset))

	def step(self):
		for proc in reversed(self.processes):
			proc.step()

		for proc in self.events:
			proc.exec()

		self.events.clear()
