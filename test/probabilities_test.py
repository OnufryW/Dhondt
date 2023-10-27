import random

def ChooseManual(N, K, L):
  res = 0
  while K > 0:
    choice = random.randint(0, N-1)
    if choice < L:
      L -= 1
      res += 1
    N -= 1
    K -= 1
  return res

def ChooseIndependent(N, K, L):
  res = 0
  while K > 0:
    choice = random.randint(0, N-1)
    if choice < L:
      res += 1
    K -= 1
  return res

def GetDistribution(N, K, L, repeats, choice):
  res = {}
  for x in range(K+1):
    res[x] = 0
  for x in range(repeats):
    res[choice(N, K, L)] += 1
  return res

def GetCdfDelta(N, K, L, repeats):
  res1 = GetDistribution(N, K, L, repeats, ChooseManual)
  res2 = GetDistribution(N, K, L, repeats, ChooseIndependent)
  res = {}
  cdf1 = 0
  cdf2 = 0
  total = 0
  for x in range(K+1):
    cdf1 += res1[x]
    cdf2 += res2[x]
    res[x] = (cdf1 - cdf2) * 1. / repeats
    total += res[x] if res[x] > 0 else -res[x]
  return res, total

REPS = 10000
NN = 1000
LL = 500
KK = 500

res, total = GetCdfDelta(NN, KK, LL, REPS)
print ("TOTAL DIFF: ", total)
for x in res:
  print(x, ": ", 100 * res[x])

