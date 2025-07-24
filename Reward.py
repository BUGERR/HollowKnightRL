
# 游戏数值和奖励分数的比例
PLAYER_HP_REWARD_RATIO = 1
BOSS_HP_REWARD_RATIO = 0.01

PLAYER_HP_REWARD_RATIO_WIN = 10



# 玩家血量奖励，掉血就惩罚，否则无（因为没让它学回血，鼓励躲技能）
def player_hp_reward(player_hp, prev_player_hp):
    player_hp_increase = player_hp - prev_player_hp
    if player_hp_increase < 0:
        return PLAYER_HP_REWARD_RATIO * player_hp_increase
    return 0


# boss 血量奖励，鼓励让 boss 掉血
def boss_hp_reward(boss_hp, prev_boss_hp):
    boss_hp_reduce = prev_boss_hp - boss_hp
    if boss_hp_reduce > 0:
        return boss_hp_reduce * BOSS_HP_REWARD_RATIO
    return 0


def done_reward(boss_hp, player_hp):
    if boss_hp <= 0:
        return player_hp * PLAYER_HP_REWARD_RATIO_WIN # 胜利奖励
    else:
        return -boss_hp * BOSS_HP_REWARD_RATIO  # 失败惩罚，boss 血量越高惩罚越大