# Sejm election results

Each year has its own format, because, well, why not.

The sources:

 - For 2023: https://wybory.gov.pl/sejmsenat2023/pl/dane_w_arkuszach, retrieved February 27th, 2024.
 - For 2019: https://sejmsenat2019.pkw.gov.pl/sejmsenat2019/pl/dane_w_arkuszach, retrieved February 27th, 2024.
 - For 2015: https://parlament2015.pkw.gov.pl/355_Wyniki_Sejm_XLS.html, retrieved February 27th, 2024. This is XLS data, converted to CSV using OpenOffice.
 - For 2011: Doesn't seem there's a CSV available. Did a data puller (`/data_pullers/pull_sejm_2011.py`), pulled on 20th July 2025.

Older elections don't seem to be exposed in a fetchable format, because why would they. I have some old BeautifulSoup code to parse the PKW pages somewhere, I might dig it up some day.
