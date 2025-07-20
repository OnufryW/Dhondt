#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import json
import soup_getter
import teryt_chooser

class Wybory(object):
  def __init__(self, teryt):
    # teryt is a teryt chooser object.
    self.teryt = teryt
    # Keys is a list of all the keys supported by results.
    self.keys = [
      'teryt',
      'community_name',
      'county_name',
      'voivodship_name',
      'number_of_commissions',
      'eligible_voters',
      'cards_given_out',
      'valid_cards',
      'valid_votes',
    ]
    # results is a map of maps, keyed by teryt, containing keys from keys,
    # plus 'results' (the value is a map from party name to total votes)
    self.results = {}
    # Set of (voivodship, powiat) pairs.
    self.done = set()

    # Checkpointing data
    self.version = 1
    self.filename = 'sejm_2011_ckpt.json'

  def Parties(self):
    parties = set()
    for t in self.results:
      for party in self.results[t]['results']:
        parties.add(party)
    return parties

  def Serialize(self):
    with open(self.filename, 'w') as f:
      f.write(json.dumps((self.version, self.results, list(self.done))))

  def Deserialize(self):
    if os.path.isfile(self.filename):
      with open(self.filename, "r") as f:
        s = f.read()
        v, self.results, donelist = json.loads(s)
        for vo, po in donelist:
          self.done.add((vo,po))
        assert(v == 1)

  def UrlFor(self, voivodshipteryt=None, teryt_or_district=None):
    res = "http://wybory2011.pkw.gov.pl/wyn/"
    # All of Poland.
    if not voivodshipteryt:
      res += "pl/000000.html"
      return res
    res += voivodshipteryt + "/pl/" + teryt_or_district + ".html"
    return res

  def ExtractHrefs(self, url, debug, headers, address_extract):
    # Extracts all the hrefs from a table with the given header from the given
    # URL, using the provided lambda to extract a href from a row (more precisely,
    # it takes the first link in every td, and extracts it).
    # Returns a list of triples: voivodshipteryt, teryt_or_district, name.
    result = {}
    page = soup_getter.WithRetries(url, debug, 3)
    tables = page.find_all('tbody')
    for table in tables:
      tds = table.find_all('td')
      if not tds[0].string or tds[0].string.strip() not in headers:
        continue
      for td in tds:
        ass = td.find_all('a')
        if not ass:
          continue
        a = ass[0]
        addr = address_extract(a['href'])
        if addr:
          result[(addr[0], addr[1])] = a.string
    return [(r[0], r[1], result[r]) for r in result]

  def GetCircleList(self):
    # We need the voivodship data, which is why we don't use ExtractHrefs direct.
    # Return a list of (voivodship teryt, district id, district name, voivodship)
    page = soup_getter.WithRetries(self.UrlFor(), 'Whole Poland', 3)
    tables = page.find_all('tbody')
    current_voivodship = None
    # The same href appears multiple times. We need to make sure that we always
    # get the same data.
    res = {}
    for table in tables:
      tds = table.find_all('td')
      header = u'Wyniki głosowania w okręgach wyborczych'
      if not tds[0].string or tds[0].string.strip() != header:
        continue
      for td in tds:
        if td.has_attr('rowspan'):
          current_voivodship = td.string
        links = td.find_all('a')
        if not links:
          continue
        link = links[0]
        href = link['href']
        districtid = href.split('/')[3].split('.')[0]
        isname = td.has_attr('class') and 'all_left' in td['class']
        districtnum = None if isname else link.string.strip()
        districtname = link.string.strip() if isname else None
        if districtid not in res:
          res[districtid] = [
              href.split('/')[1], districtnum, districtname, current_voivodship]
        if districtnum and not res[districtid][1]:
          res[districtid][1] = districtnum
        if districtname and not res[districtid][2]:
          res[districtid][2] = districtname
        assert res[districtid][0] == href.split('/')[1]
        assert res[districtid][1] == districtnum or not districtnum
        assert res[districtid][2] == districtname or not districtname
        assert res[districtid][3] == current_voivodship
      # This is necessary, because the second table with the exact same header
      # contains Senate districts.
      break
    return [(r, res[r][0], res[r][1], res[r][2], res[r][3]) for r in res]

  def GetPowiatList(self, districtid, voivodship_teryt, debug):
    hrefs = self.ExtractHrefs(self.UrlFor(voivodship_teryt, districtid), debug,
        [u'Powiaty', u'Statki, Warszawa, Zagranica'], lambda href: (voivodship_teryt, href.split('.')[0]))
    return [href for href in hrefs if u'Senatu nr' not in href[2] and href[2] != 'Statki (Warszawa)' and href[2] != 'Zagranica']

  def GetCityList(self, districtid, voivodship_teryt, debug):
    hrefs = self.ExtractHrefs(self.UrlFor(voivodship_teryt, districtid), debug,
        [u'Miasta na prawach powiatu', u'Statki, Warszawa, Zagranica'],
        lambda href: (voivodship_teryt, href.split('.')[0]))
    return [href for href in hrefs if u'Senatu nr' not in href[2] and href[2] != u'Warszawa']

  def GetCommunityList(self, voivodship_teryt, powiat_teryt, debug):
    return self.ExtractHrefs(self.UrlFor(voivodship_teryt, powiat_teryt), debug,
        [u'Gminy', u'Dzielnice'], lambda href: (voivodship_teryt, href.split('.')[0]))

  def GetResults(self, voivodship_teryt, community_teryt, debug):
    """Returns a map from committee name to number of votes, and the number
       of voting places."""
    result = {}
    page = soup_getter.WithRetries(
        self.UrlFor(voivodship_teryt, community_teryt), debug, 3)
    tables = page.find_all('tbody')
    for table in tables:
      tds = table.find_all('td')
      if len(tds) < 5:
        continue
      if not tds[0].get_text() or u'Lista nr ' not in tds[0].get_text():
        continue
      party = tds[0].find_all('a')[0].string
      if not tds[-4].get_text() or u'Głosów na listę' not in tds[-4].get_text():
        continue
      result[party] = int(tds[-3].string.replace(' ', '').replace(u'\xa0', ''))
    commissions = 0
    for table in tables:
      tds = table.find_all('td')
      if not tds[0].get_text() or u'Obwody' not in tds[0].get_text() or commissions:
        continue
      for td in tds:
        links = td.find_all('a')
        if links and u'/prt/' in links[0]['href']:
          commissions += 1
    # I have no idea what's happening in the foreign commissions, and I can't be
    # bothered to debug.
    assert (commissions and commissions % 2 == 0) or commissions == 517
    return result, commissions // 2

  def GetCommunityStats(
      self, voivodship_teryt, community_teryt, communities, debug):
    """Takes (besides the page data) a list of communities to find on the page.

    Returns a map from each community to a map with keys 'Uprawnionych',
    'Kart wydanych', 'Kart waznych' and 'Glosow waznych', denoting overall stats
    for the community."""
    def getnum(td):
      return int(td.get_text().replace(' ', '').replace(u'\xa0', ''))
    page = soup_getter.WithRetries(
        self.UrlFor(voivodship_teryt, community_teryt), debug, 3)
    res = {}
    curindex = 0
    curcom = None
    tables = page.find_all('tbody')
    for table in tables:
      tds = table.find_all('td')
      for td in tds:
        if curcom:
          if curindex == 1:
            res[curcom]['Uprawnionych'] = getnum(td)
            curindex += 1
          elif curindex == 2:
            res[curcom]['Kart wydanych'] = getnum(td)
            curindex += 1
          elif curindex == 3:
            res[curcom]['Kart waznych'] = getnum(td)
            curindex += 1
          elif curindex in [4, 5]:
            curindex += 1
          elif curindex == 6:
            res[curcom]['Glosow waznych'] = getnum(td)
            curindex = 0
            curcom = None
        else:
          text = td.get_text().strip()
          if text in communities and text not in res:
            curcom = text
            res[curcom] = {}
            curindex = 1
    for comm in communities:
      if comm not in res or len(res[comm]) != 4:
        print(comm)
        print(res)
        print(communities)
        print(res[comm])
        assert False
    return res

  def AddResults(self, teryt, community, powiat, voivodship, numcommissions,
                 stats, results):
    result = {}
    new_teryt = self.FixTeryt(teryt, community)
    result['teryt'] = new_teryt
    result['community_name'] = community
    result['county_name'] = powiat
    result['voivodship_name'] = voivodship
    result['number_of_commissions'] = numcommissions
    result['eligible_voters'] = stats['Uprawnionych']
    result['cards_given_out'] = stats['Kart wydanych']
    result['valid_cards'] = stats['Kart waznych']
    result['valid_votes'] = stats['Glosow waznych']
    result['results'] = results
    self.results[new_teryt] = result

  def GetPowiatResults(self, voivodship_teryt, powiat_teryt, voivodshipname,
                       powiatname):
    if ((voivodship_teryt, powiat_teryt)) in self.done:
      print('Skipping', powiatname)
      return
    comms = self.GetCommunityList(voivodship_teryt, powiat_teryt, powiatname)
    comm_stats = self.GetCommunityStats(voivodship_teryt, powiat_teryt,
                                        [c[2] for c in comms], powiatname)
    for _, community_teryt, name in comms:
      comm_results, commiss = self.GetResults(
          voivodship_teryt, community_teryt, name)
      stats = comm_stats[name]
      self.AddResults(community_teryt, name, powiatname, voivodshipname, commiss,
                      stats, comm_results)
    self.done.add((voivodship_teryt, powiat_teryt))
    self.Serialize()

  def GetCircleResults(self, circle):
    # The circle is a quintuple: district id, voivodship teryt, district num,
    # district name and voivodship name. The first two go into the address.
    districtid, voivodship_teryt, districtnum, districtname, voivodshipname = circle
    powiats = self.GetPowiatList(districtid, voivodship_teryt, districtname)
    for _, powiat_teryt, name in powiats:
      self.GetPowiatResults(voivodship_teryt, powiat_teryt, voivodshipname, name)
    cities = self.GetCityList(districtid, voivodship_teryt, districtname)
    city_stats = self.GetCommunityStats(
        voivodship_teryt, districtid, [c[2] for c in cities], districtname)
    for _, city_teryt, name in cities:
      if ((voivodship_teryt, city_teryt)) in self.done:
        continue
      city_results, commiss = self.GetResults(voivodship_teryt, city_teryt, name)
      stats = city_stats[name]
      self.AddResults(city_teryt, name, name, voivodshipname, commiss, 
                      stats, city_results)
      self.done.add((voivodship_teryt, city_teryt))
    self.Serialize()

  def GetPolandResults(self):
    self.Deserialize()
        
    circles = self.GetCircleList()
    for circle in circles:
      self.GetCircleResults(circle)

  def FixTeryt(self, teryt, name): 
    suffix = '?'
    near_code = teryt + '0'
    if name[-1:] == u',':
      name = name[:-1]
    if name[-5:] == u', gm.':
      name = name[:-5]
    if name[-4:] == u', m.':
      name = name[:-4]
      suffix = '1'
    try:
      return self.teryt.BestCode(
          name, suffix=suffix, near_code=near_code, certainty=3)
    except teryt_chooser.CodeError as e:
      # There are the town + community places. Default to town, with the
      # assumption town would've had a 'm.'
      if suffix == '?':
        suffix = '2'
        try:
          return self.teryt.BestCode(
              name, suffix=suffix, near_code=near_code, certainty=3)
        except teryt_chooser.CodeError as e:
          print(str(e) + ' - reported teryt: ' + res[0] + ' (' + name + ')')
      else:
        print(str(e) + ' - reported teryt: ' + res[0])

