from .errors import *
from . import abilities


# TODO: buff de-cast on minion death

class BaseEntity:
    def __init__(self, name='Bob', health=None, mana=None, master=None, my_class=None, rollover=True, add_action=None,
                 add_status=None, automation=None, level=1):
        self.master = master
        self.my_class = my_class
        self.rollover = rollover
        self.name = name
        self.automation = automation
        self.level = level
        if add_action is None:
            add_action = []
        else:
            if not hasattr(add_action, '__iter__'):
                add_action = [add_action]
        if add_status is None:
            add_status = []
        else:
            if not hasattr(add_status, '__iter__'):
                add_status = [add_status]
        if my_class is not None:
            # TODO: classes
            self.actions = my_class.get_actions(self) + add_action
            self.status = my_class.get_status(self) + add_status
            if health is None:
                health = my_class.health
            if mana is None:
                mana = my_class.mana
        else:
            self.actions = add_action
            self.status = add_status
        if health is None:
            health = 1
        if mana is None:
            mana = 0
        self.max_health = health
        self.max_mana = mana
        # attributes set by init_encounter
        self.health = None
        self.mana = None
        self.buffs = None
        self.minions = None
        self.alive = None
        self.opponent = None
        self.init_encounter()

    def init_encounter(self, opponent=None):
        self.alive = True
        self.health = self.max_health
        self.mana = self.max_mana
        self.buffs = []
        self.minions = []
        self.opponent = opponent

    def all_minions(self):
        return sum([[i] + i.all_minions() for i in self.minions], [])

    def friendlies(self):
        if self.master is None:
            return self.all_minions()
        tmp = self.master.all_minions()
        tmp.remove(self)
        return tmp

    def is_enemy(self, target):
        if target == self:
            return False
        if target in self.friendlies():
            return False
        return True

    def redirect(self, caster):
        if caster in (self.friendlies() + [self]):
            return self
        # TODO: check targeting order with Mesome
        tmp = self.minions + [self]
        return tmp[0]

    def _sum_buffs(self):
        return sum(self.buffs)

    def buff_outgoing(self):
        return self._sum_buffs()['outgoing']

    def buff_incoming(self):
        return self._sum_buffs()['incoming']

    def buff_casting(self):
        return self._sum_buffs()['casting']

    def on_ability_use(self):
        for i, b in enumerate(self.buffs):
            if b.query_decast('ability use'):
                self.buffs.pop(i)

    def apply(self, incoming):
        self.health += incoming['health']
        self.mana += incoming['mana_gain']
        self.mana -= incoming['mana_drain']
        self.health -= incoming['damage']
        if self.health <= 0:
            self.on_death()

    def verify_cast(self, cost):
        if not self.alive:
            raise DeathError('Death prevents {0:} from performing this action.'.format(self.name))
        if self.health - cost['health'] <= 0:
            return False
        if self.mana - cost['mana_drain'] < 0:
            return False
        return True

    def on_death(self):
        self.alive = False
        if self.master:
            if self.rollover:
                self.master.apply(abilities.ApplyDict(damage=-self.health))
        self.health = 0

    def choose_action(self, phase=None):
        raise NotImplementedError('Must be set in child class.')

    def determine_action(self, phase=None):
        if self.automation is None:
            try:
                return self.choose_action(phase=phase)
            except NotImplementedError:
                return self.actions[0]
        if self.automation == 'first':
            return self.actions[0]
        try:
            return self.actions(phase=phase)
        except TypeError:
            pass
        msg = 'Automation of action option "{0:}" not recognized.'.format(self.automation)
        raise ValueError(msg)


class Minion(BaseEntity):
    def __init__(self, name='Bob', health=1, damage=1, mana=0, master=None, my_class=None, rollover=True,
                 add_action=None, add_status=None, automation='first'):
        if add_action is None:
            add_action = []
        else:
            if not hasattr(add_action, '__iter__'):
                add_action = [add_action]
        if damage:
            if damage > 0:
                add_action += abilities.BasicAttack(self, apply2target=damage)
        super().__init__(name=name, health=health, mana=mana, master=master, my_class=my_class, rollover=rollover,
                         add_action=add_action, add_status=add_status, automation=automation)


class PunchingBag(BaseEntity):
    def __init__(self, name='Punching Bag', health=99999):
        super().__init__(name=name, health=health, add_action=abilities.NoAction(self), automation='first')


class Player(BaseEntity):
    def __init__(self, name, my_class, level):
        super().__init__(name=name, my_class=my_class, level=level)
