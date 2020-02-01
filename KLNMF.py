import numpy as np
import numpy.linalg as lin
import time as t

class KLNMF:
   
    epsilon = 1e-3
    beta = 0.1
    alpha = 0.005 #learning rate
    m = 0
    n = 0
    
    iterations = 500
    repetitions = 500


    def __init__(self,
                 beta = 0.1,
                 alpha=0.005,
                 epsilon = 1e-3,
                 iterations = 500,
                 repetitions =500):

        KLNMF.epsilon = epsilon        
        KLNMF.beta = beta
        KLNMF.alpha = alpha
        KLNMF.iterations = iterations
        KLNMF.repetitions = repetitions

    @classmethod
    def setEpsilon(cls, eps):
        cls.epsilon = eps
    @classmethod
    def setAlpha(cls, alpha):
        cls.alpha = alpha
    @classmethod
    def setBeta(cls, beta):
        cls.beta = beta
    @classmethod    
    def setIterations(cls, its):
        cls.iterations = its        
    @classmethod
    def setRepetitions(cls, reps):
        cls.repetitions = reps 
    
    @staticmethod
    def zeroTruncatedPoisson(loc=1, size=1):
        '''
        Draws random values from zero truncated poisson distribution for initialising 
        purposes. Will return array of specified size containing instances from ZTP distribution
        
        For initialising purposes
        '''
        x = np.random.poisson(loc, size)
        mask = x == 0
        while mask.sum() > 0:
            x[mask] = np.random.poisson(loc, mask.sum())
            mask = x == 0
        return x.squeeze()[()]
    
    
    @staticmethod
    def initialiseWandH(m, n, r):
        '''
        Function to initialise two matrix: Wo - m by r - and Ho - r by n. Where r is the
        rank of the chosen decomposition. Wo and Ho are both non-negative and column stochastic
        matrices.
        
        For testing purposes.
        '''
        Wo = KLNMF.zeroTruncatedPoisson(size=(m,r))
        Ho = KLNMF.zeroTruncatedPoisson(size=(r,n))
        Wo = np.reshape(Wo,(m,r)).astype(float)
        Ho = np.reshape(Ho,(r,n)).astype(float)
        
        for i in range(r):
            l1NormWo = sum(Wo[:,i])
            Wo[:,i] = Wo[:,i] / l1NormWo   
        for j in range(n):
            l1NormHo = sum(Ho[:,j])
            Ho[:,j] = Ho[:,j] / l1NormHo
        
        
        return Wo, Ho
    
    @staticmethod    
    def KLDivergenceObjectiveFunction(X, W, H):
        
        Xrecon = W @ H
        cost = 0 

        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                
                cost +=  X[i][j] * np.log(  (X[i][j])/(Xrecon[i][j]) )- X[i][j] +  Xrecon[i][j]

        return cost    
        
    @staticmethod
    def GDOpt(X,
              r,
              beta = 0.1,
              alpha=0.005,
              epsilon = 1e-3,
              iterations = 500,
              repetitions =500):
        
        start = t.time()

        KLNMF.epsilon = epsilon        
        KLNMF.beta = beta
        KLNMF.alpha = alpha
        KLNMF.iterations = iterations
        KLNMF.repetitions = repetitions
        
        Wprox, Hprox = KLNMF.initialiseWandH( X.shape[0], X.shape[1], r)
        
        cost = KLNMF.KLDivergenceObjectiveFunction(X, Wprox, Hprox) 
        
        
        ite = 0
        rep = 0 
     
        while rep <= KLNMF.repetitions:
            
            ite = 0
            Wprox, Hprox = KLNMF.initialiseWandH( X.shape[0], X.shape[1], r)
            
            while cost > KLNMF.epsilon and ite <= KLNMF.iterations:
                
                #Updating W first 
                gradW = (Wprox @ Hprox - X) @ Hprox.T
                Wprox -= KLNMF.alpha * gradW
                
                #Updating H second
                gradH = Wprox.T @ (Wprox @ Hprox - X)
                Hprox -= KLNMF.alpha * gradH
                
                cost = KLNMF.KLDivergenceObjectiveFunction(X, Wprox, Hprox) 
                
                ite += 1
                
                if ite == KLNMF.iterations: # if run through iterations, and no sol, repeat
                    rep += 1
                
                if cost <= KLNMF.epsilon:
                    break 
                
            if cost <= KLNMF.epsilon:
                
                endcomplete = t.time()
                Wprime, Hprime = Wprox, Hprox
                print('Optimisation complete using Kullback-Leibler divergence'
                      ' objective and gradient descent NMF. \n'
                  ' Proccessing time: {:.3f} seconds. \n'
                  ' Error: {} \n'
                  ' Parameter information:- \n'
                  '     -rank: {} \n'
                  '     -beta: {} \n'
                  ' Number of re-initialisations required: {}.'
                  ''.format((endcomplete-start), 
                            np.absolute(cost),
                            (r),
                            (KLNMF.beta),
                            (rep)))
                break
            
            if rep == KLNMF.repetitions:
                
                endbad = t.time()
                Wprime, Hprime = 0,0
                print('Failed to optimise with achieved error: {:.3f}. \n'
                      ' Try increasing the error tolerance epsilon through the class method \n'
                      ' or increase the repitions of instantiation or iterations \n'
                      ' The parameters current values are: \n'
                      ' Epsilon: {} \n'
                      ' Repitions: {} \n'
                      ' Iterations: {} \n'
                      ' Time wasted: {:.3f} seconds'.format((np.absolute(cost)),
                                                             (KLNMF.epsilon),
                                                             (KLNMF.repetitions),
                                                             (KLNMF.iterations),
                                                             (endbad-start)))
                break
            
            
        return Wprime, Hprime, cost 
    
    


    
