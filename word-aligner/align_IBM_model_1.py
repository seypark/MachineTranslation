#!/usr/bin/env python
import optparse
import sys
from collections import defaultdict

optparser = optparse.OptionParser()
optparser.add_option("-b", "--bitext", dest="bitext", default="data/dev-test-train.de-en", help="Parallel corpus (default data/dev-test-train.de-en)")
optparser.add_option("-t", "--threshold", dest="threshold", default=0.5, type="float", help="Threshold for aligning with Dice's coefficient (default=0.5)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
(opts, _) = optparser.parse_args()

sys.stderr.write("Training with IBM model_1 coefficient...")
bitext = [[sentence.strip().split() for sentence in pair.split(' ||| ')] for pair in open(opts.bitext)][:opts.num_sents]
e_count = defaultdict(int)
g_count = defaultdict(int)
t = defaultdict(lambda : defaultdict(float))
q = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(float))))


#P(e|g)
e_word_count = 0
g_word_count = 0

#Init
for (n, (g, e)) in enumerate(bitext):
    for e_i in set(e):
        if (e_count[e_i] == 1):
            continue
        else:
            e_count[e_i] = 1
            e_word_count += 1

    for g_j in set(g):
        if (g_count[g_j] == 1):
            continue
        else:
            g_count[g_j] = 1
            g_word_count += 1


# initialize p(e|g)
for g_word in g_count.keys():
    for e_word in e_count.keys():
        #Uniform distribution
        #sum_e t(e|g) = 1
        t[e_word][g_word] = 1.0 / e_word_count    
        
# initialize q
#sum_j=0^l q(j|i, l, m) where l is the length of g, m is the length of e
for (n, (g, e)) in enumerate(bitext):
    m = length(e)
    l = length(g)
    for i in xrange(m):
        for j in xrange(l)+1:
            q[j][i][l][m] = (1 / (l+1))

#EM
for t in xrange(T):
    # set all counts c(...) = 0
    
    c_2 = defaultdict(float)
    c_1 = defaultdict(lambda : defaultdict(float))
    c_4 = defaultdict(lambda : defaultdict(lambda : defaultdict(float)))
    c_3 = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(float))))

    #set all c_ to zero
    for (k, (g, e)) in enumerate(bitext):
        m_k = length(e)
        l_k = length(g)

        for i in xrange(m_k):
            for j in xrange(l_k)+1:
                c_1[g_j][e_i] = 0
                c_2[g_j] = 0
                c_3[j][i][l_k][m_k] = 0
                c_4[i][l_k][m_k] = 0

    for (k, (g, e)) in enumerate(bitext):
        m_k = length(e)
        l_k = length(g)



        for i in xrange(m_k):
            for j in xrange(l_k)+1:
                
                e_i = e[i]
                g_j = g[j]

                sum_j = 0.0
                for j in xrange(l_k)+1:
                    sum_j += (t[e_i][g_j])

                delta = t[e_i][g_j] / sum_j


                c_1[g_j][e_i] = c_1[g_j][e_i] + delta
                c_2[g_j] = c[g_j] + delta
                c_3[j][i][l_k][m_k] = c_3[j][i][l_k][m_k] + delta
                c_4[i][l_k][m_k] = c_4[i][l_k][m_k] + delta

    # Update parameters
    for g_j in t.keys():
        for e_i in t[g_j].keys():
            t[e_i][g_j] = t[e_i][g_j][e_i] / c_2[g_j]

    for j in q.keys():
        for i in q[j].keys():
            for l in q[j[i]].keys():
                for m in q[j[i[m]]].keys():
                    q[j][i][l][m] = c_3[j][i][l][m] / c_4[i][l][m]


'''

# count the number of word
e_word_count = 0
f_word_count = 0
for (n, (f, e)) in enumerate(bitext):
    for e_i in set(e):
        if (e_count[e_i] == 1):
            continue
        else:
            e_count[e_i] = 1
            e_word_count += 1

    for f_i in set(f):
        if (f_count[f_i] == 1):
            continue
        else:
            f_count[f_i] = 1
            f_word_count += 1

prob_e_given_g = defaultdict(float)

# initialize p(e|g)
for e_word in e_count:
    for g_word in g_count:
        prob_e_given_g[e_word][g_word] = 1.0 / e_word_count


# initialize p(a_i = j)
for (n, (f, e)) in enumerate(bitext):
    len_e = len(e) #m : target sentence
    len_f = len(f) #n : source sentence

    length_pair = str(f_len) + "," + str(e_len)

    # m is target sentence length
    prod_i = 1;
    for i in xrange(len_e)
        e_word = e[i]
        for j in xrange(len_f)
            p_a[length_pair][str(i)][str(j)] = 1 / (1 + float(len_e))

# EM
max_iter = 50

for iter in xrange(max_iter)
    for

for i in xrange(m+1)

'''
'''

    
    for f_i in set(f):
        f_count[f_i] += 1
        for e_j in set(e):
            fe_count[(f_i,e_j)] += 1
    for e_j in set(e):
        e_count[e_j] += 1
    if n % 500 == 0:
        sys.stderr.write(".")

    dice = defaultdict(int)

for (k, (f_i, e_j)) in enumerate(fe_count.keys()):
    dice[(f_i,e_j)] = 2.0 * fe_count[(f_i, e_j)] / (f_count[f_i] + e_count[e_j])
    if k % 5000 == 0:
        sys.stderr.write(".")
sys.stderr.write("\n")

for (f, e) in bitext:
    for (i, f_i) in enumerate(f): 
        for (j, e_j) in enumerate(e):
            if dice[(f_i,e_j)] >= opts.threshold:
                sys.stdout.write("%i-%i " % (i,j))
    sys.stdout.write("\n")
    '''
