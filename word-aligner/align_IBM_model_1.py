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
#print 'Counting words'
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

#print 'Initializing t and q function'
# initialize p(e|g)
for (n, (g, e)) in enumerate(bitext):
    m = len(e)
    l = len(g)

    for i in xrange(m):
        for j in xrange(l+1):
            
            e_i = e[i]
            g_j = 'null'
            if (j < l):
                g_j = g[j]

            t[e_i][g_j] = 1.0 / e_word_count
            #if t[e_i][g_j] == 0.0:
                #print e_word_count
            q[j][i][l][m] = (1 / l+1)

#for g_word in g_count.keys():
#    for e_word in e_count.keys():
        #Uniform distribution
        #sum_e t(e|g) = 1
#        t[e_word][g_word] = 1.0 / e_word_count    
        
#print 'q initialization'        
# initialize q
#sum_j=0^l q(j|i, l, m) where l is the length of g, m is the length of e
#for (n, (g, e)) in enumerate(bitext):
#    m = len(e)
#    l = len(g)
#    for i in xrange(m):
#        for j in xrange(l+1):
#            q[j][i][l][m] = (1 / (l+1))

#print 'EM'
#EM
T = 10
for tt in xrange(T):
    #print tt
    # set all counts c(...) = 0
    
    c_2 = defaultdict(float)
    c_1 = defaultdict(lambda : defaultdict(float))
    c_4 = defaultdict(lambda : defaultdict(lambda : defaultdict(float)))
    c_3 = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(float))))

    #set all c_ to zero
    for (k, (g, e)) in enumerate(bitext):
        m_k = len(e)
        l_k = len(g)

        for i in xrange(m_k):
            for j in xrange(l_k+1):
                e_i = e[i]
                g_j = 'null'
                if j < l_k:
                    g_j = g[j]

                c_1[g_j][e_i] = 0
                c_2[g_j] = 0
                c_3[j][i][l_k][m_k] = 0
                c_4[j][i][m_k] = 0

    for (k, (g, e)) in enumerate(bitext):
        m_k = len(e)
        l_k = len(g)

        for i in xrange(m_k):

            sum_j = 0.0
            for j in xrange(l_k+1):
                e_i = e[i]
                g_j = 'null'
                if j < l_k:
                    g_j = g[j]

                #if t[e_i][g_j] == 0:
                    #print t[e_i][g_j]
                sum_j += (t[e_i][g_j])
            #print sum_j
            for j in xrange(l_k+1):
                e_i = e[i]
                g_j = 'null'
                if j < l_k:
                    g_j = g[j]

                delta = t[e_i][g_j] / sum_j
                c_1[g_j][e_i] = c_1[g_j][e_i] + delta
                c_2[g_j] = c_2[g_j] + delta

                c_3[j][i][l_k][m_k] = c_3[j][i][l_k][m_k] + delta
                c_4[i][l_k][m_k] = c_4[i][l_k][m_k] + delta

    # Update parameters
    for (k, (g, e)) in enumerate(bitext):
        m_k = len(e)
        l_k = len(g)

        for i in xrange(m_k):
            for j in xrange(l_k+1):

                e_i = e[i]
                g_j = 'null'
                if j < l_k:
                    g_j = g[j]
                
                t[e_i][g_j] = c_1[g_j][e_i] / c_2[g_j]
                #print '%f %f %f' % (t[e_i][g_j], c_1[e_i][g_j], c_2[g_j])
                q[j][i][l_k][m_k] = c_3[j][i][l_k][m_k] / c_4[i][l_k][m_k]
                #print '%f %f %f' % (q[j][i][l_k][m_k], c_3[j][i][l_k][m_k], c_4[i][l_k][m_k])
            
    #for j in q.keys():
    #    for i in q[j].keys():
    #        for l in q[j][i].keys():
    #            for m in q[j][i][m].keys():
    #                if (i,l,m) in c_4:
                        

    #                    q[j][i][l][m] = c_3[j][i][l][m] / c_4[i][l][m]


# use params to calculate alignment
for (k, (g, e)) in enumerate(bitext):
    m_k = len(e)
    l_k = len(g)

    for i in xrange(m_k):
        #fine a_i = arg max_j
        a_i = -1
        best_pr = -99.9
        for j in xrange(l_k):
            e_i = e[i]
            g_j = 'null'
            if j < l_k:
                g_j = g[j]

            pr = q[j][i][l_k][m_k] * t[e_i][g_j]
            #print 'q %f' % q[g_j][e_i][l_k][m_k]
            #print t[e_i][g_j]
            #print pr
            if pr > best_pr:
                best_pr = pr
                a_i = j

        sys.stdout.write("%i-%i " % (a_i,i))

    sys.stdout.write("\n")