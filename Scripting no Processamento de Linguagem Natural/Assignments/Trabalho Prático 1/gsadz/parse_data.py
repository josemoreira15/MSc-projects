import re
import os

class SentilexData:

    def __init__(self, package_directory, p_weight=1, n_weight=1):
        self.lemma = {}
        self.flex = {}
        self.boosters = {}
        self.negate = []
        self.package_directory = package_directory


    def read_sentilex_lemma(self):
        with open(os.path.join(self.package_directory, 'pt', 'SentiLex-lem-PT02.txt'),"r") as file:
            pattern = r"([\w\s\-]+)\.PoS=([A-Za-z]+);TG=([A-Za-z:0-9]+);POL:([A-Z0-9=\-]+)(;POL:([A-Z0-9=\-]+))*;ANOT=(MAN|JALC)"

            for line in file.readlines():
                match = re.match(pattern,line)

                if match:
                    elem = match.group(1)

                    if elem not in self.lemma:
                        self.lemma[elem] = []

                    holder = {}
                    holder["PoS"] = match.group(2)
                    tg = match.group(3).split(":")
                    holder["TG"] = tg[1:]
                    holder["POL"] = {}
                    polaridade1 = match.group(4).split("=")
                    holder["POL"][polaridade1[0]] = polaridade1[1]

                    if match.group(6):
                        polaridade2 = match.group(6).split("=")
                        holder["POL"][polaridade2[0]] = polaridade2[1]
                    holder["ANOT"] = match.group(7)

                    self.lemma[elem].append(holder)

        return self.lemma


    def read_sentilex_flex(self):
        with open(os.path.join(self.package_directory, 'pt', 'SentiLex-flex-PT02.txt'),"r") as file:
            pattern = r"([\w\s\-]+),([\w\s\-]+)\.PoS=([A-Za-z]+);(FLEX|Flex|)=?([A-Za-z:0-9\|\/]+);TG=([A-Za-z:0-1]+);POL:([A-Z0-9=\-]+)(;POL:([A-Z0-1=\-]+))*;ANOT=(MAN|JALC)(;(REV:POL|REV=AMB))?"

            for line in file.readlines():
                match = re.match(pattern,line)
                if match:
                    palavra = match.group(1)

                    if palavra not in self.flex:
                        self.flex[palavra] = []

                    holder = {}
                    holder["LEMMA"] = match.group(2)
                    holder["PoS"] = match.group(3)
                    holder["FLEX"] = match.group(5)
                    tg = match.group(6).split(":")
                    holder["TG"] = tg[1:]
                    holder["POL"] = {}
                    polaridade1 = match.group(7).split("=")
                    holder["POL"][polaridade1[0]] = polaridade1[1]
                    if match.group(9):
                        polaridade2 = match.group(9).split("=")
                        holder["POL"][polaridade2[0]] = polaridade2[1]
                    holder["ANOT"] = match.group(10)

                    self.flex[palavra].append(holder)
    
        return self.flex
    

    def read_boosters(self):
        with open(os.path.join(self.package_directory, 'pt', 'booster.txt'),"r") as file:
            pattern = r"([\w\s]+) (INCR|DECR)"

            for line in file.readlines():
                match = re.match(pattern, line)
                if match:
                    self.boosters[match.group(1)] = match.group(2)

        return self.boosters
    

    def read_negate(self):
        with open(os.path.join(self.package_directory, 'pt', 'negate.txt'),"r") as file:
            self.negate = [line.rstrip() for line in file.readlines()]

        return self.negate
    
   
    def read_sentilex(self):
        self.read_sentilex_lemma()
        self.read_sentilex_flex()
        self.read_boosters()
        self.read_negate()