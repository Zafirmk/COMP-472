from sklearn import preprocessing
import matplotlib.pyplot as plt
from afinn import Afinn
import sklearn.cluster
import pandas as pd
import random
import spacy



# Display num entries for each cluster in clusters
def display_clusters(clusters, num):
    '''
    clusters: Kmeans clustering output
    num: Number of entries to display for each cluster
    '''
    for key in clusters.keys():
        lst = []
        for i in range(num):
            if len(clusters[key]) <= num:
                lst = clusters[key]
                break
            curr_int = random.randint(0, len(clusters[key])-1)
            lst.append(clusters[key][curr_int])
        
        print("Cluster " + str(key) + ": ")
        print(lst)
        print("\n")


# Generate an elbow graph
def elbow_graph(table, iterations, NEtype_idx, fileName):
    '''
    table: Table to generate elbow graph for
    iterations: Number of iterations to run for
    NEtype_idx: Index of the NEtype column
    fileName: File name to save graph
    '''
    X = table.to_numpy()
    le = preprocessing.LabelEncoder()
    X[:, NEtype_idx] = le.fit_transform(X[:, NEtype_idx])
    
    distorsions = []
    for k in range(1, iterations):
        kmeans = sklearn.cluster.KMeans(n_clusters=k)
        kmeans.fit(X)
        distorsions.append(kmeans.inertia_)

    fig = plt.figure(figsize=(15, 5))
    plt.plot(range(1, iterations), distorsions)
    plt.grid(True)
    plt.title('Elbow curve')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Inertia')
    plt.savefig('Elbow Graphs/'+fileName+'.png')


# Populate t1 table
def build_t1(table, doc, afinn):
    '''
    table: Empty initialized table with column names
    doc: Doc to use to populate table
    afinn: Afinn object for sentiment analysis
    '''
    for sent in doc.sents:
        sentimentAnalysis = afinn.score(str(sent))
        for token in sent:
            if not token.is_punct:
                row_t1 = {
                        'Token': token.vector_norm,
                        'NE?': 1 if token.ent_type > 0 else 0,
                        'NEtype': token.ent_type_,
                        'Governor': token.vector_norm,
                        'SentimentValueofToken': afinn.score(str(token)),
                        'SentimentValueofSentence': sentimentAnalysis
                        }
                table = table.append(row_t1, ignore_index = True)
    return table

def build_t2(table, doc, afinn):
    '''
    table: Empty initialized table with column names
    doc: Doc to use to populate table
    afinn: Afinn object for sentiment analysis
    '''
    for ent in doc.ents:
        row_t2 = {
                'Token': ent.vector_norm,
                'NEtype': ent.label_,
                'Governor': ent.root.head.vector_norm,
                'SentimentValueofToken': afinn.score(str(ent)),
                'SentimentValueofSentence': afinn.score(str(ent.sent))
                }
        table = table.append(row_t2, ignore_index = True)
    return table          

def cluster_t1(table, doc, NEtype_idx, clusters):
    '''
    table: Populated table to cluster on
    doc: Doc to used to populate table
    NEtype_idx: Index of NEtype column
    clusters: Number of clusters
    '''
    X = table.to_numpy()
    le = preprocessing.LabelEncoder()
    X[:, NEtype_idx] = le.fit_transform(X[:, NEtype_idx])

    seen = []
    kmeans = sklearn.cluster.KMeans(clusters, max_iter=1000).fit(X)
    clusters_T1 = {}
    idx = 0
    for sent in doc.sents: 
        for token in sent:
            if not token.is_punct and str(token) not in seen:
                curr_cluster = kmeans.labels_[idx] + 1
                if curr_cluster not in clusters_T1:
                    clusters_T1[curr_cluster] = [str(token)]
                else:
                    clusters_T1[curr_cluster].append(str(token))        
                idx += 1
                seen.append(str(token))
        
    return clusters_T1

def cluster_t2(table, doc, NEtype_idx, clusters):
    '''
    table: Populated table to cluster on
    doc: Doc to used to populate table
    NEtype_idx: index of NEtype column
    afinn: Afinn object for sentiment analysis
    '''
    X = table.to_numpy()
    le = preprocessing.LabelEncoder()
    X[:, NEtype_idx] = le.fit_transform(X[:, NEtype_idx])
    seen = []
    kmeans = sklearn.cluster.KMeans(clusters, max_iter=1000).fit(X)
    clusters_T2 = {}
    idx = 0
    for ent in doc.ents:
        if str(ent) not in seen:
            curr_cluster = kmeans.labels_[idx] + 1
            if curr_cluster not in clusters_T2:
                clusters_T2[curr_cluster] = [str(ent)]
            else:
                clusters_T2[curr_cluster].append(str(ent))        
            seen.append(str(ent))
        idx += 1
    return clusters_T2

def main():
    nlp = spacy.load('en_core_web_sm')

    # Open document and clean up punctuation
    f = open("APonTrump").read().replace("\n\n", " ").replace("``", "\"")
    f2 = open("S1.txt").read()
    doc_APonTrump = nlp(f)
    doc_S1 = nlp(f2)

    afinn = Afinn()

    # Table Headings
    t1_headings = ['Token', 'NE?', 'NEtype', 'Governor', 'SentimentValueofToken', 'SentimentValueofSentence']
    t2_headings = ['Token', 'NEtype', 'Governor', 'SentimentValueofToken', 'SentimentValueofSentence']

    # Initialize Tables
    t1_APonTrump = pd.DataFrame(columns=t1_headings)
    t2_APonTrump = pd.DataFrame(columns=t2_headings)
    t1_S1 = pd.DataFrame(columns=t1_headings)
    t2_S1 = pd.DataFrame(columns=t2_headings)



    t1_APonTrump = build_t1(t1_APonTrump, doc_APonTrump, afinn)
    t2_APonTrump = build_t2(t2_APonTrump, doc_APonTrump, afinn)
    t1_S1 = build_t1(t1_S1, doc_S1, afinn)
    t2_S1 = build_t2(t2_S1, doc_S1, afinn)
    
    print('\n')
    print("T1_S1")
    print(t1_S1)
    print("T2_S1")
    print(t2_S1)


    clusters_t1 = cluster_t1(t1_APonTrump, doc_APonTrump, 2, 3)
    clusters_t2 = cluster_t2(t2_APonTrump, doc_APonTrump, 1, 2)

    print('\n')
    print('Now showing T1 clustering (APonTrump)')
    display_clusters(clusters_t1, 20)

    print('Now showing T2 clustering (APonTrump)')
    print('\n')
    display_clusters(clusters_t2, 20)

    elbow_graph(t1_APonTrump, 10, 2, 'elbow_graph_t1')
    elbow_graph(t2_APonTrump, 10, 1, 'elbow_graph_t2')
    
if __name__ == '__main__':
    main()