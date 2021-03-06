/*
 * Copyright (C) 2006,2014 Edward d'Auvergne
 * Copyright (C) 2006 Chris MacRaild
 * Copyright (C) 2006 Gary S Thompson
 *
 * This file is part of the program relax (http://www.nmr-relax.com).
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/* Get the maximum dimensions. */
#include "dimensions.h"

#ifndef RELAX_EXPONENTIAL 
#define RELAX_EXPONENTIAL

/* Define all of the functions. */
void exponential(double I0, double R, double relax_times[MAX_DATA], double back_calc[MAX_DATA], int num_times);
void exponential_dI0(double I0, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times);
void exponential_dR(double I0, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times);
void exponential_dI02(double I0, double R, int I0_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);
void exponential_dR_dI0(double I0, double R, int R_index, int IO_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);
void exponential_dR2(double I0, double R, int R_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);

void exponential_inv(double I0, double Iinf, double R, double relax_times[MAX_DATA], double back_calc[MAX_DATA], int num_times);
void exponential_inv_dI0(double I0, double Iinf, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times);
void exponential_inv_dIinf(double I0, double Iinf, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times);
void exponential_inv_dR(double I0, double Iinf, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times);
void exponential_inv_dI02(double I0, double Iinf, double R, int I0_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);
void exponential_inv_dIinf2(double I0, double Iinf, double R, int Iinf_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);
void exponential_inv_dI0_dIinf(double I0, double Iinf, double R, int I0_index, int Iinf_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);
void exponential_inv_dR_dI0(double I0, double Iinf, double R, int R_index, int I0_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);
void exponential_inv_dR_dIinf(double I0, double Iinf, double R, int R_index, int Iinf_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);
void exponential_inv_dR2(double I0, double Iinf, double R, int R_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);

void exponential_sat(double Iinf, double R, double relax_times[MAX_DATA], double back_calc[MAX_DATA], int num_times);
void exponential_sat_dIinf(double Iinf, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times);
void exponential_sat_dR(double Iinf, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times);
void exponential_sat_dIinf2(double Iinf, double R, int Iinf_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);
void exponential_sat_dR_dIinf(double Iinf, double R, int R_index, int I0_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);
void exponential_sat_dR2(double Iinf, double R, int R_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times);

/* Define the function for calculating the square of a number. */
#define square(x) ((x)*(x))

#endif
