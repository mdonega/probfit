import unittest
from dist_fit import *
import numpy as np
from numpy.random import randn
from math import sqrt
class TestOneshot(unittest.TestCase):
    
    def setUp(self):
        self.ndata = 20000
        self.data = randn(self.ndata)*2. + 5.
        self.wdown = np.empty(self.ndata)
        self.wdown.fill(0.1)
        
        self.ndata_small = 2000
        self.data_small = randn(self.ndata_small)*2. + 5.

    def test_binx2(self):
        egauss = Extend(gaussian)
        fit,m = fit_binx2(egauss,self.data,bins=100, range=(1.,9.), quiet=True, mean=4., sigma=1.,N=10000.,printlevel=-1)
        self.assertAlmostEqual(m.values['mean'],5.,delta=3*m.errors['mean'])
        self.assertAlmostEqual(m.values['sigma'],2.,delta=3*m.errors['sigma'])
    
    def test_binlh(self):
        ngauss=Normalize(gaussian,(1.,9.))
        fit,m = fit_binlh(ngauss,self.data,bins=1000, range=(1.,9.), quiet=True, mean=4., sigma=1.5,printlevel=-1,f_verbose=False)
        self.assertAlmostEqual(m.values['mean'],5.,delta=3*m.errors['mean'])
        self.assertAlmostEqual(m.values['sigma'],2.,delta=3*m.errors['sigma'])
    
    def test_extended_binlh(self):
        egauss = Extend(gaussian)
        fit,m = fit_binlh(egauss,self.data,bins=1000, range=(1.,9.), quiet=True, 
            mean=4., sigma=1.,N=10000.,
            printlevel=-1,f_verbose=False, extended=True)
        self.assertAlmostEqual(m.values['mean'],5.,delta=3*m.errors['mean'])
        self.assertAlmostEqual(m.values['sigma'],2.,delta=3*m.errors['sigma'])
        self.assertAlmostEqual(m.values['N'],20000,delta=3*m.errors['N'])
    
    def test_extended_binlh_ww(self):
        egauss = Extend(gaussian)
        fit,m = fit_binlh(egauss,self.data,bins=1000, range=(1.,9.), quiet=True, 
            mean=4., sigma=1.,N=1000., weights=self.wdown,
            printlevel=-1,f_verbose=False, extended=True)
        self.assertAlmostEqual(m.values['mean'],5.,delta=3*m.errors['mean'])
        self.assertAlmostEqual(m.values['sigma'],2.,delta=3*m.errors['sigma'])
        self.assertAlmostEqual(m.values['N'],2000,delta=3*m.errors['N'])
    
    def test_extended_binlh_ww_w2(self):
        egauss = Extend(gaussian)
        fit,m = fit_binlh(egauss,self.data,bins=1000, range=(1.,9.), quiet=True, 
            mean=4., sigma=1.,N=1000., weights=self.wdown,
            printlevel=-1,f_verbose=False, extended=True)
        self.assertAlmostEqual(m.values['mean'],5.,delta=3*m.errors['mean'])
        self.assertAlmostEqual(m.values['sigma'],2.,delta=3*m.errors['sigma'])
        self.assertAlmostEqual(m.values['N'],2000,delta=3*m.errors['N'])
        
        fit2,m2 = fit_binlh(egauss,self.data,bins=1000, range=(1.,9.), quiet=True, 
            mean=4., sigma=1.,N=1000., weights=self.wdown,
            printlevel=-1,f_verbose=False, extended=True,use_w2=True)
        #self.assertAlmostEqual(m2.values['mean'],5.,delta=3*m2.errors['mean'])
        self.assertAlmostEqual(m2.values['sigma'],2.,delta=3*m2.errors['sigma'])
        self.assertAlmostEqual(m2.values['N'],2000.,delta=3*m2.errors['N'])
        m.minos()
        m2.minos()
        
        #now error should scale correctly
        self.assertAlmostEqual(m.errors['mean']/sqrt(10),m2.errors['mean'],delta = m.errors['mean']/sqrt(10))
        self.assertAlmostEqual(m.errors['sigma']/sqrt(10),m2.errors['sigma'],delta = m.errors['sigma']/sqrt(10))
        self.assertAlmostEqual(m.errors['N']/sqrt(10),m2.errors['N'],delta = m.errors['N']/sqrt(10))

    def test_uml(self):
        fit,m = fit_uml(gaussian,self.data, quiet=True, mean=4.5, sigma=1.5,printlevel=-1)
        self.assertAlmostEqual(m.values['mean'],5.,delta=3*m.errors['mean'])
        self.assertAlmostEqual(m.values['sigma'],2.,delta=3*m.errors['sigma'])

if __name__ == '__main__':
    unittest.main()