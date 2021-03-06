# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# probfit Basic Tutorial

# <markdowncell>

# [probfit](http://iminuit.github.io/probfit/) is a modeling / fitting package to be used together with [iminuit](http://iminuit.github.com/iminuit/).
# 
# This tutorial is a fast-paced introduction to the probfit features:
# 
# * built-in common models: polynomial, gaussian, ...
# * build-in common fit statistics: chi^2, binned and unbinned likelihood
# * tools to get your fits to converge and check the results: try_uml, draw, draw_residuals, ...
# * tools to help you implement your own models and fit statistics: Normalize, Extended, integrate_1d, ...
# 
# Please start this notebook with the ``ipython --pylab=inline`` option to get inline plots.

# <codecell>

# We assume you have executed this cell in all the following examples
import numpy as np
import matplotlib.pyplot as plt
import iminuit
import probfit

# <markdowncell>

# In your own code you can explicitly import what you need to save
# typing in interactive sessions, e.g.
# 
#     from iminuit import Minuit, describe
#     from probfit import gaussian, BinnedLH
# 
# We don't do this here, we only import `iminuit` and `probfit` into our
# namespace so that it is clear to you which functions and classes come
# from which package while reading the code below.

# <markdowncell>

# ## Chi^2 straight line fit
# 
# We can't really call this a fitting package without being able to fit a straight line, right?

# <codecell>

# Let's make a straight line with gaussian(mu=0, sigma=1) noise
np.random.seed(0)
x = np.linspace(0, 10, 20) 
y = 3 * x + 15 + np.random.randn(len(x))
err = np.ones(len(x))
plt.errorbar(x, y, err, fmt='.');

# <codecell>

# Let's define our line.
# First argument has to be the independent variable,
# arguments after that are shape parameters.
def line(x, m, c): # define it to be parabolic or whatever you like
    return m * x + c

# <codecell>

iminuit.describe(line)

# <codecell>

# Define a chi^2 cost function
chi2 = probfit.Chi2Regression(line, x, y, err)

# <codecell>

# Chi2Regression is just a callable object; nothing special about it
iminuit.describe(chi2)

# <codecell>

# minimize it
# yes, it gives you a heads up that you didn't give it initial value
# we can ignore it for now
minuit = iminuit.Minuit(chi2) # see iminuit tutorial on how to give initial value/range/error
minuit.migrad(); # MIGRAD is a very stable robust minimization method
# you can look at your terminal to see what it is doing;

# <codecell>

# The output above is a pretty-printed summary of the fit results from
# minuit.print_fmin()
# which was automatically called by iminuit.Minuit.migrad() after running MIGRAD.

# Let's see our results as Python dictionaries ...
print(minuit.values)
print(minuit.errors)

# <markdowncell>

# #### Parabolic error
# is calculated using the second derivative at the minimum
# This is good in most cases where the uncertainty is symmetric not much correlation
# exists. Migrad usually got this accurately but if you want ot be sure
# call `minuit.hesse()` after calling `minuit.migrad()`.
# 
# #### Minos Error
# is obtained by scanning the chi^2 or likelihood profile and find the point
# where chi^2 is increased by `minuit.errordef`. Note that in the Minuit documentation
# and output `errordef` is often called `up` ... it's the same thing.
# 
# #### What `errordef` should I use?
# 
# As explained in the Minuit documentation you should use:
# 
# * `errordef = 1` for chi^2 fits
# * `errordef = 0.5` for likelihood fits
# 
# `errordef=1` is the default, so you only have to set it to `errordef=0.5`
# if you are defining a likelihood cost function (if you don't your HESSE and MINOS errors will be incorrect).
# `probfit` helps you by defining a `default_errordef()` attribute on the
# cost function classes, which is automatically detected by the `Minuit` constructor
# and can be used to set `Minuit.errordef` correctly, so that users can't forget.
# Classes used in this tutorial:
# 
# * `probfit.Chi2Regression.get_errordef()` and `probfit.BinnedChi2.get_errordef()` return 1.
# * `probfit.BinnedLH.get_errordef()` and `probfit.UnbinnedLH.get_errordef()` return 0.5.

# <codecell>

# Let's visualize our line
chi2.draw(minuit)
# looks good;

# <codecell>

# Sometimes we want the error matrix (a.k.a. covariance matrix)
print('error matrix:')
print(minuit.matrix())
# or the correlation matrix
print('correlation matrix:')
print(minuit.matrix(correlation=True))
# or a pretty html representation
# Note that `print_matrix()` shows the correlation matrix, not the error matrix
minuit.print_matrix()

# <markdowncell>

# ## Binned Poisson likelihood fit of a Gaussian distribution
# In high energy physics, we usually want to fit a distribution to a histogram. Let's look at simple Gaussian distribution.

# <codecell>

# First let's make some example data
np.random.seed(0)
data = np.random.randn(10000) * 4 + 1
# sigma = 4 and mean = 1
plt.hist(data, bins=100, histtype='step');

# <codecell>

# Define your PDF / model
def gauss_pdf(x, mu, sigma):
    """Normalized Gaussian"""
    return 1 / np.sqrt(2 * np.pi) / sigma * np.exp(-(x - mu) ** 2 / 2. / sigma ** 2)

# <codecell>

# Build your cost function
# Here we use binned likelihood
binned_likelihood = probfit.BinnedLH(gauss_pdf, data)

# <codecell>

# Create the minuit
# and give an initial value for the sigma parameter
minuit = iminuit.Minuit(binned_likelihood, sigma=3)
# Remember: minuit.errordef is automatically set to 0.5
# as required for likelihood fits (this was explained above)
binned_likelihood.draw(minuit);

# <codecell>

minuit.migrad()
# Like in all binned fit with long zero tail. It will have to do something about the zero bin
# probfit.BinnedLH does handle them gracefully but will give you a warning;

# <codecell>

# Visually check if the fit succeeded by plotting the model over the data
binned_likelihood.draw(minuit) # uncertainty is given by symmetric Poisson;

# <codecell>

# Let's see the result
print('Value: {}'.format(minuit.values))
print('Error: {}'.format(minuit.errors))

# <codecell>

# That printout can get out of hand quickly
minuit.print_fmin()
# Also print the correlation matrix
minuit.print_matrix()

# <codecell>

# Looking at a likelihood profile is a good method
# to check that the reported errors make sense
minuit.draw_mnprofile('mu');

# <codecell>

# Plot a 2d contour error
# You can notice that it takes some time to draw
# We will this is because our PDF is defined in Python
# We will show how to speed this up later
minuit.draw_mncontour('mu', 'sigma');

# <markdowncell>

# ## Chi^2 fit of a Gaussian distribution
# 
# Let's explore another popular cost function chi^2.
# Chi^2 is bad when you have bin with 0.
# ROOT just ignore.
# ROOFIT does something I don't remember.
# But it's best to avoid using chi^2 when you have bin with 0 count.

# <codecell>

# We will use the same data as in the previous example
np.random.seed(0)
data = np.random.randn(10000) * 4 + 1
# sigma = 4 and mean = 1
plt.hist(data, bins=100, histtype='step');

# <codecell>

# We will use the same PDF as in the previous example
def gauss_pdf(x, mu, sigma):
    """Normalized Gaussian"""
    return 1 / np.sqrt(2 * np.pi) / sigma * np.exp(-(x - mu) **2 / 2. / sigma ** 2)

# <codecell>

# Binned chi^2 fit only makes sense (for now) for extended PDFs
# probfit.Extended adds a norm parameter with name 'N'
extended_gauss_pdf = probfit.Extended(gauss_pdf)

# <codecell>

# Describe the function signature
iminuit.describe(extended_gauss_pdf)

# <codecell>

# Chi^2 distribution fit is really bad for distribution with long tail
# since when bin count=0... poisson error=0 and blows up chi^2
# so give it some range
chi2 = probfit.BinnedChi2(extended_gauss_pdf, data, bound=(-7,10))
# This time we use the pedantic=False option to tell Minuit
# that we don't want warnings about parameters without initial
# value or step size.
# And print_level=0 means that no output is generated
minuit = iminuit.Minuit(chi2, sigma=1, pedantic=False, print_level=0)
minuit.migrad();

# <codecell>

# Now let's look at the results
minuit.print_fmin()
minuit.print_matrix()
chi2.draw(minuit);

# <markdowncell>

# ## Fast unbinned likelihood fit Cython
# 
# Unbinned likelihood is computationally very very expensive if you have a lot of data.
# It's now a good time that we talk about how to speed things up with [Cython](http://cython.org).

# <codecell>

# We will use the same data as in the previous example
np.random.seed(0)
data = np.random.randn(10000) * 4 + 1
# sigma = 4 and mean = 1
plt.hist(data, bins=100, histtype='step');

# <codecell>

# We want to speed things up with Cython
%load_ext cythonmagic

# <codecell>

%%cython
# Same gaussian distribution but now written in Cython
# The %%cython IPython does the following:
# * Call Cython to generate C code for a Python C extension.
# * Compile it into a Python C extension (a shared library)
# * Load it into the current namespace
# If you don't understand these things, don't worry, it basically means:
# * Get full-metal speed easily
cimport cython
from libc.math cimport exp, M_PI, sqrt
@cython.binding(True) # IMPORTANT: this tells Cython to dump the function signature
def gauss_pdf_cython(double x, double mu, double sigma):
    return 1 / sqrt(2 * M_PI) / sigma * exp(-(x - mu) ** 2 / 2. / sigma ** 2)

# <codecell>

# Define the unbinned likelihood cost function 
unbinned_likelihood = probfit.UnbinnedLH(gauss_pdf_cython, data)

# <codecell>

minuit = iminuit.Minuit(unbinned_likelihood, sigma=2, pedantic=False, print_level=0)
# Remember: minuit.errordef is automatically set to 0.5
# as required for likelihood fits (this was explained above)
minuit.migrad() # yes: amazingly fast
unbinned_likelihood.show(minuit)
minuit.print_fmin()
minuit.print_matrix() 

# <codecell>

# Remember how slow draw_mnprofile() was in the last example?
# Now it's super fast (even though the unbinned
# likelihood computation is more compute-intensive).
minuit.draw_mnprofile('mu');

# <markdowncell>

# But you really don't have to write your own gaussian, there are tons of builtin functions written in Cython for you.

# <codecell>

# Here's how you can list them
import probfit.pdf
print(dir(probfit.pdf))
print(iminuit.describe(probfit.pdf.gaussian))
print(type(probfit.pdf.gaussian))
# But actually they are always all imported into the main probfit
# namespace, so we'll keep using the simpler probfit.gaussian instead of
# probfit.pdf.gaussian here.

# <codecell>

unbinned_likelihood = probfit.UnbinnedLH(probfit.gaussian, data)
minuit = iminuit.Minuit(unbinned_likelihood, sigma=2, pedantic=False)
# Remember: minuit.errordef is automatically set to 0.5
# as required for likelihood fits (this was explained above)
minuit.migrad() # yes: amazingly fast
unbinned_likelihood.draw(minuit, show_errbars='normal') # control how fit is displayed too;

# <codecell>

# Draw the difference between data and PDF
plt.figure(figsize=(13,4))
plt.subplot(121)
unbinned_likelihood.draw_residual(minuit)
plt.subplot(122)
unbinned_likelihood.draw_residual(minuit, show_errbars=True, errbar_algo='sumw2', norm=True)

# <markdowncell>

# ##But... We can't normalize everything analytically and how to generate toy sample from PDF
# 
# When fitting distribution to a PDF, one of the common problem that we run into is normalization.
# Not all function is analytically integrable on the range of our interest.
# 
# Let's look at an example: the [Crystal Ball function](http://en.wikipedia.org/wiki/Crystal_Ball_function).
# It's simply a gaussian with a power law tail ... normally found in energy deposited in crystals ...
# impossible to normalize analytically and normalization will depend on shape parameters.

# <codecell>

numpy.random.seed(0)
bound = (-1, 2)
data = probfit.gen_toy(probfit.crystalball, 10000, bound=bound, alpha=1., n=2., mean=1., sigma=0.3, quiet=False)
# quiet=False tells gen_toy to plot out original function
# toy histogram and poisson error from both orignal distribution and toy

# <codecell>

# To fit this function as a distribution we need to normalize
# so that is becomes a PDF ober the range we consider here.
# We do this with the probfit.Normalized functor, which implements
# the trapezoid numerical integration method with a simple cache mechanism
normalized_crystalball = probfit.Normalized(probfit.crystalball, bound)
# this can also bedone with decorator
# @probfit.normalized(bound)
# def my_function(x, blah):
#    return something
pars = 1.0, 1, 2, 1, 0.3
print('function: {}'.format(probfit.crystalball(*pars)))
print('     pdf: {}'.format(normalized_crystalball(*pars)))

# <codecell>

# The normalized version has the same signature as the non-normalized version
print(iminuit.describe(probfit.crystalball))
print(iminuit.describe(normalized_crystalball))

# <codecell>

# We can fit the normalized function in the usual way ...
unbinned_likelihood = probfit.UnbinnedLH(normalized_crystalball, data)
start_pars = dict(alpha=1, n=2.1, mean=1.2, sigma=0.3)
minuit = iminuit.Minuit(unbinned_likelihood, **start_pars)
# Remember: minuit.errordef is automatically set to 0.5
# as required for likelihood fits (this was explained above)
minuit.migrad() # yes: amazingly fast Normalize is written in Cython
unbinned_likelihood.show(minuit)
# The Crystal Ball function is notorious for its sensitivity on the 'n' parameter
# probfit give you a heads up where it might have float overflow;

# <markdowncell>

# ## But what if I know the analytical integral formula for my distribution?
# 
# `probfit` checks for a method called `integrate` with the signature `integrate(bound, nint, *arg)` to
# compute definite integrals for given `bound` and `nint` (pieces of integral this is normally ignored)
# and the rest will be passed as positional argument.
# 
# For some `probfit` built-in distributions analytical formulae have been implemented.

# <codecell>

def line(x, m, c):
    return m * x + c

# compute integral of line from x=(0,1) using 10 intevals with m=1. and c=2.
# all probfit internal use this
# no integrate method available probfit use simpson3/8
print(probfit.integrate1d(line, (0, 1), 10, (1., 2.)))

# Let us illustrate the point by forcing it to have integral that's off by
# factor of two
def wrong_line_integrate(bound, nint, m, c):
    a, b = bound
    # I know this is wrong:
    return 2 * (m * (b ** 2 / 2. - a ** 2 / 2.) + c * (b - a))

line.integrate = wrong_line_integrate
# line.integrate = lambda bound, nint, m, c: blah blah # this works too
print(probfit.integrate1d(line, (0, 1), 10, (1., 2.)))

# <headingcell level=2>

# What if things go wrong?

# <markdowncell>

# In this section we show you what happens when your distribution doesn't fit and how you can make it.
# 
# We again use the Crystal Ball distribution as an example, which is notoriously sensitive to initial parameter values.

# <codecell>

unbinned_likelihood = probfit.UnbinnedLH(normalized_crystalball, data)
# No initial values given -> all parameters have default initial value 0
minuit = iminuit.Minuit(unbinned_likelihood)
# Remember: minuit.errordef is automatically set to 0.5
# as required for likelihood fits (this was explained above)
minuit.migrad() # yes: amazingly fast but tons of output on the console
# Remember there is a heads up;

# <codecell>

# This shows that we failed.
# The parameters are still at the default initial values
unbinned_likelihood.show(minuit);

# <codecell>

# These two status flags tell you if the best-fit parameter values
# and the covariance matrix (the parameter errors) are OK.
print(minuit.migrad_ok())
print(minuit.matrix_accurate())

# <markdowncell>

# To make MIGRAD converge we need start parameter values that are roughly correct. Remember that above the same fit converged when we used ::
# 
#     start_pars = dict(alpha=1, n=2.1, mean=1.2, sigma=0.3)
#     minuit = iminuit.Minuit(unbinned_likelihood, **start_pars)
#     
# #### But how can we guess these initial values?
# 
# This is a hard question that doesn't have one simple answer. Visualizing your data and model helps.

# <codecell>

# Try one set of parameters
best_try = probfit.try_uml(normalized_crystalball, data, alpha=1., n=2.1, mean=1.2, sigma=0.3)
print(best_try)

# <codecell>

# Or try multiple sets of parameters
# (too many will just confuse you)
best_try = probfit.try_uml(normalized_crystalball, data, alpha=1., n=2.1, mean=[1.2, 1.1], sigma=[0.3, 0.5])
# try_uml computes the unbinned likelihood for each set of parameters and returns the best
# one as a dictionary.
# This is actually a poor-man's optimization algorithm in itself called grid search
# which is popular to find good start values for other, faster optimization methods like MIGRAD.
print(best_try)

# <headingcell level=2>

# Extended fit: two Gaussians with polynomial background

# <markdowncell>

# Here we show how to create and fit a model that is the sum of several other models.

# <codecell>

# Generate some example data
np.random.seed(0)
data_peak1 = np.random.randn(3000) * 0.2 + 2
data_peak2 = np.random.randn(5000) * 0.1 + 4
data_range = (-2, 5)
data_bg = probfit.gen_toy(lambda x : 4 + 4 * x + x ** 2, 20000, data_range)
data_all = np.concatenate([data_peak1, data_peak2, data_bg])
plt.hist((data_peak1, data_peak2, data_bg, data_all),
         label=['Signal 1', 'Signal 2', 'Background', 'Total'],
         bins=200, histtype='step', range=data_range)
plt.legend(loc='upper left');

# <codecell>

# Using a polynomial to fit a distribution is problematic, because the
# polynomial can assume negative values, which results in NaN (not a number)
# values in the likelihood function.
# To avoid this problem we restrict the fit to the range (0, 5) where
# the polynomial is clearly positive.
fit_range = (0, 5)
normalized_poly = probfit.Normalized(probfit.Polynomial(2), fit_range)
normalized_poly = probfit.Extended(normalized_poly, extname='NBkg')

gauss1 = probfit.Extended(probfit.rename(probfit.gaussian, ['x', 'mu1', 'sigma1']), extname='N1')
gauss2 = probfit.Extended(probfit.rename(probfit.gaussian, ['x', 'mu2', 'sigma2']), extname='N2')

# Define an extended PDF consisting of three components
pdf = probfit.AddPdf(normalized_poly, gauss1, gauss2)

print('normalized_poly: {}'.format(probfit.describe(normalized_poly)))
print('gauss1:          {}'.format(probfit.describe(gauss1)))
print('gauss2:          {}'.format(probfit.describe(gauss2)))
print('pdf:             {}'.format(probfit.describe(pdf)))

# <codecell>

# Define the cost function in the usual way ...
binned_likelihood = probfit.BinnedLH(pdf, data_all, bins=200, extended=True, bound=fit_range)

# This is a quite complex fit (11 free parameters!), so we need good starting values.
# Actually we even need to set an initial parameter error
# for 'mu1' and 'mu2' to make MIGRAD converge.
# The initial parameter error is used as the initial step size in the minimization.
pars = dict(mu1=1.9, error_mu1=0.1, sigma1=0.2, N1=3000,
            mu2=4.1, error_mu2=0.1, sigma2=0.1, N2=5000,
            c_0=4, c_1=4, c_2=1, NBkg=20000)
minuit = iminuit.Minuit(binned_likelihood, pedantic=False, print_level=0, **pars)
# You can see that the model already roughly matches the data
binned_likelihood.draw(minuit, parts=True);

# <codecell>

# This can take a while ... the likelihood is evaluated a few 100 times
# (and each time the distributions are evaluated, including the
# numerical computation of the normalizing integrals)
minuit.migrad();

# <codecell>

binned_likelihood.show(minuit, parts=True);
minuit.print_fmin()
minuit.print_matrix()

# <markdowncell>

# Note the red upper left corner in the correlation matrix above?
# 
# It shows that the three polynomial parameters `c_0`, `c_1` and `c_2` are highly correlated?
# The reason is that we put a constraint on the polynomial to be normalized over the fit range:
# 
#     fit_range = (0, 5)
#     normalized_poly = probfit.Normalized(probfit.Polynomial(2), fit_range)
#     normalized_poly = probfit.Extended(normalized_poly, extname='NBkg')
# 
# To resolve this problem you could simply use a non-normalized and non-extended polynomial to model the background. We won't do this here, though ...

# <markdowncell>

# ## Custom Drawing
# 
# The `draw()` and `show()` method we provide is intended to just give you a quick look at your fit.
# 
# To make a custom drawing you can use the return value of `draw()` and `show()`.

# <codecell>

# You should copy & paste the return tuple from the `draw` docstring ...
((data_edges, datay), (errorp, errorm), (total_pdf_x, total_pdf_y), parts) = binned_likelihood.draw(minuit, parts=True);
# ... now we have everything to make our own plot

# <codecell>

# Now make the plot as pretty as you like, e.g. with matplotlib.
plt.figure(figsize=(8, 5))
plt.errorbar(probfit.mid(data_edges), datay, errorp, fmt='.', capsize=0, color='Gray', label='Data')
plt.plot(total_pdf_x, total_pdf_y, color='blue', lw=2, label='Total Model')
colors = ['orange', 'purple', 'DarkGreen']
labels = ['Background', 'Signal 1', 'Signal 2']
for color, label, part in zip(colors, labels, parts):
    x, y = part
    plt.plot(x, y, ls='--', color=color, label=label)
plt.grid(True)
plt.legend(loc='upper left');

# <markdowncell>

# ## Simultaneous fit to several data sets
# 
# Sometimes, what we want to fit is the sum of likelihood /chi^2 of two PDFs for two different datasets that share some parameters.
# 
# In this example, we will fit two Gaussian distributions where we know that the widths are the same
# but the peaks are at different places.

# <codecell>

# Generate some example data
np.random.seed(0)
data1 = np.random.randn(10000) + 3 # mean =  3, sigma = 1
data2 = np.random.randn(10000) - 2 # mean = -2, sigma = 1
plt.figure(figsize=(12,4))
plt.subplot(121)
plt.hist(data1, bins=100, range=(-7, 7), histtype='step', label='data1')
plt.legend()
plt.subplot(122)
plt.hist(data2, bins=100, range=(-7, 7), histtype='step', label='data2')
plt.legend();

# <codecell>

# There is nothing special about built-in cost function
# except some utility function like draw and show
likelihood1 = probfit.UnbinnedLH(probfit.rename(probfit.gaussian, ('x', 'mean2', 'sigma')), data1)
likelihood2 = probfit.UnbinnedLH(probfit.gaussian, data2)
simultaneous_likelihood = probfit.SimultaneousFit(likelihood1, likelihood2)
print(probfit.describe(likelihood1))
print(probfit.describe(likelihood2))
# Note that the simultaneous likelihood has only 3 parameters, because the
# 'sigma' parameter is tied (i.e. linked to always be the same).
print(probfit.describe(simultaneous_likelihood))

# <codecell>

# Ah, the beauty of Minuit ... it doesn't care what your cost funtion is ...
# you can use it to fit (i.e. compute optimal parameters and parameter errors) anything.
minuit = iminuit.Minuit(simultaneous_likelihood, sigma=0.5, pedantic=False, print_level=0)
# Well, there's one thing we have to tell Minuit so that it can compute parameter errors,
# and that is the value of `errordef`, a.k.a. `up` (explained above).
# This is a likelihood fit, so we need `errordef = 0.5` and not the default `errordef = 1`:
minuit.errordef = 0.5

# <codecell>

# Run the fit and print the results
minuit.migrad();
minuit.print_fmin()
minuit.print_matrix()

# <codecell>

simultaneous_likelihood.draw(minuit);

# <markdowncell>

# ## Blinding parameters
# 
# Often, an analyst would like to avoid looking at the result of the fitted parameter(s) before he/she finalized the analysis in order to avoid biases due to the prejudice of the analyst. Probfit provids a transformation function that hides the true value(s) of the parameter(s). The transformation function requires a string to set the seed of the random number generator, and a scale to smear the parameter(s) using a Gaussian.

# <codecell>

from probfit import UnbinnedLH, BlindFunc, rename, AddPdfNorm
from probfit import gaussian
from iminuit import Minuit, describe
from probfit import gen_toy

# <codecell>

g0= rename(gaussian, ['x', 'm0', 's0'])
g1= rename(gaussian, ['x', 'm1', 's1'])
pdf= AddPdfNorm(g0,g1)
describe(pdf)

# <codecell>

seed(0)
toydata = gen_toy(pdf, 1000,(-10,10), m0=-2, m1=2, s0=1, s1=1, f_0=0.3, quiet=False)

# <codecell>

inipars= dict(m0=0, m1=0, s0=1, s1=1, f_0=0.5, error_m0=0.1, error_m1=0.1, error_s0=0.1, error_s1=0.1, error_f_0=0.1)

# <codecell>

# Normal fit
uh1= UnbinnedLH(pdf, toydata)
m1= Minuit(uh1, print_level=1, **inipars)
m1.migrad();
uh1.draw();
print m1.values

# <codecell>

# Blind one parameter
uh2= UnbinnedLH( BlindFunc(pdf, toblind='m1', seedstring='some_random_stuff', width=0.5, signflip=False), toydata)
m2= Minuit(uh2, print_level=1, **inipars)
m2.migrad();
uh2.draw();
print m2.values

# <codecell>

# Blind more than one parameter. They will be shifted by the same amount
uh3= UnbinnedLH( BlindFunc(pdf, ['m0','m1'], seedstring='some_random_stuff', width=0.5, signflip=False), toydata)
m3= Minuit(uh3, print_level=1, **inipars)
m3.migrad();
uh3.draw();
print m3.values

# <codecell>

print m1.values
print m2.values
print m3.values
print 
print m1.errors
print m2.errors
print m3.errors

# <codecell>

print m3.values['m0']-m1.values['m0']
print m3.values['m1']-m1.values['m1']

# <codecell>

# Now it's your turn ...
# try and apply probfit / iminuit and to your modeling / fitting task! 

