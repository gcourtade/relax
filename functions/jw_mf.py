###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


############################
# Spectral density values. #
############################

def create_jw_struct(data, calc_jw):
    """Function to create the model-free spectral density values.

    The spectral density equation
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Data structure:  data.jw
    Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
    Type:  Numeric matrix, Float64
    Dependencies:  None
    Required by:  data.ri, data.dri, data.d2ri


    Formulae
    ~~~~~~~~

    Original
    ~~~~~~~~

                 2    /      S2             (1 - S2)(te + tm)te    \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (te + tm)^2 + (w.te.tm)^2 /


    Extended
    ~~~~~~~~

                 2    /      S2            (1 - S2f)(tf + tm)tf          (S2f - S2)(ts + tm)ts   \ 
        J(w)  =  - tm | ------------  +  -------------------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


    Extended 2
    ~~~~~~~~~~

                 2    /   S2f . S2s        (1 - S2f)(tf + tm)tf         S2f(1 - S2s)(ts + tm)ts  \ 
        J(w)  =  - tm | ------------  +  -------------------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    data.jw = calc_jw(data)


# Original, no params and {tm}.
###############################

def calc_iso_jw(data):
    """Spectral density function.

    Calculate the isotropic spectral density value for the original model-free formula with no
    parameters.

    The formula is:

                 2 /      tm      \ 
        J(w)  =  - | ------------ |
                 5 \ 1 + (w.tm)^2 /
    """

    return data.two_fifths_tm * data.fact_tm


# Original {S2} and {tm, S2}.
#############################

def calc_iso_s2_jw(data):
    """Spectral density function.

    Calculate the isotropic spectral density value for the original model-free formula with the
    single parameter S2.

    The formula is:

                 2 /   S2 . tm    \ 
        J(w)  =  - | ------------ |
                 5 \ 1 + (w.tm)^2 /
    """

    return data.two_fifths_tm * (data.params[data.s2_index] * data.fact_tm)


# Original {S2, te} and {tm, S2, te}.
#####################################

def calc_iso_s2_te_jw(data):
    """Spectral density function.

    Calculate the isotropic spectral density value for the original model-free formula with the
    parameters S2 and te.

    The model-free formula is:

                 2    /      S2             (1 - S2)(te + tm)te    \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (te + tm)^2 + (w.te.tm)^2 /
    """

    return data.two_fifths_tm * (data.params[data.s2_index] * data.fact_tm + data.one_s2 * data.te_tm_te / data.te_denom)


# Extended {S2f, S2, ts}.
#########################

def calc_iso_s2f_s2_ts_jw(data):
    """Spectral density function.

    Calculate the isotropic spectral density value for the extended model-free formula with the
    parameters S2f, S2, and ts.

    The model-free formula is:

                 2    /      S2            (S2f - S2)(ts + tm)ts   \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.two_fifths_tm * (data.params[data.s2_index] * data.fact_tm + data.s2f_s2 * data.ts_tm_ts / data.ts_denom)


# Extended {S2f, tf, S2, ts}.
#############################

def calc_iso_s2f_tf_s2_ts_jw(data):
    """Spectral density function.

    Calculate the isotropic spectral density value for the extended model-free formula with the
    parameters S2f, tf, S2, and ts.

    The model-free formula is:

                 2    /      S2            (1 - S2f)(tf + tm)tf          (S2f - S2)(ts + tm)ts   \ 
        J(w)  =  - tm | ------------  +  -------------------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.two_fifths_tm * (data.params[data.s2_index] * data.fact_tm + data.one_s2f * data.tf_tm_tf / data.tf_denom + data.s2f_s2 * data.ts_tm_ts / data.ts_denom)


# Extended 2 {S2f, S2s, ts}.
############################

def calc_iso_s2f_s2s_ts_jw(data):
    """Spectral density function.

    Calculate the isotropic spectral density value for the extended model-free formula with the
    parameters S2f, S2s, and ts.

    The model-free formula is:

                 2    /   S2f . S2s       S2f(1 - S2s)(ts + tm)ts  \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.two_fifths_tm * (data.params[data.s2f_index] * data.params[data.s2s_index] * data.fact_tm + data.s2f_s2 * data.ts_tm_ts / data.ts_denom)


# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_iso_s2f_tf_s2s_ts_jw(data):
    """Spectral density function.

    Calculate the isotropic spectral density value for the extended model-free formula with the
    parameters S2f, tf, S2s, and ts.

    The model-free formula is:

                 2    /   S2f . S2s        (1 - S2f)(tf + tm)tf         S2f(1 - S2s)(ts + tm)ts  \ 
        J(w)  =  - tm | ------------  +  -------------------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.two_fifths_tm * (data.params[data.s2f_index] * data.params[data.s2s_index] * data.fact_tm + data.one_s2f * data.tf_tm_tf / data.tf_denom + data.s2f_s2 * data.ts_tm_ts / data.ts_denom)



###############################
# Spectral density gradients. #
###############################

def create_djw_struct(data, calc_djw):
    """Function to create model-free spectral density gradients.

    The spectral density gradients
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Data structure:  data.djw
    Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies,
        model-free parameters)
    Type:  Numeric 3D matrix, Float64
    Dependencies:  None
    Required by:  data.dri, data.d2ri


    Formulae
    ~~~~~~~~

    Original
    ~~~~~~~~

        dJ(w)     2    /      1                 (te + tm).te        \ 
        -----  =  - tm | ------------  -  ------------------------- |
         dS2      5    \ 1 + (w.tm)^2     (te + tm)^2 + (w.te.tm)^2 /


        dJ(w)     2                   (te + tm)^2 - (w.te.tm)^2
        -----  =  - tm^2 . (1 - S2) -----------------------------
         dte      5                 ((te + tm)^2 + (w.te.tm)^2)^2


        dJ(w)
        -----  =  0
        dRex


        dJ(w)
        -----  =  0
        dcsa


        dJ(w)
        -----  =  0
         dr


    Extended
    ~~~~~~~~

        dJ(w)       2    /       (tf + tm).tf                  (ts + tm).ts        \ 
        -----  =  - - tm | -------------------------  -  ------------------------- |
        dS2f        5    \ (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


        dJ(w)     2    /      1                 (ts + tm).ts        \ 
        -----  =  - tm | ------------  -  ------------------------- |
         dS2      5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


        dJ(w)     2                    (tf + tm)^2 - (w.tf.tm)^2
        -----  =  - tm^2 . (1 - S2f) -----------------------------
         dtf      5                  ((tf + tm)^2 + (w.tf.tm)^2)^2


        dJ(w)     2                     (ts + tm)^2 - (w.ts.tm)^2
        -----  =  - tm^2 . (S2f - S2) -----------------------------
         dts      5                   ((ts + tm)^2 + (w.ts.tm)^2)^2


        dJ(w)
        -----  =  0
        dRex


        dJ(w)
        -----  =  0
        dcsa


        dJ(w)
        -----  =  0
         dr


    Extended 2
    ~~~~~~~~~~

        dJ(w)     2    /     S2s                (tf + tm).tf              (1 - S2s)(ts + tm).ts   \ 
        -----  =  - tm | ------------  -  -------------------------  +  ------------------------- |
        dS2f      5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


        dJ(w)     2        /      1                 (ts + tm).ts        \ 
        -----  =  - tm.S2f | ------------  -  ------------------------- |
        dS2s      5        \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


        dJ(w)     2                    (tf + tm)^2 - (w.tf.tm)^2
        -----  =  - tm^2 . (1 - S2f) -----------------------------
         dtf      5                  ((tf + tm)^2 + (w.tf.tm)^2)^2


        dJ(w)     2                       (ts + tm)^2 - (w.ts.tm)^2
        -----  =  - tm^2 . S2f(1 - S2s) -----------------------------
         dts      5                     ((ts + tm)^2 + (w.ts.tm)^2)^2


        dJ(w)
        -----  =  0
        dRex


        dJ(w)
        -----  =  0
        dcsa


        dJ(w)
        -----  =  0
         dr
    """

    for j in range(len(data.params)):
        if calc_djw[j]:
            data.djw[:, :, j] = calc_djw[j](data)


# Original {S2}.
################

def calc_iso_S2_djw_dS2(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the S2 partial derivative of the original
    model-free formula with the single parameter S2.

    The model-free gradient is:

        dJ(w)     2    /      1       \ 
        -----  =  - tm | ------------ |
         dS2      5    \ 1 + (w.tm)^2 /
    """

    return data.two_fifths_tm * data.fact_tm


# Original {S2, te}.
####################

def calc_iso_S2_te_djw_dS2(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the S2 partial derivative of the original
    model-free formula with the parameters S2 and te.

    The model-free gradient is:

        dJ(w)     2    /      1                 (te + tm).te        \ 
        -----  =  - tm | ------------  -  ------------------------- |
         dS2      5    \ 1 + (w.tm)^2     (te + tm)^2 + (w.te.tm)^2 /
    """

    return data.two_fifths_tm * (data.fact_tm - data.te_tm_te / data.te_denom)


def calc_iso_S2_te_djw_dte(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the te partial derivative of the original
    model-free formula with the parameters S2 and te.

    The model-free gradient is:

        dJ(w)     2                   (te + tm)^2 - (w.te.tm)^2
        -----  =  - tm^2 . (1 - S2) -----------------------------
         dte      5                 ((te + tm)^2 + (w.te.tm)^2)^2
    """

    return data.fact_djw_dte * data.one_s2



# Extended {S2f, S2, ts}.
#########################

def calc_iso_S2f_S2_ts_djw_dS2f(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the S2f partial derivative of the extended
    model-free formula with the parameters S2f, S2 and ts.

    The formula is:

        dJ(w)     2    /       (ts + tm).ts        \ 
        -----  =  - tm | ------------------------- |
        dS2f      5    \ (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.two_fifths_tm * data.ts_tm_ts / data.ts_denom


def calc_iso_S2f_S2_ts_djw_dS2(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the S2 partial derivative of the extended
    model-free formula with the parameters S2f, S2 and ts.

    The formula is:

        dJ(w)     2    /      1                 (ts + tm).ts        \ 
        -----  =  - tm | ------------  -  ------------------------- |
         dS2      5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.fact_djw_ds2


def calc_iso_S2f_S2_ts_djw_dts(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the ts partial derivative of the extended
    model-free formula with the parameters S2f, S2 and ts.

    The formula is:

        dJ(w)     2                     (ts + tm)^2 - (w.ts.tm)^2
        -----  =  - tm^2 . (S2f - S2) -----------------------------
         dts      5                   ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return data.fact_djw_dts * data.s2f_s2



# Extended {S2f, tf, S2, ts}.
#############################

def calc_iso_S2f_tf_S2_ts_djw_dS2f(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the S2f partial derivative of the extended
    model-free formula with the parameters S2f, tf, S2 and ts.

    The formula is:

        dJ(w)       2    /       (tf + tm).tf                  (ts + tm).ts        \ 
        -----  =  - - tm | -------------------------  -  ------------------------- |
        dS2f        5    \ (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return - data.two_fifths_tm * (data.tf_tm_tf / data.tf_denom - data.ts_tm_ts / data.ts_denom)


def calc_iso_S2f_tf_S2_ts_djw_dS2(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the S2 partial derivative of the extended
    model-free formula with the parameters S2f, tf, S2 and ts.

    The formula is:

        dJ(w)     2    /      1                 (ts + tm).ts        \ 
        -----  =  - tm | ------------  -  ------------------------- |
         dS2      5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.fact_djw_ds2


def calc_iso_S2f_tf_S2_ts_djw_dtf(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the tf partial derivative of the extended
    model-free formula with the parameters S2f, tf, S2 and ts.

    The formula is:

        dJ(w)     2                    (tf + tm)^2 - (w.tf.tm)^2
        -----  =  - tm^2 . (1 - S2f) -----------------------------
         dtf      5                  ((tf + tm)^2 + (w.tf.tm)^2)^2
    """

    return data.fact_djw_dtf * data.one_s2f


def calc_iso_S2f_tf_S2_ts_djw_dts(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the ts partial derivative of the extended
    model-free formula with the parameters S2f, S2 and ts.

    The formula is:

        dJ(w)     2                     (ts + tm)^2 - (w.ts.tm)^2
        -----  =  - tm^2 . (S2f - S2) -----------------------------
         dts      5                   ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return data.fact_djw_dts * data.s2f_s2


# Extended 2 {S2f, S2s, ts}.
############################

def calc_iso_S2f_S2s_ts_djw_dS2f(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the S2f partial derivative of the extended
    model-free formula with the parameters S2f, S2s and ts.

    The formula is:

        dJ(w)     2    /     S2s            (1 - S2s)(ts + tm).ts   \ 
        -----  =  - tm | ------------  +  ------------------------- |
        dS2f      5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.two_fifths_tm * (data.params[data.s2s_index] * data.fact_tm + data.one_s2s * data.ts_tm_ts / data.ts_denom)


def calc_iso_S2f_S2s_ts_djw_dS2s(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the S2s partial derivative of the extended
    model-free formula with the parameters S2f, S2s and ts.

    The formula is:

        dJ(w)     2        /      1                 (ts + tm).ts        \ 
        -----  =  - tm.S2f | ------------  -  ------------------------- |
        dS2s      5        \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.fact_djw_ds2s * data.params[data.s2f_index]


def calc_iso_S2f_S2s_ts_djw_dts(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the ts partial derivative of the extended
    model-free formula with the parameters S2f, S2s and ts.

    The formula is:

        dJ(w)     2                       (ts + tm)^2 - (w.ts.tm)^2
        -----  =  - tm^2 . S2f(1 - S2s) -----------------------------
         dts      5                     ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return data.fact_djw_dts * data.s2f_s2



# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_iso_S2f_tf_S2s_ts_djw_dS2f(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the S2f partial derivative of the extended
    model-free formula with the parameters S2f, tf, S2s and ts.

    The formula is:

        dJ(w)     2    /     S2s                (tf + tm).tf              (1 - S2s)(ts + tm).ts   \ 
        -----  =  - tm | ------------  -  -------------------------  +  ------------------------- |
        dS2f      5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.two_fifths_tm * (data.params[data.s2s_index] * data.fact_tm - data.tf_tm_tf / data.tf_denom + data.one_s2s * data.ts_tm_ts / data.ts_denom)


def calc_iso_S2f_tf_S2s_ts_djw_dS2s(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the S2s partial derivative of the extended
    model-free formula with the parameters S2f, tf, S2s and ts.

    The formula is:

        dJ(w)     2        /      1                 (ts + tm).ts        \ 
        -----  =  - tm.S2f | ------------  -  ------------------------- |
        dS2s      5        \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.fact_djw_ds2s * data.params[data.s2f_index]


def calc_iso_S2f_tf_S2s_ts_djw_dtf(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the tf partial derivative of the extended
    model-free formula with the parameters S2f, tf, S2s and ts.

    The formula is:

        dJ(w)     2                    (tf + tm)^2 - (w.tf.tm)^2
        -----  =  - tm^2 . (1 - S2f) -----------------------------
         dtf      5                  ((tf + tm)^2 + (w.tf.tm)^2)^2
    """

    return data.fact_djw_dtf * data.one_s2f


def calc_iso_S2f_tf_S2s_ts_djw_dts(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity value for the ts partial derivative of the extended
    model-free formula with the parameters S2f, S2s and ts.

    The formula is:

        dJ(w)     2                       (ts + tm)^2 - (w.ts.tm)^2
        -----  =  - tm^2 . S2f(1 - S2s) -----------------------------
         dts      5                     ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return data.fact_djw_dts * data.s2f_s2



##############################
# Spectral density Hessians. #
##############################

def create_d2jw_struct(data, calc_d2jw):
    """Function to create model-free spectral density Hessians.

    The spectral density Hessians
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Data structure:  data.d2jw
    Dimension:  4D, (number of NMR frequencies, 5 spectral density frequencies, model-free
        parameters, model-free parameters)
    Type:  Numeric 4D matrix, Float64
    Dependencies:  None
    Required by:  data.d2ri


    Formulae
    ~~~~~~~~

    Original:  Model-free parameter - Model-free parameter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        d2J(w)
        ------  =  0
        dS2**2


         d2J(w)       2        (te + tm)^2 - (w.te.tm)^2
        -------  =  - - tm^2 -----------------------------
        dS2.dte       5      ((te + tm)^2 + (w.te.tm)^2)^2


        d2J(w)       4                 (te + tm)^3 + 3.tm^3.te.w^2.(te + tm) - (w.tm)^4.te^3
        ------  =  - - tm^2 . (1 - S2) -----------------------------------------------------
        dte**2       5                             ((te + tm)^2 + (w.te.tm)^2)^3


    Original:  Other parameters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dS2.dRex             dS2.dcsa             dS2.dr


         d2J(w)              d2J(w)               d2J(w)
        --------  =  0   ,  --------  =  0   ,    ------  =  0
        dte.dRex            dte.dcsa              dte.dr


         d2J(w)              d2J(w)                d2J(w)
        -------  =  0   ,  ---------  =  0   ,    -------  =  0
        dRex**2            dRex.dcsa              dRex.dr


         d2J(w)             d2J(w)
        -------  =  0   ,  -------  =  0
        dcsa**2            dcsa.dr


        d2J(w)
        ------  =  0
        dr**2


    Extended:  Model-free parameter - Model-free parameter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

         d2J(w)
        -------  =  0
        dS2f**2


         d2J(w)
        --------  =  0
        dS2f.dS2


         d2J(w)        2        (tf + tm)^2 - (w.tf.tm)^2
        --------  =  - - tm^2 -----------------------------
        dS2f.dtf       5      ((tf + tm)^2 + (w.tf.tm)^2)^2


         d2J(w)      2        (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - tm^2 -----------------------------
        dS2f.dts     5      ((ts + tm)^2 + (w.ts.tm)^2)^2


        d2J(w)              d2J(w)
        ------  =  0   ,   -------  =  0
        dS2**2             dS2.dtf


         d2J(w)       2        (ts + tm)^2 - (w.ts.tm)^2
        -------  =  - - tm^2 -----------------------------
        dS2.dts       5      ((ts + tm)^2 + (w.ts.tm)^2)^2


        d2J(w)       4                  (tf + tm)^3 + 3.tm^3.tf.w^2.(tf + tm) - (w.tm)^4.tf^3
        ------  =  - - tm^2 . (1 - S2f) -----------------------------------------------------
        dtf**2       5                              ((tf + tm)^2 + (w.tf.tm)^2)^3


         d2J(w)
        -------  =  0
        dtf.dts


        d2J(w)       4                   (ts + tm)^3 + 3.tm^3.ts.w^2.(ts + tm) - (w.tm)^4.ts^3
        ------  =  - - tm^2 . (S2f - S2) -----------------------------------------------------
        dts**2       5                               ((ts + tm)^2 + (w.ts.tm)^2)^3


    Extended:  Other parameters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

          d2J(w)                d2J(w)               d2J(w)
        ---------  =  0   ,   ---------  =  0   ,   -------  =  0
        dS2f.dRex             dS2f.dcsa             dS2f.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dS2.dRex             dS2.dcsa             dS2.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dtf.dRex             dtf.dcsa             dtf.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dts.dRex             dts.dcsa             dts.dr


         d2J(w)               d2J(w)               d2J(w)
        -------  =  0   ,   ---------  =  0   ,   -------  =  0
        dRex**2             dRex.dcsa             dRex.dr


         d2J(w)              d2J(w)
        -------  =  0   ,   -------  =  0
        dcsa**2             dcsa.dr


        d2J(w)
        ------  =  0
        dr**2


    Extended 2:  Model-free parameter - Model-free parameter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

         d2J(w)
        -------  =  0
        dS2f**2


          d2J(w)      2    /      1                 (ts + tm).ts        \ 
        ---------  =  - tm | ------------  -  ------------------------- |
        dS2f.dS2s     5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


         d2J(w)        2        (tf + tm)^2 - (w.tf.tm)^2
        --------  =  - - tm^2 -----------------------------
        dS2f.dtf       5      ((tf + tm)^2 + (w.tf.tm)^2)^2


         d2J(w)      2                    (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - tm^2 . (1 - S2s) -----------------------------
        dS2f.dts     5                  ((ts + tm)^2 + (w.ts.tm)^2)^2


         d2J(w)              d2J(w)
        -------  =  0   ,   --------  =  0
        dS2s**2             dS2s.dtf


         d2J(w)        2              (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - - tm^2 . S2f -----------------------------
        dS2s.dts       5            ((ts + tm)^2 + (w.ts.tm)^2)^2


        d2J(w)       4                  (tf + tm)^3 + 3.tm^3.tf.w^2.(tf + tm) - (w.tm)^4.tf^3
        ------  =  - - tm^2 . (1 - S2f) -----------------------------------------------------
        dtf**2       5                              ((tf + tm)^2 + (w.tf.tm)^2)^3


         d2J(w)
        -------  =  0
        dtf.dts


        d2J(w)       4                     (ts + tm)^3 + 3.tm^3.ts.w^2.(ts + tm) - (w.tm)^4.ts^3
        ------  =  - - tm^2 . S2f(1 - S2s) -----------------------------------------------------
        dts**2       5                                 ((ts + tm)^2 + (w.ts.tm)^2)^3


    Extended 2:  Other parameters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

          d2J(w)                d2J(w)               d2J(w)
        ---------  =  0   ,   ---------  =  0   ,   -------  =  0
        dS2f.dRex             dS2f.dcsa             dS2f.dr


          d2J(w)                d2J(w)               d2J(w)
        ---------  =  0   ,   ---------  =  0   ,   -------  =  0
        dS2s.dRex             dS2s.dcsa             dS2s.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dtf.dRex             dtf.dcsa             dtf.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dts.dRex             dts.dcsa             dts.dr


         d2J(w)               d2J(w)               d2J(w)
        -------  =  0   ,   ---------  =  0   ,   -------  =  0
        dRex**2             dRex.dcsa             dRex.dr


         d2J(w)              d2J(w)
        -------  =  0   ,   -------  =  0
        dcsa**2             dcsa.dr


        d2J(w)
        ------  =  0
        dr**2
    """

    for j in range(len(data.params)):
        for k in range(j + 1):
            if calc_d2jw[j][k]:
                data.d2jw[:, :, j, k] = calc_d2jw[j][k](data)
                # Make the Hessian symmetric.
                if j != k:
                    data.d2jw[:, :, k, j] = data.d2jw[:, :, j, k]


# Original {S2, te}.
###################

def calc_iso_S2_te_d2jw_dS2dte(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2 - te double partial derivative of the
    original model-free formula with the parameters S2 and te.

    The model-free Hessian is:

         d2J(w)       2        (te + tm)^2 - (w.te.tm)^2
        -------  =  - - tm^2 -----------------------------
        dS2.dte       5      ((te + tm)^2 + (w.te.tm)^2)^2
    """

    return -data.fact_djw_dte


def calc_iso_S2_te_d2jw_dte2(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the te - te double partial derivative of the
    original model-free formula with the parameters S2 and te.

    The model-free Hessian is:

        d2J(w)       4                 (te + tm)^3 + 3.tm^3.te.w^2.(te + tm) - (w.tm)^4.te^3
        ------  =  - - tm^2 . (1 - S2) -----------------------------------------------------
        dte**2       5                             ((te + tm)^2 + (w.te.tm)^2)^3
    """

    num = data.te_tm**3 + 3.0 * data.diff_params[0]**3 * data.params[data.te_index] * data.frq_sqrd_list * data.te_tm - data.w_tm_sqrd**2 * data.params[data.te_index]**3
    return -2.0*data.two_fifths_tm_sqrd * data.one_s2 * num / data.te_denom**3


# Extended {S2f, S2, ts}.
#########################

def calc_iso_S2f_S2_ts_d2jw_dS2fdts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2f - ts double partial derivative of the
    extended model-free formula with the parameters S2f, S2, and ts.

    The model-free Hessian is:

         d2J(w)      2        (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - tm^2 -----------------------------
        dS2f.dts     5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return data.fact_djw_dts


def calc_iso_S2f_S2_ts_d2jw_dS2dts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2 - ts double partial derivative of the
    extended model-free formula with the parameters S2f, S2, and ts.

    The model-free Hessian is:

         d2J(w)       2        (ts + tm)^2 - (w.ts.tm)^2
        -------  =  - - tm^2 -----------------------------
        dS2.dts       5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return -data.fact_djw_dts


def calc_iso_S2f_S2_ts_d2jw_dts2(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the ts - ts double partial derivative of the
    extended model-free formula with the parameters S2f, S2, and ts.

    The model-free Hessian is:

        d2J(w)       4                   (ts + tm)^3 + 3.tm^3.ts.w^2.(ts + tm) - (w.tm)^4.ts^3
        ------  =  - - tm^2 . (S2f - S2) -----------------------------------------------------
        dts**2       5                               ((ts + tm)^2 + (w.ts.tm)^2)^3
    """

    num = data.ts_tm**3 + 3.0 * data.diff_params[0]**3 * data.params[data.ts_index] * data.frq_sqrd_list * data.ts_tm - data.w_tm_sqrd**2 * data.params[data.ts_index]**3
    return -2.0*data.two_fifths_tm_sqrd * data.s2f_s2 * num / data.ts_denom**3


# Extended {S2f, tf, S2, ts}.
#############################

def calc_iso_S2f_tf_S2_ts_d2jw_dS2fdtf(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2f - tf double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2, and ts.

    The model-free Hessian is:

         d2J(w)        2        (tf + tm)^2 - (w.tf.tm)^2
        --------  =  - - tm^2 -----------------------------
        dS2f.dtf       5      ((tf + tm)^2 + (w.tf.tm)^2)^2
    """

    return -data.fact_djw_dtf


def calc_iso_S2f_tf_S2_ts_d2jw_dS2fdts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2f - ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2, and ts.

    The model-free Hessian is:

         d2J(w)      2        (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - tm^2 -----------------------------
        dS2f.dts     5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return data.fact_djw_dts


def calc_iso_S2f_tf_S2_ts_d2jw_dS2dts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2 - ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2, and ts.

    The model-free Hessian is:

         d2J(w)       2        (ts + tm)^2 - (w.ts.tm)^2
        -------  =  - - tm^2 -----------------------------
        dS2.dts       5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return -data.fact_djw_dts


def calc_iso_S2f_tf_S2_ts_d2jw_dtf2(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the tf - tf double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2, and ts.

    The model-free Hessian is:

        d2J(w)       4                  (tf + tm)^3 + 3.tm^3.tf.w^2.(tf + tm) - (w.tm)^4.tf^3
        ------  =  - - tm^2 . (1 - S2f) -----------------------------------------------------
        dtf**2       5                              ((tf + tm)^2 + (w.tf.tm)^2)^3
    """

    num = data.tf_tm**3 + 3.0 * data.diff_params[0]**3 * data.params[data.tf_index] * data.frq_sqrd_list * data.tf_tm - data.w_tm_sqrd**2 * data.params[data.tf_index]**3
    return -2.0*data.two_fifths_tm_sqrd * data.one_s2f * num / data.tf_denom**3


def calc_iso_S2f_tf_S2_ts_d2jw_dts2(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the ts - ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2, and ts.

    The model-free Hessian is:

        d2J(w)       4                   (ts + tm)^3 + 3.tm^3.ts.w^2.(ts + tm) - (w.tm)^4.ts^3
        ------  =  - - tm^2 . (S2f - S2) -----------------------------------------------------
        dts**2       5                               ((ts + tm)^2 + (w.ts.tm)^2)^3
    """

    num = data.ts_tm**3 + 3.0 * data.diff_params[0]**3 * data.params[data.ts_index] * data.frq_sqrd_list * data.ts_tm - data.w_tm_sqrd**2 * data.params[data.ts_index]**3
    return -2.0*data.two_fifths_tm_sqrd * data.s2f_s2 * num / data.ts_denom**3


# Extended 2 {S2f, S2s, ts}.
############################

def calc_iso_S2f_S2s_ts_d2jw_dS2fdS2s(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2f/S2s double partial derivative of the
    extended model-free formula with the parameters S2f, S2s, and ts.

    The model-free Hessian is:

          d2J(w)      2    /      1                 (ts + tm).ts        \ 
        ---------  =  - tm | ------------  -  ------------------------- |
        dS2f.dS2s     5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.fact_djw_ds2s


def calc_iso_S2f_S2s_ts_d2jw_dS2fdts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2f/ts double partial derivative of the
    extended model-free formula with the parameters S2f, S2s, and ts.

    The model-free Hessian is:

         d2J(w)      2                    (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - tm^2 . (1 - S2s) -----------------------------
        dS2f.dts     5                  ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return data.fact_djw_dts * data.one_s2s


def calc_iso_S2f_S2s_ts_d2jw_dS2sdts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2s/ts double partial derivative of the
    extended model-free formula with the parameters S2f, S2s, and ts.

    The model-free Hessian is:

         d2J(w)        2              (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - - tm^2 . S2f -----------------------------
        dS2s.dts       5            ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return -data.fact_djw_dts * data.params[data.s2f_index]


def calc_iso_S2f_S2s_ts_d2jw_dts2(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the ts/ts double partial derivative of the
    extended model-free formula with the parameters S2f, S2s, and ts.

    The model-free Hessian is:

        d2J(w)       4                     (ts + tm)^3 + 3.tm^3.ts.w^2.(ts + tm) - (w.tm)^4.ts^3
        ------  =  - - tm^2 . S2f(1 - S2s) -----------------------------------------------------
        dts**2       5                                 ((ts + tm)^2 + (w.ts.tm)^2)^3
    """

    num = data.ts_tm**3 + 3.0 * data.diff_params[0]**3 * data.params[data.ts_index] * data.frq_sqrd_list * data.ts_tm - data.w_tm_sqrd**2 * data.params[data.ts_index]**3
    return -2.0*data.two_fifths_tm_sqrd * data.s2f_s2 * num / data.ts_denom**3



# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_iso_S2f_tf_S2s_ts_d2jw_dS2fdS2s(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2f/S2s double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

          d2J(w)      2    /      1                 (ts + tm).ts        \ 
        ---------  =  - tm | ------------  -  ------------------------- |
        dS2f.dS2s     5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.fact_djw_ds2s


def calc_iso_S2f_tf_S2s_ts_d2jw_dS2fdtf(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2f/ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

         d2J(w)        2        (tf + tm)^2 - (w.tf.tm)^2
        --------  =  - - tm^2 -----------------------------
        dS2f.dtf       5      ((tf + tm)^2 + (w.tf.tm)^2)^2
    """

    return -data.fact_djw_dtf


def calc_iso_S2f_tf_S2s_ts_d2jw_dS2fdts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2f/ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

         d2J(w)      2                    (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - tm^2 . (1 - S2s) -----------------------------
        dS2f.dts     5                  ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return data.fact_djw_dts * data.one_s2s


def calc_iso_S2f_tf_S2s_ts_d2jw_dS2sdts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the S2s/ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

         d2J(w)        2              (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - - tm^2 . S2f -----------------------------
        dS2s.dts       5            ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return -data.fact_djw_dts * data.params[data.s2f_index]


def calc_iso_S2f_tf_S2s_ts_d2jw_dtf2(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the ts/ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

        d2J(w)       4                  (tf + tm)^3 + 3.tm^3.tf.w^2.(tf + tm) - (w.tm)^4.tf^3
        ------  =  - - tm^2 . (1 - S2f) -----------------------------------------------------
        dtf**2       5                              ((tf + tm)^2 + (w.tf.tm)^2)^3
    """

    num = data.tf_tm**3 + 3.0 * data.diff_params[0]**3 * data.params[data.tf_index] * data.frq_sqrd_list * data.tf_tm - data.w_tm_sqrd**2 * data.params[data.tf_index]**3
    return -2.0*data.two_fifths_tm_sqrd * data.one_s2f * num / data.tf_denom**3


def calc_iso_S2f_tf_S2s_ts_d2jw_dts2(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity value for the ts/ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

        d2J(w)       4                     (ts + tm)^3 + 3.tm^3.ts.w^2.(ts + tm) - (w.tm)^4.ts^3
        ------  =  - - tm^2 . S2f(1 - S2s) -----------------------------------------------------
        dts**2       5                                 ((ts + tm)^2 + (w.ts.tm)^2)^3
    """

    num = data.ts_tm**3 + 3.0 * data.diff_params[0]**3 * data.params[data.ts_index] * data.frq_sqrd_list * data.ts_tm - data.w_tm_sqrd**2 * data.params[data.ts_index]**3
    return -2.0*data.two_fifths_tm_sqrd * data.s2f_s2 * num / data.ts_denom**3
