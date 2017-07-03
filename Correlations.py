import numpy as np
import visualize as vs


def get_correlation_with_time_delay(seq1, seq2,time_interval,delta_t=1):
    prov_corr = 0
    for i in range(-time_interval/delta_t,time_interval/delta_t):
  
        seq1_new,seq2_new = time_shift_sequences(seq1[:],seq2[:], i*delta_t)

        cor = get_correlation(seq1_new,seq2_new)

        if abs(prov_corr)<abs(cor):
            prov_corr = cor
            pov_deltatime = i*delta_t
    
    return prov_corr, pov_deltatime



def get_correlation(X,Y):
    
        cor = np.zeros((2,len(X)))

        cor[0] = X[:]
        cor[1] = Y[:]
        c = np.corrcoef(cor)

        return c[0][1]



def time_shift_sequences(seq1, seq2, delta_t):
    """
    Apply a time shift of delta_t to two sequeces
    """
    
    if delta_t > 0:
        seq1_new = seq1[delta_t:]
        seq2_new = seq2[:-delta_t]
        
    if delta_t < 0:
        seq1_new = seq1[:delta_t]
        seq2_new = seq2[-delta_t:]
        
    if  delta_t == 0:
        seq1_new = seq1[:]
        seq2_new = seq2[:]
    
    return seq1_new, seq2_new
