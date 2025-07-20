#!/usr/bin/python
# -*- encoding: utf-8 -*-

class CodeError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class TerytChooser(object):
  def __init__(self, code_map, overrides):
    self.code_map = code_map
    self.overrides = overrides

  def BestCode(self, municipality, suffix='?', near_code='', certainty=5):
    """Suffix can be ?, 1, 2 or 3. 1 stands for town, 2 stands for rural,
       3 stands for mixed, ? stands for "I don't know".

       near_code can either be an empty string or a code of a nearby place.
        
       certainty ranges from 1 to 5. On 5, we will return only if there is
       a unique certain match. On 1 we will always return something. On 4,
       we will use only the suffix. On 3, we will use the near code, but only
       if it's a very sure thing. On 2, we will do our best with the near code.
    """
    # If we don't have any code for the municipality, not much we can do.
    if municipality not in self.code_map and municipality not in self.overrides:
      if certainty == 1:
        return u'000000'
      else:
        raise CodeError('No listing for municipality: "' + municipality + '"')
    if municipality in self.code_map and municipality in self.overrides:
      if certainty == 5:
        raise CodeError(municipality + ' defined both in overrides and in code map')
    # These are hand-crafted overrides, we always consider them superior.
    if municipality in self.overrides:
      candidates = self.overrides[municipality]
    else:
      candidates = self.code_map[municipality]
    # If there is only one choice, return it.
    if len(candidates) == 1:
      return candidates[0]
    # Now, this is all we could do if we want to be _certain_.
    if certainty == 5:
      raise CodeError('Multiple codes (lvl 5) for: ' + municipality + ': ' +
          str(candidates))
    # Try perfect-matching the suffix.
    if suffix != '?':
      new_cands = [x for x in candidates if x[-1:] == suffix]
      if new_cands:
        candidates = new_cands
      # No perfect match. But if the suffix is given as "2", we prefer a
      # 3 to a 1, and if it's given as "1", we prefer a 3 to a 2.
      elif certainty < 4:
        new_cands = [x for x in candidates if x[-1:] == u'3']
      if new_cands:
        candidates = new_cands
    if len(candidates) == 1:
      return candidates[0]
    # If we want to only use the suffix, no more can be done.
    if certainty == 4:
      raise CodeError('Multiple codes (lvl 4) for: ' + municipality + ': ' +
          str(candidates))
    # Let's try getting a prefix-match.
    if near_code:
      # Cut off the last 3 digits and see what happens.
      new_cands = [x for x in candidates if x[:-3] == near_code[:-3]]
      if len(new_cands):
        candidates = new_cands
      # Now try cutting off the last 5 (we'll be left with V-code).
      elif certainty < 3:
        new_cands = [x for x in candidates if x[:-5] == near_code[:-5]]
        if len(new_cands):
          candidates = new_cands
      # Try finding a near code.
      int_near_code = int(near_code)
      def dist(x):
        return abs(int(x) - int_near_code)
      best = min([dist(x) for x in candidates])
      multiplier = 10
      if certainty == 2:
        multiplier = 3
      if certainty == 1:
        multiplier = 1
      # Restrict ourselves to codes that 
      candidates = [x for x in candidates if dist(x) <= multiplier * best]
    if certainty == 1 or len(candidates) == 1:
      return candidates[0]
    raise CodeError('No nearby code to resolve by for: ' + municipality + ' (' +
        str(near_code) + '): ' + str(candidates))

