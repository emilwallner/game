import numpy as np
from collections import deque

#define IND_SIZE				2
#define REG_SIZE				4
#define DIR_SIZE				REG_SIZE

# define REG_CODE				1
# define DIR_CODE				2
# define IND_CODE				3

#define MAX_ARGS_NUMBER			4
#define MAX_PLAYERS				4
MEM_SIZE = (4*1024)
#define IDX_MOD					(MEM_SIZE / 8)
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

#define T_REG					1
#define T_DIR					2
#define T_IND					4
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

OP_LIVE = 0x1

class Process:
	PID = 0

	def __init__(self, parent, mars, position):
		Process.PID += 1
		self.PID = Process.PID
		self.parent = parent
		self.mars = mars

		self.registers = [r for r in range(REG_NUMBER)]
		self.PC = position
		self.carry = 0
		self.op = None
		self.countdown = 0

	def step(self):
		if self.op is None:
			self.op = self.mars.memory[self.PC]

			if self.op == OP_LIVE:
				self.countdown = 10
			else:
				self.op = None
				self.PC = (self.PC + 1) % self.mars.size
		else:
			self.countdown -= 1
			if self.countdown == 0:
				self.mars.events.append(self)

		print("Proc: {}, PC: {}, op: {}, cd:{}".format(self.PID, self.PC, self.op, self.countdown))

class Champion:
	ID = 0xffffffff
	def __init__(self, data, name = ""):
		self.ID = Champion.ID
		Champion.ID -= 1
		self.name = name
		self.data = data

	def __str__(self):
		return ("Champion: {}".format(self.name))

	def spawn_process(self, mars, position = 0):
		proc = Process(self, mars, position)
		return proc

class MARS:
	def __init__(self):
		self.size = MEM_SIZE
		self.memory = np.zeros((self.size,), dtype = np.byte)
		self.new_PID = 0
		self.champions = []
		self.processes = [] #make a linked list!
		self.events = deque()

	def add_champion(self, champion):
		self.champions.append(champion)
		self.memory[0:champion.data.shape[0]] = champion.data
		self.processes.append(champion.spawn_process(self))

	def step(self):
		for proc in reversed(self.processes):
			proc.step()

		for proc in self.events:
			print("process {} triggered an event({})".format(proc.PID, proc.op))
			proc.op = None
