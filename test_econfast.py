import unittest, json
from index_publis import *
from index_authors import *

TITLE_0 = u"Labor market and employment in Uzbekistan"
ABSTRACT_0 = u"The aim of this article is to discuss how to increase employment in different regions. Conclusions drawn are that town halls play key role in regional employment. They should analyze and estimate formed social and demographic situation in the region clarify the share of the employed and unemployed body-able population, the reasons of the formed situation, elaborate and realize the measures on providing rational employment. A special attention should be paid to the existing disproportion between the rates of the new working places growth and the population increase creating definite difficulties for the youth entering the labor market, restraining the latter s migration to the capital, other regions and abroad in searching a job. It is obvious that one shouldn t fail to take into account the measures connected with the motivation and stimulation of labor and enhancement of the social protection of the population as a whole."

class TestEconFast(unittest.TestCase):

    def test_parse_journal_file(self):
        path = "repec_data/data/aae/journl/vol12.rdf"
        publis = list(parse_repec_file(path))
        print("Parsed {} publications from {}".format(len(publis), path))
        self.assertEqual(len(publis), 24)

    def test_parse_repec_file(self):
        obj = list(parse_repec_file("./repec_data/data/aad/ejbejj/ejbejj.rdf"))[0]
        self.assertEqual({
                          "jel-codes": [
                            "J08", 
                            "R23"
                          ], 
                          "abstract": u"The aim of this article is to discuss how to increase employment in different regions. Conclusions drawn are that town halls play key role in regional employment. They should analyze and estimate formed social and demographic situation in the region clarify the share of the employed and unemployed body-able population, the reasons of the formed situation, elaborate and realize the measures on providing rational employment. A special attention should be paid to the existing disproportion between the rates of the new working places growth and the population increase creating definite difficulties for the youth entering the labor market, restraining the latter\u2019s migration to the capital, other regions and abroad in searching a job. It is obvious that one shouldn\u2019t fail to take into account the measures connected with the motivation and stimulation of labor and enhancement of the social protection of the population as a whole.", 
                          "title": "Labor market and employment in Uzbekistan", 
                          "type": "ReDIF-Article 1.0", 
                          "authors": [
                            {
                              "email": "papers@journals.cz", 
                              "full_name": "Abdimannon Khaiitov", 
                              "institution": "Tashkent State Economic University"
                            }
                          ]
                        }, obj)

    def test_parse_error_file(self):
        path = "repec_data/data/abc/gakuep/volume55-4.rdf"
        publis = list(parse_repec_file(path))
        print("Parsed {} publications from {}".format(len(publis), path))
        self.assertEqual(len(publis), 4)

    def test_name_hashing(self):
      aliases = ["Stiglitz Joseph E", "Stiglitz, Joseph E.", "Joseph E. Stiglitz", "Joesph E. Stiglitz"]
      hashes = set([hash_name(full_name) for full_name in aliases])
      self.assertEqual(len(hashes), 1, "Found several hashes: {}".format(hashes))      

if __name__ == '__main__':
    unittest.main()