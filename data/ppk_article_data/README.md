# Data for the PPK article.

This calculates a bunch of inequality of vote strength metrics; based on the
definitions provided [here](https://czasopisma.marszalek.com.pl/images/pliki/ppk/75/ppk7515.pdf?fbclid=IwY2xjawG65-BleHRuA2FlbQIxMAABHeUwh25WdZ4bmjfdLrN8Ix8JxRyPXe5jLDThvBzu2UMirqFIrK7UJnelUQ_aem_uyeDftRVeQnN_TkRJoRGfA).

Seat allocation methods P0 to P6 are defined in the article. In short, they're all
running a seat allocation method (smallest remainder, which is what our electoral system uses), based
on various numerical parameters for the districts. Namely:
 - P0 is the current allocation, based on the CRW data about number of
   inhabitants from 2011.
 - P1 is based on GUS statisticas about the number of citizens, from the end of
   the year prior to the election.
 - P2 is based on the CRW data from the end of the year prior to the election (so,
   it's basically P0 if it was updated).
 - P3 is similar to P2, but it uses eligible voters rather than inhabitants.
 - P4 is the number of eligible voters at election start time.
 - P5 is the number of eligible voters at election end time (this changes
   because right-to-vote voters come in and vote)
 - P6 is the number of actual voters (meaning number of valid cards).
 - P7 is the proposed metric, which is the number of valid cards from the
   previous election.
