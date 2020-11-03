import re

class MTE2UDmapper:
    def __init__(self, mapping_file, abbreviation_file):
        self.msd_upos = {}
        self.msd_mtefeat = {}
        self.msd_udfeat = {}
        with open(mapping_file, 'r', encoding='utf-8') as mapfile:
            for line in mapfile:
                parts = line.strip().split('\t')
                self.msd_upos[parts[0]] = parts[1]
                self.msd_mtefeat[parts[0]] = parts[2]
                self.msd_udfeat[parts[0]] = parts[3]

        self.abv_upos_map = { line.split()[0] : line.split()[1] for line in open(abbreviation_file) }


    def map_word(self, surface_form, lemma, msd):
        mtefeat = self.msd_mtefeat[msd]
        upos = self.msd_upos[msd]
        udfeat = self.msd_udfeat[msd]

        if msd.startswith('Pi') and lemma in ('чиј', 'нечиј','ничиј', 'сечиј'):
            udfeat = udfeat[0:udfeat.rfind('|')] + '|Poss=Yes|PronType=Int,Rel'

        if msd.startswith('P'):
            if lemma in ('секој', 'никој', 'некој', 'сешто', 'ништо', 'нешто'):
                upos = 'PRON'
            if lemma in ('сиот', 'ничиј', 'нечиј', 'сечиј'): #check what happens with adjectives ? poss pron in MK are poss adj: секаков, некаков, никаков
                upos = 'DET' #check twice!!!
            if lemma in ('сиот', 'сѐ', 'секој', 'сешто', 'сечиј'): #check секаков 
                if 'PronType' in udfeat:
                    udfeat = udfeat[0:udfeat.find('PronType')] + 'PronType=Tot'
                else:
                    udfeat += 'PronType=Tot'
            elif lemma in ('некој', 'нешто', 'неколку', 'нечиј', 'некаков'):  #check некаков
                if 'PronType' in udfeat:
                    udfeat = udfeat[0:udfeat.find('PronType')] + 'PronType=Ind'
                else:
                    udfeat += '|PronType=Ind'

        if msd.startswith('Rg'):
          if lemma in ('олку', 'вака', 'ваму','овде' 'онолку', 'онака', 'онаму','онде', 'толку', 'така', 'тогаш', 'таму', 'тука'):
            udfeat += '|PronType=Dem'
          elif lemma in ('колку', 'како', 'кога', 'зошто', 'каде'):
            udfeat += '|PronType=Int,Rel'
          elif lemma in ('неколку', 'некако', 'некогаш', 'понекогаш', 'некаде'):
            udfeat += '|PronType=Ind'
          elif lemma in ('сѐ', 'секако', 'секогаш', 'секаде', 'насекаде'):
            udfeat += '|PronType=Tot'
          elif lemma in ('николку', 'никако', 'никогаш', 'никаде'):
            udfeat += '|PronType=Neg'


        if msd.startswith('Mlc') and msd != 'Mlc':
          if 'Number' not in udfeat:
            if lemma == 'еден':
                numstr = 'Sing'
            else:
                numstr = 'Plur'
            udfeat = udfeat[0:udfeat.find('NumType')] + 'Number=' + numstr + '|NumType=Card'

          if '%' in surface_form or '$' in surface_form:
            upos = 'SYM'
            if re.search('[0-9]+', surface_form):
              udfeat = 'NumType=Mult'
            else:
              udfeat = '_'

        if msd == 'Y':
            upos = self.abv_upos_map[lemma]

        return mtefeat, upos, udfeat

    def map_file(self, infilename, outfilename):
        with open(infilename, 'r', encoding='utf-8') as infile:
            with open(outfilename, 'w', encoding='utf-8') as outfile:
                for line in infile:
                    if '\t' in line:
                        parts = line.split('\t')
                        # print(parts)
                        mtefeat, upos, udfeat = self.map_word(parts[1], parts[2], parts[4])
                        outfile.write(parts[0] + '\t' + parts[1] + '\t' + parts[2] + '\t' + upos + '\t' + parts[4] + '\t' + udfeat + '\t' + '\t'.join(parts[6:])+'\n')
                    else:
                        outfile.write(line)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Mapping MTE V6 to UD')
    parser.add_argument('mapping', help='Path to the mapping file')
    parser.add_argument('input', help='Path to the input file in conllu format')
    parser.add_argument('output', help='Path to an output file')
    parser.add_argument('abbreviation', help='Path to an abbreviations file')
    args = parser.parse_args()

    mapper = MTE2UDmapper(args.mapping, args.abbreviation)
    mapper.map_file(args.input, args.output)
