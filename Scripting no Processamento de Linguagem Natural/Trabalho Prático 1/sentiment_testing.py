from gsadz import SentimentAnalysis



def tests(sa):
    polarity1 = sa.polarity_result("És muito muito incrivelmente inteligente.")
    print(f"Polaridade do teste 1: {polarity1}")
 
    polarity2 = sa.polarity_result("Não gosto nada de ti.")
    print(f"Polaridade do teste 2: {polarity2}")

    polarity3 = sa.polarity_result("O João dá de frosques.")
    print(f"Polaridade do teste 3: {polarity3}")

    polarity4 = sa.polarity_result("Sim!")
    print(f"Polaridade do teste 4: {polarity4}")

    polarity5 = sa.polarity_result("A vida é algo normal.")
    print(f"Polaridade do teste 5: {polarity5}")

    polarity6 = sa.polarity_result("Não sou feio.")
    print(f"Polaridade do teste 6: {polarity6}")

    polarity7 = sa.polarity_result("Às vezes, isso acontece.")
    print(f"Polaridade do teste 7: {polarity7}")

    polarity8 = sa.polarity_result("Sempre gostei da tua família.")
    print(f"Polaridade do teste 8: {polarity8}")

    polarity9 = sa.polarity_result("Detesto o que estás a fazer.")
    print(f"Polaridade do teste 9: {polarity9}")

    polarity10 = sa.polarity_result("Ela fez o teste e deu negativo, isso é positivo.")
    print(f"Polaridade do teste 10: {polarity10}")


def corpus_analysis(sa):
    with open("data/corpus.txt") as corpus_file:
        corpus = corpus_file.read()

    corpus_polarity = sa.polarity_result(corpus)
    print(f'Corpus: {corpus_polarity}')


def main():
    sa = SentimentAnalysis()
    tests(sa)
    corpus_analysis(sa)


if __name__ == '__main__':
    main()