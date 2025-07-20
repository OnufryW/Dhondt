import sejm_2011
import file_teryt
import teryt_chooser
import printer

file_data = file_teryt.GetTerytData('teryt_source.csv')
teryt = teryt_chooser.TerytChooser(file_data, file_teryt.overrides_2011)
wybory = sejm_2011.Wybory(teryt)
wybory.GetPolandResults()
printer.PrintToSsv(wybory.results, wybory.keys, wybory.Parties(), '../data/sejm_election_results/raw/2011_by_community.csv')
