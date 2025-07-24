import gymnasium as gym
from gymnasium import spaces
import numpy as np

from utils import get_frame_grey_resized, HpXy_getter, restart
import time

from Actions import *
from Reward import player_hp_reward, boss_hp_reward, done_reward

IMG_SIZE = 84
NUM_FRAME = 4

NUM_MOVE = 4
NUM_ATTACK = 4

NUM_STATE = 2 # player_hp, boss_hp, 如果放技能加上 player_souls

# SKILL_SOULS_COST = 33

PLAYER_MAX_HP = 9
BOSS_MAX_HP = 900
# PLAYER_MAX_SOULS = 99




class HollowKnightEnv(gym.Env):
    def __init__(self):
        super().__init__()

        self.image_shape = (IMG_SIZE, IMG_SIZE, NUM_FRAME)

        self.action_space = spaces.MultiDiscrete([NUM_MOVE, NUM_ATTACK])
        self.observation_space = spaces.Dict({
            "image": spaces.Box(low=0, high=255, shape=self.image_shape, dtype=np.uint8), 
            "vector": spaces.Box(low=0.0, high=1.0, shape=(NUM_STATE,), dtype=np.float32)
        })
        self.frame_stack = np.zeros(self.image_shape, dtype=np.uint8)

        self.prev_state = None

        self.epoch = 0
        self.time_step = 0
        self.prev_time = 0
        self.act_time_gap = 0.08

        self.Actions = [
            Move_Left, Move_Right, Turn_Left,Turn_Right,# move
            Attack_Down, Mid_Jump_Attack, # jump x
            Attack, Attack_Up,   # attack
        ]

        self.MOVE = [ "Move_Left", "Move_Right", "Turn_Left","Turn_Right"]
        self.ATTACK = ["Attack_Down", "Mid_Jump_Attack",
            "Attack", "Attack_Up"]
        

    def _get_frame(self):
        return get_frame_grey_resized().astype(np.uint8)

    # ------ 帧栈更新 ------
    def _update_stack(self, new_frame):

        self.frame_stack = np.roll(self.frame_stack, -1, axis=2)
        self.frame_stack[:, :, -1] = new_frame
        return self.frame_stack.copy()
    

    def _get_state_vector(self):
        getter = HpXy_getter()
        
        player_hp = getter.get_player_hp()
        boss_hp = getter.get_boss_hp()
        player_souls = getter.get_player_souls()

        state = {
            "player_hp": player_hp,
            "boss_hp": boss_hp,
            # "player_souls": player_souls
        }

        return state

    def _state_to_observation(self, state):
        observation = np.array([
            state["player_hp"] / PLAYER_MAX_HP, 
            state["boss_hp"] / BOSS_MAX_HP, 
            # state["player_souls"] / PLAYER_MAX_SOULS
            ], dtype=np.float32)
        
        return observation
    

    def _calculate_time(self):
        t = self.act_time_gap - (time.time() - self.prev_time)
        if t > 0:
            time.sleep(t)
        self.prev_time = time.time()
        self.time_step += 1

    
    def reset(self, *, seed = None, options = None):
        super().reset(seed=seed, options=options)

        restart()

        self.epoch += 1
        print(f"[RESET] 第{self.epoch}轮战斗")

        self.prev_time = time.time()

        self.frame_stack.fill(0)
        frame = self._get_frame()
        for _ in range(NUM_FRAME):
            self._update_stack(frame)

        raw_state = self._get_state_vector()
        self.prev_state = raw_state

        image_observation = self.frame_stack.copy()
        vector_observation = self._state_to_observation(raw_state)

        observation = {
            "image": image_observation,
            "vector": vector_observation
        }

        return observation, {}
        
    def step(self, action):
        move_index, attack_index = action

        self._calculate_time()

        print(f"timestep:{self.time_step}, action:{self.MOVE[move_index], self.ATTACK[attack_index]}", end = "")

        # 执行移动
        self.Actions[move_index]()

        self._calculate_time()

        # 执行攻击
        self.Actions[attack_index + 4]()

        raw_state = self._get_state_vector()

        # 计算奖励
        reward, done = self._get_reward_done(raw_state, self.prev_state, action)

        print(f" reward:{reward:.3f}, boss_hp:{raw_state['boss_hp']}")

        new_frame = self._get_frame()
        image_observation = self._update_stack(new_frame)
        vector_observation = self._state_to_observation(raw_state)

        self.prev_state = raw_state


        observation = {
            "image": image_observation,
            "vector": vector_observation
        }

        return observation, reward, done, False, {}
    

    def _get_reward_done(self, state, prev_state, action):
        move_index, attack_index = action

        done = state["player_hp"] <= 0 or state["boss_hp"] <= 0

        reward = 0.0
        reward += player_hp_reward(player_hp=state["player_hp"], prev_player_hp=prev_state["player_hp"])
        reward += boss_hp_reward(boss_hp=state["boss_hp"], prev_boss_hp=prev_state["boss_hp"])

        # if done:
        #     reward += done_reward(boss_hp=state["boss_hp"], player_hp=state["player_hp"])

        return reward, done
