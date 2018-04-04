from .errors import *
from .entities import BaseEntity


class _MyDict(dict):
    def __add__(self, other):
        keys = set(list(self.keys()) + list(other.keys()))
        tmp = {i: max(0, other.get(i, 0) + self.get(i, 0)) for i in keys}
        return self.__class__(**tmp)

    def __sub__(self, other):
        keys = set(list(self.keys()) + list(other.keys()))
        tmp = {i: max(0, self.get(i, 0) - other.get(i, 0)) for i in keys}
        return self.__class__(**tmp)


class ApplyDict(_MyDict):
    def __init__(self, mana_gain=0, damage=0, health=0, mana_drain=0, targetable=0, block=0, unblockable=0,
                 counterable=0, buffs=None):
        if buffs is None:
            buffs = []
        super().__init__(mana_gain=mana_gain, damage=damage, health=health, mana_drain=mana_drain,
                         targetable=targetable, block=block, unblockable=unblockable, counterable=counterable,
                         buffs=buffs)
        for i in ['health', 'mana_gain', 'damage', 'mana_drain']:
            self[i] = max(0, self[i])


class BuffDict(_MyDict):
    def __init__(self, outgoing=None, incoming=None, casting=None, discard=None):
        if outgoing is None:
            outgoing = ApplyDict()
        if incoming is None:
            incoming = ApplyDict()
        if casting is None:
            casting = ApplyDict()
        self.valid_reasons = ['ability use']
        if discard not in self.valid_reasons:
            raise ValueError('Buff discard must be one of the options {0:}'.format(self.valid_reasons))
        self.discard = discard
        super().__init__(outgoing=outgoing, incoming=incoming, casting=casting)

    def query_decast(self, reason=None):
        if self.discard is True:
            return True
        if self.discard == reason:
            return True
        return False


class _AbilityBase:
    caster: BaseEntity
    default_target: BaseEntity

    def __init__(self, caster, name='Basic Ability', description='', apply2caster=None, apply2target=None,
                 default_target=None):
        self.caster = caster
        self.name = name
        self.description = description
        if default_target is None:
            if self._is_valid_target(caster):
                default_target = caster
            else:
                default_target = caster.opponant
        elif default_target == 'opponent':
            default_target = caster.opponant
        self.default_target = default_target

        if apply2caster is None:
            self._apply2caster = ApplyDict()
        else:
            try:
                if int(apply2caster) == apply2caster:
                    apply2caster = {'mana_drain': apply2caster}
            except TypeError:
                pass
            self._apply2caster = ApplyDict(**apply2caster)

        if apply2target is None:
            self._apply2target = ApplyDict()
        else:
            try:
                if int(apply2target) == apply2target:
                    apply2target = {'mana_drain': apply2target}
            except TypeError:
                pass
            self._apply2target = ApplyDict(**apply2target)

    def _determine_outgoing(self, target: BaseEntity):
        out = self._apply2target
        try:
            out += self.caster.buff_outgoing()
        except AttributeError:
            pass
        try:
            out += target.buff_incoming()
        except AttributeError:
            pass
        return out

    def _determine_cost(self):
        out = self._apply2target
        try:
            out += self.caster.buff_casting()
        except AttributeError:
            pass
        return out

    def _is_valid_target(self, target: BaseEntity):
        raise NotImplementedError('Must be set in child class.')

    def acquire_target(self, target: BaseEntity=None):
        if target is None:
            target = self.caster
        if not self._is_valid_target(target):
            msg = '{0:} is not a valid target for this ability.'.format(target)
            raise InvalidTargetError(msg)
        if not self._determine_outgoing(target)['targetable']:
            target = target.redirect(self.caster)
        return target

    def castable(self):
        return self.caster.verify_cast(self._determine_cost())

    def on_cast(self):
        self.caster.apply(self._determine_cost())
        self.caster.on_ability_use()

    def attempt_cast(self, target: BaseEntity=None):
        target = self.acquire_target(target)
        if not self.castable():
            msg = '{0:} has insufficient resources to cast {1:}.'.format(self.caster.name, self.name)
            raise CastingError(msg)
        self.on_cast()
        outgoing = self._determine_outgoing(target)
        if target.query_evasion(outgoing):
            return None
        target.apply(outgoing)
        return outgoing


class BasicAttack(_AbilityBase):
    def __init__(self, caster, name='Basic Attack', description='', apply2caster=None, apply2target=1,
                 default_target=None):
        super().__init__(caster, name=name, description=description, apply2caster=apply2caster,
                         apply2target=apply2target, default_target=default_target)

    def _is_valid_target(self, target):
        if self.caster.is_enemy(target):
            return True
        return False


class NoAction(_AbilityBase):
    def __init__(self, caster, name='pass', description=''):
        super().__init__(caster, name=name, description=description)

    def _is_valid_target(self, target):
        return True
