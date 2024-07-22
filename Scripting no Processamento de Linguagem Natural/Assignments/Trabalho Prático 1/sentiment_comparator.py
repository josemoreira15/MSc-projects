from LeIA.leia import SentimentIntensityAnalyzer
from textblob import TextBlob
from gsadz import SentimentAnalysis
import matplotlib.pyplot as plt
import re



class SentimentComparator:
    
    def __init__(self, pt_input, en_input):
        with open(pt_input) as pt_input_file:
            self.pt_content = pt_input_file.read()

        with open(en_input) as en_input_file:
            self.en_content = en_input_file.read()


    def pt_analysis(self):
        sleia = SentimentIntensityAnalyzer()
        sgsadz = SentimentAnalysis(p_weight=2)

        chaps = re.split(r'# [IVX]*', self.pt_content)[1:]
        nrs = re.findall(r'# [IVX]*', self.pt_content)

        leia_scores = []
        gsadz_scores = []

        for chap in chaps:
            gsadz_scores.append(sgsadz.polarity_result(chap)['Polarity'])
            leia_scores.append(sleia.polarity_scores(chap)['compound'])

        return leia_scores, gsadz_scores, nrs

    
    def blob_analysis(self):
        chaps = re.split(r'CHAPTER \w+\n', self.en_content)[1:]

        blob_scores = []

        for chap in chaps:
            blob = TextBlob(chap)
            blob_scores.append(blob.sentiment.polarity)

        return blob_scores
    

    def plotline_graph(self, leia_scores, gsadz_scores, blob_scores, nrs):
        plt.figure(figsize=(10,6))
        plt.plot(nrs, leia_scores, label='LeIA')
        plt.plot(nrs, gsadz_scores, label='gsadz')
        plt.plot(nrs, blob_scores, label='BLOB')
        plt.title('Sentiment Analysis Comparator')
        plt.xlabel('Chapter')
        plt.ylabel('Score')
        plt.legend()
        plt.savefig('graphs/sac_plotline.png')

    
    def histograms(self, leia_scores, gsadz_scores, blob_scores, nrs):
        plt.figure(figsize=(10, 6))
        plt.bar(nrs, gsadz_scores, label='gsadz', width=0.4, align='edge', color='darkorange')
        plt.bar(nrs, blob_scores, label='BLOB', width=-0.4, align='edge', color='green')
        plt.legend()
        plt.savefig('graphs/gsadz-blob.png')

        plt.figure(figsize=(10, 6))
        plt.bar(nrs, gsadz_scores, label='gsadz', width=0.4, align='edge', color='darkorange')
        plt.bar(nrs, leia_scores, label='LeIA', width=-0.4, align='edge', color='blue')
        plt.legend()
        plt.savefig('graphs/gsadz-leia.png')

    
        
sc = SentimentComparator('data/HP - PT.txt', 'data/HP - EN.txt')
leia_scores, gsadz_scores, nrs = sc.pt_analysis()
blob_scores = sc.blob_analysis()

sc.plotline_graph(leia_scores, gsadz_scores, blob_scores, nrs)
sc.histograms(leia_scores, gsadz_scores, blob_scores, nrs)