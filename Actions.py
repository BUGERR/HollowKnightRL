from SendKey import PressKey, ReleaseKey
import time

# Hash code for key we may use: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes?redirectedfrom=MSDN
UP_ARROW = 0x26
DOWN_ARROW = 0x28
LEFT_ARROW = 0x25
RIGHT_ARROW = 0x27

L_SHIFT = 0xA0
A = 0x41
C = 0x43
F = 0x46
X = 0x58
Z = 0x5A


JUMP = Z
ATTACK = X
RUSH = C
SPELL = A
QUICK_SPELL = F

QUICK_ATTACK_TIME = 0.1

# 0
def Nothing():
    ReleaseKey(LEFT_ARROW)
    ReleaseKey(RIGHT_ARROW)
    # pass

# Move

# 0
def Move_Left():
    PressKey(LEFT_ARROW)
    time.sleep(0.01)
# 1
def Move_Right():
    PressKey(RIGHT_ARROW)
    time.sleep(0.01)

# 2
def Turn_Left():
    PressKey(LEFT_ARROW)
    time.sleep(0.01)
    ReleaseKey(LEFT_ARROW)

# 3
def Turn_Right():
    PressKey(RIGHT_ARROW)
    time.sleep(0.01)
    ReleaseKey(RIGHT_ARROW)

# ----------------------------------------------------------------------

def press_and_release_ATTACK():
    PressKey(ATTACK)
    time.sleep(QUICK_ATTACK_TIME)
    ReleaseKey(ATTACK)

def press_and_release_JUMP():
    PressKey(JUMP)
    time.sleep(QUICK_ATTACK_TIME)
    ReleaseKey(JUMP)

# Action

# 带快劈间隔小一点

def Attack():
    press_and_release_ATTACK()
    Nothing()
    # time.sleep(0.01)


def Attack_Up():
    PressKey(UP_ARROW)
    press_and_release_ATTACK()
    ReleaseKey(UP_ARROW)
    Nothing()
    # time.sleep(0.01)


def Attack_Down():
    PressKey(JUMP)
    PressKey(DOWN_ARROW)

    press_and_release_ATTACK()

    ReleaseKey(DOWN_ARROW)
    ReleaseKey(JUMP)
    Nothing()


# 6
def Mid_Jump_Attack():
    PressKey(JUMP)
    time.sleep(0.15)

    press_and_release_ATTACK()

    ReleaseKey(JUMP)
    Nothing()

# Dash 好像不好用，可以去掉
def Dash():
    PressKey(RUSH)
    time.sleep(0.1)
    ReleaseKey(RUSH)

    PressKey(ATTACK)
    time.sleep(0.03)
    ReleaseKey(ATTACK)
    


# 技能之间是否穿插普通攻击？让模型自己学吧

def Skill():
    PressKey(QUICK_SPELL)
    time.sleep(QUICK_ATTACK_TIME)
    ReleaseKey(QUICK_SPELL)
    # time.sleep(0.01)



def Skill_Up():
    PressKey(UP_ARROW)
    PressKey(QUICK_SPELL)
    time.sleep(0.15)

    ReleaseKey(UP_ARROW)
    ReleaseKey(QUICK_SPELL)
    Nothing()
    time.sleep(0.15)



def Skill_Down():
    PressKey(DOWN_ARROW)
    PressKey(QUICK_SPELL)
    time.sleep(0.2)

    ReleaseKey(DOWN_ARROW)
    ReleaseKey(QUICK_SPELL)
    Nothing()
    time.sleep(0.3)



def Look_up():
    PressKey(UP_ARROW)
    time.sleep(0.1)
    ReleaseKey(UP_ARROW)


# def Cure():
#     PressKey(A)
#     time.sleep(1.4)
#     ReleaseKey(A)
#     time.sleep(0.1)



Action_set = [Attack, Attack_Up, Attack_Down, Mid_Jump_Attack, 
              Skill, Skill_Up, Skill_Down, Dash]

Move_set = [Move_Left, Move_Right, Turn_Left, Turn_Right]


def take_action(action_name):
    Action_set[action_name]()

def take_move(move_name):
    Move_set[move_name]()

