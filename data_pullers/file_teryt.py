#!/usr/bin/python
# -*- encoding: utf-8 -*-

import codecs

overrides_2000 = {
    u'Piwniczna': ['1210133'],
    u'Rabka': ['1211123'],
    u'Siemiątkowo Koziebrodzkie': ['1437052'],
    u'Wesoła': ['1465158'],
    u'Zbuczyn Poduchowny': ['1426132'],
    u'Horyniec': ['1809032'],
    u'Stary Dzikowiec': ['1806062'],
    u'Radomyśl': ['1818042'],
    u'Dobrzyniewo Kościelne': ['2002032'],
    u'Kolbudy Górne': ['2204032'],
    u'Święta Katarzyna': ['223083'],
    u'Grążawy': ['402062'],
    u'Krynica': ['1210073'],
    u'¦wierzawa': ['226043'],
    u'Z³otoryja': ['226021', '226062'],
    u'P³ock': ['1462011'],
    u'Bia³ystok': ['2061011'],
    u'Bia³ogard': ['3201011', '3201022'],
    u'Józefów': ['1417011', '602073', '612022'],
    u'Kostrzyn': ['3021083', '801011'],
    u'Brzeg': ['1601011', '1601022']
}

overrides_2001 = {
    u'Horyniec': ['1809032'],
    u'Święta Katarzyna': ['223083'],
    u'Krynica': ['1210073'],
    u'Piwniczna': ['1210133'],
    u'Rabka': ['1211123'],
    u'Siemiątkowo Koziebrodzkie': ['1437052'],
    u'Zbuczyn Poduchowny': ['1426132'],
    u'Brzeg': ['1601011', '1601022'],
    u'Stary Dzikowiec': ['1806062'],
    u'Radomyśl': ['1818042'],
    u'Dobrzyniewo Kościelne': ['2002032'],
    u'Kolbudy Górne': ['2204032'],
    u'Grążawy': ['402062'],
    u'Wesoła': ['1465158'],
    u'Warszawa-Centrum': ['1465011'],
    u'Józefów': ['1417011', '602073', '612022'],
    u'Kostrzyn': ['3021083', '801011']}

overrides_2004 = {
    u'Grążawy': ['402062'],
    u'st. Warszawa': ['1465011'],
    u'Szczawin Kośc.': ['1404052'],
    u'Święta Katarzyna': ['223083'],
    u'Zagranica': ['0000000'],
    u'Statki': ['00000001'],
}

overrides_2005 = {
    u'Zagranica': ['0000000'],
    u'm. st. Warszawa - zagranica': ['0000000'],
    u'm. Gdańsk - statki': ['0000001'],
    u'm. Gdynia - statki': ['0000001'],
    u'm. Szczecin - statek': ['0000001'],
    u'Statki': ['00000001'],
    u'Święta Katarzyna': ['0223083'],
    u'Warszawa': ['1465011'],
    u'Józefów': ['1417011', '602073', '612022'],
    u'Szczawin Kośc.': ['1404052'],
}

overrides_2009 = {
    u'Warszawa': ['1465011'],
    u'Święta Katarzyna': ['223083'],
    u'Szczawin Kośc.': ['1404052'],
}

overrides_2010 = {
    u'Zagranica': ['0000000'],
    u'Jaśliska': ['0000001'],
}

overrides_2011 = {
    u'Zagranica': ['149901'],
    u'm. st. Warszawa - zagranica': ['0000000'],
    u'Statki (Warszawa)': ['149801'],
    u'Bemowo, dz.': ['146502'],
    u'Białołęka, dz.': ['146503'],
    u'Bielany, dz.': ['146504'],
    u'Mokotów, dz.': ['146505'],
    u'Ochota, dz.': ['146506'],
    u'Praga-Południe, dz.': ['146507'],
    u'Praga-Północ, dz.': ['146508'],
    u'Rembertów, dz.': ['146509'],
    u'Śródmieście, dz.': ['146510'],
    u'Targówek, dz.': ['146511'],
    u'Ursus, dz.': ['146512'],
    u'Ursynów, dz.': ['146513'],
    u'Wawer, dz.': ['146514'],
    u'Wesoła, dz.': ['146515'],
    u'Wilanów, dz.': ['146516'],
    u'Włochy, dz.': ['146517'],
    u'Wola, dz.': ['146518'],
    u'Żoliborz, dz.': ['146519'],
    u'm. Gdańsk - statki': ['0000001'],
    u'm. Gdynia - statki': ['0000001'],
    u'm. Szczecin - statek': ['0000001'],
    u'Statki': ['00000001'],
    u'Statki (Gdańsk)': ['229801'],
    u'Święta Katarzyna': ['0223083'],
    u'Warszawa': ['1465011'],
    u'Józefów': ['1417011', '602073', '612022'],
    u'Szczawin Kośc.': ['1404052'],
    u'Kąkolewnica': ['615042'],
    u'Czyżew': ['2013032'],
    u'Jaśliska': ['1807102'],
}

def TerytDataFromIterable(source):
  code_map = {}
  for line in source:
    split_line = line.split('\t')
    assert len(split_line) > 1
    municipality = split_line[0].strip()
    code = split_line[1]
    if municipality[-5:] == u'-wieś':
      municipality = municipality[:-5]
    if municipality[-7:] == u'-miasto':
      municipality = municipality[:-7]
    if municipality[-12:] == u' - dzielnica':
      municipality = u'Warszawa-' + municipality[:-12]
    if municipality in code_map:
      code_map[municipality].append(code)
    else:
      code_map[municipality] = [code]
  return code_map

def GetTerytData(filename):
  with codecs.open(filename, mode='r', encoding='utf-8') as source:
    return TerytDataFromIterable(source.readlines())
